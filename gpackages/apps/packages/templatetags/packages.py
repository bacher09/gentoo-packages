from django.utils.safestring import mark_safe
from django import template

register = template.Library()

from ..models import RepositoryModel

@register.inclusion_tag('last_updated.html')
def last_updated():
    l = RepositoryModel.objects.only('updated_datetime').latest('updated_datetime')
    return {'last_updated': l.updated_datetime}

@register.inclusion_tag('keywords_table.html')
def render_keywords_table(obj, *arch_list):
    ebuilds = obj.get_ebuilds_and_keywords(arch_list)
    return {'arches': arch_list, 'ebuilds' : ebuilds}

def text_sincode(text):
    text_l = map(lambda x: '&#%s;' % ord(x), text)
    return mark_safe(''.join(text_l))

register.filter('obfuscate', text_sincode)
