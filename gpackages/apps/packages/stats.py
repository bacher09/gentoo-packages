from django.db.models import Count
from itertools import starmap

gen_prefix = lambda x: x + '_prefix'

def gen_query_dict(params):
    query_dict = {}
    for key, value in starmap(lambda x,y: (gen_prefix(x), y), params):
        query_dict[key] = Count(value, distinct = True)

    return query_dict

def make_query_for_stats(model, params):
    query_dict = gen_query_dict(params)
    return model.objects.annotate(**query_dict)

def update_stats(model, params):
    query = make_query_for_stats(model, params)
    for obj in query:
        for key, mykey in starmap(lambda  x,y: (x, gen_prefix(x)), params):
            setattr(obj, key, getattr(obj, mykey))

        obj.save(force_update = True)

class StatsMixin(object):

    stats_params = ((),)

    @classmethod
    def calc_stats(cls):
        update_stats(cls, cls.stats_params)
