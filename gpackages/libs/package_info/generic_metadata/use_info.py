import re
from collections import defaultdict
import os.path
import os

__all__ = ('get_uses_info', 'get_local_uses_info', 'get_use_special_info')

USES_RE = r'(?P<use>[a-zA-Z0-9\-_]+) - (?P<description>.*)'
USES_DESC_RE = r'^%s$' % USES_RE
USES_LOCAL_DESC_RE = r'^(?P<package>[^#].*):%s$' % USES_RE
DESC_USE_RE = r'^(?P<name>[^\.]+)\.desc$'

use_re = re.compile(USES_DESC_RE)
use_local_re = re.compile(USES_LOCAL_DESC_RE)
desc_re = re.compile(DESC_USE_RE)

def _get_info(filename, re_string, modify_function, res_var = None):
    if res_var is None:
        res_var = {}
    use_desc = open(filename, 'r').read()
    uses_desc = use_desc.split("\n")
    res_dict = res_var
    for use_str in uses_desc:
        res_match = re_string.match(use_str)
        if res_match is not None:
            modify_function(res_dict, res_match.groupdict())

    return res_dict

def get_uses_info(filename = '/usr/portage/profiles/use.desc'):
    """Args:
        filename -- full path to use.desc file
    Returns:
        dict with use flag as key, and description as value
    Example:
        {'doc': 'Doc description', ...}
    Notice:
        In portage public api `get_use_flag_dict`
    """
    def action(res_dict, match):
        res_dict[match['use'].lower()] = match['description']

    return _get_info(filename, use_re, action)

def get_local_uses_info(filename = '/usr/portage/profiles/use.local.desc'):
    """Args:
        filename -- full path to use.local.desc file
    Returns:
        defaultdict(dict) with use flag as first key, package name as second
        key, and description as value
    Example:
        {'api': {'app-emulation/xen-tools': 'Use descr', ...} , ...}
    Notice:
        In portage public api `get_use_flag_dict`
    """
    def action(res_dict, match):
        res_dict[match['use'].lower()][match['package']] = match['description']

    return _get_info(filename, use_local_re, action, defaultdict(dict))

def _set_prefixes(prefix, dct):
    newdct = {}
    for key, item in dct.iteritems():
        newdct['%s_%s' % (prefix, key)] = item
    return newdct

def get_use_special_info(dirname = '/usr/portage/profiles/desc'):
    """Args:
        dirname -- full path to descrs files, /usr/portage/profiles/desc \
        by default
    Returns:
        dict with use flag as key, and description as value
    Example:
        {'kernel_linux': 'KERNEL setting for system using the Linux ...', ...}
    """
    uses = {}
    for name in os.listdir(dirname):
        m = desc_re.match(name)
        if m is not None:
            prefix = m.groupdict().get('name')
            if prefix is None:
                continue
            filename = os.path.join(dirname, name)
            uses.update(_set_prefixes(prefix, get_uses_info(filename)))
    return uses


