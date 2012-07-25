from __future__ import absolute_import
from ..generic import ToStrMixin, Enum
#XML
from .my_etree import etree
# Maintainers
from .herds import Maintainer

REMOTE_ID_TYPE = ( 'bitbucket', 'cpan', 'cpan-module', 'cran', 'ctan', 
                   'freshmeat', 'github', 'gitorious', 'google-code', 
                   'launchpad', 'pear', 'pecl', 'pypi', 'rubyforge', 
                   'rubygems', 'sourceforge', 'sourceforge-jp', 'vim'
                 )

REMOTE_IDS_TYPE = Enum(REMOTE_ID_TYPE)

#TODO: Add support of restrict attribute !!!

class PackageMetaData(ToStrMixin):

    def __init__(self, metadata_path):
        self._metadata_path = metadata_path
        self.descr = {'en': None}
        self._herds = ()
        self._maintainers = ()
        self.upstream = None
        try:
            self._metadata_xml = etree.parse(metadata_path)
        except (IOError, etree.ParseError):
            pass
        else:
            self._parse_all()

    def _parse_all(self):
        self._parse_herds()
        self._parse_description()
        self._parse_maintainers()
        self._parse_upstream()

    def _parse_herds(self):
        herd_set = set()
        for herd in self._metadata_xml.iterfind('herd'):
            herd_set.add(herd.text)
        self._herds = tuple(herd_set)

    def _parse_description(self):
        for descr in self._metadata_xml.iterfind('longdescription'):
            lang = descr.attrib.get('lang', 'en')
            self.descr[lang] = descr.text

    def iter_mainteiner(self):
        for maintainer_tree in self._metadata_xml.iterfind('maintainer'):
            yield Maintainer(maintainer_tree)

    def _parse_maintainers(self):
        maintainers = set()
        for maintainer in self.iter_mainteiner():
            maintainers.add(maintainer)
        self._maintainers = tuple(maintainers)

    def _parse_upstream(self):
        upstream_xml = self._metadata_xml.find('upstream')
        if upstream_xml is not None:
            self.upstream = Upstream(upstream_xml, self._metadata_path)

    @property
    def description(self):
        return self.descr['en']

    def descriptions(self):
        return self.descr.values()

    def descriptions_dict(self):
        return self.descr

    def herds(self):
        return self._herds

    def maintainers(self):
        return self._maintainers
    
    def __unicode__(self):
        return self._metadata_path

class Upstream(ToStrMixin):
    
    simple_attrs = (('changelog', 'changelog'),
                    ('bugs-to', 'bugs_to'),)

    def __init__(self, upstream_t, metadata_path):
        self.metadata_path = metadata_path
        self.remote_id = {}
        for name in ('doc',):
            res = {}
            for item in upstream_t.iterfind(name):
                lang = item.attrib.get('lang', 'en')
                res[lang] = item.text
            setattr(self, name, res)

        for name, attr_name in self.simple_attrs:
            setattr(self, attr_name, None)
            item = upstream_t.find(name)
            if item is not None:
                setattr(self, attr_name, item.text)

        for item in upstream_t.iterfind('remote-id'):
            type = item.attrib.get('type')
            type_id = REMOTE_IDS_TYPE.repo_dict.get(type)
            self.remote_id[type_id] = item.text

        maintainers = []
        for maintainer in upstream_t.iterfind('maintainer'):
            m = UpstreamMaintainer(maintainer)
            maintainers.append(m)

        self.maintainers = maintainers

    @property
    def main_doc(self):
        return self.doc.get('en')

    def __unicode__(self):
        return self.metadata_path

class UpstreamMaintainer(Maintainer):
    status_dict = {'inactive' : 0, 'active': 1}

    def __init__(self, xml_object):
        super(UpstreamMaintainer, self).__init__(xml_object)
        st = xml_object.attrib.get('status','inactive')
        self.status = self.status_dict.get(st, 0)

