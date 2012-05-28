from django.contrib import admin
from models import EbuildModel, PackageModel, LicensModel, CategoryModel, \
                   UseFlagModel, MetaDataModel, RepositoryModel

admin.site.register(EbuildModel)
admin.site.register(PackageModel)
admin.site.register(LicensModel)
admin.site.register(CategoryModel)
admin.site.register(UseFlagModel)
admin.site.register(RepositoryModel)
admin.site.register(MetaDataModel)
