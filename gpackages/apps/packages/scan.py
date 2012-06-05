from packages import models
from collections import defaultdict
import porttree
import herds
import use_info

porttree = porttree.PortTree()

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
    if queryset is None:
        return None
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
    main_dict = {}
    mo_dict = {}
    #to_del = []
    _update_cache_by_queryset(main_dict, maintainers_dict.keys(), 'email')
    for maintainer_object in existend_maintainers:
        if maintainer_object.email in main_dict:
            maintainer_cmp = main_dict[maintainer_object.email]
            # need update ?
            if maintainer_object.check_or_need_update(maintainer_cmp):
                # updating
                maintainer_object.update_by_maintainer(maintainer_cmp)
                maintainer_object.save(force_update = True)
            mo_dict[maintainer_object.email] = maintainer_object
        #else:
            #to_del.append(maintainer_object.pk)
    #print to_del
    #print mo_dict
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
    maintainers_dict = herds_object.get_maintainers_with_herds()
    ho_dict = {}
    to_del = []
    for herd_object in existent_herds:
        if herd_object.name not in herds_dict:
            to_del.append(herd_object.pk)
        else:
            herd_cmp = herds_dict[herd_object.name]
            # need update ?
            if herd_object.check_or_need_update(herd_cmp):
                # updating 
                herd_object.update_by_herd(herd_cmp)
                herd_object.save(force_update = True)
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

def update_globals_uses_descriptions():
    # Need changes 
    uses_g = use_info.get_uses_info()
    existend_use_objects = models.UseFlagModel.objects.filter(name__in = uses_g.keys())
    for use_object in existend_use_objects:
        use_object.description = uses_g[use_object.name]
        use_object.save(force_update = True)
    

def scan_uses_description():
    uses_local = use_info.get_local_uses_info()
    existend_use_objects = models.UseFlagModel.objects.filter(name__in = uses_local.keys())
    existend_use_local_descr = models.UseFlagDescriptionModel.objects.all()
    cache_uses = {}
    _update_cache_by_queryset(cache_uses, existend_use_objects, 'name')
    use_local_cache = defaultdict(dict)
    for use_obj in existend_use_local_descr:
        use_local_cache[use_obj.use_flag.name][use_obj.package.cp] = use_obj

    package_cache = dict()
    for use_flag, packages_dict in uses_local.iteritems():
        if use_flag not in cache_uses:
            continue
        use_flag_object = cache_uses[use_flag]
        to_create = []
        for package, description in packages_dict.iteritems():
            if package in package_cache:
                package_object = package_cache[package]
            else:
                try:
                    package_object = models.PackageModel.objects.get(package = package)
                except models.PackageModel.DoesNotExist:
                    continue
                else:
                    package_cache[package] = package_object
            if package not in use_local_cache[use_flag]:
                to_create.append(
                models.UseFlagDescriptionModel(package = package_object,
                                               use_flag = use_flag_object,
                                               description = description))
            else:
                use_desc_obj = use_local_cache[use_flag][package]
                if use_desc_obj.check_or_need_update(description):
                    use_desc_obj.description = description
                    use_desc_obj.save(force_update = True)
        models.UseFlagDescriptionModel.objects.bulk_create(to_create)
            
def scanpackages(delete = True, force_update = False):
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

    def add_related_to_ebuild(ebuild, ebuild_object):
        # Add licenses
        ebuild_object.licenses.add(*get_licenses_objects(ebuild))
        ebuild_object.use_flags.add(*get_uses_objects(ebuild))
        ebuild_object.homepages.add(*get_homepages_objects(ebuild))
        get_keywords_objects(ebuild, ebuild_object)
        
    def clear_related_to_ebuild(ebuild_object):
        ebuild_object.licenses.clear()
        ebuild_object.use_flags.clear()
        ebuild_object.homepages.clear()
        models.Keyword.objects.filter(ebuild = ebuild_object).delete()

    def update_related_to_ebuild(ebuild, ebuild_object):
        clear_related_to_ebuild(ebuild_object)
        add_related_to_ebuild(ebuild, ebuild_object)

    def create_ebuilds(package, package_object):
        for ebuild in package.iter_ebuilds():
            ebuild_object = models.EbuildModel()
            ebuild_object.init_by_ebuild(ebuild)
            ebuild_object.package = package_object
            # To Add some related objects it should have pk
            ebuild_object.save(force_insert=True)
            add_related_to_ebuild(ebuild, ebuild_object)

    def update_ebuilds(package, package_object, delete = True):
        not_del = []
        for ebuild in package.iter_ebuilds():
            ebuild_object, ebuild_created = models.EbuildModel.objects.get_or_create(ebuild = ebuild, package = package_object)
            not_del.append(ebuild_object.pk)
            if ebuild_created:
                add_related_to_ebuild(ebuild, ebuild_object)
                continue
            if ebuild_object.check_or_need_update(ebuild):
                ebuild_object.update_by_ebuild(ebuild)
                update_related_to_ebuild(ebuild, ebuild_object)
                ebuild_object.save(force_update = True)
        if delete:
            models.EbuildModel.objects.filter(package = package_object).exclude(pk__in = not_del).delete()

    def update_package(package, package_object, force_update = False):
        if package_object.need_update_metadata(package) or force_update:
            package_object.herds.clear()
            package_object.maintainers.clear()

        if package_object.need_update_ebuilds(package) or force_update:
            update_ebuilds(package, package_object)

        package_object.update_info(package)
        package_object.save(force_update = True)

    # Load homepages to cache
    #for homepage in models.HomepageModel.objects.all():
        #homepages_cache[homepage.url] = homepage
    existend_categorys = []
    for category in porttree.iter_categories():
        existend_packages = []
        category_object, category_created = models.CategoryModel.objects.get_or_create(category = category)
        existend_categorys.append(category_object.pk)
        for package in category.iter_packages():
            print package
            package_object, package_created = models.PackageModel.objects.get_or_create(package = package, category = category_object)
            existend_packages.append(package_object.pk)
            if not package_created:
                if package_object.check_or_need_update(package) or force_update:
                    print package
                    # need update
                    update_package(package, package_object)
                else:
                    # not need to update, ebuilds too
                    continue
            package_object.herds.add(*get_herds_objects(package))
            package_object.maintainers.add(*get_maintainers_objects(package))
            if package_created:
                create_ebuilds(package, package_object)

        if delete:
            models.PackageModel.objects.filter(category = category_object).exclude(pk__in = existend_packages).delete()
    # del 
    #models.CategoryModel.objects.exclude(pk__in = existend_categorys).delete()


