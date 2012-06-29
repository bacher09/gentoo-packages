from django.views.generic import TemplateView, ListView
from string import Template

class ContextView(object):
    extra_context = {}
    def get_context_data(self, **kwargs):
        ret = super(ContextView, self).get_context_data(**kwargs)
        ret.update(self.extra_context)
        return ret

class ContextListView(ContextView, ListView):
    pass

class ContextTemplateView(ContextView, TemplateView):
    pass

class SetLang(ContextTemplateView):
    template_name = 'setlang.html'
    extra_context = {'page_name': 'Set Language', 'nav_name' : 'setlanguage'}

set_lang_view = SetLang.as_view()

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

class MultipleFilterListViewMixin(object):
    allowed_filter = {}
    allowed_order = {}

    base_queryset = None # should be queryset

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

    @classmethod
    def get_url_part(cls):
        t = "(?:{0}/(?P<{0}>[^/]+)/)?"
        l =[]
        for key in cls.allowed_filter.iterkeys():
            l.append(t.format(key))

        return ''.join(l) + "(?:order/(?P<order>[a-z]*)/)?(?P<rev>rev/)?"
            
