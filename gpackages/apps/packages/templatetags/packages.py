from django.utils.safestring import mark_safe
from django import template
from django.core.cache import cache

register = template.Library()

from ..models import RepositoryModel, EbuildModel
from ..views import arches
from ..forms import ArchChoiceForm, FilteringForm

@register.inclusion_tag('last_updated.html')
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

register.filter('obfuscate', text_sincode)

@register.inclusion_tag('recent_ebuilds.html')
def recent_ebuilds(num = 10):
    query = EbuildModel.objects.order_by('-updated_datetime').all().\
        select_related('package',
                       'package__virtual_package',
                       'package__virtual_package__category'). \
                       prefetch_related('package__repository')[:num]
    return {'ebuilds': query}

@register.inclusion_tag('arch_choice_modal.html', takes_context = True)
def arch_choice_modal(context):
    request = context['request']
    arches_s = request.session.get('arches')
    arches_s = arches_s or arches
    return {'form': ArchChoiceForm(initial = {'arches': arches_s}),
            'arches': arches_s}

@register.inclusion_tag('filtering_modal.html')
def filtering_modal():
    form = FilteringForm()
    return {'form': form }
