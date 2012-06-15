from django import template

register = template.Library()

from ..models import RepositoryModel

@register.inclusion_tag('last_updated.html')
def last_updated():
    l = RepositoryModel.objects.only('updated_datetime').latest('updated_datetime')
    return {'last_updated': l.updated_datetime}
