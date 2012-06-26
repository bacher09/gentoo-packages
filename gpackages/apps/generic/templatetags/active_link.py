from django import template
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
register = template.Library()

@register.simple_tag(takes_context = True)
def active_str(context, url):
    request = context['request']
    if request.path == url :
        return "active"
    return ""

# Waring this work only in django>=1.4
@register.simple_tag(takes_context = True)
def active_link(context, url_name, text, *args, **kwargs):
    request = context['request']
    try:
        url = reverse(url_name, *args, **kwargs)
    except NoReverseMatch:
        url = '#'

    class_str = ''
    if request.path == url:
        class_str = ' class="active"'
    # This would be faster that render in template :)
    format_str = '<li{2}><a href="{0}">{1}</a><li>'
    return format_str.format(url, text, class_str)
