from django.core.management.base import BaseCommand, CommandError
from packages import models
import porttree

import datetime
import logging
#l = logging.getLogger('django.db.backends')
#l.setLevel(logging.DEBUG)
#l.addHandler(logging.FileHandler('database.log'))

def _get_from_cache(cache, what):
    save_to = []
    geted_items = set()
    for item in what:
        if item in cache:
            geted_items.add(item)
            save_to.append(cache[item])
    return save_to, geted_items

def _get_from_database(Model, field_name, request_items):
    request_items = list(request_items)
    if not request_items:
        return None
    return Model.objects.filter(**{field_name + '__in': request_items})

def _update_cache_by_queryset(cache, queryset, field_name):
    geted_items = set()
    for item in queryset:
        cache[getattr(item, field_name)] = item
        geted_items.add(getattr(item, field_name))
    return geted_items

def _get_from_database_and_update_cache(Model, field_name, request_items, cache):
    queryset = _get_from_database(Model, field_name, request_items)
    if queryset is None:
        return None, set()
    geted =  _update_cache_by_queryset(cache, queryset, field_name)
    return queryset, geted

def _create_objects(Model, field_name, need_create):
    if not need_create:
        return None
    creating_list = []
    for item in need_create:
        creating_list.append(Model(**{field_name: item}))

    Model.objects.bulk_create(creating_list)
    created = Model.objects.filter(**{field_name + '__in': need_create})
    return created

def _create_objects_and_update_cache(Model, field_name, need_create, cache):
    created = _create_objects(Model, field_name, need_create)
    if created is None:
        return None, None
    geted = _update_cache_by_queryset(cache, created, field_name)
    return created, geted

def _get_items(items_list, Model, field_name, cache_var):
    items_set = frozenset(items_list)
    # Getting from cache
    items_objects, geted_items = _get_from_cache(cache_var, items_set)
    # Getting from database
    queryset, geted = _get_from_database_and_update_cache(Model, field_name, items_set - geted_items, cache_var)
    if queryset is None:
        return items_objects
    geted_items = geted_items | geted

    # Add to list with items 
    items_objects.extend(queryset)
    # Create not existend items fast using bulk_create, works only in django 1.4 or gt
    need_create = list(items_set - geted_items)
    created, geted = _create_objects_and_update_cache(Model, field_name, need_create, cache_var)
    if created is None:
        return items_objects
    items_objects.extend(created)
    geted_items = geted_items | geted
    return items_objects
    

class Command(BaseCommand):
    args = ''
    help = 'Will scan package tree and update info about it in database'
    porttree = porttree.PortTree()
    def handle(self, *args, **options):
        licenses_cache = {}
        def get_licenses_objects(ebuild):
            licenses = ebuild.licenses
            return _get_items(licenses, models.LicensModel, 'name', licenses_cache)

        uses_cache = {}
        def get_uses_objects(ebuild):
            uses = [ use.name for use in ebuild.iter_uses() ]
            return _get_items(uses, models.UseFlagModel, 'name', uses_cache)

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



        homepages_cache = {}    
        def get_homepages_objects(ebuild):
            homepages = ebuild.homepages
            return _get_items(homepages, models.HomepageModel, 'url', homepages_cache)
        
        st = datetime.datetime.now()
        # Load homepages to cache
        for homepage in models.HomepageModel.objects.all():
            homepages_cache[homepage.url] = homepage

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
                    ebuild_object.homepages.add(*get_homepages_objects(ebuild))
                    get_keywords_objects(ebuild, ebuild_object)
                    #homepages_list = []
                    #for homepage in ebuild.homepages:
                        #homepage_object = models.HomepageModel(url = homepage,
                                                               #ebuild = ebuild_object)
                        #homepages_list.append(homepage_object)
                    #models.HomepageModel.objects.bulk_create(homepages_list)


        print (datetime.datetime.now() - st).total_seconds()
