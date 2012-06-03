import re
from collections import defaultdict

USES_RE = r'(?P<use>[^#].*) - (?P<description>.*)'
USES_DESC_RE = r'^%s$' % USES_RE
USES_LOCAL_DESC_RE = r'^(?P<package>[^#].*):%s$' % USES_RE

use_re = re.compile(USES_DESC_RE)
use_local_re = re.compile(USES_LOCAL_DESC_RE)

def _get_info(filename, re_string, modify_function, res_var = {}):
    use_desc = open(filename, 'r').read()
    uses_desc = use_desc.split("\n")
    res_dict = res_var
    for use_str in uses_desc:
        res_match = re_string.match(use_str)
        if res_match is not None:
            modify_function(res_dict, res_match.groupdict())

    return res_dict

def get_uses_info(filename = '/usr/portage/profiles/use.desc'):
    def action(res_dict, match):
        res_dict[match['use']] = match['description']

    return _get_info(filename, use_re, action)

def get_local_uses_info(filename = '/usr/portage/profiles/use.local.desc'):
    def action(res_dict, match):
        res_dict[match['use']][match['package']] = match['description']

    return _get_info(filename, use_local_re, action, defaultdict(dict))
