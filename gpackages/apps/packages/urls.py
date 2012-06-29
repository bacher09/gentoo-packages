from django.conf.urls import patterns, include, url
from views import CategoriesListView, HerdsListView, MaintainersListView, \
                  RepositoriesListView, LicenseGroupsView , EbuildsListView, \
                  PackagesListsView, PackageDetailView

urlpatterns = patterns('',
    url(r'^categories/$', CategoriesListView.as_view(), name = 'categories'),
    url(r'^herds/$', HerdsListView.as_view(), name = 'herds'),
    url(r'^maintainers/$', MaintainersListView.as_view(), name = 'maintainers'),
    url(r'^repositories/$', RepositoriesListView.as_view(), name = 'repositories'),
    url(r'^license-groups/$', LicenseGroupsView.as_view(), name = 'license_groups'),
    url(r'^$', EbuildsListView.as_view(), name = 'ebuilds'),
    url(r'^packages/(?:category/(?P<category>[^/]+)/)?(?:repo/(?P<repo>[^/]*)/)?(?:herd/(?P<herd>[^/]+)/)?(?:maintainer/(?P<maintainer_pk>[^/]+)/)?(?:order/(?P<order>[a-z]*)/)?(?P<rev>rev/)?$',
    PackagesListsView.as_view(), name = 'packages'),

    # In Future I will write my onw URL Resolver !!!
    #url(r'^package/(?:(?P<pk>\d+)|(?P<category>[^/]+)/(?P<name>[^/]+))/$', PackageDetailView.as_view(), name = 'package'),
    url(r'^package/(?P<pk>\d+)/$', PackageDetailView.as_view(), name = 'package'),
    url(r'^package/(?P<category>[^/]+)/(?P<name>[^/:]+)/$', PackageDetailView.as_view(), name = 'package'),
    url(r'^package/(?P<category>[^/]+)/(?P<name>[^/:]+)::(?P<repository>[^/]+)/$', PackageDetailView.as_view(), name = 'package'),
)
