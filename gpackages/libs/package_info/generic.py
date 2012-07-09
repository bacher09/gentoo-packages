import os.path
import hashlib
import types
from datetime import datetime

__all__ = ('StrThatIgnoreCase', 'ToStrMixin', 'file_get_content', 'file_sha1',\
           'file_mtime', 'cached_property', 'iter_over_gen', 'lofstr_to_ig', \
           'toint', 'Enum')

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

def iter_over_gen(iterat, name):
    for obj in iterat:
        for item in getattr(obj, name)():
            yield item
def del_from_dict(what_list, dict_todel):
    for item in what_list:
        if item in dict_todel:
            del dict_todel[item]
    #dict_todel already modified
    return dict_todel

def get_from_kwargs_and_del(list_what, kwargs):
    ret_list = []
    if isinstance(list_what, types.StringTypes):
        list_what = (list_what, )
    for item in list_what:
        if item in kwargs:
            ret_list.append(kwargs[item])
        else:
            ret_list.append(None)
    del_from_dict(list_what, kwargs)
    if len(ret_list)==1:
        return ret_list[0]
    else:
        return ret_list
            
def toint(val, defval):
    try:
        return int(val)
    except ValueError:
        return defval

class StrThatIgnoreCase(unicode):
    __slots__ = ('_forcmp',)

    def __init__(self, value):
        super(StrThatIgnoreCase, self).__init__(value)
        self._forcmp = self.lower()

    def __hash__(self):
        return hash(self._forcmp)

    def __eq__(self, other):
        return self._forcmp == unicode(other).lower()

    def __ne__(self, other):
        return self._forcmp != unicode(other).lower()

def lofstr_to_ig(list_obj):
    return [ StrThatIgnoreCase(item) for item in list_obj]

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
        self.__doc__ = func.__doc__

    def __get__(self, inst, owner):
        try:
            value = inst._cache[self.__name__]
        except (KeyError, AttributeError):
            value = self.func(inst)
            if not hasattr(inst, '_cache'):
                inst._cache = {}
            inst._cache[self.__name__] = value
        return value
