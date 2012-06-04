from django.core.management.base import BaseCommand, CommandError
import datetime
import logging
from packages import scan


class Command(BaseCommand):
    args = ''
    help = 'Will scan use descriptions'
    def handle(self, *args, **options):
        st = datetime.datetime.now()
        scan.update_globals_uses_descriptions()
        scan.scan_uses_description()
        print (datetime.datetime.now() - st).total_seconds()
