from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from packages import models
from django.db.models import Count
import porttree


class Command(BaseCommand):

    args = ''
    help = 'Will show some stats for repos'
    def handle(self, *args, **options):
        query = models.RepositoryModel.objects.annotate(
            packages_count = Count('packagemodel', distinct = True),
            ebuilds_count = Count('packagemodel__ebuildmodel', distinct = True),
            maintainers_count = Count('packagemodel__maintainers', distinct = True),
            herds_count = Count('packagemodel__herds', distinct = True))

        self.stdout.write('"%s"               "%s"  "%s" "%s" "%s"\n' %
            ('Repo name', 'Packages', 'Ebuilds' , 'Maintainers', 'Herds'))

        for repo_object in query:
            self.stdout.write("%-25s %+9s %+9s %+9s %+9s\n" % (
                                                repo_object.name,
                                                repo_object.packages_count,
                                                repo_object.ebuilds_count,
                                                repo_object.maintainers_count,
                                                repo_object.herds_count))
