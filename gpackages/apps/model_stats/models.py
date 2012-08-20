from django.db import models 
from itertools import starmap, ifilter
import inspect
from django.db.models.base import ModelBase
from django.db.models.loading import get_models

def get_predicate(obj):
    "Predicate for searching `StatsMixin` objects"
    if inspect.isclass(obj) and issubclass(obj, StatsMixin):
        return obj != StatsMixin

def filter_models(models_list):
    return ifilter(get_predicate, models_list)

gen_prefix = lambda x: x + '_prefix'

def gen_query_dict(params):
    query_dict = {}
    for key, value in starmap(lambda x,y: (gen_prefix(x), y), params):
        query_dict[key] = models.Count(value, distinct = True)

    return query_dict

def make_query_for_stats(model, params):
    query_dict = gen_query_dict(params)
    only = query_dict.keys() + ['pk']
    return model.objects.annotate(**query_dict).values(*only)

def update_stats(model, params):
    query = make_query_for_stats(model, params)
    for item in query:
        kwargs = {}
        for key, mykey in starmap(lambda  x,y: (x, gen_prefix(x)), params):
            kwargs[key] = item.get(mykey)

        model.objects.filter(pk = item['pk']).update(**kwargs)

class StatsMixin(object):
    "Basic mixin for calc stats"

    #iterable of 2-tuples
    stats_params = ()
    "Atributes for stats"

    @classmethod
    def calc_stats(cls):
        "Update stats for this model"
        update_stats(cls, cls.stats_params)

def get_stats_models(module):
    "Search stats models in module"
    return inspect.getmembers(module, get_predicate)

def update_stats_for_models(models_list):
    """Update stats for special model's list
    Args: 
        models_list -- list of models     
    """
    for model in models_list:
        model.calc_stats()

def update_all_stats():
    "Will update stats for all models"
    update_stats_for_models(filter_models(get_models()))

class StatsModelBase(ModelBase):
    """Metaclass for models with stats
    Will automaticaly add model fields for stats by ``stats_params`` attribute
    """

    def __init__(cls, name, bases, attrs):
        super(StatsModelBase, cls).__init__(name, bases, attrs)
        stats_m = False
        for base in bases:
            if issubclass(base, StatsMixin):
                stats_m = True
                break
        #if not stats_m or not hasattr(cls, stats_params):
        if not (stats_m and hasattr(cls, 'stats_params')):
            return None

        if not cls.stats_params:
            return None
        
        for key, value in cls.stats_params:
            if not hasattr(cls, key):
                cls.add_to_class(key, models. \
                    PositiveIntegerField(default = 0, editable = False))

class StatsModel(StatsMixin, models.Model):
    """Base model for models with stats, should be used instead of 
    default django model class.
    
    This class will automaticaly add model fields for stats, but you could 
    override this by defining own definition in model class.
    """
    __metaclass__ = StatsModelBase

    stats_params = ()
    """This param used for automaticaly add model fields for stats and for 
    stats calculation

    It should contains iterable of 2-tuples

    First value in tuple should be new field name, second Count agreggation value.

    Example:
        stats_params = [('books_count', 'booksmodel')]

    For more examples see tests.
    """

    class Meta:
        abstract = True
