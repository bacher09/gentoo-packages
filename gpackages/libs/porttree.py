import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from gentoolkit.package import Package as PackageInfo
from gentoolkit.metadata import MetaData
from generic import ToStrMixin, file_sha1, file_mtime, cached_property, \
                    file_get_content, StrThatIgnoreCase
from use_info import get_uses_info, get_local_uses_info
import os

BINDB = portage.db[portage.root]["bintree"].dbapi
PORTDB = portage.db[portage.root]["porttree"].dbapi
VARDB = portage.db[portage.root]["vartree"].dbapi

ARCHES = PORTDB.settings["PORTAGE_ARCHLIST"].split()

_license_filter = lambda x: False if x.startswith('|') or x.startswith('(') or \
                                     x.endswith('?') or x.startswith(')') \
                                  else True

def _file_path(file_name):
    return lambda self: os.path.join(self.package_path, file_name)


def _file_hash(attr):
    return lambda self: file_sha1(getattr(self, attr))

def _file_mtime(attr):
    return lambda self: file_mtime(getattr(self, attr))

def _ebuild_environment(name):
    return lambda self: self.package_object.environment(name)


def _get_info_by_func(func, path1, path2):
        path = os.path.join(path1, path2)
        try:
            return func(path)
        except IOError:
            return None

class FakeMetaData(ToStrMixin):

    def herds(self):
        return []

    def maintainers(self):
        return []

    def descriptions(self):
        return []
    
    def __unicode__(self):
        return 'fake'


class Use(ToStrMixin):
    "Represend Use flag as object"
    __slots__ = ('name',)

    def __init__(self, name):
        """Args:
            name -- name of use flag, may start with + or -
        """
        if name.startswith('+') or name.startswith('-'):
            name = name[1:]
        self.name = StrThatIgnoreCase(name)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        self.name == other.name

    def __ne__(self, other):
        self.name != other.name

    def __hash__(self):
        return hash(self.name)
        

class Keyword(ToStrMixin):
    "Represend ebuild Keyword as object"
    __slots__ = ('name', 'status')
    status_repr = ['','~','-']
    
    def __init__(self, name, status = 0):
        """Args:
            name -- name of keyword, it may start with ~ or -, if so than 
                    status will be auto seting.
            status -- status of keyword: 0 - stable, 
                                         1 - utested '~',
                                         2 - unstable '-'
                    Also may get by name parameter.
        """
        if name.startswith('~'):
            name = name[1:]
            status = 1
        elif name.startswith('-'):
            name = name[1:]
            status = 2
        self.name = name
        self.status = status

    def __unicode__(self):
        return self.status_repr[self.status] + self.name

    @property
    def arch(self):
        "Return arch name"
        return self.name

def _gen_all_use(func, iterator):
    use_g = iterator
    use_all_dict = next(use_g)
    for use_dict in use_g:
        if use_dict is not None:
            func(use_all_dict, use_dict)
    return use_all_dict

class Portage(object):

    def __init__(self):
        self.treemap = PORTDB.repositories.treemap
        self.tree_order = PORTDB.repositories.prepos_order

    def get_tree_by_name(self, tree_name):
        if tree_name in self.treemap:
            return PortTree(self.treemap[tree_name], tree_name)
        else:
            raise AttributeError
    
    def iter_trees(self):
        tree_dict = self.treemap
        for tree_name in self.tree_order:
            yield PortTree(tree_dict[tree_name], tree_name)

    def iter_packages(self):
        for tree in self.iter_trees():
            for package in tree.iter_package():
                yield package

    def iter_ebuilds(self):
        for tree in self.iter_trees():
            for ebuild in tree.iter_ebuilds():
                yield ebuild
    
    def iter_use_desc(self):
        for tree in self.iter_trees():
            yield tree.use_desc

    def iter_use_local_desc(self):
        for tree in self.iter_trees():
            yield tree.use_local_desc

    def get_all_use_desc(self):
        return _gen_all_use(lambda x,y: x.update(y), self.iter_use_desc())

    def get_all_use_local_desc(self):
        def action(all_dict, use_dict):
            for key, value in use_dict.iteritems():
                all_dict[key].update(value)

        return _gen_all_use(action, self.iter_use_local_desc())


class PortTree(ToStrMixin):
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

    def iter_packages(self):
        for category in self.iter_categories():
            for package in category.iter_packages():
                yield package
    
    def iter_ebuilds(self):
        for package in self.iter_packages():
            for ebuild in package.iter_ebuilds():
                yield ebuild

    def __unicode__(self):
        return self.porttree
    
    @property
    def porttree_path(self):
        "Full path to portage tree"
        return self.porttree

    @cached_property
    def use_desc(self):
        return _get_info_by_func(get_uses_info,
                                 self.porttree_path,
                                 'profiles/use.desc')

    @cached_property
    def use_local_desc(self):
        return _get_info_by_func(get_local_uses_info,
                                 self.porttree_path,
                                 'profiles/use.local.desc')


