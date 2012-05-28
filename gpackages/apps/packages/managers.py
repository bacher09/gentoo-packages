from django.db import models
from porttree import Category, Package, Ebuild, Keyword
import packages.models


class PackageMixin(object):
    def get_or_create(self, **kwargs):
        if 'package' in kwargs:
            po = kwargs['package']
            if isinstance(po, Package):
                del kwargs['package']
                if 'category' not in kwargs:
                    co, created = packages.models.CategoryModel. \
                            objects.get_or_create(category = po.category)
                    kwargs.update({'category': co})
                
                kwargs.update({'name': po.name})
            else:
                raise ValueError("Bad package object")

        return super(PackageMixin, self).get_or_create(**kwargs)

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
