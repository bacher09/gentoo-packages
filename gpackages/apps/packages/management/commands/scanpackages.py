from django.core.management.base import BaseCommand, CommandError
import datetime
import logging
from packages.scan import Scanner
from optparse import make_option
#l = logging.getLogger('django.db.backends')
#l.setLevel(logging.DEBUG)
#l.addHandler(logging.FileHandler('database.log'))


class Command(BaseCommand):
    args = ''
    help = 'Will scan package tree and update info about it in database'
    def handle(self, *args, **options):
        st = datetime.datetime.now()
        #scan.scanpackages()
        #scan.scan_all_repos()
        Scanner().scan_all_repos()
        self.stdout.write(unicode((datetime.datetime.now() - st).total_seconds()))
        self.stdout.write("\n")
