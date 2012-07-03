from functools import total_ordering
from package_info.generic import ToStrMixin

class KeywordRepr(ToStrMixin):

    __slots__ = ('status', 'arch', 'hardmask')

    status_repr_list = ('', '+', '~','-')
    status_class_list = ('blank', 'stable', 'unstable', 'hardmask')
    
    def __init__(self, arch, status, hardmask = False):
        self.arch = arch
        self.status = status
        self.hardmask = hardmask

    @property
    def status_repr(self):
        st = self.status_repr_list[self.status + 1]
        if self.hardmask and st:
            st = 'M' + st
        return st

    @property
    def status_class(self):
        # Maybe set hardmask class only for status > 0 
        if self.hardmask:
            return self.status_class_list[3]
        return self.status_class_list[self.status + 1]

    def __unicode__(self):
        return unicode(self.status_repr + self.arch)

