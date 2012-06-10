from django.contrib import admin
from django.db.models import Count
from models import EbuildModel, PackageModel, LicensModel, CategoryModel, \
                   UseFlagModel,  RepositoryModel, HomepageModel, HerdsModel, \
                   MaintainerModel, Keyword, ArchesModel, UseFlagDescriptionModel

class AbstractAnnotateAdmin(object):
    annotate_dict = {}

    def queryset(self, request):
        return super(AbstractAnnotateAdmin, self).queryset(request) \
            .annotate(**self.annotate_dict)

class EbuildsCountAdmin(AbstractAnnotateAdmin):
    annotate_dict = {'ebuilds_count': Count('ebuildmodel')}
    
    def ebuilds_count(self, obj):
        return obj.ebuilds_count

class PackagesCountAdmin(AbstractAnnotateAdmin):
    annotate_dict = {'packages_count': Count('packagemodel')}

    def packages_count(self, obj):
        return obj.packages_count

class KeywordAdmin(admin.TabularInline):
    model = Keyword 

class ArchesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class EbuildAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_masked', )
    list_filter = ('created_datetime','updated_datetime', 'licenses', 'is_masked')
    filter_horizontal = ('licenses', 'use_flags', 'homepages')
    date_hierarchy = 'updated_datetime'
    list_select_related = True
    inlines = (KeywordAdmin,)

class PackageAdmin(EbuildsCountAdmin, admin.ModelAdmin):
    list_display = ('__unicode__', 'ebuilds_count')
    list_filter = ('created_datetime', 'updated_datetime', 'herds')
    list_select_related = True

class HerdsAdmin(PackagesCountAdmin, admin.ModelAdmin):
    list_display = ('name', 'email', 'description', 'packages_count')
    search_fields = ('name', 'email')

class MaintainerAdmin(PackagesCountAdmin, admin.ModelAdmin):
    list_display = ('name', 'email', 'packages_count')
    search_fields = ('name', 'email')

class UseFlagAdmin(EbuildsCountAdmin, admin.ModelAdmin):
    list_display = ('name', 'description', 'ebuilds_count')
    search_fields = ('name', 'description')

class UseFlagDescriptionAdmin(admin.ModelAdmin):
    list_display = ('use_flag', 'package', 'description')
    list_select_related = True

class HomepageAdmin(admin.ModelAdmin):
    list_display = ('url',)
    search_fields = ('url',)

class LicensAdmin(EbuildsCountAdmin, admin.ModelAdmin):
    list_display = ('name', 'ebuilds_count')
    search_fields = ('name',)


admin.site.register(EbuildModel, EbuildAdmin)
admin.site.register(PackageModel, PackageAdmin)
admin.site.register(LicensModel, LicensAdmin)
admin.site.register(CategoryModel)
admin.site.register(UseFlagModel, UseFlagAdmin)
admin.site.register(UseFlagDescriptionModel, UseFlagDescriptionAdmin)
admin.site.register(RepositoryModel)
admin.site.register(HomepageModel, HomepageAdmin)
admin.site.register(HerdsModel, HerdsAdmin)
admin.site.register(MaintainerModel, MaintainerAdmin)
admin.site.register(ArchesModel, ArchesAdmin)
