import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from gentoolkit.package import Package as PackageInfo

BINDB = portage.db[portage.root]["bintree"].dbapi
PORTDB = portage.db[portage.root]["porttree"].dbapi
VARDB = portage.db[portage.root]["vartree"].dbapi

class Keyword(object):
    def __init__(self, name, is_stable = False):
        if name[0] == '~':
            name = name[1:]
            is_stable = False
        self.name = name
        self.is_stable = is_stable

    def __str__(self):
        return ('' if self.is_stable else '~' ) + self.name

    def __repr__(self):
        return '<Keyword %s>' % self.__str__()

class Portage(object):
    
    def iter_trees(self):
        for tree in PORTDB.porttrees:
            yield PortTree(tree)

    def iter_ebuilds():
        for tree in self.iter_trees():
            for ebuild in tree.iter_ebuilds():
                yield ebuild
    

class PortTree(object):
    
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
    
    def __repr__(self):
        return '<PortTree %s>' % self.porttree


class Category(object):
    
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
    
    def __repr__(self):
        return '<Category %s>' % self.category

class Package(object):
    def __init__(self, category, package):
        self.category = category
        self.package = package

    def iter_ebuilds(self):
        ebuilds = PORTDB.cp_list(self.package, mytree=self.category.porttree.porttree)
        for ebuild in ebuilds:
            yield Ebuild(self ,ebuild)

    def __repr__(self):
        return '<Package %s>' % self.package


class Ebuild(object):
    def __init__(self, package, ebuild):
        self.package = package
        self.ebuild = ebuild
        self.package_object = PackageInfo(ebuild)
    
    def iter_keyworkds(self):
        keywords = self.package_object.environment("KEYWORDS").split()
        for keyword in keywords:
            yield Keyword(keyword)
        
    def get_keywords(self):
        l = []
        for keyword in self.iter_keyworkds():
            l.append(keyword)
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
    def ebuild_path(self):
        return self.package_object.ebuild_path()

    @property
    def homepage(self):
        return self.package_object.environment('HOMEPAGE')
    
    @property
    def description(self):
        return self.package_object.environment('DESCRIPTION') # Bad code, it repeats many times
    
    def __repr__(self):
        return '<Ebuild %s>' % self.ebuild
