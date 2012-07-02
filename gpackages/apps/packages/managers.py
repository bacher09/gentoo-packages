from django.db import models, connections, router, transaction, IntegrityError
from package_info.abstract import AbstarctPackage, AbstractEbuild, \
                                  AbstractKeywords 
import packages.models
from package_info.generic import get_from_kwargs_and_del
from collections import defaultdict
from prefetch import PrefetchManagerMixin, PrefetchManager, PrefetchQuerySet, \
                     Prefetcher, P

def _gen_query_and_manager(MixinClass, QueryClassName, ManagerClassName):
    QueryClass = type(QueryClassName, (MixinClass, models.query.QuerySet), {})
    ManagerClass = type(ManagerClassName, (MixinClass, models.Manager),{
        'get_query_set': lambda self: QueryClass(self.model, using=self._db)
        })
    return QueryClass, ManagerClass

def _gen_all_query_and_manager(mixin_name, name_for_query, name_for_manager, *args):
    for arg in args:
        basename = arg.__name__
        if basename.endswith(mixin_name):
            end_index = len(basename) - len(mixin_name)
            basename = basename[ : end_index]
        q_name = basename + name_for_query
        m_name = basename + name_for_manager
        q, m = _gen_query_and_manager(arg, q_name, m_name)
        globals()[q_name], globals()[m_name] = q, m
        
class EbuildsWithKeywrods(Prefetcher):
    def __init__(self, keywords):
        self.keywords = keywords

    def filter(self, ids):
        return packages.models.EbuildModel.objects. \
            filter(package__in = ids).order_by('-version', '-revision'). \
            prefetch_keywords(self.keywords)

    def reverse_mapper(self, ebuild):
        return [ebuild.package_id]

    def decorator(self, package, ebuilds = ()):
        setattr(package, 'ebuilds', ebuilds)
        for ebuild in ebuilds:
            ebuild.package = package

class KeywordsPrefetch(Prefetcher):
    def __init__(self, arches):
        self.arches = arches

    def filter(self, ids):
        return packages.models.Keyword.objects. \
            filter(ebuild__in = ids, arch__name__in = self.arches). \
            select_related('arch')

    def reverse_mapper(self, keyword):
        return [keyword.ebuild_id]

    def decorator(self, ebuild, keywords = ()):
        setattr(ebuild, '_prefetched_keywords', keywords)


class PackageMixin(object):
    def get(self, package = None, *args, **kwargs):
        if package is not None and isinstance(package, AbstarctPackage):
            if 'category' not in kwargs:
                kwargs.update({'category' : package.category})
            name = package.name
            if len(args)>=1:
                args[0] = name
            if len(args)>=2:
                args[1] = category
            else:
                kwargs.update({'name': name})
        elif package is not None:
            # Bad code !!
            category, name = package.split('/')
            kwargs.update({'name': name, 'category': category})
        return super(PackageMixin, self).get(*args, **kwargs)

    def filter(self, **kwargs):
        category, name = get_from_kwargs_and_del(('category','name'), kwargs)
        if name is not None:
            kwargs.update({'virtual_package__name': name})
        if category is not None:
            if isinstance(category, packages.models.CategoryModel):
                kwargs.update({'virtual_package__category': category})
            else:
                kwargs.update({'virtual_package__category__category': category})

        return super(PackageMixin, self).filter(**kwargs)

class PackageQuerySet(PackageMixin, PrefetchQuerySet):
    def prefetch_keywords(self, arch_list):
        return self.prefetch(P('ebuilds', keywords = arch_list))

class PackageManager(PackageMixin, PrefetchManagerMixin):
    @classmethod
    def get_query_set_class(cls):
        return PackageQuerySet

    prefetch_definitions = {'ebuilds': EbuildsWithKeywrods}

class KeywordMixin(object):#{{{
    def get_or_create(self, keyword=None,  **kwargs):
        if keyword is not None:
            if isinstance(keyword, AbstractKeywords):
                arch, created = packages.models.ArchesModel.objects \
                    .get_or_create(name = keyword.name)
                kwargs.update({'arch': arch, 'status': keyword.status})
            else:
                raise ValueError("Bad keyword object")

        return super(KeywordMixin, self).get_or_create(**kwargs)#}}}


class EbuildMixin(object):

    def get(self, ebuild=None, package = None, *args, **kwargs):
        if ebuild is not None and isinstance(ebuild, AbstractEbuild):
            if package is None:
                kwargs.update({
                        'package__category__category': ebuild.package.category,
                        'package__name': ebuild.package.name })
            else:
                kwargs.update({'package': package})
            kwargs.update({ 'version': ebuild.version,
                            'revision': ebuild.revision_as_int })
        return super(EbuildMixin, self).get(*args, **kwargs)

    def all_by_numbers(self):
        return super(EbuildMixin, self).order_by('version', 'revision')

class EbuildQuerySet(EbuildMixin, PrefetchQuerySet):

    def prefetch_keywords(self, arch_list):
        return self.prefetch(P('keywords', arches = arch_list))

class EbuildManager(EbuildMixin, PrefetchManagerMixin):
    prefetch_definitions = {'keywords': KeywordsPrefetch}

    @classmethod
    def get_query_set_class(cls):
        return EbuildQuerySet

class HerdsMixin(object):#{{{
    def filter(self, *args, **kwargs):
        herd__in = get_from_kwargs_and_del('herd__in',kwargs)
        if herd__in is not None:
            kwargs['name__in'] = herd__in
        return super(HerdsMixin, self).filter(*args, **kwargs)#}}}


class MaintainerMixin(object):#{{{
    def filter(self, *args, **kwargs):
        maintainer__in, maintainer = \
            get_from_kwargs_and_del(['maintainer__in', 'maintainer'], kwargs)
        if maintainer__in is not None:
            kwargs['email__in'] = maintainer__in
        elif maintainer is not None:
            kwargs['email'] = maintainer.email
        return super(MaintainerMixin, self).filter(*args, **kwargs)#}}}

def get_name_and_category_by_cp(package):
    return package.split('/')


class VirtualPackageMixin(object):
    def filter(self,*args, **kwargs):
        package = get_from_kwargs_and_del('package', kwargs)
        if package is not None:
            category, name = get_name_and_category_by_cp(package)
            kwargs.update({'name': name, 'category__category': category})

        return super(VirtualPackageMixin, self).filter(*args, **kwargs)

class RepositoryMixin(object):
    def filter(self, *args, **kwargs):
        repo = get_from_kwargs_and_del('repo', kwargs)
        if repo is not None:
            kwargs['name'] = repo.name
        return super(RepositoryMixin, self).filter(*args, **kwargs)


_gen_all_query_and_manager('Mixin', 'QuerySet', 'Manager',
                           KeywordMixin, HerdsMixin,
                           MaintainerMixin, VirtualPackageMixin,
                           RepositoryMixin)
