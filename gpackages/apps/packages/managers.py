from django.db import models
from porttree import Category, Package, Ebuild, Keyword
import packages.models


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

class PackageQuerySet(PackageMixin, models.query.QuerySet):
    pass

class PackageManager(PackageMixin, models.Manager):
    def get_query_set(self):
        return PackageQuerySet(self.model, using=self._db)


class KeywordMixin(object):
    def get_or_create(self, keyword=None,  **kwargs):
        if keyword is not None:
            if isinstance(keyword, Keyword):
                arch, created = packages.models.ArchesModel.objects.get_or_create(name = keyword.name)
                kwargs.update({'arch': arch, 'is_stable': keyword.is_stable })
            else:
                raise ValueError("Bad keyword object")

        return super(KeywordMixin, self).get_or_create(**kwargs)

class KeywordQuerySet(KeywordMixin, models.query.QuerySet):
    pass

class KeywordManager(KeywordMixin, models.Manager):
    def get_query_set(self):
        return KeywordQuerySet(self.model, using=self._db)


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
            

class EbuildQuerySet(EbuildMixin, models.query.QuerySet):
    pass

class EbuildManager(EbuildMixin, models.Manager):
    def get_query_set(self):
        return EbuildQuerySet(self.model, using=self._db)
