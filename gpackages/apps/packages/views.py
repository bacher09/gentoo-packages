from generic.views import ContextListView, ContextTemplateView
from models import CategoryModel, HerdsModel, MaintainerModel, \
                   RepositoryModel, LicenseGroupModel, EbuildModel, \
                   PackageModel

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
    paginate_by = 40
    extra_context = {'page_name': 'Ebuilds',}
    template_name = 'ebuilds.html'
    context_object_name = 'ebuilds'
    queryset = EbuildModel.objects.all(). \
        select_related('package',
                       'package__virtual_package',
                       'package__virtual_package__category')

class PackagesListsView(ContextListView):
    paginate_by = 40
    extra_context = {'page_name': 'Packages',}
    template_name = 'packages.html'
    context_object_name = 'packages'
    queryset = PackageModel.objects.all(). \
        select_related('virtual_package', 'virtual_package__category')
        #prefetch_related('ebuildmodel_set')
