from django.core.management.base import BaseCommand, CommandError
import datetime
import logging
from packages import scan


class Command(BaseCommand):
    args = ''
    help = 'Will scan only herds and maintainers'
    def handle(self, *args, **options):
        st = datetime.datetime.now()
        scan.scan_herds()
        print (datetime.datetime.now() - st).total_seconds()
