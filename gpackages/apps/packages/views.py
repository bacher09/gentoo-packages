from django.views.generic import TemplateView, ListView
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import Http404

from models import CategoryModel, HerdsModel, MaintainerModel, \
                   RepositoryModel, LicenseGroupModel

class ContextListView(ListView):
    extra_context = {}
    def get_context_data(self, **kwargs):
        ret = super(ContextListView, self).get_context_data(**kwargs)
        ret.update(self.extra_context)
        return ret

class CategoriesListView(ContextListView):
    extra_context = {'page_name': 'Categories', 'nav_name' : 'categories'}
    template_name = 'categories.html'
    queryset = CategoryModel.objects.defer('metadata_hash').all()
    context_object_name = 'categories'

class HerdsListView(ContextListView):
    extra_context = {'page_name': 'Herds', 'nav_name': 'herds'}
    template_name = 'herds.html'
    queryset = HerdsModel.objects.only('name', 'email', 'description').all()
    context_object_name = 'herds'

class MaintainersListView(ContextListView):
    paginate_by = 40
    extra_context = {'page_name': 'Maintainers', 'nav_name': 'maintainers'}
    template_name = 'maintainers.html'
    queryset = MaintainerModel.objects.only('name', 'email' ).all()
    context_object_name = 'maintainers'

class RepositoriesListView(ContextListView):
    extra_context = {'page_name': 'Repsitories', 'nav_name': 'repositories'}
    template_name = 'repositories.html'
    queryset = RepositoryModel.objects.only('name', 'description' ).all()
    context_object_name = 'repositories'

class LicenseGroupsView(ContextListView):
    extra_context = {'page_name': 'License Groups', 'nav_name': 'license_groups'}
    queryset = LicenseGroupModel.objects.all().prefetch_related('licenses')
    template_name = 'license_groups.html'
    context_object_name = 'license_groups'

class TemplatesDebugView(TemplateView):

    def get_template_names(self):
        templatename = self.kwargs.get('templatename')
        if not templatename:
            raise Http404
        return [templatename, templatename +'.html', templatename + '.htm']
