from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from packages import models
from django.db.models import Count

def get_query(precalculated = False):
    if precalculated == True:
        return models.RepositoryModel.objects. \
            values_list('name', 'packages_count', 'ebuilds_count',
                        'maintainers_count', 'herds_count')

    return models.RepositoryModel.objects.annotate(
        packages_countr = Count('packagemodel', distinct = True),
        ebuilds_countr = Count('packagemodel__ebuildmodel', distinct = True),
        maintainers_countr = Count('packagemodel__maintainers', distinct = True),
        herds_countr = Count('packagemodel__herds', distinct = True)). \
        values_list('name', 'packages_countr', 'ebuilds_countr', 
                    'maintainers_countr', 'herds_countr')

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-p', '--precalculated',
            action='store_true',
            dest='precalculated',
            default=False,
            help='Use precalculated stats'),
        )
    args = ''
    help = 'Will show some stats for repos'

    def handle(self, *args, **options):
        precalculated = options.get('precalculated', False)
        query = get_query(precalculated)

        self.stdout.write('"%s"               "%s"  "%s" "%s" "%s"\n' %
            ('Repo name', 'Packages', 'Ebuilds' , 'Maintainers', 'Herds'))

        for repo_object in query:
            self.stdout.write("%-25s %+9s %+9s %+9s %+9s\n" % (
                                                repo_object[0],
                                                repo_object[1],
                                                repo_object[2],
                                                repo_object[3],
                                                repo_object[4]))
