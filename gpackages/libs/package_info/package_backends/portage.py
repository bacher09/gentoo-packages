from __future__ import absolute_import
import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from gentoolkit.package import Package as PackageInfo
from gentoolkit import errors
from ..generic import cached_property 
import os.path

# Not need
from ..generic_objects import Use, Keyword, KeywordsSet
#Mixins
from ..mixins import PortageMixin, PortTreeMixin, CategoryMixin, PackageMixin, \
                     EbuildMixin

__all__ = ('Portage','PortTree', 'Category', 'Package', 'Ebuild')

BINDB = portage.db[portage.root]["bintree"].dbapi
PORTDB = portage.db[portage.root]["porttree"].dbapi
VARDB = portage.db[portage.root]["vartree"].dbapi

ARCHES = PORTDB.settings["PORTAGE_ARCHLIST"].split()

def _ebuild_environment(name):
    return lambda self: self.package_object.environment(name)

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

    def __unicode__(self):
        return u'portage'

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
            self.eapi
        except errors.GentoolkitFatalError:
            return False
        else:
            return True

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

    homepage_env = cached_property(_ebuild_environment('HOMEPAGE'),
                                   name = 'homepage_env')
    license = cached_property(_ebuild_environment('LICENSE'),
                              name = 'license')
    description = cached_property(_ebuild_environment('DESCRIPTION'),
                                  name = 'description')
    eapi = cached_property(_ebuild_environment('EAPI'),
                           name = 'eapi')
    slot = cached_property(_ebuild_environment('SLOT'),
                           name = 'slot')

    iuse_env = cached_property(_ebuild_environment('IUSE'),
                           name = 'iuse')

    @property
    def cpv(self):
        return self.package
