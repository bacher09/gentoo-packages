from .generic import StrThatIgnoreCase, ToStrMixin
from functools import total_ordering
from collections import defaultdict
from .abstract import AbstractKeywords, AbstractUse

__all__ = ('Use', 'Keyword', 'KeywordsSet')

class Use(ToStrMixin, AbstractUse):
    "Represend Use flag as object"
    __slots__ = ('name',)

    def __init__(self, name):
        """Args:
            name -- name of use flag, may start with + or -
        """
        if name.startswith('+') or name.startswith('-'):
            name = name[1:]
        self.name = StrThatIgnoreCase(name)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, self):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)
        
@total_ordering
class Keyword(ToStrMixin, AbstractKeywords):
    "Represend ebuild Keyword as object"
    __slots__ = ('name', 'status')
    status_repr = ['','~','-']
    
    def __init__(self, name, status = 0):
        """Args:
            name -- name of keyword, it may start with ~ or -, if so than 
                    status will be auto seting.
            status -- status of keyword: 0 - stable, 
                                         1 - utested '~',
                                         2 - unstable '-'
                    Also may get by name parameter.
        """
        if name.startswith('~'):
            name = name[1:]
            status = 1
        elif name.startswith('-'):
            name = name[1:]
            status = 2
        self.name = name
        self.status = status

    def __unicode__(self):
        return self.status_repr[self.status] + self.name

    def __hash__(self):
        return hash((self.name, self.status))

    def is_same(self, other):
        return self.name == other.name

    def is_higer(self, other):
        return self.status < other.status

    def is_lower(self, other):
        return self.status > other.status

    def __eq__(self, other):
        if not isinstance(other, Keyword):
            return False
        return (self.arch, self.status) == (other.arch, other.status)

    def __lt__(self, other):
        if not isinstance(other, Keyword):
            return NotImplemented
        return (self.status, self.arch) > (other.status, other.arch)

    @property
    def arch(self):
        "Return arch name"
        return self.name

class KeywordsSet(set):
    def __init__(self, init_list):
        start = defaultdict(list)
        for item in init_list:
            start[item.arch].append(item)

        to_create = []
        for item in start.itervalues():
            item.sort(reverse = True)
            if len(item)>=1:
                to_create.append(item[0])
        super(KeywordsSet, self).__init__(to_create)
