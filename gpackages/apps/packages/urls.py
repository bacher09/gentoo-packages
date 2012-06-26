from django.conf.urls import patterns, include, url
from views import CategoriesListView, HerdsListView, MaintainersListView, \
                  RepositoriesListView, LicenseGroupsView 

urlpatterns = patterns('',
    url(r'^categories/$', CategoriesListView.as_view(), name = 'categories'),
    url(r'^herds/$', HerdsListView.as_view(), name = 'herds'),
    url(r'^maintainers/$', MaintainersListView.as_view(), name = 'maintainers'),
    url(r'^repositories/$', RepositoriesListView.as_view(), name = 'repositories'),
    url(r'^license-groups/$', LicenseGroupsView.as_view(), name = 'license_groups'),
)
