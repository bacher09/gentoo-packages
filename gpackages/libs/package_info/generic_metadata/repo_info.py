from __future__ import absolute_import
from functools import total_ordering
# Layman API
from layman.api import LaymanAPI
layman_api = LaymanAPI()

# Validators
from ..validators import validate_url, validate_email, ValidationError

from ..generic import ToStrMixin, cached_property

__all__ = ('TreeMetadata',)

def _gen_funct(name):
    func = lambda self: self._dct.get(name)
    func.__name__ = name
    return func

class Enum(object):

    def __init__(self, lst):
        dct = {}
        dct2 = {}
        self.list = lst
        for num, item in enumerate(lst):
            dct[item] = num
            dct2[num] = item

        self.repo_dict = dct
        self.num_dict = dct2

    def get_as_tuple(self):
       return tuple([(num, item) for num, item in enumerate(self.list)])
            
REPO_TYPE = (  'git', 
               'g-common',
               'cvs' ,
               'subversion',
               'rsync',
               'tar',
               'bzr',
               'mercurial',
               'darcs',
             )

REPOS_TYPE = Enum(REPO_TYPE)

@total_ordering
class SourcesObject(ToStrMixin):

    def __init__(self, source_tuple):
        self.source_url = source_tuple[0].lower()
        self.source_type = REPOS_TYPE.repo_dict[source_tuple[1].lower()]
        self.source_subpath = source_tuple[2]

    def __hash__(self):
        return hash(self.source_url)

    def __eq__(self, other):
        return self.source_url == other.source_url

    def __lt__(self, other):
        return self.source_url < other.source_url

    @property
    def type(self):
        return REPOS_TYPE.num_dict[self.source_type]

    def __unicode__(self):
        return self.source_url

class TreeMetadataMetaclass(type):
    
    def __init__(cls, name, bases, dct):
        super(TreeMetadataMetaclass, cls).__init__(name, bases, dct)
        for v in cls.simple_attrs:
            setattr(cls, v, property(_gen_funct(v)))

class TreeMetadata(ToStrMixin):
    __metaclass__ = TreeMetadataMetaclass

    simple_attrs = ( 'name', 'description', 'supported', 'owner_name',
                     'official', 'irc'
                   )
    statuses = {'official': 0, 'unofficial': 1}
    qualities = {'stable': 0 , 'testing': 1, 'experimental': 2}

    def __init__(self, repo_name, dct = None):
        repo_name = self._find_real_repo_name(repo_name)
        self.repo_name = repo_name

        if dct is None:
            dct = self._get_info(repo_name)

        self._dct = dct

    def _find_real_repo_name(self, repo_name):
        gen_str = 'gentoo-'

        if repo_name == 'gentoo':
            return repo_name
        elif layman_api.is_repo(repo_name):
            return repo_name
        elif layman_api.is_repo(gen_str + repo_name):
            return gen_str + repo_name
        elif repo_name.startswith(gen_str) and \
            layman_api.is_repo(repo_name[len(gen_str):]):

            return repo_name[len(gen_str):]

        return None

    def _get_info(self, repo_name):
        if repo_name == 'gentoo':
            return {'name': 'gentoo',
                    'description': 'Gentoo main repository',
                    'supported': True,
                    'owner_name': None,
                    'owner_email': None,
                    'official': True,
                    'irc': None,
                    'homepage': 'http://gentoo.org/',
                    'quality': 'stable',
                    'status': 'official',
                    'feeds': [],
                    'sources': [],
                   }
        elif repo_name is None:
            return {'name': 'none',
                    'description': None,
                    'quality': 'experimental',
                    'official': False,
                    'feeds': [],
                    'sources': [],
                   }
        else:
            return layman_api.get_all_info(repo_name)[repo_name]

    @property
    def int_status(self):
        return self.statuses.get(self._dct['status'], 1)

    @cached_property
    def homepage(self):
        homepage = self._dct.get('homepage')
        try:
            validate_url(homepage)
        except ValidationError:
            return None
        else:
            return homepage

    @cached_property
    def owner_email(self):
        email = self._dct.get('owner_email')
        try:
            validate_email(email)
        except ValidationError:
            return None
        else:
            return email

    @cached_property
    def feeds(self):
        ret = set()
        for feed in self._dct.get('feeds', ()):
            try:
                validate_url(feed)
            except ValidationError:
                pass
            else:
                ret.add(feed)
        return list(ret)

    @cached_property
    def sources(self):
        ret = set() 
        for source in self._dct['sources']:
            ret.add(SourcesObject(source))
        return list(ret)

    @property
    def int_quality(self):
        return self.qualities.get(self._dct['quality'], 2)

    def __unicode__(self):
        return self.repo_name

