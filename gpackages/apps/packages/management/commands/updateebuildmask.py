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
        make_option('-m', '--update-missing',
            action='store_true',
            dest='missing',
            default=False,
            help='Add missing ebuilds'),
        )
    args = ''
    help = 'Will update ebuild mask status'
    def handle(self, *args, **options):
        missing = options.get('missing', False) # maybe move it to function ?
        Scanner(**options).update_ebuild_mask(missing = missing)
