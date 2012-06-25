from collections import defaultdict
from ..generic import file_get_content, StrThatIgnoreCase

def first_and_other(lst):
    return (lst[0], lst[1:]) if len(lst) > 0 else (None, [])

def split_without_comment(lic_str):
    ci = lic_str.find('#')
    if ci == -1:
        return lic_str.split()
    else:
        return lic_str[:ci].split()

def parse_groups(groups_str):
    lic_dct = defaultdict(set)
    gr_dct = defaultdict(set)
    for line in groups_str.splitlines():
        line = line.strip()
        if line.startswith('#'):
            continue

        first, lic_lst = first_and_other(split_without_comment(line))
        if first is None:
            continue

        first = StrThatIgnoreCase(first)
        for lic in lic_lst:
            if lic.startswith('@'):
                gr_dct[first].add(StrThatIgnoreCase(lic[1:]))
            else:
                lic_dct[first].add(StrThatIgnoreCase(lic))

    for group, groups in gr_dct.iteritems():
        for gr in groups:
            lic_dct[group].update(lic_dct[gr])

    return lic_dct


def load_groups(file_path = '/usr/portage/profiles/license_groups'):
    fc = file_get_content(file_path)

    if fc is None:
        return []

    return parse_groups(fc)
