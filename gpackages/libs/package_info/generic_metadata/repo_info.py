from __future__ import absolute_import
from functools import total_ordering
import os.path
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
    "Enum object"

    def __init__(self, lst):
        """Args:
        lst -- list of strings"""
        dct = {}
        dct2 = {}
        self.list = lst
        for num, item in enumerate(lst):
            dct[item] = num
            dct2[num] = item

        self.repo_dict = dct
        self.num_dict = dct2

    def get_as_tuple(self):
       "Return tuple to use as choices in django model"
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
    "Represent source of repository"

    def __init__(self, source_tuple):
        """Args:
            source_tuple -- tuple (source_url, source_type, source_subpath)
        """
        self.source_url = source_tuple[0].lower()
        self.source_type = REPOS_TYPE.repo_dict[source_tuple[1].lower()]
        self.source_subpath = source_tuple[2]

    def __hash__(self):
        return hash(self.source_url)

    def __eq__(self, other):
        if not isinstance(other, SourcesObject):
            return False
        return self.source_url == other.source_url

    def __lt__(self, other):
        if not isinstance(other, SourcesObject):
            return NotImplemented
        return self.source_url < other.source_url

    @property
    def type(self):
        return REPOS_TYPE.num_dict[self.source_type]

    def __unicode__(self):
        return self.source_url

class TreeMetadataMetaclass(type):
    """Dynamicaly add properties by `simple_attrs` tuple
    It gets this name from `_dct` dict in object"""
    
    def __init__(cls, name, bases, dct):
        super(TreeMetadataMetaclass, cls).__init__(name, bases, dct)
        for v in cls.simple_attrs:
            setattr(cls, v, property(_gen_funct(v)))

class TreeMetadata(ToStrMixin):
    "Represent metadata information about portage tree (overlay)"
    __metaclass__ = TreeMetadataMetaclass

    simple_attrs = ( 'name', 'description', 'supported', 'owner_name',
                     'official', 'irc'
                   )
    statuses = {'official': 0, 'unofficial': 1}
    qualities = {'stable': 0 , 'testing': 1, 'experimental': 2}

    storage_path = os.path.join(layman_api.config['storage'], '')
    installed = frozenset(layman_api.get_installed())
    available = frozenset(layman_api.get_available())

    def __init__(self, repo_name, repo_location = None, dct = None):
        """Args:
            repo_name -- repository name
            dct -- dict of params, could be None that it will be calculated 
        """
        repo_name = self._find_real_repo_name(repo_name, repo_location)
        self.repo_name = repo_name

        if dct is None:
            dct = self._get_info(repo_name)

        self._dct = dct

    def _find_name_by_path(self, repo_name, repo_location):
        try_name = repo_location.replace(self.storage_path, '')
        if try_name in self.installed:
            return try_name
        else:
            return None
        
    def _find_real_repo_name(self, repo_name, repo_location = None):
        gen_str = 'gentoo-'

        try_name = None
        if repo_location is not None:
            try_name = self._find_name_by_path(repo_name, repo_location)

        if repo_name == 'gentoo':
            return repo_name
        elif try_name is not None:
            return try_name
        elif repo_name in self.available:
            return repo_name
        elif (gen_str + repo_name) in self.available:
            return gen_str + repo_name
        elif repo_name.startswith(gen_str) and \
            (repo_name[len(gen_str):]) in self.available:

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
        "Return repostory status as int, int values a keys in `statuses`"
        return self.statuses.get(self._dct['status'], 1)

    @cached_property
    def homepage(self):
        "Return valid str homepage"
        homepage = self._dct.get('homepage')
        try:
            validate_url(homepage)
        except ValidationError:
            return None
        else:
            return homepage

    @cached_property
    def owner_email(self):
        "Return valid str owner email"
        email = self._dct.get('owner_email')
        try:
            validate_email(email)
        except ValidationError:
            return None
        else:
            return email

    @cached_property
    def feeds(self):
        "Return validated list of feeds"
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
        "Return list of `SourcesObject`s"
        ret = set() 
        for source in self._dct['sources']:
            ret.add(SourcesObject(source))
        return list(ret)

    @property
    def int_quality(self):
        "Return repostory quality as int, int values a keys in `qualities`"
        return self.qualities.get(self._dct['quality'], 2)

    def __unicode__(self):
        return self.repo_name

