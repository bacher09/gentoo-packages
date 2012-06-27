from functools import total_ordering
from package_info.generic import ToStrMixin

class KeywordRepr(ToStrMixin):

    __slots__ = ('status', 'arch')

    status_repr_list = ('', '+', '~','-')
    status_class_list = ('blank', 'stable', 'unstable', 'hardmask')
    
    def __init__(self, arch, status):
        self.arch = arch
        self.status = status

    @property
    def status_repr(self):
        return self.status_repr_list[self.status + 1]

    @property
    def status_class(self):
        return self.status_class_list[self.status + 1]

    def __unicode__(self):
        return unicode(self.status_repr + self.arch)

