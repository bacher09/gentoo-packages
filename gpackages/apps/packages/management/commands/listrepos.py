from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from package_info.porttree import porttree as portage


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--simple',
            action='store_true',
            dest='simple',
            default=False,
            help='Simple'),
        )

    args = ''
    help = 'Will names of all available repos'
    def handle(self, *args, **options):
        self.portage = portage

        simple = options.get('simple',False)
        if simple:
            self.simple()
        else:
            self.complex()


    def complex(self):
        # Maybe this is bad name
        repo_dict = self.portage.dict_repos
        for repo_name in self.portage.list_repos:
            self.stdout.write("%s %s\n" % 
                (("[%s]" % repo_name).ljust(30), repo_dict[repo_name]))

    def simple(self):
        for repo_name in self.portage.list_repos:
            self.stdout.write('%s\n' % repo_name)
