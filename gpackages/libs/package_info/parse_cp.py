import re
from .validators import REVISION_RE, VERSION_RE, NAME_RE
from .generic import ToStrMixin
from .mixins import EbuildRevMixin

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

package_re = re.compile(PACKAGE_RE)
package_cpr_re = re.compile(PACKAGE_CPV_RE)
ebuild_cpvr_re = re.compile(EBUILD_CPVR_RE)
ebuild_cpv_re = re.compile(EBUILD_CPV_RE)

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
