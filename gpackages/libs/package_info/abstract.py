#from abc import ABCMeta, abstractmethod, abstractproperty
from .generic import ToStrMixin

class AbstractPortage(object):
    pass

class AbstractPortTree(object):
    pass

class AbstractCategory(object):
    pass

class AbstarctPackage(object):
    pass

class AbstractEbuild(object):
    pass

class AbstractKeywords(object):
    pass

class AbstractUse(object):
    pass

class AbstractNewsItem(object):
    pass

class SimpleMaintainer(ToStrMixin):

    def __init__(self, email, name = None):
        self.email = email
        self.name = name

    def __eq__(self, other):
        if isinstance(other, SimpleMaintainer):
            return self.email == other.email
        else:
            return self.email == unicode(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.email)

    def __unicode__(self):
        return unicode(self.email)

