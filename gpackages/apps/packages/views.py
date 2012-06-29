from django.views.generic import DetailView
from generic.views import ContextListView, ContextTemplateView, ContextView
from models import CategoryModel, HerdsModel, MaintainerModel, \
                   RepositoryModel, LicenseGroupModel, EbuildModel, \
                   PackageModel

from django.shortcuts import get_object_or_404

class CategoriesListView(ContextListView):
    extra_context = {'page_name': 'Categories',}
    template_name = 'categories.html'
    queryset = CategoryModel.objects.defer('metadata_hash').all()
    context_object_name = 'categories'

class HerdsListView(ContextListView):
    extra_context = {'page_name': 'Herds',}
    template_name = 'herds.html'
    queryset = HerdsModel.objects.only('name', 'email', 'description').all()
    context_object_name = 'herds'

class MaintainersListView(ContextListView):
    paginate_by = 40
    extra_context = {'page_name': 'Maintainers',}
    template_name = 'maintainers.html'
    queryset = MaintainerModel.objects.only('name', 'email' ).all()
    context_object_name = 'maintainers'

class RepositoriesListView(ContextListView):
    extra_context = {'page_name': 'Repsitories',}
    template_name = 'repositories.html'
    queryset = RepositoryModel.objects.only('name', 'description' ).all()
    context_object_name = 'repositories'

class LicenseGroupsView(ContextListView):
    extra_context = {'page_name': 'License Groups',}
    queryset = LicenseGroupModel.objects.all().prefetch_related('licenses')
    template_name = 'license_groups.html'
    context_object_name = 'license_groups'

class EbuildsListView(ContextListView):
    arches = ['alpha', 'amd64', 'arm', 'hppa', 'ia64', 'ppc', 'ppc64', 'sparc', 'x86']
    paginate_by = 40
    extra_context = {'page_name': 'Ebuilds', 'arches' : arches}
    template_name = 'ebuilds.html'
    context_object_name = 'ebuilds'
    queryset = EbuildModel.objects.all(). \
        select_related('package',
                       'package__virtual_package',
                       'package__virtual_package__category').prefetch_keywords(arches)

# there is another dynamic filter for django, and it maybe better 
# but it is too big and i need just a litle of its functionly
# but if this code have to be grove maybe i replace it to django-filter
# application or another.
def dynamic_filter(filter_set, allowed):
    result = {}
    for k in allowed.iterkeys():
        if k in filter_set:
            result[allowed[k]] = filter_set[k]
    return result

def exclude_blank(res_dict):
    result = {}
    for k in res_dict.iterkeys():
        if res_dict[k]:
            result[k] = res_dict[k]
    return result

def dynamic_order(args_list, allowed_list, reverse = None):
    order = allowed_list.get(None)
    if reverse is None:
        reverse = args_list.get('reverse', False)
    if args_list.get('order') in allowed_list:
        order = allowed_list.get(args_list.get('order'))

    if order == '?':
        return order
    
    if reverse and order[0] != '-':
        order = '-' + order
    elif reverse:
        order =  order[1:]
    return order

class PackagesListsView(ContextListView):
    allowed_filter = { 'category':'virtual_package__category__category',
                       'repo':'repository__name',
                       'herd':'herds__name',
                       'maintainer_pk': 'maintainers__pk',
                       'license': 'licenses__name'
                    }

    allowed_order = { 'create': 'created_datetime',
                      'update': 'updated_datetime',
                      'rand':'?', # it slow
                      None: '-updated_datetime'
                    }
    arches = ['alpha', 'amd64', 'arm', 'hppa', 'ia64', 'ppc', 'ppc64', 'sparc', 'x86']
    paginate_by = 40
    extra_context = {'page_name': 'Packages', 'arches': arches}
    template_name = 'packages.html'
    context_object_name = 'packages'
    # Faster query !!
    #SELECT t.id, t.virtual_package_id, t.description, t.repository_id, vp.id
    #as virtual_package__name FROM 
    #(SELECT * FROM packages_packagemodel 
    #ORDER BY updated_datetime DESC LIMIT 3 ) as t 
    #INNER JOIN packages_virtualpackagemodel vp 
    #ON( `vp`.id = t.virtual_package_id) INNER JOIN `packages_categorymodel` cp
    #ON (vp.category_id = cp.id);
    base_queryset = PackageModel.objects.all(). \
        select_related('virtual_package',
                       'virtual_package__category'). \
        prefetch_related('repository'). \
        prefetch_keywords(arches)

    def get_queryset(self):
        qs = dynamic_filter(exclude_blank(self.request.GET),
                                        self.allowed_filter)
        qs.update( dynamic_filter(exclude_blank(self.kwargs),
                                        self.allowed_filter) )
        
        if self.kwargs.get('rev') is None:
            reverse = bool(self.request.GET.get('rev',False))
        else:
            reverse = bool(self.kwargs.get('rev',False))
        
        if 'order' in self.request.GET:
            order = dynamic_order(self.request.GET, self.allowed_order,reverse)
        else:
            order = dynamic_order(self.kwargs, self.allowed_order, reverse)
            if self.kwargs.get('order') not in self.allowed_order:
                raise Http404('no such order')

        return self.base_queryset.filter(**qs).order_by(order)

class PackageDetailView(ContextView, DetailView):
    arches = ['alpha', 'amd64', 'arm', 'hppa', 'ia64', 'ppc', 'ppc64', 'sparc', 'x86']
    template_name = 'package.html'
    extra_context = {'page_name': 'Package', 'arches': arches}
    context_object_name = 'package'
    queryset = PackageModel.objects.all(). \
        select_related('virtual_package',
                       'virtual_package__category'). \
        prefetch_related('repository'). \
        prefetch_keywords(arches)

    def get_object(self, queryset = None):
        pk = self.kwargs.get('pk')
        if pk is not None:
            return super(PackageDetailView, self).get_object(queryset)
        if queryset is None:
            queryset = self.get_queryset()

        name, category = self.kwargs.get('name'), self.kwargs.get('category')
        repository = self.kwargs.get('repository')
        if repository is None:
            repository = 'gentoo'
        obj = get_object_or_404(queryset, name = name,
                                          category = category,
                                          repository__name = repository)
        return obj
