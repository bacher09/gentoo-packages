from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from packages import models
from django.db.models import Count


class Command(BaseCommand):

    args = ''
    help = 'Will show some stats for repos'
    def handle(self, *args, **options):
        query = models.RepositoryModel.objects.annotate(
            packages_countr = Count('packagemodel', distinct = True),
            ebuilds_countr = Count('packagemodel__ebuildmodel', distinct = True),
            maintainers_countr = Count('packagemodel__maintainers', distinct = True),
            herds_countr = Count('packagemodel__herds', distinct = True))

        self.stdout.write('"%s"               "%s"  "%s" "%s" "%s"\n' %
            ('Repo name', 'Packages', 'Ebuilds' , 'Maintainers', 'Herds'))

        for repo_object in query:
            self.stdout.write("%-25s %+9s %+9s %+9s %+9s\n" % (
                                                repo_object.name,
                                                repo_object.packages_countr,
                                                repo_object.ebuilds_countr,
                                                repo_object.maintainers_countr,
                                                repo_object.herds_countr))
