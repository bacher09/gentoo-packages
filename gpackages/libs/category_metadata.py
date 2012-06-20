from generic import ToStrMixin
#XML
from my_etree import etree

__all__ = ('CategoryMetadata', )

class CategoryMetadata(ToStrMixin):

    def __init__(self, metadata_path):
        self._metadata_path = metadata_path
        self._descrs = {}
        try:
            self._metadata_xml = etree.parse(metadata_path)
        except IOError:
            pass
        else:
            self._parse_descrs()

    def _parse_descrs(self):
        for descr_xml in self._metadata_xml.iterfind('longdescription'):
            lang = descr_xml.attrib.get('lang', 'en')
            self._descrs[lang] = descr_xml.text

    @property
    def descrs(self):
        return self._descrs

    @property
    def default_descr(self):
        return self._descrs.get('en')

    def __unicode__(self):
        return unicode(self._metadata_path)


class FakeMetaData(ToStrMixin):

    def herds(self):
        return []

    def maintainers(self):
        return []

    def descriptions(self):
        return []
    
    def __unicode__(self):
        return 'fake'

