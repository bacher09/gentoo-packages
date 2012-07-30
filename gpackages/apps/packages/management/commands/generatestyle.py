from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from package_info.generic_metadata import changelog_highlight


class Command(BaseCommand):

    args = ''
    help = 'Will show some stats for repos'
    def handle(self, *args, **options):
        self.stdout.write(changelog_highlight.changelog_style_css() + '\n')
