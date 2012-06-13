from django.core.management.base import BaseCommand, CommandError
from packages.scan import Scanner
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--not-show-time',
            action='store_false',
            dest='show_time',
            default=True,
            help='Show time of scanning'),
        )
    args = ''
    help = 'Will scan only herds and maintainers'
    def handle(self, *args, **options):
        Scanner(scan_herds = True, **options).scan()
