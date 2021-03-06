from django.conf.urls import patterns, include, url
from django.contrib import admin
from main.settings import DEBUG
from django.contrib.sitemaps import FlatPageSitemap
from packages.views import PackageSitemap

# For caching sitemap
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page

sitemaps = {
    'flatpages': FlatPageSitemap,
    'packages' : PackageSitemap,
}
cached_sitemap = cache_page(3600)(sitemaps_views.sitemap)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/' , include('django.conf.urls.i18n')),
    url(r'^setlang/$', 'generic.views.set_lang_view', name = 'setlang'),
    url(r'', include('packages.urls')),
    (r'^sitemap\.xml$', cached_sitemap, {'sitemaps': sitemaps}),
)

if DEBUG:
    from django.contrib import databrowse
    from packages.models import EbuildModel, PackageModel, UseFlagModel, \
                                LicenseModel, CategoryModel, Keyword, \
                                ArchesModel, HomepageModel, HerdsModel, \
                                MaintainerModel, UseFlagDescriptionModel, \
                                RepositoryModel, VirtualPackageModel, \
                                RepositoryFeedModel, RepositorySourceModel, \
                                LicenseGroupModel, PortageNewsModel

    databrowse.site.register(EbuildModel, PackageModel, UseFlagModel, 
                             LicenseModel, LicenseGroupModel, CategoryModel,
                             Keyword, ArchesModel, HomepageModel, HerdsModel,
                             MaintainerModel, UseFlagDescriptionModel, 
                             RepositoryModel, VirtualPackageModel, 
                             RepositoryFeedModel, RepositorySourceModel,
                             PortageNewsModel)
    urlpatterns += (
        url(r'^data/(.*)', databrowse.site.root),
        url(r'^templateview/(?P<templatename>.*)/?$', 
            'generic_debug.views.template_debug_view'),

        url(r'^404/$', 'django.views.defaults.page_not_found', name = '404'),
        url(r'^500/$', 'django.views.defaults.server_error', name = '500'),
        )
