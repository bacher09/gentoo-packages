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
        make_option('-d' ,'--del',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete'),
        )

    args = '<repository names ...>'
    help = 'Will scan repositories info'
    def handle(self, *args, **options):
        if len(args) > 0:
            scan_all = False
        else:
            scan_all = True

        Scanner(repos = args, scan_all = scan_all,
                only_repo_info = True, **options).scan()
