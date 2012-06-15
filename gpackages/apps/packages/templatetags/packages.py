from django.utils.safestring import mark_safe
from django import template

register = template.Library()

from ..models import RepositoryModel

@register.inclusion_tag('last_updated.html')
def last_updated():
    l = RepositoryModel.objects.only('updated_datetime').latest('updated_datetime')
    return {'last_updated': l.updated_datetime}


def text_sincode(text):
    text_l = map(lambda x: '&#%s;' % ord(x), text)
    return mark_safe(''.join(text_l))

register.filter('obfuscate', text_sincode)
