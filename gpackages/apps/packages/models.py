from django.db import models

from porttree import Category, Package, Ebuild
import managers

class HomepageModel(models.Model):
    url = models.URLField(max_length=255, unique = True)

    def __unicode__(self):
        return self.url

class ArchesModel(models.Model):
    name = models.CharField(unique = True, max_length = 22)
    
    def __unicode__(self):
        return self.name

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

class MaintainerModel(models.Model):

    def __init__(self, *args, **kwargs):
        #TODO: Bad code, maybe use some libraries for overload methods
        maintainer = None
        if 'maintainer' in kwargs:
            maintainer = kwargs['maintainer']
            del kwargs['maintainer']
        super(MaintainerModel, self).__init__(*args, **kwargs)
        if maintainer is not None:
            self.init_by_maintainer(maintainer)
        
    name = models.CharField(max_length = 255, blank = True, null = True)
    email = models.EmailField(unique = True)
    role = models.TextField(blank = True, null = True)

    objects = managers.MaintainerManager()

    def init_by_maintainer(self, maintainer):
        self.name = maintainer.name
        self.email = maintainer.email
        self.role = maintainer.role
    
    def __unicode__(self):
        return ':'.join((unicode(self.name), self.email))

class HerdsModel(models.Model):

    def __init__(self, *args, **kwargs):
        herd = None
        if 'herd' in kwargs:
            herd = kwargs['herd']
            del kwargs['herd']
        super(HerdsModel, self).__init__(*args, **kwargs)
        if herd is not None:
            self.init_by_herd(herd)

    name = models.CharField(unique = True, max_length = 150)
    email = models.EmailField()
    description = models.TextField(blank = True, null = True)
    maintainers = models.ManyToManyField(MaintainerModel, blank = True)

    objects = managers.HerdsManager()

    def init_by_herd(self, herd):
        self.name = herd.name
        self.email = herd.email
        self.description = herd.description

    def __unicode__(self):
        return self.name

class PackageModel(models.Model):
    def __init__(self, *args, **kwargs):
        # TODO: Bad code, maybe use some library to overload method
        package_object = None
        if len(args)>=1:
            package_object = args[0] 
        
        if 'package' in kwargs:
            package_object = kwargs['package']

        if isinstance(package_object, Package):
            super(PackageModel, self).__init__()
            self.init_by_package(package_object, category = kwargs.get('category'))
        else:
            super(PackageModel, self).__init__(*args, **kwargs)
            
        

    name = models.CharField(max_length = 254)
    category = models.ForeignKey(CategoryModel)
    changelog = models.TextField(blank = True)
    changelog_hash = models.CharField(max_length = 128)
    manifest_hash = models.CharField(max_length = 128)
    changelog_mtime = models.DateTimeField(blank = True, null = True)
    manifest_mtime = models.DateTimeField(blank = True, null = True)
    mtime = models.DateTimeField(blank = True, null = True)

    herds = models.ManyToManyField(HerdsModel, blank = True)
    maintainers = models.ManyToManyField(MaintainerModel, blank = True)
    # Different versions can have different licenses, or homepages.
    
    objects = managers.PackageManager()

    def __unicode__(self):
        return '%s/%s' % (self.category, self.name)
    
    def init_by_package(self, package, category = None):
        self.name = package.name
        self.update_info(package)
        if category is None:
            self.category, created = CategoryModel.objects.get_or_create(category = package.category)
        elif isinstance(category, CategoryModel):
            self.category = category

    def update_info(self, package):
        self.mtime = package.mtime
        self.changelog_mtime = package.changelog_mtime
        self.changelog = package.changelog
        self.changelog_hash = package.changelog_sha1
        self.manifest_mtime = package.manifest_mtime
        self.manifest_hash = package.manifest_sha1

    class Meta:
        unique_together = ('name', 'category')

class UseFlagModel(models.Model):
    name = models.CharField(unique = True, max_length = 60)
    description = models.TextField(blank = True)
    
    def __unicode__(self):
        return self.name

class LicensModel(models.Model):
    name = models.CharField(unique = True, max_length = 60)
    #description = TextField()
    
    def __unicode__(self):
        return self.name


