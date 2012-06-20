from pkgcore.config import load_config
from pkgcore.ebuild.repository import UnconfiguredTree, SlavedTree
from pkgcore.util.repo_utils import get_raw_repos, get_virtual_repos
from pkgcore.ebuild.atom import atom

from generic import ToStrMixin

from porttree import AutoGeneratorMixin

import os.path


class Portage(AutoGeneratorMixin):

    generator_names = ('iter_categories', 'iter_packages', 'iter_ebuilds')
    main_iterator = 'iter_trees'

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
        finally:
            self._domain = domain

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
            yield PortTree(tree)

    def get_tree_by_name(self, tree_name):
        if tree_name in self.repo_dict:
            return PortTree(self.tree_dict[tree_name])
        else:
            raise ValueError
        
class PortTree(ToStrMixin, AutoGeneratorMixin):

    generator_names = ('iter_packages', 'iter_ebuilds')
    main_iterator = 'iter_categories'

    def __init__(self, repo_obj):
        self._repo_obj = repo_obj
        self.name = repo_obj.repo_id
        self.categories = sorted(repo_obj.categories)

    def iter_categories(self):
        for category in self.categories:
            yield Category(category, self)

    @property
    def porttree_path(self):
        "Full path to portage tree"
        return self._repo_obj.location

    def __unicode__(self):
        return self.name

    @property
    def _packages(self):
        return self._repo_obj.packages

    def _itermatch(self, res):
        return self._repo_obj.itermatch(res)

    @property
    def _versions(self):
        return self._repo_obj.versions

class Category(ToStrMixin, AutoGeneratorMixin):

    generator_names = ('iter_ebuilds', )
    main_iterator = 'iter_packages'
    
    def __init__(self, category_name, repo_obj):
        self._repo_obj = repo_obj
        self.name = category_name

    def iter_packages(self):
        for package_name in self._get_packages_names():
            yield Package(package_name, self)

    @property
    def category_path(self):
        "Full path to category"
        return os.path.join(self.porttree_path, self.category)

    def _get_packages_names(self):
        return self._repo_obj._packages[self.name]

    def _get_ebuilds_names_by_name(self, package_name):
        return self._repo_obj._versions[(self.name, package_name)]

    def __unicode__(self):
        return self.name

class Package(ToStrMixin):
    
    def __init__(self, package_name, category_obj):
        self.name = package_name
        self.category_obj = category_obj

    def iter_ebuilds(self):
        for ebuild in self.category_obj._repo_obj._itermatch(atom(self.cp)):
            yield Ebuild(ebuild, self)

    def __unicode__(self):
        return self.cp

    def _get_ebuilds_versions(self):
        return self.category_obj._get_ebuilds_names_by_name(self.name)

    @property
    def cp(self):
        return '%s/%s' % (self.category_obj.name, self.name)


class Ebuild(ToStrMixin):
    
    def __init__(self, ebuild, package_obj):
        self._ebuild = ebuild
        self.package_obj = package_obj

    def __unicode__(self):
        return self.cpv

    @property
    def cpv(self):
        return self._ebuild.cpvstr
