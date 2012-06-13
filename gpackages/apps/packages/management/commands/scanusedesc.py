from django.core.management.base import BaseCommand, CommandError
from packages.scan import Scanner
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-g','--no-globals',
            action='store_false',
            dest='scan_global_use',
            default=True,
            help='Don\'t scan globals use descriptions'),
        make_option('-l', '--no-locals',
            action='store_false',
            dest='scan_local_use',
            default=True,
            help='Don\'t scan globals use descriptions'),
        make_option('--not-show-time',
            action='store_false',
            dest='show_time',
            default=True,
            help='Show time of scanning'),
        )
    args = ''
    help = 'Will scan use descriptions'
    def handle(self, *args, **options):
        Scanner(**options).scan()
