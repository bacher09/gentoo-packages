from __future__ import absolute_import
from gentoolkit.metadata import MetaData
from ..generic import ToStrMixin

class FakeMetaData(ToStrMixin):

    def herds(self):
        return []

    def maintainers(self):
        return []

    def descriptions(self):
        return []
    
    def __unicode__(self):
        return 'fake'

def PackageMetaData(path):
    try:
        return MetaData(path)
    except IOError:
        return FakeMetaData()
