
class ToStrMixin(object):
    """Abstract class for inheritence, allow add simple `__str__` and `__repr__`
    methods
    """
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.__str__())

