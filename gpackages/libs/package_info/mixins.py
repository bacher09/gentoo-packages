from __future__ import absolute_import
from .generic import ToStrMixin, file_sha1, file_mtime, cached_property, \
                    file_get_content, iter_over_gen, lofstr_to_ig

from .generic_metadata.use_info import get_uses_info, get_local_uses_info
# Repo info
from .generic_metadata.repo_info import TreeMetadata
# Herds
from .generic_metadata.herds import Herds
# Category metadata
from .generic_metadata.category_metadata import CategoryMetadata
#Package metadata
from .generic_metadata.package_metadata import PackageMetaData
#License group metadata
from .generic_metadata.license_groups import LicenseGroups
# Validators
from .validators import validate_url, validate_email, ValidationError
#Generic objects
from .generic_objects import Use, Keyword, KeywordsSet
# Abstract classes
from .abstract import AbstractPortage, AbstractPortTree, AbstractCategory, \
                      AbstarctPackage, AbstractEbuild

import os.path

def _file_path(file_name):
    return lambda self: os.path.join(self.package_path, file_name)

def _file_hash(attr):
    return lambda self: file_sha1(getattr(self, attr))

def _file_mtime(attr):
    return lambda self: file_mtime(getattr(self, attr))


def gen_generator_over_gen(gen_name, name):
    return lambda self: iter_over_gen(getattr(self, gen_name)(), name)

class IteratorAddMetaclass(type):
    
    def __init__(cls, name, bases, dct):
        super(IteratorAddMetaclass, cls).__init__(name, bases, dct)
        for name in cls.generator_names:
            setattr(cls, name, gen_generator_over_gen(cls.main_iterator, name))

class AutoGeneratorMixin(object):

    __metaclass__ = IteratorAddMetaclass
    generator_names = ()
    #main_iterator = 'generator_name'

def _gen_all_use(func, iterator):
    use_g = iterator
    use_all_dict = next(use_g)
    for use_dict in use_g:
        if use_dict is not None:
            func(use_all_dict, use_dict)
    return use_all_dict

class PortageBaseMixin(ToStrMixin):
    def iter_use_desc(self):
        for tree in self.iter_trees():
            yield tree.use_desc

    def iter_use_local_desc(self):
        for tree in self.iter_trees():
            yield tree.use_local_desc

    def get_all_use_desc(self):
        return _gen_all_use(lambda x,y: x.update(y), self.iter_use_desc())

    def get_all_use_local_desc(self):
        def action(all_dict, use_dict):
            for key, value in use_dict.iteritems():
                all_dict[key].update(value)

        return _gen_all_use(action, self.iter_use_local_desc())

class PortageIteratorMixin(AutoGeneratorMixin):
    main_iterator = 'iter_trees'
    generator_names = ('iter_categories', 'iter_packages', 'iter_ebuilds')

class PortageHerdsMixin(object):
    
    @cached_property
    def herds(self):
        "Return new `Herds` object"
        return Herds()

    @cached_property
    def license_groups(self):
        "Return new `LicenseGroups` object"
        return LicenseGroups()

def _get_info_by_func(func, path1, path2):
        path = os.path.join(path1, path2)
        try:
            return func(path)
        except IOError:
            return None

class PortTreeBaseMixin(ToStrMixin):

    @cached_property
    def metadata(self):
        return TreeMetadata(self.name)

    @cached_property
    def use_desc(self):
        return _get_info_by_func(get_uses_info,
                                 self.porttree_path,
                                 'profiles/use.desc')

    @cached_property
    def use_local_desc(self):
        return _get_info_by_func(get_local_uses_info,
                                 self.porttree_path,
                                 'profiles/use.local.desc')

    def __unicode__(self):
        return self.name

class PortTreeIteratorMixin(AutoGeneratorMixin):
    main_iterator = 'iter_categories'
    generator_names = ('iter_packages', 'iter_ebuilds')
    
class CategoryBaseMixin(ToStrMixin):

    @property
    def metadata_path(self):
        return os.path.join(self.category_path, 'metadata.xml')

    @cached_property
    def metadata_sha1(self):
        return file_sha1(self.metadata_path)

    @cached_property
    def metadata(self):
        return CategoryMetadata(self.metadata_path)

    def __unicode__(self):
        return self.name

class CategoryIteratorMixin(AutoGeneratorMixin):
    main_iterator = 'iter_packages'
    generator_names = ('iter_ebuilds', )

