import os.path
import hashlib
from datetime import datetime

class ToStrMixin(object):
    """Abstract class for inheritence, allow add simple `__str__` and `__repr__`
    methods
    """
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.__str__())


def file_sha1(file_path):
    sha1 = 'NULL'
    if os.path.exists(file_path):
        f = open(file_path, 'r')
        sha1 = hashlib.sha1(f.read()).hexdigest()
        f.close()
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
