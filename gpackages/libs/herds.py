try:
    import xml.etree.cElementTree as etree
except (ImportError, SystemError):
    import xml.etree.ElementTree as etree


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

class Maintainer(AbstarctXmlObject):
    attrs = ('name', 'email', 'role')

class Herd(AbstarctXmlObject):
    # create name, email and description property
    attrs = ('name', 'email', 'description')

    def __init__(self, xml_object):
        super(Herd, self).__init__(xml_object) 
        self._iter_maintainer = xml_object.iterfind('maintainer')

    def iter_mainteiner(self):
        for maintainer_tree in self._iter_maintainer:
            yield Maintainer(maintainer_tree)


class Herds(object):
    def __init__(self, herd_path='/usr/portage/metadata/herds.xml'):
        self._herd_path = herd_path
        self._herd_parse = etree.parse(herd_path)
        self._iter_herd = self._herd_parse.iterfind('herd')

    def iter_herd(self):
        for herd_tree in self._iter_herd:
            yield Herd(herd_tree)
