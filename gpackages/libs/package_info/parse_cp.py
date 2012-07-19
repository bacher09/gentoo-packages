import re
from functools import total_ordering
from types import StringTypes
from .validators import REVISION_RE, VERSION_RE, NAME_RE
from .generic import ToStrMixin, toint, cached_property

PACKAGE_RE_P = r'(?P<category>[^/]+)/(?P<name>%(name)s)' %  \
                    {'name' : NAME_RE}

REPOSITORY_RE_P = r'(?:::(?P<repository>\w+))?'

PACKAGE_CPR_RE_P = r'%(base)s%(repository)s' % {'base' : PACKAGE_RE_P,
                                           'repository' : REPOSITORY_RE_P}

PACKAGE_RE = r'^%s$' % PACKAGE_RE_P
PACKAGE_CPV_RE = r'^%s$' % PACKAGE_CPR_RE_P

VERSIONS_RE_P = r'-(?P<version>%(version)s)(?:-(?P<revision>%(revision)s))?' % \
                    { 'version' : VERSION_RE,
                      'revision': REVISION_RE
                    }

EBUILD_CPV_RE_P = r'%(base)s%(versions)s' % {
                    'base': PACKAGE_RE_P,
                    'versions': VERSIONS_RE_P,
                   }

EBUILD_CPVR_RE_P = r'%(cpv)s%(repository)s' % {
                    'cpv': EBUILD_CPV_RE_P,
                    'repository': REPOSITORY_RE_P
                   }

EBUILD_CPV_RE = r'^%s$' % EBUILD_CPV_RE_P
EBUILD_CPVR_RE = r'^%s$' % EBUILD_CPVR_RE_P

VERSION_MAJ_P_RE = r'(?P<mver>(?P<num>(?:\d+\.)*\d+)(?P<alpha>[a-z])?)'
VERSION_PREFIX_RE = r'(?:_(?P<prefix>alpha|beta|pre|rc|p)(?P<prefix_num>\d*))?'
VERSION_MINS_P_RE = r'(?P<prefixes>(?:_(?:alpha|beta|pre|rc|p)(?:\d*))*)'
VERSION_P_RE = '^%(maj)s%(mins)s$' % {'maj'  : VERSION_MAJ_P_RE,
                                      'mins' : VERSION_MINS_P_RE }

package_re = re.compile(PACKAGE_RE)
package_cpr_re = re.compile(PACKAGE_CPV_RE)
ebuild_cpvr_re = re.compile(EBUILD_CPVR_RE)
ebuild_cpv_re = re.compile(EBUILD_CPV_RE)
version_parse_re = re.compile(VERSION_P_RE)
version_prefix_re = re.compile(VERSION_PREFIX_RE)

def maj_parse(nums, alpha):
    lst = []
    for num in nums.split('.'):
        rnum = toint(num)
        if rnum is not None:
            lst.append(rnum)
    if alpha:
        lst.append(alpha)
    return tuple(lst)

PREFIX_WEIGHT = {'alpha': 0, 'beta': 1, 'pre': 2, 'rc': 3, None: 4, 'p' : 5}
def prefix_info(prefix, prefix_num = 0):
    p_weight = PREFIX_WEIGHT.get(prefix, 4)
    if p_weight == 4:
        prefix_num = 0

    return (p_weight, toint(prefix_num, 0))

def min_parse(prefixes):
    if not prefixes:
        return (prefix_info(None),)

    lst = []
    for matched in version_prefix_re.finditer(prefixes):
        if matched is not None:
            dct = matched.groupdict()
            prefix, prefix_num = dct['prefix'], dct['prefix_num']
            if prefix is not None:
                lst.append(prefix_info(prefix, prefix_num))

    return tuple(lst)

REV_STR_RE = '^r(?P<rev>\d+)$'
rev_re = re.compile(REV_STR_RE)

class EbuildRevMixin(object):
    
    @cached_property
    def revision_as_int(self):
        d = 0 # Maybe None ?
        if self.revision:
            m = rev_re.match(self.revision)
            if m is not None:
                d = m.groupdict().get('rev')
                d = toint(d, 0)
        return d

@total_ordering
class VersionParse(ToStrMixin):

    __slots__ = ('version', 'maj', 'min', 'cmp_attr')
    
    def __init__(self, version):
        self.version = version
        m = version_parse_re.match(version)
        if m is None:
            raise ValueError('Bad version "%s"' % version)

        dct = m.groupdict()
        self.maj = maj_parse(dct['num'], dct['alpha'])
        self.min = min_parse(dct['prefixes'])
        self.cmp_attr = (self.maj, self.min)

    def __eq__(self, other):
        if not isinstance(other, VersionParse):
            return False
        return self.cmp_attr == other.cmp_attr

    def __lt__(self, other):
        if not isinstance(other, VersionParse):
            return NotImplemented
        return self.cmp_attr < other.cmp_attr

    def __unicode__(self):
        return unicode(self.version)

def _gen_func(name):
    return lambda self: self.gr_dict.get(name)

class ParseMetaClass(type):
    
    def __init__(cls, name, bases, dct):
        super(ParseMetaClass, cls).__init__(name, bases, dct)
        for v in cls.simple_attrs:
            setattr(cls, v, property(_gen_func(v)))

class PackageParse(ToStrMixin):
    
    __metaclass__ = ParseMetaClass
    re = package_re
    simple_attrs = ('category', 'name')
    
    def __init__(self, parse = None, dct = None):
        assert parse or dct, 'Should set parse or dct'
        self.parse_str = parse
        self.is_valid = False

        if parse is not None:
            m = self.re.match(parse)
            self.gr_dict = {}
            if m is not None:
                self.gr_dict = m.groupdict()
                self.is_valid = True
        elif dct is not None:
            self.gr_dict = dct

    def __unicode__(self):
        return unicode(self.parse_str)

    @property
    def re_str(self):
        return PACKAGE_RE_P

    @property
    def cp(self):
        return '%s/%s' % (self.category, self.name)

class PackageParseCPR(PackageParse):
    simple_attrs = ('category', 'name', 'repository')
    re = package_cpr_re

    @property
    def re_str(self):
        return PACKAGE_CPR_RE_P

    @property
    def repository_for_q(self):
        if self.repository:
            return self.repository
        else:
            return 'gentoo'

    @property
    def cpr(self):
        return '%s::%s' % (self.cp, self.repository_for_q)
    
class EbuildParse(EbuildRevMixin, PackageParse):
    #NOTICE: It three time faster than CPV from gentoolkit.cpv

    re = ebuild_cpv_re
    simple_attrs = ('category', 'name', 'version', 'revision')

    @property
    def re_str(self):
        return  EBUILD_CPV_RE_P

    @property
    def revision_for_q(self):
        if self.revision:
            return self.revision_as_int
        else:
            return 0

    @property
    def revision_as_str(self):
        if self.revision:
            return self.revision
        else:
            return ''

    @property
    def cpv(self):
        return '%s-%s' % (self.cp, self.fullversion)

    @property
    def fullversion(self):
        rev_p = '-' + self.revision if self.revision else ''
        return '%s%s' % (self.version, rev_p)

class EbuildParseCPVR(EbuildParse, PackageParseCPR):

    re = ebuild_cpvr_re
    simple_attrs = ('category', 'name', 'repository', 'version', 'revision')

    @property
    def re_str(self):
        return  EBUILD_CPVR_RE_P

    @property
    def cpvr(self):
        return '%s::%s' % (self.cpv, self.repository_for_q)
