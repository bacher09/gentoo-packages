from __future__ import absolute_import
from ..generic import ToStrMixin
#XML
from .my_etree import etree

__all__ = ('CategoryMetadata', )

class CategoryMetadata(ToStrMixin):
    "Represent category metadata.xml as object"

    def __init__(self, metadata_path):
        """Args: 
            metadata_path - full path to category metadata.xml file"""
        self._metadata_path = metadata_path
        self._descrs = {}
        try:
            self._metadata_xml = etree.parse(metadata_path)
        except (IOError, etree.ParseError):
            pass
        else:
            self._parse_descrs()

    def _parse_descrs(self):
        for descr_xml in self._metadata_xml.iterfind('longdescription'):
            lang = descr_xml.attrib.get('lang', 'en')
            self._descrs[lang] = descr_xml.text

    @property
    def descrs(self):
        "Dict with language code as key and text as value"
        return self._descrs

    @property
    def default_descr(self):
        "Return text of English description"
        return self._descrs.get('en')

    def __unicode__(self):
        return unicode(self._metadata_path)

