from django.core.management.base import BaseCommand, CommandError
from packages import models
import porttree

import datetime
import logging
#l = logging.getLogger('django.db.backends')
#l.setLevel(logging.DEBUG)
#l.addHandler(logging.FileHandler('database.log'))

class Command(BaseCommand):
    args = ''
    help = 'Will scan package tree and update info about it in database'
    porttree = porttree.PortTree()
    def handle(self, *args, **options):
        licenses_cache = {}
        def get_licenses_objects(ebuild):
            licenses = ebuild.licenses
            license_objects = []
            licenses_set = frozenset(licenses)
            cached_licenses = set(licenses_cache.keys())
            # Getting from cache
            geted_licenses = set()
            for license in (cached_licenses & licenses_set):
                geted_licenses.add(license)
                license_objects.append(licenses_cache[license])
            # Getting from database
            request_licenses = list(licenses_set - geted_licenses)
            if not request_licenses:
                return license_objects
            request = models.LicensModel.objects.filter(name__in = request_licenses)
            # Add to list with licenses
            license_objects.extend(request)
            # Update cache
            for license in request:
                licenses_cache[license.name] = license
                geted_licenses.add(license.name)
            # Create not existend licenses fast using bulk_create, works only in django 1.4 or gt
            need_create = list(licenses_set - geted_licenses)
            if not need_create:
                return license_objects
            creating_list = []
            for license in need_create:
                creating_list.append(models.LicensModel(name = license))
            
            models.LicensModel.objects.bulk_create(creating_list)
            # Retriwing created licenses from database
            request_created = models.LicensModel.objects.filter(name__in = need_create)
            license_objects.extend(request_created)
            # Update cache
            for license in request_created:
                licenses_cache[license.name] = license
                geted_licenses.add(license.name)
            return license_objects

        uses_cache = {}
        def get_uses_objects(ebuild):
            uses = [ use.name for use in ebuild.iter_uses() ]
            uses_objects = []
            uses_set = frozenset(uses)
            cached_uses = set(uses_cache.keys())
            # Getting from cache
            geted_uses = set()
            for use in (cached_uses & uses_set):
                geted_uses.add(use)
                uses_objects.append(uses_cache[use])
            # Getting from database
            request_use = list(uses_set - geted_uses)
            if not request_use:
                return uses_objects
            request = models.UseFlagModel.objects.filter(name__in = request_use)
            # Add to list with licenses
            uses_objects.extend(request)
            # Update cache
            for use in request:
                uses_cache[use.name] = use
                geted_uses.add(use.name)
            # Create not existend licenses fast using bulk_create, works only in django 1.4 or gt
            need_create = list(uses_set - geted_uses)
            if not need_create:
                return license_objects
            creating_list = []
            for use in need_create:
                creating_list.append(models.UseFlagModel(name = use))
            
            models.UseFlagModel.objects.bulk_create(creating_list)
            # Retriwing created licenses from database
            request_created = models.UseFlagModel.objects.filter(name__in = need_create)
            uses_objects.extend(request_created)
            # Update cache 
            for use in request_created:
                uses_cache[use.name] = use
                geted_uses.add(use.name)
            return uses_objects

        arches_cache = {}
        def get_keywords_objects(ebuild, ebuild_object):
            keywords_list = []
            for keyword in ebuild.get_keywords():
                keyword_object = models.Keyword(status = keyword.status,
                                                ebuild = ebuild_object)

                if keyword.arch in arches_cache:
                    arch = arches_cache[keyword.arch]
                else:
                    arch, created = models.ArchesModel.objects.get_or_create(name = keyword.arch)
                    arches_cache[keyword.arch] = arch
                
                keyword_object.arch = arch
                keywords_list.append(keyword_object)

            models.Keyword.objects.bulk_create(keywords_list)



            
        st = datetime.datetime.now()
        for category in self.porttree.iter_categories():
            category_object, categor_created = models.CategoryModel.objects.get_or_create(category = category)
            for package in category.iter_packages():
                print package
                package_object, package_created = models.PackageModel.objects.get_or_create(package = package, category = category_object)
                for ebuild in package.iter_ebuilds():
                    ebuild_object = models.EbuildModel()
                    ebuild_object.init_by_ebuild(ebuild)
                    ebuild_object.package = package_object
                    # To Add some related objects it should have pk
                    ebuild_object.save(force_insert=True)
                    # Add licenses
                    ebuild_object.licenses.add(*get_licenses_objects(ebuild))
                    ebuild_object.use_flags.add(*get_uses_objects(ebuild))
                    get_keywords_objects(ebuild, ebuild_object)
                    homepages_list = []
                    for homepage in ebuild.homepages:
                        homepage_object = models.HomepageModel(url = homepage,
                                                               ebuild = ebuild_object)
                        homepages_list.append(homepage_object)
                    models.HomepageModel.objects.bulk_create(homepages_list)


        print (datetime.datetime.now() - st).total_seconds()
