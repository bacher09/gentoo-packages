from __future__ import absolute_import
import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from ..generic import cached_property 
from ..parse_cp import EbuildParse
import os.path
#Mixins
from ..mixins import PortageMixin, PortTreeMixin, CategoryMixin, PackageMixin, \
                     EbuildMixin

__all__ = ('Portage','PortTree', 'Category', 'Package', 'Ebuild')

BINDB = portage.db[portage.root]["bintree"].dbapi
PORTDB = portage.db[portage.root]["porttree"].dbapi
VARDB = portage.db[portage.root]["vartree"].dbapi

ARCHES = PORTDB.settings["PORTAGE_ARCHLIST"].split()

def _ebuild_environment(name):
    return lambda self: self._env.get(name, '')

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

    @property
    def porttree_name(self):
        return self.porttree.name

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
        return os.path.join(self.category.porttree_path, self.package)

    @property
    def cp(self):
        return self.package

    @property
    def name(self):
        return self.package.split('/')[1]


class Ebuild(EbuildMixin):
    "Represent ebuild as object"

    __slots__ = ('package', 'ebuild', 'cpv_object', '_cache', '_env',
                 '_is_valid')
    ENV_VARS = PORTDB._aux_cache_keys

    def __init__(self, package, ebuild):
        self.package = package
        self.ebuild = ebuild
        self.cpv_object = EbuildParse(ebuild)
        self._cache = {}
        self._env = None
        # Maybe this should be lazy ?
        if not self.cpv_object.is_valid:
            self._is_valid = False
        else:
            self._set_env()

    def _set_env(self):
        try:
            env_t = PORTDB.aux_get(self.cpv, self.ENV_VARS,
                    mytree = self.package.category.porttree_path)
        except KeyError: 
            env_t = ()
            self._is_valid = False
        else:
            self._is_valid = True
        env = {}

        if self._is_valid:
            env = dict(zip(self.ENV_VARS, env_t))

        self._env = env

    @property
    def keywords_env(self):
        return self._env.get("KEYWORDS")

    @property
    def is_valid(self):
        "Check if ebuild is valid"
        return self._is_valid

    @cached_property
    def is_hard_masked(self):
        if self.mask_reason:
            return True
        else:
            return False

    @property
    def version(self):
        "Ebuild version"
        return self.cpv_object.version

    @property
    def revision(self):
        "Ebuild revision"
        return self.cpv_object.revision

    @property
    def fullversion(self):
        "Version with revision"
        return self.cpv_object.fullversion

    @cached_property
    def ebuild_path(self):
        "Full path to ebuild"
        return os.path.join(self.package.package_path, self.ebuild_file)

    @property
    def name(self):
        return self.cpv_object.name

    @property
    def ebuild_file(self):
        return '%s-%s.ebuild' % (self.name, self.fullversion)

    homepage_env = property(_ebuild_environment('HOMEPAGE'))
    license = property(_ebuild_environment('LICENSE'))
    description = property(_ebuild_environment('DESCRIPTION'))
    eapi = property(_ebuild_environment('EAPI'))
    slot = property(_ebuild_environment('SLOT'))

    iuse_env = property(_ebuild_environment('IUSE'))

    @property
    def cpv(self):
        return self.cpv_object.cpv

    @cached_property
    def mask_reason(self):
        reas, in_file = portage.getmaskingreason(self.cpv,
                                                 metadata = self._env,
                                                 return_location=True,
                                 myrepo = self.package.category.porttree_name)
        if in_file is None:
            return None
        elif in_file.startswith('/etc/portage/'):
            return None
        else:
            return reas
