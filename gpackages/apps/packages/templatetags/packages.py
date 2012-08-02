from django.utils.safestring import mark_safe
from django import template
from django.core.cache import cache
from package_info.generic_metadata.changelog_highlight import changelog_highlight

register = template.Library()

from ..models import RepositoryModel, EbuildModel, UseFlagDescriptionModel
from ..views import arches
from ..forms import ArchChoiceForm, FilteringForm
from ..utils import license_urlize
from generic.utils import inclusion_cached_tag

def last_updated_key():
    return 'last_updated_th'

@inclusion_cached_tag('last_updated.html', register, last_updated_key, \
                                                     time_zone = False)
def last_updated():
    updated = cache.get('last_updated_t')
    if not updated:
        try:
            l = RepositoryModel.objects.only('updated_datetime'). \
                latest('updated_datetime')
        except RepositoryModel.DoesNotExist:
            updated = None
        else:
            updated = l.updated_datetime
            cache.set('last_udpated_t', updated)

    return {'last_updated': updated}

@register.inclusion_tag('keywords_table.html')
def render_keywords_table(obj, arch_list):
    ebuilds = obj.get_ebuilds_and_keywords(arch_list)
    return {'arches': arch_list, 'ebuilds' : ebuilds}

def text_sincode(text):
    if not text:
        return ''
    text_l = map(lambda x: '&#%s;' % ord(x), text)
    return mark_safe(''.join(text_l))

@register.filter('changelog_highlight')
def changelog_highlight_filter(text):
    return mark_safe(changelog_highlight(text))

register.filter('obfuscate', text_sincode)
register.filter('license_urlize', license_urlize)

def recent_ebuilds_cache_key(num = 10):
    return 'recent_ebuilds_th_' + str(num)

@inclusion_cached_tag('recent_ebuilds.html', register, \
                      recent_ebuilds_cache_key, time_zone = False)
def recent_ebuilds(num = 10):
    query = EbuildModel.objects.order_by('-updated_datetime').all().\
        select_related('package',
                       'package__virtual_package',
                       'package__virtual_package__category'). \
                       prefetch_related('package__repository')[:num]
    return {'ebuilds': query}

@register.inclusion_tag('modals/arch_choice_modal.html', takes_context = True)
def arch_choice_modal(context):
    request = context['request']
    arches_s = request.session.get('arches')
    arches_s = arches_s or arches
    initial = {'arches': arches_s, 'next' : request.path}
    return {'form': ArchChoiceForm(initial = initial), 'arches': arches_s}

@register.inclusion_tag('modals/filtering_modal.html', takes_context = True)
def filtering_modal(context):
    filters = context.get('filters_dict')
    initial = {}
    if filters:
        for item, k in zip(FilteringForm.names, FilteringForm.f_names):
            if k in filters:
                v = filters[k]
                if not isinstance(v, list):
                    v = [v]
                initial[item] = v

    form = FilteringForm(initial = initial)
    return {'form': form }

def use_flag_table_key(ebuild):
    if ebuild:
        return 'use_flag_table_ebuild' + str(ebuild.pk)
    else:
        return 'use_flag_table_ebuild' + str(ebuild)

@inclusion_cached_tag('ebuild_use_flag.html', register, use_flag_table_key,
                                                        time_zone = False)
def use_flag_table(ebuild):
    use_flags = []
    if ebuild is not None:
        use_flags = ebuild.use_flags_with_descr()

    return {'use_flags': use_flags}
