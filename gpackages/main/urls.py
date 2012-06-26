from django.conf.urls import patterns, include, url
from django.contrib import admin
from main.settings import DEBUG

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/' , include('django.conf.urls.i18n')),
    url(r'', include('packages.urls')),
)

if DEBUG:
    from django.contrib import databrowse
    from packages.views import TemplatesDebugView 
    from packages.models import EbuildModel, PackageModel, UseFlagModel, \
                                LicenseModel, CategoryModel, Keyword, \
                                ArchesModel, HomepageModel, HerdsModel, \
                                MaintainerModel, UseFlagDescriptionModel, \
                                RepositoryModel, VirtualPackageModel, \
                                RepositoryFeedModel, RepositorySourceModel, \
                                LicenseGroupModel

    databrowse.site.register(EbuildModel, PackageModel, UseFlagModel, 
                             LicenseModel, LicenseGroupModel, CategoryModel,
                             Keyword, ArchesModel, HomepageModel, HerdsModel,
                             MaintainerModel, UseFlagDescriptionModel, 
                             RepositoryModel, VirtualPackageModel, 
                             RepositoryFeedModel, RepositorySourceModel )
    urlpatterns += (
        url(r'^data/(.*)', databrowse.site.root),
        url(r'^templateview/(?P<templatename>.*)/?$', TemplatesDebugView.as_view()),
        url(r'^404/$', 'django.views.defaults.page_not_found', name = '404'),
        url(r'^500/$', 'django.views.defaults.server_error', name = '500'),
        )
