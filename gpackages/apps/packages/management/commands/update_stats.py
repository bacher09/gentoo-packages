from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from packages.stats import update_all_stats

class Command(BaseCommand):

    args = ''
    help = 'Will update stats in models'
    def handle(self, *args, **options):
        update_all_stats()
