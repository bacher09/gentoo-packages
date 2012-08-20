from django.views.generic import TemplateView, ListView
from string import Template
import re
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, rfc3339_date
from django.utils import tzinfo
from django.utils.timezone import is_naive
from django.http import Http404

class ContextView(object):
    "Mixin to add additional data to context"
    extra_context = {}
    """Attribute that wold be added to  context data.
    Should contains :py:class:`.dict`"""
    def get_context_data(self, **kwargs):
        ret = super(ContextView, self).get_context_data(**kwargs)
        ret.update(self.extra_context)
        return ret

class ContextListView(ContextView, ListView):
    pass

class ContextTemplateView(ContextView, TemplateView):
    pass

class SetLang(ContextTemplateView):
    "View for changing language js is unavailable"
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

def dynamic_order(order_attr, allowed_list, reverse = None):
    order = allowed_list.get(None)
    if order_attr in allowed_list:
        order = allowed_list.get(order_attr)

    if order == '?':
        return order
    
    if reverse and order[0] != '-':
        order = '-' + order
    elif reverse:
        order =  order[1:]
    return order

class MultipleFilterListViewMixin(object):
    """Mixin for dynamical objects filtering
    """
    allowed_filter = {}
    """Dict of allowed filters, filter name is key, filter field is value
    """
    allowed_order = {}
    """Dict of allowed orders, order name is key, order field is value
    """
    boolean_filters = ()
    """Set or tuple of boolean filters, indicates that filtering by that 
    attribute should done as boolean.
    """
    # allowed_many = {'name': int_count}
    allowed_many = {}
    """Dict where key is filter name, value is integer.
    Indicates that this filter could search by many values using ``__in`` query.
    Value is used as limit of max allowed filtering values, if it is 0 then 
    unlimited.
    """
    m2m_filter = set()
    """Indicates that this attribute is m2m fields and filtering by it should done
    with ``distinct`` attribute.
    """

    def get_context_data(self, **kwargs):
        """In addition to default context value will return all filters as 
        :py:class:`.dict`.
        """
        cd = super(MultipleFilterListViewMixin, self).get_context_data(**kwargs)
        cd['filters_dict'] = self.queries_dict
        return cd

    def get_base_filters(self):
        qs = filter_req(self.request.GET, self.allowed_filter)
        qs.update(filter_req(self.kwargs, self.allowed_filter))
        return qs

    def get_filters(self):
        """Return filters dict
        """
        qs = self.get_base_filters()
        newqs = {}
        for k, v in qs.iteritems():
            if k in self.allowed_many:
                vm = v.split(',')
                if len(vm)>1:
                    v = cut_to_len(vm, self.allowed_many[k])
            elif k in self.boolean_filters:
                v = True if v == 'yes' else False
            newqs[k] = v 
        self.queries_dict = newqs
        return newqs

    def is_reverse(self):
        """Return boolean value that which indicates that objects should sorted
        in reverse order
        """
        if self.kwargs.get('rev') is None:
            reverse = bool(self.request.GET.get('rev', False))
        else:
            reverse = bool(self.kwargs.get('rev', False))

        return reverse

    def get_order(self):
        """Will return order value for using in 
        :py:meth:`order_by <django:django.db.models.query.QuerySet.order_by>`
        method or raise :py:class:`Http404 <django:django.http.Http404>` exception.
        """
        reverse = self.is_reverse()
        
        if 'order' in self.request.GET:
            order_attr =  self.request.GET.get('order')
        else:
            order_attr = self.kwargs.get('order')

        if order_attr not in self.allowed_order:
            raise Http404('no such order')
        order = dynamic_order(order_attr, self.allowed_order, reverse)
        return order

    def get_queryset(self):
        """Will return 
        :py:class:`QuerySet <django:django.db.models.query.QuerySet>` of 
        filtered objects."""
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
        "Return url sufix for transfering filter params in url."
        t = "(?:{0}/(?P<{0}>[^/]+)/)?"
        t_bool = "(?:{0}/(?P<{0}>yes|no)/)?"
        l =[]
        for key in cls.allowed_filter.iterkeys():
            if key in cls.boolean_filters:
                l.append(t_bool.format(re.escape(key)))
            else:
                l.append(t.format(re.escape(key)))

        # Maybe add num chars to order attribute ?
        return ''.join(l) + "(?:order/(?P<order>[a-z]*)/)?(?P<rev>rev/)?"

class FeedWithUpdated(Feed):
    """Extend Feed class that have ``item_update`` method for object updated
    date
    """
    def item_extra_kwargs(self, item):
        # for future
        kwargs = super(FeedWithUpdated, self).item_extra_kwargs(item)
        # hack for access to private method !!!
        updated = self._Feed__get_dynamic_attr('item_update', item)
        if updated and is_naive(updated):
            ltz = tzinfo.LocalTimezone(updated)
            updated = updated.replace(tzinfo=ltz)
        kwargs['updated'] = updated
        return kwargs
            
# see bug https://code.djangoproject.com/ticket/14656
class RightAtom1Feed(Atom1Feed):
    """Extended Atom Feed wich have updated attribute
    """
    def add_item_elements(self, handler, item):
        if item['pubdate'] is not None:
            handler.addQuickElement(u"published", 
                rfc3339_date(item['pubdate']).decode('utf-8'))

            item['pubdate'] = None

        if item['updated'] is not None:
            handler.addQuickElement(u"updated", 
                rfc3339_date(item['updated']).decode('utf-8'))

        return super(RightAtom1Feed, self).add_item_elements(handler, item)
