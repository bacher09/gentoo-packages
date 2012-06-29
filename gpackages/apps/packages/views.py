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

class PackagesListsView(ContextListView):
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
    queryset = PackageModel.objects.all(). \
        select_related('virtual_package',
                       'virtual_package__category'). \
        prefetch_related('repository'). \
        prefetch_keywords(arches)

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
