try:
    import xml.etree.cElementTree as etree
except (ImportError, SystemError):
    import xml.etree.ElementTree as etree

from collections import defaultdict
from generic import ToStrMixin

def _gen_func(name):
    return lambda self: getattr(self, name)

class AbstarctXmlObject(object):
    attrs = ()
    
    def __new__(cls, *args, **kwargs):
        for val in cls.attrs:
            setattr(cls, val, property(_gen_func('_'+val)))
        ins = super(AbstarctXmlObject, cls).__new__(cls, *args, **kwargs) 
        #attrs = getattr(ins, 'attrs')
        return ins
    
    def __init__(self, xml_object):
        for val in self.attrs:
            obj_xml = xml_object.find(val) 
            setattr(self, '_' + val, None)
            if obj_xml is not None:
                setattr(self, '_' + val, obj_xml.text)

class Maintainer(AbstarctXmlObject, ToStrMixin):
    attrs = ('name', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super(Maintainer, self).__init__(*args, **kwargs)
        if self._email is not None:
            self._email = self._email.lower()

    def __eq__(self, other):
        return self.email == other.email

    def __ne__(self, other):
        return self.email != other.email

    def __hash__(self):
        return hash(self.email)

    def __unicode__(self):
        return self.email

class Herd(AbstarctXmlObject, ToStrMixin):
    # create name, email and description property
    attrs = ('name', 'email', 'description')

    def __init__(self, xml_object):
        super(Herd, self).__init__(xml_object) 
        self._xml_object = xml_object

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)

    def iter_mainteiner(self):
        for maintainer_tree in self._xml_object.iterfind('maintainer'):
            yield Maintainer(maintainer_tree)

    def __unicode__(self):
        return self.name


class Herds(ToStrMixin):
    def __init__(self, herd_path='/usr/portage/metadata/herds.xml'):
        self._herd_path = herd_path
        self._herd_parse = etree.parse(herd_path)
        self._herds_dict = None
        self._maintainers_dict = None

    def iter_herd(self):
        for herd_tree in self._herd_parse.iterfind('herd'):
            yield Herd(herd_tree)

    def get_herds_indict(self):
        if self._herds_dict is not None:
            return self._herds_dict
        res = {}
        for herd in self.iter_herd():
            res[herd.name] = herd
        self._herds_dict = res
        return res

    def get_maintainers_with_hers(self):
        if self._maintainers_dict is not None:
            return self._maintainers_dict
        herd_dict = self.get_herds_indict()
        maintainer_dict = defaultdict(list)
        for herd in herd_dict.itervalues():
            for maintainer in herd.iter_mainteiner():
                maintainer_dict[maintainer].append(herd.name)
        self._maintainers_dict = maintainer_dict
        return maintainer_dict

    def __unicode__(self):
        return self._herd_path
