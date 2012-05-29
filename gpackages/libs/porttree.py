import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from gentoolkit.package import Package as PackageInfo
import hashlib
import os

BINDB = portage.db[portage.root]["bintree"].dbapi
PORTDB = portage.db[portage.root]["porttree"].dbapi
VARDB = portage.db[portage.root]["vartree"].dbapi

_license_filter = lambda x: False if x.startswith('|') or x.startswith('(') or \
                                     x.endswith('?') or x.startswith(')') \
                                  else True

def _file_path(file_name):
    return lambda self: os.path.join(self.package_path, file_name)


def _file_hash(attr):
    return lambda self: file_sha1(getattr(self, attr))

def _ebuild_environment(name):
    return lambda self: self.package_object.environment(name)

def file_sha1(file_path):
    sha1 = 'NULL'
    if os.path.exists(file_path):
        f = open(file_path, 'r')
        sha1 = hashlib.sha1(f.read()).hexdigest()
        f.close()
    return sha1


class ToStrMixin(object):
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.__str__())

class Use(ToStrMixin):
    def __init__(self, name):
        if name.startswith('+') or name.startswith('-'):
            name = name[1:]
        self.name = name

    def __unicode__(self):
        return self.name


class Keyword(ToStrMixin):
    status_repr = ['','~','-']
    
    def __init__(self, name, status = 0):
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


class Portage(object):
    
    def iter_trees(self):
        for tree in PORTDB.porttrees:
            yield PortTree(tree)

    def iter_ebuilds():
        for tree in self.iter_trees():
            for ebuild in tree.iter_ebuilds():
                yield ebuild
    

class PortTree(ToStrMixin):
    
    def __init__(self, porttree = '/usr/portage'):
        self.porttree = porttree # TODO: it should be read-only

    def iter_categories(self):
        for category in PORTDB.settings.categories:
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
        return self.porttree


class Category(ToStrMixin):
    
    def __init__(self, porttree, category):
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
        return os.path.join(self.porttree.porttree_path, self.category)


class Package(ToStrMixin):
    def __init__(self, category, package):
        self.category = category
        self.package = package

    def iter_ebuilds(self):
        ebuilds = PORTDB.cp_list(self.package, mytree=self.category.porttree.porttree)
        for ebuild in ebuilds:
            yield Ebuild(self ,ebuild)

    def __unicode__(self):
        return '%s' % self.package

    @property
    def package_path(self):
        return os.path.join(self.category.porttree.porttree_path, self.package)

    @property
    def name(self):
        return self.package.split('/')[1]

    manifest_path = property(_file_path('Manifest'))
    changelog_path = property(_file_path('ChangeLog'))
    manifest_sha1 = property(_file_hash('manifest_path'))
    changelog_sha1 = property(_file_hash('changelog_path'))


class Ebuild(ToStrMixin):
    def __init__(self, package, ebuild):
        self.package = package
        self.ebuild = ebuild
        self.package_object = PackageInfo(ebuild)
    
    def iter_keywords(self):
        keywords = self.package_object.environment("KEYWORDS").split()
        for keyword in keywords:
            yield Keyword(keyword)
        
    def get_keywords(self):
        l = []
        for keyword in self.iter_keyworkds():
            l.append(keyword)
        return l

    def iter_uses(self):
        uses = self.package_object.environment("IUSE").split()
        for use in uses:
            yield Use(use)

    def get_uses(self):
        l = [] # Bad code, it repeats
        for use in self.iter_uses():
            l.append(use)
        return l

    @property
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
        return self.package_object.fullversion

    @property
    def ebuild_path(self):
        return self.package_object.ebuild_path()

    homepage = property(_ebuild_environment('HOMEPAGE'))
    license = property(_ebuild_environment('LICENSE'))
    description = property(_ebuild_environment('DESCRIPTION'))

    @property
    def licenses(self):
        return filter(_license_filter, self.license.split())

    @property
    def ebuild_path(self):
        return self.package_object.ebuild_path()

    @property
    def sha1(self):
        return file_sha1(self.ebuild_path)

    def __unicode__(self):
        return self.ebuild
    
