from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from packages import models
from packages.stats import StatsMixin
import inspect


def get_predicate(obj):
    if inspect.isclass(obj) and issubclass(obj, StatsMixin):
        return obj != StatsMixin

class Command(BaseCommand):

    args = ''
    help = 'Will update stats in models'
    def handle(self, *args, **options):
        models_list = inspect.getmembers(models, get_predicate)
        for model_name, model in models_list:
            model.calc_stats()
