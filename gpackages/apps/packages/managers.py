from django.db import models
from porttree import Category, Package, Ebuild, Keyword
import packages.models


def _gen_query_and_manager(MixinClass, QueryClassName, ManagerClassName):
    QueryClass = type(QueryClassName, (MixinClass, models.query.QuerySet), {})
    ManagerClass = type(ManagerClassName, (MixinClass, models.Manager),{
        'get_query_set': lambda self: QueryClass(self.model, using=self._db)
        })
    return QueryClass, ManagerClass

class PackageMixin(object):
    def get(self, package = None, *args, **kwargs):
        if package is not None and isinstance(package, Package):
            try:
                category = packages.models.CategoryModel.objects.get(category = package.category)
            except packages.models.CategoryModel.DoesNotExist:
                raise self.model.DoesNotExist
            name = package.name
            if len(args)>=1:
                args[0] = name
            if len(args)>=2:
                args[1] = category
            else:
                kwargs.update({'name': name, 'category': category})
        return super(PackageMixin, self).get(*args, **kwargs)

PackageQuerySet, PackageManager = _gen_query_and_manager(PackageMixin, 
                                                        'PackageQuerySet',
                                                        'PackageManager')

class KeywordMixin(object):
    def get_or_create(self, keyword=None,  **kwargs):
        if keyword is not None:
            if isinstance(keyword, Keyword):
                arch, created = packages.models.ArchesModel.objects.get_or_create(name = keyword.name)
                kwargs.update({'arch': arch, 'is_stable': keyword.is_stable })
            else:
                raise ValueError("Bad keyword object")

        return super(KeywordMixin, self).get_or_create(**kwargs)

KeywordQuerySet, KeywordManager = _gen_query_and_manager(KeywordMixin, 
                                                        'KeywordQuerySet',
                                                        'KeywordManager')

class EbuildMixin(object):
    def get(self, ebuild=None, *args, **kwargs):
        if ebuild is not None and isinstance(ebuild, Ebuild):
            try:
                package = packages.models.PackageModel.objects.get(package = ebuild.package)
            except packages.models.PackageModel.DoesNotExist:
                raise self.model.DoesNotExist
            version = ebuild.version
            revision = ebuild.revision
            kwargs.update({ 'version': version,
                            'revision': revision,
                            'package': package })
        return super(EbuildMixin, self).get(*args, **kwargs)
            


EbuildQuerySet, EbuildManager =   _gen_query_and_manager(EbuildMixin,
                                                        'EbuildQuerySet',
                                                        'EbuildManager')
