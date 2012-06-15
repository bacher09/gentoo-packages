from django.views.generic import TemplateView, ListView
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import Http404

from models import CategoryModel, HerdsModel, MaintainerModel, RepositoryModel

class ContextListView(ListView):
    extra_context = {}
    def get_context_data(self, **kwargs):
        ret = super(ContextListView, self).get_context_data(**kwargs)
        ret.update(self.extra_context)
        return ret

class CategoriesListView(ContextListView):
    extra_context = {'page_name': 'Categories'}
    template_name = 'categories.html'
    queryset = CategoryModel.objects.defer('metadata_hash').all()
    context_object_name = 'categories'

class HerdsListView(ContextListView):
    extra_context = {'page_name': 'Herds'}
    template_name = 'herds.html'
    queryset = HerdsModel.objects.only('name', 'email', 'description').all()
    context_object_name = 'herds'

class MaintainersListView(ContextListView):
    paginate_by = 40
    extra_context = {'page_name': 'Maintainers'}
    template_name = 'maintainers.html'
    queryset = MaintainerModel.objects.only('name', 'email' ).all()
    context_object_name = 'maintainers'

class RepositoriesListView(ContextListView):
    extra_context = {'page_name': 'Repsitories'}
    template_name = 'repositories.html'
    queryset = RepositoryModel.objects.only('name', 'description' ).all()
    context_object_name = 'repositories'

class TemplatesDebugView(TemplateView):

    def get_template_names(self):
        templatename = self.kwargs.get('templatename')
        if not templatename:
            raise Http404
        return [templatename, templatename +'.html', templatename + '.htm']
