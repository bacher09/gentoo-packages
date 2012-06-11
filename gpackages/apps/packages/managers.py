from django.db import models, connections, router, transaction, IntegrityError
from porttree import Category, Package, Ebuild, Keyword
import packages.models
from generic import get_from_kwargs_and_del


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
        

class PackageMixin(object):
    def get(self, package = None, *args, **kwargs):
        if package is not None and isinstance(package, Package):
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


class KeywordMixin(object):#{{{
    def get_or_create(self, keyword=None,  **kwargs):
        if keyword is not None:
            if isinstance(keyword, Keyword):
                arch, created = packages.models.ArchesModel.objects \
                    .get_or_create(name = keyword.name)
                kwargs.update({'arch': arch, 'status': keyword.status})
            else:
                raise ValueError("Bad keyword object")

        return super(KeywordMixin, self).get_or_create(**kwargs)#}}}


class EbuildMixin(object):#{{{
    
    def get(self, ebuild=None,package = None, *args, **kwargs):
        if ebuild is not None and isinstance(ebuild, Ebuild):
            if package is None:
                kwargs.update({
                        'package__category__category': ebuild.package.category,
                        'package__name': ebuild.package.name })
            else:
                kwargs.update({'package': package})
            kwargs.update({ 'version': ebuild.version,
                            'revision': ebuild.revision })
        return super(EbuildMixin, self).get(*args, **kwargs)#}}}


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


_gen_all_query_and_manager('Mixin', 'QuerySet', 'Manager',
                           PackageMixin, KeywordMixin, EbuildMixin, HerdsMixin,
                           MaintainerMixin)
