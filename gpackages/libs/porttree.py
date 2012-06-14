from functools import total_ordering
from collections import defaultdict
import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from gentoolkit.package import Package as PackageInfo
from gentoolkit.metadata import MetaData
from gentoolkit import errors
from generic import ToStrMixin, file_sha1, file_mtime, cached_property, \
                    file_get_content, StrThatIgnoreCase, lofstr_to_ig
from use_info import get_uses_info, get_local_uses_info
import os

#XML
from my_etree import etree

# Validators
from django.core.validators import URLValidator, validate_email 
from django.core.exceptions import ValidationError

validate_url = URLValidator()

__all__ = ('Portage','PortTree', 'Category', 'Package', 'Ebuild')

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
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)
        
@total_ordering
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

    def __hash__(self):
        return hash((self.name, self.status))

    def is_same(self, other):
        return self.name == other.name

    def is_higer(self, other):
        return self.status < other.status

    def is_lower(self, other):
        return self.status > other.status

    def __eq__(self, other):
        return (self.arch, self.status) == (other.arch, other.status)

    def __lt__(self, other):
        return (self.status, self.arch) > (other.status, other.arch)

    @property
    def arch(self):
        "Return arch name"
        return self.name

class KeywordsSet(set):
    def __init__(self, init_list):
        start = defaultdict(list)
        for item in init_list:
            start[item.arch].append(item)

        to_create = []
        for item in start.itervalues():
            item.sort(reverse = True)
            if len(item)>=1:
                to_create.append(item[0])
        super(KeywordsSet, self).__init__(to_create)

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
            raise ValueError
    
    def iter_trees(self):
        tree_dict = self.treemap
        for tree_name in self.tree_order:
            yield PortTree(tree_dict[tree_name], tree_name)

    def iter_categories(self):
        for tree in self.iter_trees():
            for category in tree.iter_categories():
                yield category

    def iter_packages(self):
        for tree in self.iter_trees():
            for package in tree.iter_packages():
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

    @property
    def list_repos(self):
        return self.tree_order

    @property
    def dict_repos(self):
        return self.treemap


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
        return self.name
    
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

class CategoryMetadata(ToStrMixin):

    def __init__(self, metadata_path):
        self._metadata_path = metadata_path
        self._descrs = {}
        try:
            self._metadata_xml = etree.parse(metadata_path)
        except IOError:
            pass
        else:
            self._parse_descrs()

    def _parse_descrs(self):
        for descr_xml in self._metadata_xml.iterfind('longdescription'):
            lang = descr_xml.attrib.get('lang', 'en')
            self._descrs[lang] = descr_xml.text

    @property
    def descrs(self):
        return self._descrs

    @property
    def default_descr(self):
        return self._descrs.get('en')

    def __unicode__(self):
        return unicode(self._metadata_path)


class Category(ToStrMixin):
    "Represent category of portage tree as object"

    __slots__ = ('porttree', 'category', '_cache')
    
    def __init__(self, porttree, category):
        """Args:
            porttree -- PortTree object
            category -- category name as str
        """
        self.porttree = porttree
        self.category = category
        self._cache = {}
    
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
    def metadata_path(self):
        return os.path.join(self.category_path, 'metadata.xml')

    @cached_property
    def metadata_sha1(self):
        return file_sha1(self.metadata_path)

    @cached_property
    def metadata(self):
        return CategoryMetadata(self.metadata_path)

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
            ebuild_obj = Ebuild(self, ebuild)
            if ebuild_obj.is_valid:
                yield ebuild_obj

    def __unicode__(self):
        return '%s' % self.package

    @property
    def package_path(self):
        return os.path.join(self.category.porttree.porttree_path, self.package)

    @cached_property
    def metadata(self):
        "Return `MetaData` object that represent package metadata.xml file"
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
        "Return first description in package metadata.xml"
        if len(self.descriptions)>0:
            return self.descriptions[0]
        else:
            return None

    @cached_property
    def changelog(self):
        "Return ChangeLog content"
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

    sha1 = cached_property(_file_hash("ebuild_path"), name = 'sha1')
    mtime = cached_property(_file_mtime("ebuild_path"), name = 'mtime')

    def __unicode__(self):
        return self.ebuild
    
