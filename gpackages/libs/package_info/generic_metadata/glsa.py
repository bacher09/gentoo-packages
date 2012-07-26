import os
import os.path
import re
from .my_etree import etree
from ..generic import ToStrMixin

GLSA_FILE_RE = r'^glsa-\d{6}-\d{2}\.xml$'
glsa_re = re.compile(GLSA_FILE_RE)

def children_text(node):
    parts = ([node.text] +
             [etree.tostring(c) for c in node.getchildren()]
            )
    return ''.join(filter(None, parts))


class GLSAs(ToStrMixin):

    def __init__(self, repo_path = '/usr/portage'):
        self.glsa_path = os.path.join(repo_path, 'metadata', 'glsa')
        if not os.path.isdir(self.glsa_path):
            raise ValueError
        # For repr
        self.repo_path = repo_path 

    def iter_glsa(self):
        for name in os.listdir(self.glsa_path):
            try:
                i = GLSA(os.path.join(self.glsa_path, name))
            except ValueError:
                pass
            else:
                yield i

    def __unicode__(self):
        return self.repo_path 

class GLSA(ToStrMixin):
    
    simple_attrs = ('synopsis', 'background', 'description',
                    'workaround', 'resolution')

    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            raise ValueError

        dir, name = os.path.split(file_name)
        m = glsa_re.match(name)
        if m is None:
            raise ValueError

        xml = etree.parse(file_name)

        root = xml.getroot()
        id = root.attrib.get('id')
        self.glsa_id = id
        self.title = root.find('title').text
        for attr in self.simple_attrs:
            node = root.find(attr)
            if node is not None:
                setattr(self, attr, children_text(node))
            else:
                setattr(self, attr, None)
                
        impact_xml = root.find('impact')
        self.impact_type = impact_xml.attrib.get('type')
        self.impact = children_text(impact_xml)
        
    
    def __unicode__(self):
        return unicode(self.glsa_id) 
