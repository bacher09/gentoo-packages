from ..generic import ToStrMixin, file_get_content
from itertools import ifilter, izip
from functools import wraps
import collections
import os
import os.path

def reverse_enumerate(lst):
    return izip(xrange(len(lst)-1, -1, -1), reversed(lst))

def filter_predicate(file_name, file_path):
    full_file = os.path.join(file_path, file_name)
    return not file_name.startswith('.') and os.path.isfile(full_file)

class LicenseMixin(ToStrMixin):

    def get_license(self, license):
        try:
            return self[license]
        except (TypeError, KeyError):
            return None

class Licenses(LicenseMixin):
    __slots__ = ('is_valid', 'licenses_dict', 'licenses_path', 'tree_path')

    def __init__(self, tree_path):
        self.licenses_dict = {}
        self.is_valid = False
        self.tree_path = tree_path
        self.licenses_path = os.path.join(tree_path, 'licenses')
        if os.path.isdir(self.licenses_path):
            self.is_valid = True
            self._fetch_licenses_list()

    def _fetch_licenses_list(self):
        dir_list = os.listdir(self.licenses_path)
        f = lambda x: filter_predicate(x, self.licenses_path)
        licenses_list = ((s.lower(), s) for s in ifilter(f, dir_list))
        self.licenses_dict = dict(licenses_list)

    def __len__(self):
        return len(self.licenses_dict)

    def __contains__(self, item):
        item = unicode(item)
        return item.lower() in self.licenses_dict

    def __iter__(self):
        return self.licenses_dict.itervalues()

    def __eq__(self, other):
        if isinstance(other, Licenses):
            return other.tree_path == self.tree_path

    def __ne__(self, other):
        return not self.__eq__(other)

    def __or__(self, other):
        return LicensesSet([self, other])

    def hash(self):
        return hash(self.tree_path)

    def get_license_path(self, license):
        try:
            key = unicode(license).lower()
        except:
            raise TypeError
        return os.path.join(self.licenses_path, self.licenses_dict[key])

    def __getitem__(self, key):
        return file_get_content(self.get_license_path(key))

    def __unicode__(self):
        return unicode(self.tree_path)

def preinit_cache(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._cache_is_init:
            self._precache_objects()
        return func(self, *args, **kwargs)

    return wrapper

class LicensesSet(LicenseMixin):

    __slots__ = ('licenses_list', 'licenses_set', '_cache', '_cache_is_init')
    
    def __init__(self, val):
        self.licenses_list = []
        self.licenses_set = set()
        self._cache = {}
        self._cache_is_init = False
        if isinstance(val, LicensesSet):
            obj = val.copy()
            self.licenses_list = obj.licenses_list
            self.licenses_set = obj.licenses_set
            self._cache = obj._cache
            self._cache_is_init = obj._cache_is_init
        else:
            if not isinstance(val, collections.Iterable):
                raise TypeError

            for item in val:
                if not isinstance(item, Licenses):
                    raise TypeError
                self.add_licenses(item)

    def _precache_objects(self):
        cache = {}
        for num, licenses in reverse_enumerate(self.licenses_list):
            for key in licenses.licenses_dict.iterkeys():
                cache[key] = num
        self._cache = cache
        self._cache_is_init = True
        
    def copy(self):
        return LicensesSet(self.licenses_list)

    def add_licenses(self, licenses):   
        if not isinstance(licenses, Licenses):
            return None

        if (not licenses in self.licenses_set) and licenses.is_valid: 
            self.licenses_list.append(licenses)
            self.licenses_set.add(licenses)
            self._cache_is_init = False

    def merge(self, licenses):
        if isinstance(licenses, Licenses):
            self.add_licenses(licenses)
        elif isinstance(licenses, LicensesSet):
            for licenses in licenses.licenses_list:
                self.add_licenses(licenses)
        else:
            raise TypeError

    def __or__(self, other):
        try:
            obj = self.copy()
            obj.merge(other)
            return obj
        except TypeError:
            return NotImplemented

    def __ior__(self, other):
        return self.merge(other)

    @preinit_cache
    def __contains__(self, item):
        item = unicode(item)
        return item.lower() in self._cache

    @preinit_cache
    def __len__(self):
        return len(self._cache)

    @preinit_cache
    def __getitem__(self, key):
        try:
            key = unicode(key).lower()
        except:
            raise TypeError
        return  self.licenses_list[self._cache[key.lower()]][key]

    def __unicode__(self):
        res = ""
        for num ,licenses in enumerate(self.licenses_list):
            if num == 0:
                res += repr(licenses)
            else:
                res += ', %s' % repr(licenses)
        return '[%s]' % res

