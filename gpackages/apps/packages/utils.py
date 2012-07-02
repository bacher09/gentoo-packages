import re
from .validators import REVISION_RE, VERSION_RE, NAME_RE
from package_info.generic import ToStrMixin

def gen_args(args):
    t = '%s=%s'
    l = (t % arg for arg in args)
    return '&'.join(l)

def get_link(host, script, args):
    return 'http://%(host)s/%(script)s?%(args)' % {'host': host,
                                                   'script': script,
                                                   'args': get_args(args)}

BASE_PACKAGE_RE_P = r'(?P<category>[^/]+)/(?P<name>%(name)s)' %  \
                    {'name' : NAME_RE}

REPOSITORY_RE_P = r'(?:::(?P<repository>\w+))?'

PACKAGE_RE_P = r'%(base)s%(repository)s' % {'base' : BASE_PACKAGE_RE_P,
                                           'repository' : REPOSITORY_RE_P}

PACKAGE_RE = r'^%s$' % PACKAGE_RE_P

VERSIONS_RE_P = r'-(?P<version>%(version)s)(?:-(?P<revision>%(revision)s))?' % \
                    { 'version' : VERSION_RE,
                      'revision': REVISION_RE
                    }
EBUILD_CPVR_RE_P = r'%(base)s%(versions)s%(repository)s' % {
                    'base': BASE_PACKAGE_RE_P,
                    'versions': VERSIONS_RE_P,
                    'repository': REPOSITORY_RE_P
                   }

EBUILD_CPVR_RE = r'^%s$' % EBUILD_CPVR_RE_P

ebuild_cpvr_re = re.compile(EBUILD_CPVR_RE)
package_re = re.compile(PACKAGE_RE)

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
    simple_attrs = ('category', 'name', 'repository')
    
    def __init__(self, parse = None, dct = None):
        assert parse or dct, 'Shoud set or parse or dct'
        self.parse_str = parse

        if parse is not None:
            m = self.re.match(parse)
            self.gr_dict = {}
            if m is not None:
                self.gr_dict = m.groupdict()
        elif dct is not None:
            self.gr_dict = dct

    def __unicode__(self):
        return unicode(self.parse_str)

    @property
    def re_str(self):
        return PACKAGE_RE_P

    @property
    def repository_for_q(self):
        if self.repository:
            return self.repository
        else:
            return 'gentoo'

class EbuildParse(PackageParse):

    re = ebuild_cpvr_re
    simple_attrs = ('category', 'name', 'repository', 'version', 'revision')

    @property
    def re_str(self):
        return  EBUILD_CPVR_RE_P

    @property
    def revision_for_q(self):
        if self.revision:
            return self.revision
        else:
            return ''
