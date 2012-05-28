from django.db import models
from porttree import Category, Package
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
