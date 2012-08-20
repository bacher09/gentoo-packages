from collections import defaultdict
from ..generic import file_get_content, StrThatIgnoreCase, ToStrMixin, \
                      file_sha1

DEFAULT_FILE_PATH = '/usr/portage/profiles/license_groups'

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

def load_groups(file_path = DEFAULT_FILE_PATH):
    """Load file profiles/license_groups and represend it as dict

    Args:
        file_path -- full path to license_groups file.

    Returns:
        dict with license group as key and set of licenses as value.

    Example:
        {u'EULA': set([u'cadsoft', ...]), u'GPL-COMPATIBLE': set([...]), ...}

    """
    fc = file_get_content(file_path)

    if fc is None:
        return {}

    return parse_groups(fc)


class LicenseGroups(ToStrMixin):

    def __init__(self, file_path = DEFAULT_FILE_PATH):
        """Args:
            file_path -- full path to license_groups file, by default it 
                         /usr/portage/profiles/license_groups
        """
        self.groups_path = file_path
        self.groups_dict = load_groups(file_path)
        self.reverse_group_dict = self.gen_reverse_dict()

    def gen_reverse_dict(self):
        temp_dict = defaultdict(set)
        for group, licenses in self.groups_dict.iteritems():
            for lic in licenses:
                temp_dict[lic].add(group)

        return temp_dict

    def get_licenses_by_group(self, group_name):
        """Args:
            group_name -- License group name

        Returns:
            return set of licenses that belong to group_name

        Example:
            get_licenses_by_group('OSI-APPROVED') -> set([u'AFL-3.0', ...])
        """
    
        return self.groups_dict[group_name]

    def get_groups_by_license(self, license_name):
        """Args:
            license_name -- License name

        Returns:
            return set of license groups that belong to license

        Example:
            get_groups_by_license('GPL-1') -> set([u'FREE', ...])
        """
        return self.reverse_group_dict[license_name]

    def sha1(self):
        "Return sha1 hash hexdigest of license groups file"
        return file_sha1(self.groups_path)

    def __unicode__(self):
        return unicode(self.groups_path)