class EbuildModel(models.Model):
    package = models.ForeignKey(PackageModel)
    #repository = models.ForeignKey(RepositoryModel)
    version = models.CharField(max_length = 26)
    revision = models.CharField(max_length = 12)
    use_flags = models.ManyToManyField(UseFlagModel)
    licenses = models.ManyToManyField(LicensModel)
    license = models.CharField(max_length = 254, blank = True )
    ebuild_hash = models.CharField(max_length = 128)
    ebuild_mtime = models.DateTimeField(blank = True, null = True)
    ebuild_datetime = models.DateTimeField(auto_now = True)
    is_deleted = models.BooleanField(default = False)
    is_masked = models.BooleanField(default = False)

    #homepage = models.URLField(blank = True, null = True, max_length=255)
    homepages = models.ManyToManyField(HomepageModel, blank = True)
    description = models.TextField(blank = True, null = True)

    #eapi = models.PositiveSmallIntegerField(default = 0)
    #slot = models.PositiveSmallIntegerField(default = 0)

    

    objects = managers.EbuildManager()

    def __init__(self, *args, **kwargs ):
        ebuild = None
        if 'ebuild' in kwargs:
            ebuild = kwargs['ebuild']
            del kwargs['ebuild']
        super(EbuildModel, self).__init__(*args, **kwargs)
        if ebuild is not None and isinstance(ebuild, Ebuild):
            self.init_with_keywords(ebuild)
    
    def __unicode__(self):
        return '%s-%s%s' % (self.package, self.version, ('-'+ self.revision if self.revision else '')) 
    
    def init_by_ebuild(self, ebuild):
        self.is_masked = ebuild.is_masked
        self.version = ebuild.version
        self.revision = ebuild.revision
        self.license = ebuild.license
        self.ebuild_mtime = ebuild.mtime
        self.ebuild_hash = ebuild.sha1
        #self.homepage = ebuild.homepage
        self.description = ebuild.description

    def init_related(self, ebuild, package = None):
        self.init_by_ebuild(ebuild)
        if package is None:
            self.package = PackageModel.objects.get_or_create(package = ebuild.package)[0]
        elif isinstance(package, PackageModel):
            self.package = package
        self.save()
        l = []
        for license in ebuild.licenses:
            k, created = LicensModel.objects.get_or_create(name = license)
            if created:
                k.save()
            l.append(k)
        
        self.licenses.add(*l)
        l = []
        # TODO: Bad code
        for use in ebuild.iter_uses():
            k, created = UseFlagModel.objects.get_or_create(name = use)
            if created:
                k.save()
            l.append(k)
        self.use_flags.add(*l)

    def init_with_keywords(self, ebuild):
        self.init_by_ebuild(ebuild)
        l = []
        for keyword in ebuild.iter_keywords():
            ko, created = Keyword.objects.get_or_create(keyword = keyword, ebuild = self)
            if created:
                ko.save()
            l.append(ko)
        self.keyword_set.add(*l)

    class Meta:
        unique_together = ('package', 'version', 'revision')
        
            

class Keyword(models.Model):
    STATUS_CHOICES = (
        (0, 'STABLE'),
        (1, 'NEED TESTING'),
        (2, 'NOT WORK')
    )
    status_repr = ['','~','-']

    ebuild = models.ForeignKey(EbuildModel)
    arch = models.ForeignKey(ArchesModel)
    status = models.PositiveSmallIntegerField(choices = STATUS_CHOICES)

    objects = managers.KeywordManager()

    def __unicode__(self):
        return self.status_repr[self.status] + str(self.arch)
        

    def init_by_keyword(self, keyword, ebuild):
        if isinstance(ebuild, EbuildModel):
            self.ebuild = ebuild
        elif isinstance(ebuild, Ebuild):
            self.ebuild, created = EbuildModel.objects.get_or_create(ebuild = ebuild)
        self.arch, created = ArchesModel.objects.get_or_create(name = keyword.name)
        self.status = keyword.status

    class Meta:
        unique_together = ('ebuild', 'arch')


