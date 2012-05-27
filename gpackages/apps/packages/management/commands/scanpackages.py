from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = ''
    help = 'Will scan package tree and update info about it in database'

    def handle(self, *args, **options):
        print("Not implement yet")
