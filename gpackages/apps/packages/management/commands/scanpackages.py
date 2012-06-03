from django.core.management.base import BaseCommand, CommandError
from packages import models
from collections import defaultdict
import porttree
import herds

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
    

def scan_maintainers(maintainers_dict):
    existend_maintainers = models.MaintainerModel.objects.all()
    mo_dict = {}
    to_del = []
    for maintainer_object in existend_maintainers:
        if maintainer_object in maintainers_dict:
            # to update ?
            mo_dict[maintainer_object.email] = maintainer_object
        else:
            to_del.append(maintainer_object.pk)

    to_create = []
    for maintainer in maintainers_dict.iterkeys():
        if maintainer.email not in mo_dict:
            to_create.append(maintainer)

    mobjects = _create_objects(models.MaintainerModel, 'maintainer', to_create)
    _update_cache_by_queryset(mo_dict, mobjects, 'email')

    return mo_dict
            

def scan_herds():
    existent_herds = models.HerdsModel.objects.all()
    herds_object = herds.Herds()
    herds_dict = herds_object.get_herds_indict()
    maintainers_dict = herds_object.get_maintainers_with_hers()
    ho_dict = {}
    to_del = []
    for herd_object in existent_herds:
        if herd_object.name not in herds_dict:
            to_del.append(herd_object.pk)
        else:
            # to update ?
            ho_dict[herd_object.name] = herd_object

    models.HerdsModel.objects.filter(pk__in = to_del).delete()

    to_create = []
    for herd in herds_dict.itervalues():
        if herd.name not in ho_dict:
            to_create.append(herd)

    cobjects = _create_objects(models.HerdsModel, 'herd', to_create)
    _update_cache_by_queryset(ho_dict, cobjects, 'name')

    mo_dict = scan_maintainers(maintainers_dict)
    #Gen data for relate with herds
    res = defaultdict(list)
    for mainteiner, herds_names in maintainers_dict.iteritems():
       for herd in herds_names:
           res[herd].append(mo_dict[mainteiner.email])

    for herd_name, herd_object in ho_dict.iteritems():
        herd_object.maintainers.clear()
        herd_object.maintainers.add(*res[herd_name])

    return ho_dict, mo_dict

        

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
        herds_cache, maintainers_cache = scan_herds()
        def get_maintainers_objects(package):
            maintainers = package.metadata.maintainers()
            objects = []
            for maintainer in maintainers:
                if maintainer.email in maintainers_cache:
                    objects.append(maintainers_cache[maintainer.email])
                else:
                    maintainer_object, created = models.MaintainerModel \
                            .objects.get_or_create(email = maintainer.email)
                    if created:
                        maintainer_object.name = maintainer.name
                        maintainer_object.save()
                    objects.append(maintainer_object)
            return objects
                    

        def get_herds_objects(package):
            herds = package.metadata.herds()
            herds_objects = []
            for herd in herds:
                if herd in herds_cache:
                    herds_objects.append(herds_cache[herd])

            return herds_objects
        # Load homepages to cache
        #for homepage in models.HomepageModel.objects.all():
            #homepages_cache[homepage.url] = homepage

        for category in self.porttree.iter_categories():
            category_object, categor_created = models.CategoryModel.objects.get_or_create(category = category)
            for package in category.iter_packages():
                print package
                package_object, package_created = models.PackageModel.objects.get_or_create(package = package, category = category_object)
                package_object.herds.add(*get_herds_objects(package))
                package_object.maintainers.add(*get_maintainers_objects(package))
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
