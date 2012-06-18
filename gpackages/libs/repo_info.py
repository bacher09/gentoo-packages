# Layman API
from layman.api import LaymanAPI
layman_api = LaymanAPI()

# Validators
from validators import validate_url, validate_email, ValidationError

__all__ = ('TreeMetadata',)

def _gen_funct(name):
    func = lambda self: self._dct.get(name)
    func.__name__ = name
    return func

class TreeMetadataMetaclass(type):
    
    def __init__(cls, name, bases, dct):
        super(TreeMetadataMetaclass, cls).__init__(name, bases, dct)
        for v in cls.simple_attrs:
            setattr(cls, v, property(_gen_funct(v)))

class TreeMetadata(object):
    __metaclass__ = TreeMetadataMetaclass

    simple_attrs = ( 'name', 'description', 'supported', 'owner_name',
                     'official', 'irc'
                   )
    statuses = {'official': 0, 'unofficial': 1}
    qualities = {'stable': 0 , 'testing': 1, 'experimental': 2}

    def __init__(self, repo_name, dct = None):
        if dct is None:
            dct = self._get_info(repo_name)

        self._dct = dct

    def _get_info(self, repo_name):
        if repo_name != 'gentoo':
            return layman_api.get_all_info(repo_name)[repo_name]
        else:
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
                   }

    @property
    def int_status(self):
        return self.statuses.get(self._dct['status'], 1)

    @property
    def homepage(self):
        homepage = self._dct.get('homepage')
        try:
            validate_url(homepage)
        except ValidationError:
            return None
        else:
            return homepage

    @property
    def owner_email(self):
        email = self._dct.get('owner_email')
        try:
            validate_email(email)
        except ValidationError:
            return None
        else:
            return email

    @property
    def feeds(self):
        ret = []
        for feed in self._dct.get('feeds', ()):
            try:
                validate_url(feed)
            except ValidationError:
                pass
            else:
                ret.append(feed)
        return ret

    @property
    def int_quality(self):
        return self.qualities.get(self._dct['quality'], 2)

