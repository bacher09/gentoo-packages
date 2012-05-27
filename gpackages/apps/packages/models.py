from django.db import models

class ArchesModel(models.Model):
    name = models.CharField(max_length = 12)

class Repository(models.Model):
    name = models.CharField(max_length = 60)
    description = models.TextField()
    # And other fields

class CategoryModel(models.Model):
    category = models.CharField(max_length = 70)

class PackageModel(models.Model):
   name = models.CharField(unique = True, max_length = 254)
   category = models.ForeignKey(CategoryModel)
   # Different versions can have different licenses, or homepages.

class UseFlagModel(models.Model):
    name = models.CharField(unique = True, max_length = 28)
    description = models.TextField()

class LicensModel(models.Model):
    name = models.CharField(max_length = 40)
    #description = TextField()

class MetaDataModel(models.Model):
    homepage = models.URLField()
    description = models.TextField()
    changelog = models.TextField()
    changelog_hash = models.CharField(max_length = 128)
    manifest_hash = models.CharField(max_length = 128)
    # Some other info

class EbuildModel(models.Model):
    package = models.ForeignKey(PackageModel)
    repository = models.ForeignKey(Repository)
    version = models.CharField(max_length = 24)
    metadata = models.ForeignKey(MetaDataModel)
    use_flags = models.ManyToManyField(UseFlagModel)
    licenses = models.ManyToManyField(LicensModel)
    ebuild_hash = models.CharField(max_length = 128)
    ebuld_datetime = models.DateTimeField(auto_now = True)
    is_deleted = models.BooleanField(default = False)

class Keyword(models.Model):
    ebuild = models.ForeignKey(EbuildModel)
    arch = models.ForeignKey(ArchesModel)
    status = models.SmallIntegerField() # Stable or not, masked
