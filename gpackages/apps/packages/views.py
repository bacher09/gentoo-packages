from django.views.generic import TemplateView, ListView
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import Http404

from models import CategoryModel

class CategoriesListView(ListView):
    template_name = 'categories.html'
    queryset = CategoryModel.objects.defer('metadata_hash').all()
    context_object_name = 'categories'

class TemplatesDebugView(TemplateView):

    def get_template_names(self):
        templatename = self.kwargs.get('templatename')
        if not templatename:
            raise Http404
        return [templatename, templatename +'.html', templatename + '.htm']
