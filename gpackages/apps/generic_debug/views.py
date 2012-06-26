from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.http import Http404

class TemplatesDebugView(TemplateView):

    def get_template_names(self):
        templatename = self.kwargs.get('templatename')
        if not templatename:
            raise Http404
        return [templatename, templatename +'.html', templatename + '.htm']

template_debug_view = TemplatesDebugView.as_view()