class PackageBaseMixin(ToStrMixin):

    @cached_property
    def metadata(self):
        "Return `MetaData` object that represent package metadata.xml file"
        return PackageMetaData(self.metadata_path)

    @cached_property
    def descriptions(self):
        return self.metadata.descriptions()

    @cached_property
    def description(self):
        "Return first description in package metadata.xml"
        return self.metadata.description

    @cached_property
    def descriptions_dict(self):
        return self.metadata.descriptions_dict()

    @property
    def cp(self):
        raise NotImplementedError

    def __unicode__(self):
        return unicode(self.cp)

class PackageFilesMixin(object):
    #Paths 
    manifest_path = property(_file_path('Manifest'))
    changelog_path = property(_file_path('ChangeLog'))
    metadata_path = property(_file_path('metadata.xml'))

    #Hashes
    manifest_sha1 = cached_property(_file_hash('manifest_path'),
                                    name = 'manifest_sha1')
    changelog_sha1 = cached_property(_file_hash('changelog_path'),
                                     name = 'changelog_sha1')
    metadata_sha1 = cached_property(_file_hash('metadata_path'),
                                    name = 'metadata_sha1')

    # Modify times
    manifest_mtime = property(_file_mtime("manifest_path"))
    changelog_mtime = property(_file_mtime("changelog_path"))
    metadata_mtime = property(_file_mtime("metadata_path"))

    mtime = property(_file_mtime("package_path"))

    @cached_property
    def changelog(self):
        "Return ChangeLog content"
        return file_get_content(self.changelog_path)

class EbuildBaseMixin(ToStrMixin):

    sha1 = cached_property(_file_hash("ebuild_path"), name = 'sha1')
    mtime = cached_property(_file_mtime("ebuild_path"), name = 'mtime')
    
    @property
    def cpv(self):
        raise NotImplementedError

    def __unicode__(self):
        return unicode(self.cpv)

class EbuildHomepageMixin(object):

    @cached_property
    def homepages_splited(self):
        return self.homepage_env.split()

    @cached_property
    def homepages_validated(self):
        ret = []
        for homepage in self.homepages_splited:
            try:
                validate_url(homepage)
            except ValidationError:
                pass
            else:
                ret.append(homepage)
        return ret
        
    @cached_property
    def homepages(self):
        "Tuple of valid homepages"
        return tuple(set(lofstr_to_ig(self.homepages_validated)))

    @cached_property
    def homepage(self):
        "First valid homepage in list"
        return self.homepages_validated[0] if len(self.homepages)>=1 else ''

def _license_filter(x):
    if x.startswith('|') or x.startswith('(') or x.endswith('?') or \
                                                 x.startswith(')'):
        return False
    else:
        return True

class EbuildLicenseMixin(object):

    @cached_property
    def _licenses(self):
        return filter(_license_filter, self.license.split())

    @cached_property
    def licenses(self):
        "Tuple of unique licenses"
        return tuple(set(lofstr_to_ig(self._licenses)))

class EbuildKeywordsMixin(object):

    @property
    def keywords(self):
        return tuple(set(self.keywords_env.split()))
    
    def iter_keywords(self):
        "Iterate over keywords, yields Keyword object"
        keywords = self.keywords
        for keyword in keywords:
            yield Keyword(keyword)
        
    def get_keywords(self):
        l = []
        for keyword in self.iter_keywords():
            l.append(keyword)
        return l

    def get_uniq_keywords(self):
        return KeywordsSet(self.get_keywords())

class EbuildUseMixin(object):

    @property
    def iuse(self):
        return self.iuse_env.split()
    
    def iter_uses(self):
        "Iterator over all uses, yiels `Use` object"
        for use in self.iuse:
            yield Use(use)

    def get_uses(self):
        l = [] 
        for use in self.iter_uses():
            l.append(use)
        return l

    def get_uniq_uses(self):
        return frozenset(self.get_uses())


class EbuildGenericProp(EbuildHomepageMixin, EbuildLicenseMixin, \
                        EbuildKeywordsMixin, EbuildUseMixin):
    pass


#Main mixins
class PortageMixin(PortageBaseMixin, PortageHerdsMixin, PortageIteratorMixin, AbstractPortage):
    pass

class PortTreeMixin(PortTreeBaseMixin, PortTreeIteratorMixin, AbstractPortTree):
    pass

class CategoryMixin(CategoryBaseMixin, CategoryIteratorMixin, AbstractCategory):
    pass

class PackageMixin(PackageBaseMixin, PackageFilesMixin, AbstarctPackage):
    pass

class EbuildMixin(EbuildBaseMixin, EbuildGenericProp, AbstractEbuild):
    pass
