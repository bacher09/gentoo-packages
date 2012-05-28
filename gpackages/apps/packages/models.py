from django.db import models

class ArchesModel(models.Model):
    name = models.CharField(max_length = 12)

class RepositoryModel(models.Model):
    name = models.CharField(max_length = 60)
    description = models.TextField(blank = True, null = True)
    # And other fields

class CategoryModel(models.Model):
    category = models.CharField(unique = True, max_length = 70)
    
    def __unicode__(self):
        return self.category

    @classmethod
    def create_by_category(cls, category):
        category_model = cls.objects.get_or_create(category = category.category)
        return category_model

class PackageModel(models.Model):
    name = models.CharField(unique = True, max_length = 254)
    category = models.ForeignKey(CategoryModel)
    changelog = models.TextField(blank = True)
    changelog_hash = models.CharField(max_length = 128)
    manifest_hash = models.CharField(max_length = 128)
    # Different versions can have different licenses, or homepages.
    def __unicode__(self):
        return '%s/%s' % (self.category, self.name)
    
    #@classmethod
    #def create_by_pakcage(cls, package):
        #category_object = CategoryModel.create_by_category(package.category)
        #package_model = c

class UseFlagModel(models.Model):
    name = models.CharField(unique = True, max_length = 28)
    description = models.TextField(blank = True)

class LicensModel(models.Model):
    name = models.CharField(max_length = 40)
    #description = TextField()
    
    def __unicode__(self):
        return self.name

class MetaDataModel(models.Model):
    homepage = models.URLField()
    description = models.TextField(blank = True, null = True)
    # Some other info

class EbuildModel(models.Model):
    package = models.ForeignKey(PackageModel)
    repository = models.ForeignKey(RepositoryModel)
    version = models.CharField(max_length = 16)
    revision = models.CharField(max_length = 6)
    metadata = models.ForeignKey(MetaDataModel)
    use_flags = models.ManyToManyField(UseFlagModel)
    licenses = models.ManyToManyField(LicensModel)
    license = models.CharField(max_length = 254, blank = True )
    ebuild_hash = models.CharField(max_length = 128)
    ebuld_datetime = models.DateTimeField(auto_now = True)
    is_deleted = models.BooleanField(default = False)
    is_masked = models.BooleanField(default = False)
    
    def __unicode__(self):
        return '%s-%s' % (self.package, self.version)

    #@classmethod
    #def create_by_ebuild(cls, ebuild):
        #ebuild_model = cls()
        #ebuild_model.is_masked = ebuild.is_masked
        #ebuild_model.version = ebuild.version
        #ebuild_model.revision = ebuild.revision

class Keyword(models.Model):
    ebuild = models.ForeignKey(EbuildModel)
    arch = models.ForeignKey(ArchesModel)
    is_stable = models.BooleanField() 
