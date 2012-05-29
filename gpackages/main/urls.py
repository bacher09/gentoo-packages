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
)

if DEBUG:
    from packages.models import EbuildModel, PackageModel, UseFlagModel, LicensModel, CategoryModel, Keyword, ArchesModel
    from django.contrib import databrowse
    databrowse.site.register(EbuildModel, PackageModel, UseFlagModel, LicensModel, CategoryModel, Keyword, ArchesModel)
    urlpatterns += (
        url(r'^data/(.*)',databrowse.site.root),
        )
