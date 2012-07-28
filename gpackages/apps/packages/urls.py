from django.conf.urls import patterns, include, url
from views import CategoriesListView, HerdsListView, MaintainersListView, \
                  RepositoriesListView, LicenseGroupsView , EbuildsListView, \
                  PackagesListsView, PackageDetailView, EbuildDetailView, \
                  GlobalUseListView, NewsListView, NewsDetailView, \
                  LicenseDetailView, ArchChoiceView, LicensesListView, \
                  LocalUseListView, FilteringView, RepoDetailView, \
                  MainPageFeed, MainPageFeedAtom

urlpatterns = patterns('',
    url(r'^categories/$', CategoriesListView.as_view(), name = 'categories'),
    url(r'^herds/$', HerdsListView.as_view(), name = 'herds'),
    url(r'^use/$', GlobalUseListView.as_view(), name = 'global_uses'),
    url(r'^local_use/$', LocalUseListView.as_view(), name = 'local_uses'),
    url(r'^maintainers/$', MaintainersListView.as_view(), name = 'maintainers'),
    url(r'^repositories/$', RepositoriesListView.as_view(), name = 'repositories'),
    url(r'^license-groups/$', LicenseGroupsView.as_view(), name = 'license_groups'),
    url(r'^$', EbuildsListView.as_view(), name = 'ebuilds'),
    url(r'^ebuild/(?P<pk>\d+)/$', EbuildDetailView.as_view(), name = 'ebuild'),
    url(r'^ebuild/(?P<cpvr>[^/]+/[^/]+)/$', EbuildDetailView.as_view(), name = 'ebuild'),
    url(r'^packages/{0}$'.format(PackagesListsView.get_url_part()), PackagesListsView.as_view(), name = 'packages'),
    url(r'^newpackages/$', PackagesListsView.as_view(), kwargs = {'order': 'create', 'rev': 'rev'},name = 'newpackages'),

    #url(r'^package/(?:(?P<pk>\d+)|(?P<category>[^/]+)/(?P<name>[^/]+))/$', PackageDetailView.as_view(), name = 'package'),
    url(r'^package/(?P<pk>\d+)/$', PackageDetailView.as_view(), name = 'package'),
    url(r'^package/(?P<cpr>[^/]+/[^/]+)/$', PackageDetailView.as_view(), name = 'package'),
    url(r'^news/$', NewsListView.as_view(), name = 'news'),
    url(r'^news/(?P<pk>\d+)/$', NewsDetailView.as_view(), name = 'news_item'),
    url(r'^news/(?P<slug>[^/]+)/$', NewsDetailView.as_view(), name = 'news_item'),
    url(r'^license/(?P<slug>[^/]+)/$', LicenseDetailView.as_view(), name = 'license'),
    url(r'^arches/$', ArchChoiceView.as_view(), name = 'archchoice'),
    url(r'^licenses/$', LicensesListView.as_view(), name = 'licenses'),
    url(r'^filter/$', FilteringView.as_view(), name = 'filter'),
    url(r'^repository/(?P<slug>[^/]+)/$', RepoDetailView.as_view(), name = 'repository'),
    url(r'^rss/$', MainPageFeed()),
    url(r'^atom/$', MainPageFeedAtom()),
)
