import os.path
import hashlib
from datetime import datetime

__all__ = ('StrThatIgnoreCase', 'ToStrMixin', 'file_get_content', 'file_sha1', \
           'file_mtime', 'cached_property' )

class StrThatIgnoreCase(unicode):
    __slots__ = ('_forcmp',)

    def __init__(self, value):
        super(StrThatIgnoreCase, self).__init__(value)
        self._forcmp = value.lower()

    def __hash__(self):
        return hash(self._forcmp)

    def __eq__(self, other):
        return self._forcmp == unicode(other).lower()

    def __ne__(self, other):
        return self._forcmp != unicode(other).lower()

class ToStrMixin(object):
    """Abstract class for inheritence, allow add simple `__str__` and `__repr__`
    methods
    """
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.__str__())


def file_get_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    else:
        return None

def file_sha1(file_path):
    sha1 = 'NULL'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            sha1 = hashlib.sha1(f.read()).hexdigest()
    return sha1

def file_mtime(file_path):
    if os.path.exists(file_path):
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    else:
        return None

class cached_property(object):
    def __init__(self, func, name = None):
        self.func = func
        if name is None:
            name = func.__name__
        self.__name__ = name
        self.__module__ = func.__module__

    def __get__(self, inst, owner):
        try:
            value = inst._cache[self.__name__]
        except (KeyError, AttributeError):
            value = self.func(inst)
            if not hasattr(inst, '_cache'):
                inst._cache = {}
            inst._cache[self.__name__] = value
        return value
