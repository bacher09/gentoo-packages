from __future__ import absolute_import
import os.path
from pkgcore.config import load_config, errors
from pkgcore.ebuild.repository import UnconfiguredTree, SlavedTree
from pkgcore.util.repo_utils import get_raw_repos, get_virtual_repos
from pkgcore.ebuild.atom import atom
from pkgcore.ebuild.domain import generate_unmasking_restrict

#Mixins
from ..mixins import PortageMixin, PortTreeMixin, CategoryMixin, PackageMixin, \
                     EbuildMixin

__all__ = ('Portage','PortTree', 'Category', 'Package', 'Ebuild')

class Portage(PortageMixin):

    def __init__(self):
        self._config = load_config()
        self._domains = self._config.domain
        self._set_default_domain('livefs domain')
        self._get_repos()

    def _set_default_domain(self, domain_name):
        domain = None
        try:
            domain = self._domains[domain_name]
        except KeyError:
            raise ValueError("Bad domain name - '%s'" % domain_name)
        else:
            self._domain = domain
            self._mask = generate_unmasking_restrict(domain.profile.masks)

    def _get_repos(self):
        repo_dict = {}
        repo_list = []
        repos = get_virtual_repos(get_raw_repos(self._domain.repos), False)
        for repo in repos:
            if isinstance(repo, UnconfiguredTree) or isinstance(repo, SlavedTree):
                repo_dict[repo.repo_id] = repo
                repo_list.append(repo)
        repo_list.reverse()
        self.repo_list = repo_list
        self.repo_dict = repo_dict

    def iter_trees(self):
        for tree in self.repo_list:
            yield PortTree(tree, self)

    def get_tree_by_name(self, tree_name):
        if tree_name in self.repo_dict:
            return PortTree(self.repo_dict[tree_name])
        else:
            raise ValueError

    def is_masked(self, ebuild):
        return self._mask.match(ebuild)

    def __unicode__(self):
        return u'pkgcore'

    def __len__(self):
        return len(self.repo_list)
        
class PortTree(PortTreeMixin):

    def __init__(self, repo_obj, porttree):
        self._repo_obj = repo_obj
        self.name = repo_obj.repo_id
        self.categories = sorted(repo_obj.categories)
        self.porttree = porttree

    def iter_categories(self):
        for category in self.categories:
            yield Category(category, self)

    @property
    def porttree_path(self):
        "Full path to portage tree"
        return self._repo_obj.location

    @property
    def _packages(self):
        return self._repo_obj.packages

    def _itermatch(self, res):
        return self._repo_obj.itermatch(res)

    @property
    def _versions(self):
        return self._repo_obj.versions

    def __len__(self):
        return len(self.categories)

class Category(CategoryMixin):
    
    __slots__ = ('_repo_obj', 'name')
    
    def __init__(self, category_name, repo_obj):
        self._repo_obj = repo_obj
        self.name = category_name

    def iter_packages(self):
        for package_name in self._get_packages_names():
            yield Package(package_name, self)

    @property
    def category_path(self):
        "Full path to category"
        return os.path.join(self.porttree_path, self.name)

    def _get_packages_names(self):
        return self._repo_obj._packages[self.name]

    def _get_ebuilds_names_by_name(self, package_name):
        return self._repo_obj._versions[(self.name, package_name)]

    @property
    def porttree_name(self):
        return self._repo_obj.name

    @property
    def porttree_path(self):
        return self._repo_obj.porttree_path

class Package(PackageMixin):

    __slots__ = ('name', 'category')
    
    def __init__(self, package_name, category):
        self.name = package_name
        self.category = category

    def iter_ebuilds(self):
        for ebuild in self.category._repo_obj._itermatch(atom(self.cp)):
            yield Ebuild(ebuild, self)

    def _get_ebuilds_versions(self):
        return self.category._get_ebuilds_names_by_name(self.name)

    @property
    def cp(self):
        return '%s/%s' % (self.category.name, self.name)

    @property
    def package_path(self):
        return os.path.join(self.category.category_path, self.name)


ebuild_prop = lambda var: property(lambda self: getattr(self._ebuild, var))

class Ebuild(EbuildMixin):
    
    __slots__ = ('_ebuild', 'package')

    def __init__(self, ebuild, package):
        self._ebuild = ebuild
        self.package = package

    ebuild_path = ebuild_prop('path')

    version = ebuild_prop('version')

    #revision = ebuild_prop('revision')
    @property
    def revision(self):
        if self._ebuild.revision is None:
            return ''
        else:
            return 'r' + str(self._ebuild.revision)

    fullversion = ebuild_prop('fullver')

    eapi = ebuild_prop('eapi')

    slot = ebuild_prop('slot')

    iuse = ebuild_prop('iuse')

    description = ebuild_prop('description')

    @property
    def iuse_env(self):
        return ' '.join(self.iuse)

    homepage_env = ebuild_prop('homepage')

    @property
    def keywords_env(self):
        return ' '.join(self.keywords)

    keywords = ebuild_prop('keywords')
    
    @property
    def license(self):
        return unicode(self._ebuild.license)

    cpv = ebuild_prop('cpvstr')

    @property
    def is_hard_masked(self):
        return self.package.category._repo_obj. \
            porttree.is_masked(self._ebuild)

    @property
    def depends(self):
        return str(self._ebuild.depends)

    @property
    def rdepends(self):
        return str(self._ebuild.rdepends)

    @property
    def pdepends(self):
        return str(self._ebuild.post_rdepends)
