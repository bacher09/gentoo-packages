from django.core.management.base import BaseCommand, CommandError
import logging
from packages.scan import Scanner
from optparse import make_option
#l = logging.getLogger('django.db.backends')
#l.setLevel(logging.DEBUG)
#l.addHandler(logging.FileHandler('database.log'))


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force-update',
            action='store_true',
            dest='force_update',
            default=False,
            help='Force updating'),
        make_option('--not-scan-herds',
            action='store_false',
            dest='scan_herds',
            default=True,
            help='Force updating'),
        make_option('-a', '--all',
            action='store_true',
            dest='scan_all',
            default=False,
            help='Force updating'),
        make_option('-r', '--update-repo',
            action='store_true',
            dest='update_repo',
            default=False,
            help='Update repository info'),
        make_option('--not-show-time',
            action='store_false',
            dest='show_time',
            default=True,
            help='Show time of scanning'),
        make_option('--not-del',
            action='store_false',
            dest='delete',
            default=True,
            help='Not delete'),
        make_option('--clear-cache',
            action='store_true',
            dest='cache_clear',
            default=False,
            help='Clear cache'),
        make_option('--not-license-groups',
            action='store_false',
            dest='scan_license_groups',
            default=True,
            help='Not scan license groups'),
        #make_option('-r', '--repo',
            #action='store',
            #type="string",
            #dest='reponame',
            #help='Scan only this repository'),
        )

    args = '<repository names ...>'
    help = 'Will scan package tree and update info about it in database'
    def handle(self, *args, **options):
        Scanner(repos = args, packages = True, **options).scan()
