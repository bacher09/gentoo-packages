from django.db import models, connections, router, transaction, IntegrityError
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
            if 'category' not in kwargs:
                kwargs.update({'category__category' : package.category})
            name = package.name
            if len(args)>=1:
                args[0] = name
            if len(args)>=2:
                args[1] = category
            else:
                kwargs.update({'name': name})
        return super(PackageMixin, self).get(*args, **kwargs)

PackageQuerySet, PackageManager = _gen_query_and_manager(PackageMixin, 
                                                        'PackageQuerySet',
                                                        'PackageManager')

class KeywordMixin(object):
    def get_or_create(self, keyword=None,  **kwargs):
        if keyword is not None:
            if isinstance(keyword, Keyword):
                arch, created = packages.models.ArchesModel.objects.get_or_create(name = keyword.name)
                kwargs.update({'arch': arch, 'status': keyword.status})
            else:
                raise ValueError("Bad keyword object")

        return super(KeywordMixin, self).get_or_create(**kwargs)

KeywordQuerySet, KeywordManager = _gen_query_and_manager(KeywordMixin, 
                                                        'KeywordQuerySet',
                                                        'KeywordManager')

class EbuildMixin(object):
    def create(self, **kwargs):
        if 'ebuild' in kwargs:
            obj = self.model(**kwargs)
        else:
            obj = super(EbuildMixin, self).create(**kwargs)
        return obj

    def get_or_create(self, **kwargs):
        assert kwargs, \
                'get_or_create() must be passed at least one keyword argument'
        defaults = kwargs.pop('defaults', {})
        lookup = kwargs.copy()
        for f in self.model._meta.fields:
            if f.attname in lookup:
                lookup[f.name] = lookup.pop(f.attname)
        try:
            self._for_write = True
            return self.get(**lookup), False
        except self.model.DoesNotExist:
            try:
                params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
                params.update(defaults)
                sid = transaction.savepoint(using=self.db)
                obj = self.model(**params)
                if 'ebuild' not in kwargs:
                    obj.save(force_insert=True, using=self.db)
                transaction.savepoint_commit(sid, using=self.db)
                return obj, True
            except IntegrityError as e:
                transaction.savepoint_rollback(sid, using=self.db)
                exc_info = sys.exc_info()
                try:
                    return self.get(**lookup), False
                except self.model.DoesNotExist:
                    # Re-raise the IntegrityError with its original traceback.
                    raise exc_info[1], None, exc_info[2]
    
    
    def get(self, ebuild=None,package = None, *args, **kwargs):
        if ebuild is not None and isinstance(ebuild, Ebuild):
            if package is None:
                kwargs.update({
                        'package__category__category': ebuild.package.category,
                        'package__name': ebuild.package.name })
            else:
                kwargs.update({'package': package})
            version = ebuild.version
            revision = ebuild.revision
            kwargs.update({ 'version': version,
                            'revision': revision })
        return super(EbuildMixin, self).get(*args, **kwargs)
            


EbuildQuerySet, EbuildManager =   _gen_query_and_manager(EbuildMixin,
                                                        'EbuildQuerySet',
                                                        'EbuildManager')
