from package_info.generic import ToStrMixin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
import re
LICENSE_STR_RE = r'[a-zA-Z0-9_\-\+\.]+'
USE_FLAG_RE = r'[a-zA-Z0-9]+\?'
license_re = re.compile(LICENSE_STR_RE)
use_re = re.compile(USE_FLAG_RE)

def gen_args(args):
    t = '%s=%s'
    l = (t % arg for arg in args)
    return '&'.join(l)

def get_link(host, script, args):
    return 'http://%(host)s/%(script)s?%(args)' % {'host': host,
                                                   'script': script,
                                                   'args': get_args(args)}

def license_tokenize(license_str):
    s, l = 0, len(license_str)
    while s<l:
        m = use_re.match(license_str, s)
        if m is not None:
            yield ('use', m.group())
            s = m.end()
            continue
        m = license_re.match(license_str, s)
        if m is not None:
            yield ('license', m.group())
            s = m.end()
            continue
        
        yield (None, license_str[s])
        s += 1

def license_urlize(license_str):
    res_str = u''
    for token, value in license_tokenize(license_str):
        value = escape(value)
        if token == 'license':
            try:
                link = reverse('license', kwargs = {'slug': value})
            except NoReverseMatch:
                pass
            else:
                value = mark_safe('<a href="{1}">{0}</a>'.format(value, link))

        res_str += value
    return mark_safe(res_str)
