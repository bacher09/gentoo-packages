from django.contrib import admin
from django.db.models import Count
from models import EbuildModel, PackageModel, LicensModel, CategoryModel, \
                   UseFlagModel,  RepositoryModel, HomepageModel, HerdsModel, \
                   MaintainerModel, Keyword, ArchesModel, UseFlagDescriptionModel

class EbuildAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_masked', )
    list_filter = ('created_datetime','updated_datetime', 'licenses', 'is_masked')
    filter_horizontal = ('licenses', 'use_flags', 'homepages')
    date_hierarchy = 'updated_datetime'
    list_select_related = True


class PackageAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'ebuilds_count')
    list_filter = ('created_datetime', 'updated_datetime', 'herds')
    list_select_related = True

    def queryset(self, request):
        return super(PackageAdmin, self).queryset(request).annotate(ebuilds_count = Count('ebuildmodel'))

    def ebuilds_count(self, obj):
        return obj.ebuilds_count


class HerdsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'description', 'packages_count')
    search_fields = ('name', 'email')

    def queryset(self, request):
        return super(HerdsAdmin, self).queryset(request).annotate(packages_count = Count('packagemodel'))
    
    def packages_count(self, obj):
        return obj.packages_count

class MaintainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'packages_count')
    search_fields = ('name', 'email')

    def queryset(self, request):
        return super(MaintainerAdmin, self).queryset(request).annotate(packages_count = Count('packagemodel'))

    def packages_count(self, obj):
        return obj.packages_count


class UseFlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'ebuilds_count')
    search_fields = ('name', 'description')

    def queryset(self, request):
        return super(UseFlagAdmin, self).queryset(request).annotate(ebuilds_count = Count('ebuildmodel'))

    def ebuilds_count(self, obj):
        return obj.ebuilds_count

class UseFlagDescriptionAdmin(admin.ModelAdmin):
    list_display = ('use_flag', 'package', 'description')
    list_select_related = True

class HomepageAdmin(admin.ModelAdmin):
    list_display = ('url',)
    search_fields = ('url',)

class LicensAdmin(admin.ModelAdmin):
    list_display = ('name', 'licenses_count')
    search_fields = ('name',)

    def queryset(self, request):
        return super(LicensAdmin, self).queryset(request).annotate(licenses_count = Count('ebuildmodel'))
    
    def licenses_count(self, obj):
        return obj.licenses_count

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
