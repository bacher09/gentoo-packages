import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from gentoolkit.package import Package as PackageInfo
from gentoolkit.metadata import MetaData
from gentoolkit import errors
from generic import cached_property, lofstr_to_ig 

import os.path

#Generic objects
from generic_objects import Use, Keyword, KeywordsSet

#Mixins
from mixins import PortageMixin, PortTreeMixin, CategoryMixin, PackageMixin, \
                   EbuildMixin

# Validators
from validators import validate_url, validate_url, ValidationError

from category_metadata import CategoryMetadata, FakeMetaData

__all__ = ('Portage','PortTree', 'Category', 'Package', 'Ebuild')

BINDB = portage.db[portage.root]["bintree"].dbapi
PORTDB = portage.db[portage.root]["porttree"].dbapi
VARDB = portage.db[portage.root]["vartree"].dbapi

ARCHES = PORTDB.settings["PORTAGE_ARCHLIST"].split()

_license_filter = lambda x: False if x.startswith('|') or x.startswith('(') or \
                                     x.endswith('?') or x.startswith(')') \
                                  else True

def _ebuild_environment(name):
    return lambda self: self.package_object.environment(name)


def _get_info_by_func(func, path1, path2):
        path = os.path.join(path1, path2)
        try:
            return func(path)
        except IOError:
            return None

def _gen_all_use(func, iterator):
    use_g = iterator
    use_all_dict = next(use_g)
    for use_dict in use_g:
        if use_dict is not None:
            func(use_all_dict, use_dict)
    return use_all_dict

class Portage(PortageMixin):

    def __init__(self):
        self.treemap = PORTDB.repositories.treemap
        self.tree_order = PORTDB.repositories.prepos_order

    def get_tree_by_name(self, tree_name):
        if tree_name in self.treemap:
            return PortTree(self.treemap[tree_name], tree_name)
        else:
            raise ValueError
    
    def iter_trees(self):
        tree_dict = self.treemap
        for tree_name in self.tree_order:
            yield PortTree(tree_dict[tree_name], tree_name)

    @property
    def list_repos(self):
        return self.tree_order

    @property
    def dict_repos(self):
        return self.treemap

class PortTree(PortTreeMixin):
    "Represent portage tree as object"

    def __init__(self, tree_path = '/usr/portage', name = 'main'):
        """Args:
            tree_path -- full path to portage tree as str
            name -- repo name as str
        """
        self.porttree = tree_path
        self.name = name

    def iter_categories(self):
        for category in sorted(PORTDB.settings.categories):
            if os.path.isdir(os.path.join(self.porttree_path, category)):
                    yield Category(self, category)
    
    @property
    def porttree_path(self):
        "Full path to portage tree"
        return self.porttree

class Category(CategoryMixin):
    "Represent category of portage tree as object"

    __slots__ = ('porttree', 'category', '_cache')

    def __init__(self, porttree, category):
        """Args:
            porttree -- PortTree object
            category -- category name as str
        """
        self.porttree = porttree
        self.name = category
        self._cache = {}
    
    def iter_packages(self):
        packages = listdir(self.porttree.porttree + '/'+ self.name,
                           EmptyOnError=1, ignorecvs=1, dirsonly=1) 
        for package in packages:
            try:
                atom = Atom(self.name + '/' + package)
            except InvalidAtom:
                continue
            if atom != atom.cp:
                continue
            yield Package(self, atom)

    @property
    def category_path(self):
        "Full path to category"
        return os.path.join(self.porttree_path, self.name)

    @property
    def porttree_path(self):
        return self.porttree.porttree

class Package(PackageMixin):
    "Represent package as object"

    __slots__ = ('category', 'package', '_cache')

    def __init__(self, category, package):
        self.category = category
        self.package = package
        self._cache = {}

    def iter_ebuilds(self):
        ebuilds = PORTDB.cp_list(self.package,
                                 mytree = self.category.porttree.porttree)
        for ebuild in ebuilds:
            ebuild_obj = Ebuild(self, ebuild)
            if ebuild_obj.is_valid:
                yield ebuild_obj

    @property
    def package_path(self):
        return os.path.join(self.category.porttree.porttree_path, self.package)

    @property
    def cp(self):
        return self.package

    @property
    def name(self):
        return self.package.split('/')[1]


class Ebuild(EbuildMixin):
    "Represent ebuild as object"

    __slots__ = ('package', 'ebuild', 'package_object', '_cache')

    def __init__(self, package, ebuild):
        self.package = package
        self.ebuild = ebuild
        self.package_object = PackageInfo(ebuild)
        self._cache = {}

    @property
    def keywords_env(self):
        return self.package_object.environment("KEYWORDS", prefer_vdb = False)

    @property
    def is_valid(self):
        "Check if ebuild is valid"
        try:
            self.package_object.environment("EAPI")
        except errors.GentoolkitFatalError:
            return False
        else:
            return True


    @property
    def keywords(self):
        return list(set(self.keywords_env.split()))
    
    def iter_keywords(self):
        "Iterate over keywords, yields Keyword object"
        keywords = self.keywords
        for keyword in keywords:
            yield Keyword(keyword)
        
    def get_keywords(self):
        l = []
        for keyword in self.iter_keywords():
            l.append(keyword)
        return l

    def get_uniq_keywords(self):
        return KeywordsSet(self.get_keywords())

    def get_uses_names(self):
        return self.package_object.environment("IUSE").split()
    

    def iter_uses(self):
        "Iterator over all uses, yiels `Use` object"
        for use in self.get_uses_names():
            yield Use(use)

    def get_uses(self):
        l = [] # Bad code, it repeats
        for use in self.iter_uses():
            l.append(use)
        return l

    def get_uniq_uses(self):
        return frozenset(self.get_uses())

    #Could be faster
    @cached_property
    def is_masked(self):
        return self.package_object.is_masked()

    @property
    def version(self):
        "Ebuild version"
        return self.package_object.version

    @property
    def revision(self):
        "Ebuild revision"
        return self.package_object.revision

    @property
    def fullversion(self):
        "Version with revision"
        return self.package_object.fullversion

    @property
    def ebuild_path(self):
        "Full path to ebuild"
        return self.package_object.ebuild_path()

    homepage_val = cached_property(_ebuild_environment('HOMEPAGE'),
                                   name = 'homepage_val')
    license = cached_property(_ebuild_environment('LICENSE'),
                              name = 'license')
    description = cached_property(_ebuild_environment('DESCRIPTION'),
                                  name = 'description')
    eapi = cached_property(_ebuild_environment('EAPI'),
                           name = 'eapi')
    slot = cached_property(_ebuild_environment('SLOT'),
                           name = 'slot')

    @cached_property
    def homepages_splited(self):
        return self.homepage_val.split()

    @cached_property
    def homepages_validated(self):
        ret = []
        for homepage in self.homepages_splited:
            try:
                validate_url(homepage)
            except ValidationError:
                pass
            else:
                ret.append(homepage)
        return ret
        

    @cached_property
    def homepages(self):
        "Tuple of homepages"
        return tuple(set(lofstr_to_ig(self.homepages_validated)))

    @cached_property
    def homepage(self):
        "First homepage in list"
        return self.homepages_validated[0] if len(self.homepages)>=1 else ''

    @cached_property
    def _licenses(self):
        return filter(_license_filter, self.license.split())

    @cached_property
    def licenses(self):
        return tuple(set(lofstr_to_ig(self._licenses)))

    @property
    def cpv(self):
        return self.package