class Category(ToStrMixin):
    "Represent category of portage tree as object"

    __slots__ = ('porttree', 'category')
    
    def __init__(self, porttree, category):
        """Args:
            porttree -- PortTree object
            category -- category name as str
        """
        self.porttree = porttree
        self.category = category
    
    def iter_packages(self):
        packages = listdir(self.porttree.porttree + '/'+ self.category,
                           EmptyOnError=1, ignorecvs=1, dirsonly=1) 
        for package in packages:
            try:
                atom = Atom(self.category + '/' + package)
            except InvalidAtom:
                continue
            if atom != atom.cp:
                continue
            yield Package(self, atom)

    def __unicode__(self):
        return self.category
    
    @property
    def category_path(self):
        "Full path to category"
        return os.path.join(self.porttree.porttree_path, self.category)

    @property
    def porttree_path(self):
        return self.porttree.porttree


class Package(ToStrMixin):
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
            try:
                PORTDB.aux_get(ebuild, [], mytree = self.category.porttree_path)
            except KeyError:
                pass
            else:
                yield Ebuild(self ,ebuild)

    def __unicode__(self):
        return '%s' % self.package

    @property
    def package_path(self):
        return os.path.join(self.category.porttree.porttree_path, self.package)

    @cached_property
    def metadata(self):
        try:
            return MetaData( self.metadata_path)
        except IOError:
            return FakeMetaData()

    @property
    def cp(self):
        return self.package

    mtime = property(_file_mtime("package_path"))

    @property
    def name(self):
        return self.package.split('/')[1]

    manifest_path = property(_file_path('Manifest'))
    changelog_path = property(_file_path('ChangeLog'))
    metadata_path = property(_file_path('metadata.xml'))

    #Hashes
    manifest_sha1 = cached_property(_file_hash('manifest_path'),
                                    name = 'manifest_sha1')
    changelog_sha1 = cached_property(_file_hash('changelog_path'),
                                     name = 'changelog_sha1')
    metadata_sha1 = cached_property(_file_hash('metadata_path'),
                                    name = 'metadata_sha1')
    # Modify times
    manifest_mtime = property(_file_mtime("manifest_path"))
    changelog_mtime = property(_file_mtime("changelog_path"))
    metadata_mtime = property(_file_mtime("metadata_path"))

    @cached_property
    def descriptions(self):
        return self.metadata.descriptions()

    @property
    def description(self):
        if len(self.descriptions)>0:
            return self.descriptions[0]
        else:
            return None

    @cached_property
    def changelog(self):
        return file_get_content(self.changelog_path)


class Ebuild(ToStrMixin):
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
    def keywords(self):
        return list(set(self.keywords_env.split()))
    
    def iter_keywords(self):
        keywords = self.keywords
        for keyword in keywords:
            yield Keyword(keyword)
        
    def get_keywords(self):
        l = []
        for keyword in self.iter_keywords():
            l.append(keyword)
        return l

    def get_uses_names(self):
        return self.package_object.environment("IUSE").split()
    

    def iter_uses(self):
        for use in self.get_uses_names():
            yield Use(use)

    def get_uses(self):
        l = [] # Bad code, it repeats
        for use in self.iter_uses():
            l.append(use)
        return l

    #Could be faster
    @cached_property
    def is_masked(self):
        return self.package_object.is_masked()

    @property
    def version(self):
        return self.package_object.version

    @property
    def revision(self):
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
    def homepages(self):
        "List of homepages"
        ho_list = self.homepage_val.split()
        ret_list = []
        for ho in ho_list:
            ret_list.append(StrThatIgnoreCase(ho))
        return ret_list

    @cached_property
    def homepage(self):
        "First homepage in list"
        return self.homepages[0] if len(self.homepages)>=1 else ''


    @cached_property
    def licenses(self):
        "List of licenses used in ebuild"
        license_list = filter(_license_filter, self.license.split())
        ret_list = []
        for lic in license_list:
            ret_list.append(StrThatIgnoreCase(lic))
        return ret_list

    sha1 = cached_property(_file_hash("ebuild_path"), name = 'sha1')
    mtime = cached_property(_file_mtime("ebuild_path"), name = 'mtime')

    def __unicode__(self):
        return self.ebuild
    
