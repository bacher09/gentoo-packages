from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from model_stats.models import update_all_stats
from datetime import datetime

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-t', '--show-time',
            action='store_true',
            dest='show_time',
            default=False,
            help='Show working time'),
        )
    args = ''
    help = 'Will update stats in models'
    def handle(self, *args, **options):
        st = datetime.now()
        update_all_stats()
        if options.get('show_time'):
            time = (datetime.now() - st).total_seconds()
            self.stdout.write('Updating stats %s secconds\n' % time)
