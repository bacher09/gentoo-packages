from django.contrib import admin
from django.db.models import Count
from models import EbuildModel, PackageModel, LicenseModel, CategoryModel, \
                   UseFlagModel,  RepositoryModel, HomepageModel, MaintainerModel, \
                   Keyword, ArchesModel, UseFlagDescriptionModel, HerdsModel, \
                   VirtualPackageModel, RepositoryFeedModel, \
                   RepositorySourceModel, LicenseGroupModel, PortageNewsModel

class KeywordAdmin(admin.TabularInline):
    model = Keyword 

class ArchesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class EbuildAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_hard_masked', )
    list_filter = ('created_datetime','updated_datetime', 'is_hard_masked', 'licenses')
    filter_horizontal = ('licenses', 'use_flags', 'homepages')
    date_hierarchy = 'updated_datetime'
    list_select_related = True
    inlines = (KeywordAdmin,)

class VirtualPackageAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('name','category__category')
    list_select_related = True

class PackageAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'ebuilds_count')
    list_filter = ('created_datetime', 'updated_datetime', 'herds')
    list_select_related = True

class HerdsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'description', 'packages_count',
                    'ebuilds_count', 'maintainers_count',)
                    # 'repositories_count')
    search_fields = ('name', 'email')

class MaintainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'packages_count', 'ebuilds_count',
                    'herds_count')
    search_fields = ('name', 'email')

class UseFlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'ebuilds_count')
    search_fields = ('name', 'description')

class UseFlagDescriptionAdmin(admin.ModelAdmin):
    list_display = ('use_flag', 'package', 'description')
    list_select_related = True

class HomepageAdmin(admin.ModelAdmin):
    list_display = ('url',)
    search_fields = ('url',)

class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'ebuilds_count')
    search_fields = ('name',)

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_datetime', 'official', 'homepage', 
                    'quality', 'packages_count', 'ebuilds_count')
    search_fields = ('name', 'description', 'owner_name', 'owner_email')
    list_filter = ('created_datetime', 'updated_datetime', 'official', 'quality')
    date_hierarchy = 'updated_datetime'

class RepositoryFeedAdmin(admin.ModelAdmin):
    list_display = ('repository', 'feed')
    search_fields = ('repository__name', 'feed')
    list_filter = ('repository', )
    list_select_related = True

class RepositorySourceAdmin(admin.ModelAdmin):
    list_display = ('repository', 'repo_type', 'url', 'subpath')
    search_fields = ('repository__name', 'url')
    list_filter = ('repo_type', )
    list_select_related = True

class PortageNewsAdmin(admin.ModelAdmin):
    list_display = ('name', 'lang', 'date')
    list_filter = ('lang',)
    search_fields = ('name', 'title', 'message')
    date_hierarchy = 'date'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'virtual_packages_count', 'packages_count',
                    'ebuilds_count', 'repositories_count')
    search_fields = ('category', 'description')


admin.site.register(EbuildModel, EbuildAdmin)
admin.site.register(VirtualPackageModel, VirtualPackageAdmin)
admin.site.register(PackageModel, PackageAdmin)
admin.site.register(LicenseModel, LicenseAdmin)
admin.site.register(LicenseGroupModel)
admin.site.register(CategoryModel, CategoryAdmin)
admin.site.register(UseFlagModel, UseFlagAdmin)
admin.site.register(UseFlagDescriptionModel, UseFlagDescriptionAdmin)
admin.site.register(RepositoryModel, RepositoryAdmin)
admin.site.register(RepositoryFeedModel, RepositoryFeedAdmin)
admin.site.register(RepositorySourceModel, RepositorySourceAdmin)
admin.site.register(HomepageModel, HomepageAdmin)
admin.site.register(HerdsModel, HerdsAdmin)
admin.site.register(MaintainerModel, MaintainerAdmin)
admin.site.register(ArchesModel, ArchesAdmin)
admin.site.register(PortageNewsModel, PortageNewsAdmin)
