from datetime import datetime
from packages import models
import sys
from django.db import IntegrityError
from django.db import transaction
from django.utils.encoding import smart_unicode
from collections import defaultdict
from package_info.generic import StrThatIgnoreCase, toint
from package_info.porttree import porttree
from django.core.cache import cache as cache_backend
import logging
import anydbm
logger = logging.getLogger(__name__)

portage = porttree

def _get_from_cache(cache, what):
    save_to = []
    geted_items = set()
    for item in what:
        if item.lower() in cache:
            item = StrThatIgnoreCase(item)
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
        val = StrThatIgnoreCase(getattr(item, field_name))
        cache[val] = item
        geted_items.add(val)
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
    queryset, geted = _get_from_database_and_update_cache(Model, field_name, 
        items_set - geted_items, cache_var)
    if queryset is None:
        return items_objects
    geted_items = geted_items | geted

    # Add to list with items 
    items_objects.extend(queryset)
    # Create not existend items fast using bulk_create, works only in django 1.4 or gt
    need_create = list(items_set - geted_items)
    created, geted = _create_objects_and_update_cache(Model, field_name, 
                                                      need_create, cache_var)
    if created is None:
        return items_objects
    items_objects.extend(created)
    geted_items = geted_items | geted
    return items_objects
    
class Scanner(object):
    "General class for scan and collect data from portage"
    def __init__(self, **kwargs):
        # maintainers_cache: maintainer.email as key, and maintainer object as
        # value
        self.maintainers_cache = {}
        self.maintainers_cache_loaded = False
        # herds cache: herd.name as key and herd object as value
        self.herds_cache = {}
        self.herds_cache_loaded = False
        self.licenses_cache = {}
        self.uses_cache = {}
        self.arches_cache = {}
        self.homepages_cache = {}    
        self.herds_cache = {}
        self.maintainers_cache = {}
        self.herds_object = portage.herds

        self.arches_cache = {}

        self.update_options(**kwargs)
        self.reset_timer()

    def reset_timer(self):
        self.start_time = datetime.now()

    def update_options(self, **kwargs):
        bool_get = lambda x,y: bool(kwargs.get(x, y))

        self.verbosity = toint(kwargs.get('verbosity',1),1)
        self.traceback = bool_get('traceback',False)
        self.s_all = bool_get('scan_all', False)
        self.s_packages = bool_get('packages', False)
        self.s_only_repo_info = bool_get('only_repo_info', False)
        self.is_show_time = bool_get('show_time', True)
        self.is_scan_herds = bool_get('scan_herds', True)
        self.force_update = bool_get('force_update', False)
        self.update_repo = bool_get('update_repo', False)
        self.delete = bool_get('delete', True)
        self.scan_repos_name = tuple(kwargs.get('repos',[]))
        self.scan_global_use_descr = bool_get('scan_global_use', False)
        self.scan_local_use_descr = bool_get('scan_local_use', False)
        self.is_scan_license_groups = bool_get('scan_license_groups', False)
        self.is_scan_news = bool_get('scan_news', False)
        self.is_scan_license_text = bool_get('license_text', False)
        self.is_cache_clear = bool_get('cache_clear', False)
        self.is_set_latest_ebuilds = bool_get('set_latest_ebuilds', False)

    def show_time(self):
        "Prints scan time"
        end = datetime.now()
        t_time = end - self.start_time
        self.output("Scanning time is: %s secconds.\n", t_time.total_seconds())

    def scan(self):
        """General method for scan and collect data
        It check object properties and scan only what property require"""
        if self.is_scan_herds:
            self.scan_herds()

        if self.s_all and self.s_packages:
            self.scan_all_repos(force_update = self.force_update,
                                delete = self.delete,
                                update_repo = self.update_repo)
        elif len(self.scan_repos_name) > 0 and self.s_packages:
            self.scan_repos_by_name(self.scan_repos_name,
                                    force_update = self.force_update,
                                    delete = self.delete,
                                    update_repo = self.update_repo)
        elif self.s_only_repo_info and self.s_all:
            self.scan_all_repo_info(delete = self.delete)
        elif self.s_only_repo_info and len(self.scan_repos_name) > 0:
            self.scan_repo_info_by_names(self.scan_repos_name)

        if self.is_set_latest_ebuilds:
            self.set_latest_ebuilds_to_package()

        if self.scan_global_use_descr:
            self.update_all_globals_uses_descriptions()

        if self.scan_local_use_descr:
            self.scan_all_uses_description()

        if self.is_scan_license_groups:
            self.scan_license_groups()

        if self.is_scan_news:
            self.scan_news()

        if self.is_scan_license_text:
            self.scan_license_text()

        if self.is_cache_clear:
            cache_backend.clear()

        if self.is_show_time:
            self.show_time()

    def write(self, what, verbosity = 1):
        """If object vervosity level are greate or equal to
        method property verbosity prints param what
        Args:
            what -- string to print
            vervosity -- level of verbosity that require for print string
        """
        if verbosity <= self.verbosity:
            sys.stdout.write(what)

    def output(self, format_str, whats, verbosity = 1):
        """If object vervosity level are greate or equal to
        method property verbosity prints param whats formated by param format_str
        Args:
            format_str -- formating string
            what -- vals to print
            vervosity -- level of verbosity that require for print string
        """
        # Maybe implement lazy format string ?
        if verbosity <= self.verbosity:
            sys.stdout.write(format_str % whats)

    def get_existent_maintainers(self):
        return models.MaintainerModel.objects.all()

    def get_existent_herds(self):
        return models.HerdsModel.objects.all()

    def get_maintainers_cache(self):
        maintainers_dict = {}
        existent_maintainers = self.get_existent_maintainers()
        _update_cache_by_queryset(maintainers_dict, existent_maintainers, 'email')
        return maintainers_dict

    def load_maintainers_to_cache(self):
        self.maintainers_cache = self.get_maintainers_cache()
        self.maintainers_cache_loaded = True
        
    def get_herds_cache(self):
        herds_dict = {}
        existent_herds = self.get_existent_herds()
        _update_cache_by_queryset(herds_dict, existent_herds, 'name')
        return herds_dict

    def load_herds_to_cache(self):
        if not self.herds_cache_loaded:
            self.herds_cache = self.get_herds_cache()
            self.herds_cache_loaded = True

    def scan_maintainers(self, maintainers_dict):
        existend_maintainers = self.get_existent_maintainers()
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

                    # Show info if need
                    self.output("update maintainer '%s'\n", maintainer_object, 2)
                mo_dict[maintainer_object.email] = maintainer_object

        to_create = []
        for maintainer in maintainers_dict.iterkeys():
            if maintainer.email not in mo_dict:
                self.output("create maintainer '%s'\n", maintainer, 2)
                to_create.append(maintainer)

        mobjects = _create_objects(models.MaintainerModel, 'maintainer', to_create)
        _update_cache_by_queryset(mo_dict, mobjects, 'email')

        self.maintainers_cache = mo_dict
        self.maitainers_cache_loaded = True

    @transaction.commit_on_success
    def scan_license_groups(self):
        "Scan license groups"
        self.write('Scaning license groups\n', 3)
        for group, licenses in portage.license_groups.groups_dict.iteritems():
            licenses_obj = self.get_licenses_objects(licenses)
            group_obj, created = models.LicenseGroupModel.objects. \
                get_or_create(name = group)

            group_obj.licenses.clear()
            group_obj.licenses.add(*licenses_obj)

            self.output("update license group '%s'\n", group, 2)
            
    @transaction.commit_on_success
    def scan_herds(self):
        "Scan herds and maintainers in herds.xml"
        self.write('Scaning herds\n', 3)
        existent_herds = self.get_existent_herds()
        herds_dict = self.herds_object.get_herds_indict()
        herds_objects_dict = {}
        to_del = []
        for herd_object in existent_herds:
            if herd_object.name not in herds_dict:
                to_del.append(herd_object.pk)
                self.output("herd to del '%s'\n", herd_object, 2)
            else:
                herd_cmp = herds_dict[herd_object.name]
                # need update ?
                if herd_object.check_or_need_update(herd_cmp):
                    # updating 
                    herd_object.update_by_herd(herd_cmp)
                    herd_object.save(force_update = True)
                    self.output("update herd '%s'\n", herd_object, 2)
                herds_objects_dict[herd_object.name] = herd_object

        models.HerdsModel.objects.filter(pk__in = to_del).delete()

        to_create = []
        for herd in herds_dict.itervalues():
            if herd.name not in herds_objects_dict:
                to_create.append(herd)
                self.output("create herd '%s'\n", herd, 2)

        cobjects = _create_objects(models.HerdsModel, 'herd', to_create)
        _update_cache_by_queryset(herds_objects_dict, cobjects, 'name')

        # Add to cache
        self.herds_cache = herds_objects_dict
        self.herds_cache_loaded = True
        # Add related maintainers to herds
        self._add_related_to_herds()


    def _get_maintainers_for_relation_with_herds(self, maintainers_dict):
        res = defaultdict(list)
        for mainteiner, herds_names in maintainers_dict.iteritems():
           for herd in herds_names:
               res[herd].append(self.maintainers_cache[mainteiner.email])
        return res

    def _add_related_to_herds(self):
        maintainers_dict = self.herds_object.get_maintainers_with_herds()
        self.scan_maintainers(maintainers_dict)
        #Gen data for relate with herds
        res = self._get_maintainers_for_relation_with_herds(maintainers_dict)

        for herd_name, herd_object in self.herds_cache.iteritems():
            herd_object.maintainers.clear()
            herd_object.maintainers.add(*res[herd_name])

            self.output("add maintainers '%s' to mantainer '%s'\n", 
                (res[herd_name], herd_object), 3)

    def get_maintainers(self):
        if not self.maintainers_cache_loaded:
            self.load_maintainers_to_cache()
        return self.maintainers_cache

    def scan_all_repos(self, **kwargs):
        "Scan packages in all available trees"
        #cache_dict = anydbm.open('cache.db','c')

        for repo in portage.iter_trees():
            self.scan_repo(repo, **kwargs)
        #cache_dict.close()

    def scan_repos_by_name(self, repo_names, **kwargs):
        for repo_name in repo_names:
            self.scan_repo_by_name(repo_name, **kwargs)

    def get_repo_by_name(self, repo_name, quiet = False, trace = False):
        try:
            repo = portage.get_tree_by_name(repo_name)
        except ValueError:
            if not quiet:
                self.output("Bad repository name '%s'\n", repo_name, 1)
            if trace:
                raise
            return None
        else:
            return repo

    def scan_repo_by_name(self, repo_name, **kwargs):
        """Scan repository by name, available repository names could be se 
        with manage.py listrepos command
        Args:
            repo_name -- repository name"""
        repo = self.get_repo_by_name(repo_name)

        if repo is not None:
            self.scan_repo(repo, **kwargs)

    @transaction.commit_on_success
    def get_repo_obj(self, repo, update_repo = False):
        repo_obj, repo_created = models.RepositoryModel \
            .objects.get_or_create(repo = repo)

        if not repo_created:
            if update_repo:
                repo_obj.update_metadata(repo)
                repo_obj.update_related(repo)
            #Update modification time
            repo_obj.save(force_update = True)
        else:
            repo_obj.add_related(repo)

        return repo_obj

    def scan_all_repo_info(self, delete = False):
        """Scan all info (metada) of all available repositories
        Args:
            delete -- if this true that repository will delete
                      if portage would be not available"""
        ex_pk = []
        for repo in portage.iter_trees():
            repo_obj = self.get_repo_obj(repo, update_repo = True)
            self.output("Scaned [%s]\n", repo.name)
            ex_pk.append(repo_obj.pk)

        if delete:
            models.RepositoryModel.objects.exclude(pk__in = ex_pk).delete()

    def scan_repo_info_by_names(self, repo_list):
        for repo_name in repo_list:
            repo = self.get_repo_by_name(repo_name)
            if repo is not None:
                self.get_repo_obj(repo, update_repo = True)
                self.output("Scaned [%s]\n", repo.name)

    def scan_repo(self, repo, update_repo = False, **kwargs):
        self.output("Scaning repository '%s'\n", repo.name, 3)

        repo_obj = self.get_repo_obj(repo, update_repo = update_repo)
        self.scanpackages(repo, repo_obj, **kwargs)
        

    def get_licenses_objects(self, licenses):
        return _get_items(licenses, models.LicenseModel, 'name', self.licenses_cache)

    def get_uses_objects(self, ebuild):
        uses = [ use.name for use in ebuild.iter_uses() ]
        return _get_items(uses, models.UseFlagModel, 'name', self.uses_cache)

    def get_homepages_objects(self, ebuild):
        homepages = ebuild.homepages
        return _get_items(homepages, models.HomepageModel, 'url', self.homepages_cache)

    def get_maintainers_objects(self, maintainers, update_maintainer = False):
        objects = []
        #for maintainer in package.metadata.maintainers():
        for maintainer in maintainers:
            if maintainer.email in self.maintainers_cache:
                m_obj = self.maintainers_cache[maintainer.email]
            else:
                m_obj, created = models.MaintainerModel \
                        .objects.get_or_create(maintainer = maintainer)
                # Add to cache
                self.maintainers_cache[m_obj.email] = m_obj

            #If we find maintainer name
            if (update_maintainer or m_obj.name is None) and \
                    smart_unicode(m_obj.name) != smart_unicode(maintainer.name):

                m_obj.name = maintainer.name
                m_obj.save(force_update = True)

            objects.append(m_obj)
        return objects

    def get_herds_objects(self, package):
        self.load_herds_to_cache()
        herds_objects = []
        for herd in package.metadata.herds():
            if herd in self.herds_cache:
                herds_objects.append(self.herds_cache[herd])

        return herds_objects

    def get_arch_object(self, arch_name):
        if arch_name in self.arches_cache:
            arch = self.arches_cache[arch_name]
        else:
            arch, created = models.ArchesModel.objects \
                .get_or_create(name = arch_name)
            self.arches_cache[arch_name] = arch
        return arch

    def create_keywords_objects(self, ebuild, ebuild_object):
        keywords_list = []
        for keyword in ebuild.get_uniq_keywords():
            keyword_object = models.Keyword(status = keyword.status,
                                            ebuild = ebuild_object)

            keyword_object.arch = self.get_arch_object(keyword.arch)
            keywords_list.append(keyword_object)

        models.Keyword.objects.bulk_create(keywords_list)

    def clean_keywords_object(self, ebuild_object):
        models.Keyword.objects.filter(ebuild = ebuild_object).delete()

    def add_related_to_ebuild(self, ebuild, ebuild_object):
        # Add licenses
        ebuild_object.licenses.add(*self.get_licenses_objects(ebuild.licenses))
        ebuild_object.use_flags.add(*self.get_uses_objects(ebuild))
        ebuild_object.homepages.add(*self.get_homepages_objects(ebuild))
        self.create_keywords_objects(ebuild, ebuild_object)
        
    def clear_related_to_ebuild(self, ebuild_object):
        ebuild_object.licenses.clear()
        ebuild_object.use_flags.clear()
        ebuild_object.homepages.clear()
        self.clean_keywords_object(ebuild_object)

    def update_related_to_ebuild(self, ebuild, ebuild_object):
        self.clear_related_to_ebuild(ebuild_object)
        self.add_related_to_ebuild(ebuild, ebuild_object)

    def create_ebuilds(self, package, package_object):
        for ebuild in package.iter_ebuilds():
            ebuild_object = models.EbuildModel()
            ebuild_object.init_by_ebuild(ebuild)
            ebuild_object.package = package_object
            # To Add some related objects it should have pk
            ebuild_object.save(force_insert=True)
            self.add_related_to_ebuild(ebuild, ebuild_object)

            self.output("ebuild created '%s'\n", ebuild_object, 3)

    def clear_related_to_package(self, package_object):
        package_object.herds.clear()
        package_object.maintainers.clear()
        

    def add_related_to_package(self, package, package_object):
        package_object.herds.add(*self.get_herds_objects(package))
        package_object.maintainers. \
            add(*self.get_maintainers_objects(package.metadata.maintainers()))

    def update_related_to_package(self, package, package_object):
        self.clear_related_to_package(package_object)
        self.add_related_to_package(package, package_object)

    def update_ebuilds(self, package, package_object, delete = True,
                                                      force_update = False):

        not_del = []
        for ebuild in package.iter_ebuilds():
            ebuild_object, ebuild_created = models.EbuildModel.objects \
                .get_or_create(ebuild = ebuild, package = package_object)

            not_del.append(ebuild_object.pk)
            if ebuild_created:
                self.add_related_to_ebuild(ebuild, ebuild_object)
                self.output("ebuild created '%s'\n", ebuild_object, 3)

            if ebuild_object.check_or_need_update(ebuild) or force_update:
                ebuild_object.update_by_ebuild(ebuild)
                self.update_related_to_ebuild(ebuild, ebuild_object)
                ebuild_object.save(force_update = True)

                self.output("ebuild updated '%s'\n", ebuild_object, 3)
        if delete:
            models.EbuildModel.objects.filter(package = package_object) \
                .exclude(pk__in = not_del).delete()

    def update_package(self, package, package_object, force_update = False):
        if package_object.need_update_metadata(package) or force_update:
            #Updating related objects to package
            self.update_related_to_package(package, package_object)

        if package_object.need_update_ebuilds(package) or force_update:
            self.update_ebuilds(package, package_object,
                force_update = force_update)

        package_object.update_info(package)
        package_object.save(force_update = True)

    def scanpackages(self, porttree, porttree_obj, delete = True,
                     force_update = False, update_cache = True, use_cache = True):
        """Scan packages (and ebuilds) in porttree
        Args:
            porttree -- `PortTree` object from packages_info
            porttree_obj -- `RepositoryModel` object
            delete -- if True will delete unavailable packages and ebuilds
            force_update -- update packages and ebuilds even if manifest not changed
        """

        existend_categorys = []
        for category in porttree.iter_categories():
            existend_packages = []
            category_object, category_created = models.CategoryModel \
                .objects.only('category','metadata_hash') \
                .get_or_create(category = category)

            if not category_created:
                if category_object.check_or_need_update(category):
                    category_object.update_by_category(category)
                    category_object.save(force_update = True)

            existend_categorys.append(category_object.pk)
            for package in category.iter_packages():
                #if use_cache:
                    #key = str(porttree.name)+'/'+str(package)
                    #val = None
                    #if key in cache_dict:
                        #val = cache_dict[key]
                    #if val is not None and val == package.manifest_sha1:
                        #continue
                self.output('%-44s [%s]\n', (package, porttree))
                package_object, package_created = models.PackageModel.objects \
                    .only('changelog_hash', 'manifest_hash', 'metadata_hash') \
                    .get_or_create(package = package,
                                   category = category_object,
                                   repository = porttree_obj)
                #if update_cache:
                    #key = str(porttree.name)+'/'+str(package)
                    #cache_dict[key] = package.manifest_sha1
                    
                existend_packages.append(package_object.pk)
                if not package_created:
                    if package_object.check_or_need_update(package) or force_update:
                        # need update
                        self.update_package(package, package_object,
                            force_update = force_update)

                    continue
                # if package_created:
                self.add_related_to_package(package, package_object)
                self.create_ebuilds(package, package_object)

            if delete:
                models.PackageModel.objects \
                .filter(category = category_object, repository = porttree_obj) \
                .exclude(pk__in = existend_packages).delete()


    def update_globals_uses_descriptions(self, use_dict):
        existend_use_objects = models.UseFlagModel.objects.only('name') \
            .filter(name__in = use_dict.keys())

        for use_object in existend_use_objects:
            use_object.description = use_dict[use_object.name.lower()]
            use_object.save(force_update = True)

    def update_all_globals_uses_descriptions(self):
        self.update_globals_uses_descriptions(portage.get_all_use_desc())

    def scan_all_uses_description(self):
        self.scan_uses_description(portage.get_all_use_local_desc())

    def scan_uses_description(self, use_local_desc):
        existent_use_objects = models.UseFlagModel.objects \
            .filter(name__in = use_local_desc.keys())

        existent_use_local_descr = models.UseFlagDescriptionModel.objects.all()
        cache_uses = {}
        _update_cache_by_queryset(cache_uses, existent_use_objects, 'name')

        # Cache existent Use Local Descr
        use_local_cache = defaultdict(dict)
        for use_obj in existent_use_local_descr:
            use_local_cache[use_obj.use_flag.name][use_obj.package.cp] = use_obj

        package_cache = dict()
        for use_flag, packages_dict in use_local_desc.iteritems():
            # If this use flag not in database than create it
            if use_flag not in cache_uses:
                # Maybe get_or_create ?
                use_flag_object = models.UseFlagModel.objects \
                    .create(name = use_flag)
                # Add to cache
                cache_uses[use_flag.lower()] = use_flag_object
            else:
                use_flag_object = cache_uses[use_flag]

            to_create = []
            for package, description in packages_dict.iteritems():
                if package in package_cache:
                    package_object = package_cache[package]
                else:
                    try:
                        package_object = models.VirtualPackageModel.objects \
                            .get(package = package)

                    except models.VirtualPackageModel.DoesNotExist:
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

    def scan_news(self):
        for tree in porttree.iter_trees():
            if tree.news is not None:
                for news in tree.news.iter_news():
                    self.scan_news_item(news)

    def add_related_to_news(self, news, news_obj):
        authors_obj = self.get_maintainers_objects(news.authors,
                                                   update_maintainer = True)
        news_obj.authors.add(*authors_obj)
        translators_obj = self.get_maintainers_objects(news.translators,
                                                       update_maintainer = True)
        news_obj.translators.add(*translators_obj)

    def update_related_to_news(self, news, news_obj):
        news_obj.clear_related()
        self.add_related_to_news(news, news_obj)
                 
    @transaction.commit_on_success
    def scan_news_item(self, news_item):
        for n in news_item.news.itervalues():
            n_obj, created = models.PortageNewsModel.objects. \
                only('hash').get_or_create(news = n)

            if created:
                self.add_related_to_news(n, n_obj)
            # and not creted 
            if n.sha1 != n_obj.hash:
                n_obj.update_by_news(n)
                n_obj.save(force_update = True)
                self.update_related_to_news(n, n_obj)

    def scan_license_text(self):
        licenses = models.LicenseModel.objects.all()
        for license in licenses:
            text = porttree.licenses.get_license(license.name)
            if text:
                license.text = smart_unicode(text, errors='ignore')
                license.save(force_update = True)

    @staticmethod
    def set_latest_ebuilds_to_package():
        for package_id, in models.PackageModel.objects.values_list('pk'):
            # search latest ebuild should done by version and revision
            # and database could not allow smart order by version becaouse
            # version are compared as string
            ebuilds = models.EbuildModel.objects.filter(package = package_id)
            try:
                latest_ebuild = max(ebuilds, key = lambda x: x.version_cmp)
            except ValueError:
                logger.exception('Bad package without ebuilds %s' % package_id)
            # Hack for not update last modified datetime
            models.PackageModel.objects.filter(pk = package_id). \
                update(latest_ebuild = latest_ebuild)
