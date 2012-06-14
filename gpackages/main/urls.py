from django.conf.urls import patterns, include, url
from django.contrib import admin
from main.settings import DEBUG

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gpackages.views.home', name='home'),
    # url(r'^gpackages/', include('gpackages.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('packages.urls')),
)

if DEBUG:
    from django.contrib import databrowse
    from packages.views import TemplatesDebugView 
    from packages.models import EbuildModel, PackageModel, UseFlagModel, \
                                LicensModel, CategoryModel, Keyword, \
                                ArchesModel, HomepageModel, HerdsModel, \
                                MaintainerModel, UseFlagDescriptionModel, \
                                RepositoryModel, VirtualPackageModel 

    databrowse.site.register(EbuildModel, PackageModel, UseFlagModel, 
                             LicensModel, CategoryModel, Keyword, ArchesModel, 
                             HomepageModel, HerdsModel, MaintainerModel, 
                             UseFlagDescriptionModel, RepositoryModel, 
                             VirtualPackageModel)
    urlpatterns += (
        url(r'^data/(.*)', databrowse.site.root),
        url(r'^templateview/(?P<templatename>.*)/?$', TemplatesDebugView.as_view()),
        url(r'^404/$', 'django.views.defaults.page_not_found', name = '404'),
        url(r'^500/$', 'django.views.defaults.server_error', name = '500'),
        )
