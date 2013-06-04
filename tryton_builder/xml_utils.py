# -*' coding: utf8 -*-
"""XMl elements comonly used in tryton"""

import xml.etree.ElementTree as ET

CDATA_KEY = "__CDATA__" #cdata tag name for sustitution

def monkey_patch():
    """Monkey Patch ElementTree, to support CDATA"""
    _serialize_xml = ET._serialize_xml

    def _serialize_xml_cdata(write, elem, encoding, qnames, namespaces):
        tag = elem.tag
        text = elem.text
        if tag == CDATA_KEY:
            write('<![CDATA[')
            if text:
                write(ET._escape_cdata(text, encoding))
            for e in elem:
                # we use the standart handler, because is not legal to have nested CDATA
                _serialize_xml(write, e, encoding, qnames, None)
            write(']]>')
        else:
            _serialize_xml(write, elem, encoding, qnames, namespaces)

    ET._serialize_xml = _serialize_xml_cdata
    print "ElementTree was Monkey Patched to suport CDATA"

monkey_patch()

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class XMLElement(object):
    """Abstract Represents a xml element"""
    def __init__(self, tag, attrs={}, value=None):
        self.element = ET.Element(tag, attrs)
        if value:
            self.element.text = value


class Document(object):
    """Represents a data document, importable by tryton"""

    def __init__(self):
        self.tree = ET.ElementTree()
        self.root = ET.Element('tryton')
        self.data = ET.SubElement(self.root, 'data')
        self.tree._setroot(self.root)

    def add(self, record):
        """Adds an element on current tree"""
        self.data.append(record.element)

    def write_xml(self, file_name):
        indent(self.root)
        with open(file_name, 'w') as fh:
            self.tree.write(fh, 'utf-8')


class Field(XMLElement):
    """Represents a Field of tryton"""
    def __init__(self, name, attrs={}, value=None):
        attrs['name'] = name
        super(Field, self).__init__('field', attrs, value)


class Record(XMLElement):
    """Represents a record of a tryton model"""
    def __init__(self, model, id):
        attrs = {'model': model, 'id': id,}
        super(Record, self).__init__('record', attrs)

    def add_field(self, field):
        """Adds a new field inside the record"""
        self.element.append(field.element)

class MenuItem(XMLElement):
    """Defines a Menu item for tryton"""
    def __init__(self, name, icon='tryton-list', sequence='10'):
        attrs = {
            'name': name,
            'id': 'menu_%s' % name.lower().replace(' ', '_'),
            'sequence': sequence,
            'icon': icon,
                }
        super(MenuItem, self).__init__('menuitem', attrs)

class CDATAWrapper(XMLElement):
    def __init__(self):
        super(CDATAWrapper, self).__init__(CDATA_KEY)

    def add(self, field):
        """Adds a new field inside the record"""
        self.element.append(field.element)




if __name__ == '__main__':
    d = Document()
    w = CDATAWrapper()
    r = Record('saraza', 'foo.bar')
    w.add(r)
    d.add(w)
    r.add_field(Field('sarasa'))
    d.write_xml('/tmp/test.xml')

