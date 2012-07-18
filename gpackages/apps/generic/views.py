from django.views.generic import TemplateView, ListView
from string import Template
import re

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
def dynamic_filter(filter_set, allowed, many_set = {}):
    result = {}
    for k, v in allowed.iteritems():
        if k in filter_set:
            vv = filter_set[k]
            if k in many_set and isinstance(vv, list):
                v += '__in'
            result[v] = vv
    return result

def cut_to_len(lst, num):
    if not num:
        return lst
    return lst[:num]

def filter_req(filter_set, allowed):
    result = {}
    for k in allowed.iterkeys():
        v = filter_set.get(k)
        if v:
            result[k] = v
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
    # allowed_many = {'name': int_count}
    allowed_many = {}
    m2m_filter = set()

    def get_context_data(self, **kwargs):
        cd = super(MultipleFilterListViewMixin, self).get_context_data(**kwargs)
        cd['filters_dict'] = self.queries_dict
        return cd

    def get_base_filters(self):
        qs = filter_req(self.request.GET, self.allowed_filter)
        qs.update(filter_req(self.kwargs, self.allowed_filter))
        return qs

    def get_filters(self):
        qs = self.get_base_filters()
        newqs = {}
        for k, v in qs.iteritems():
            if k in self.allowed_many:
                vm = v.split(',')
                if len(vm)>1:
                    v = cut_to_len(vm, self.allowed_many[k])
            newqs[k] = v 
        self.queries_dict = newqs
        return newqs

    def is_reverse(self):
        if self.kwargs.get('rev') is None:
            reverse = bool(self.request.GET.get('rev',False))
        else:
            reverse = bool(self.kwargs.get('rev',False))

        return reverse

    def get_order(self):
        reverse = self.is_reverse()
        
        if 'order' in self.request.GET:
            order = dynamic_order(self.request.GET, self.allowed_order,reverse)
        else:
            order = dynamic_order(self.kwargs, self.allowed_order, reverse)
            if self.kwargs.get('order') not in self.allowed_order:
                raise Http404('no such order')
        return order

    def get_queryset(self):
        query = super(MultipleFilterListViewMixin, self).get_queryset()
        qs = self.get_filters()
        order = self.get_order()

        qa = dynamic_filter(qs, self.allowed_filter, self.allowed_many)
        queryset = query.filter(**qa).order_by(order)

        for q in qs.iterkeys():
            if q in self.m2m_filter:
                queryset = queryset.distinct()
                break

        return queryset

    @classmethod
    def get_url_part(cls):
        t = "(?:{0}/(?P<{0}>[^/]+)/)?"
        l =[]
        for key in cls.allowed_filter.iterkeys():
            l.append(t.format(re.escape(key)))

        return ''.join(l) + "(?:order/(?P<order>[a-z]*)/)?(?P<rev>rev/)?"
            
