from django.db import models

from porttree import Category, Package

class ArchesModel(models.Model):
    name = models.CharField(max_length = 12)

class RepositoryModel(models.Model):
    name = models.CharField(max_length = 60)
    description = models.TextField(blank = True, null = True)
    # And other fields

class CategoryModel(models.Model):
    def __init__(self, *args, **kwargs):
        category_object = None
        
        if len(args)>=1:
            category_object = args[0]
        if 'category_object' in kwargs:
            category_object = kwargs['category_object']
        elif 'category' in kwargs:
            category_object = kwargs['category']
        
        if isinstance(category_object, Category):
            return super(CategoryModel, self).__init__(category = category_object.category)
        else:
            return super(CategoryModel, self).__init__(*args, **kwargs)


    category = models.CharField(unique = True, max_length = 70)
    
    def __unicode__(self):
        return self.category


class PackageModel(models.Model):
    def __init__(self, *args, **kwargs):
        # TODO: Bad code, maybe use some library to overload method
        if len(args)>=1:
            package_object = args[0] 
        
        if 'package' in kwargs:
            package_object = kwargs['package']

        if isinstance(package_object, Package):
            super(PackageModel, self).__init__()
            self.init_by_package(package_object)
        else:
            super(PackageModel, self).__init__(*args, **kwargs)
            
        

    name = models.CharField(max_length = 254)
    category = models.ForeignKey(CategoryModel)
    changelog = models.TextField(blank = True)
    changelog_hash = models.CharField(max_length = 128)
    manifest_hash = models.CharField(max_length = 128)
    # Different versions can have different licenses, or homepages.
    def __unicode__(self):
        return '%s/%s' % (self.category, self.name)
    
    def init_by_package(self, package):
        self.name = package.name
        self.update_info(package)
        self.category, created = CategoryModel.objects.get_or_create(category = package.category)

    def update_info(self, package):
        self.changelog_hash = package.changelog_sha1
        self.manifest_hash = package.manifest_sha1

    class Meta:
        unique_together = ('name', 'category')

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
    class Meta:
        unique_together = ('ebuild', 'arch')