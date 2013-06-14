from string import Template
from .utils import indent
from .xml_utils import (
        CDATAWrapper,
        Document,
        Field as XMLField,
        FormView,
        Label,
        MenuItem,
        Record,
        TreeView,
        )

class Model(object):
    """Represents a single module for tryton"""

    def __init__(self, class_name, uri, type_='model'):
        self.class_name = class_name
        self.uri = uri
        self.type = type_
        self.fields = []
        self.view_ids = []

    def get_import(self):
        """Return the import line for __init__.py"""
        return "from .%s import *\n" % self.class_name.lower()

    def get_register(self):
        """Return data to register the module"""
        return (self.class_name, self.type)

    def get_filename(self):
        """Returns model file"""
        return self.class_name.lower()

    def get_xml_file(self):
        """Returns file name of xml"""
        return "%s.xml" % self.class_name.lower()

    def _get_class_template(self):
        return """#! -*- coding: utf8 -*-
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['${class}']

class ${class}(ModelSQL, ModelView):
    "${module_name}"
    __name__ = "${uri}"
${fields}
"""

    def build_class(self, module_name):
        """Return code of the object"""
        template = Template(self._get_class_template())
        contents = template.substitute({
            'class': self.class_name,
            'module_name': module_name,
            'uri': self.uri,
            'fields': self._code_for_fields(),
            })

        return contents

    def build_xml(self, module_name):
        """Build xml string for model"""
        doc = Document()
        # Menu item
        menu = MenuItem('%s %s' % (module_name, self.class_name))
        doc.add(menu)
        # Tree View
        doc.add(self._build_tree_view())
        # Form view
        doc.add(self._build_form_view())
        # Events
        event_id = "act_%s_form" % self.class_name.lower()
        event = Record('ir.action.act_window', event_id)
        event.add(XMLField('name', value=self.class_name))
        event.add(XMLField('res_model', value=self.uri))
        doc.add(event)
        for n, view_id in enumerate(self.view_ids, 1):
            r_id = "act_%s_form_view%s" % (self.class_name.lower(), n)
            r = Record('ir.action.act_window.view', r_id)
            r.add(XMLField('sequence', {'eval': str(10 * n)}))
            r.add(XMLField('view', {'ref': view_id}))
            r.add(XMLField('act_window', {'ref': event_id}))
            doc.add(r)

        #Menu wiring
        menu_id = 'menu_%s_form' % self.class_name.lower()
        doc.add(MenuItem('', sequence='1', attrs={
                    'parent': menu.id,
                    'id': menu_id,
                    'action':event_id,
                    }))

        doc.write_xml("%s/%s.xml" % (module_name, self.class_name.lower()))

    def _code_for_fields(self):
        """Creates the block for fields"""
        code = ''
        for field in self.fields:
            code += indent(field.get_code()) + '\n'
        return code

    def add_field(self, field):
        self.fields.append(field)
        return self

    def _build_form_skel(self, view_type):
        form_id = '%s_view_%s' % (self.class_name.lower(), view_type)
        r = Record('ir.ui.view', form_id)
        r.add(XMLField('model', value=self.uri))
        r.add(XMLField('type', value=view_type))
        container = XMLField('arch', {'type': 'xml'})
        cdata = CDATAWrapper()
        container.add(cdata)
        r.add(container)
        self.view_ids.append(form_id)
        return r, cdata

    def _build_tree_view(self):
        """Creates a tree view, returns an xml element"""
        r, cdata = self._build_form_skel('tree')
        tree = TreeView(self.class_name)
        cdata.add(tree)
        for field in self.fields:
            tree.add(XMLField(field.var_name()))
        return r

    def _build_form_view(self):
        r, cdata = self._build_form_skel('form')
        form = FormView(self.class_name)
        cdata.add(form)
        for field in self.fields:
            form.add(Label(field.var_name()))
            form.add(XMLField(field.var_name()))
        return r


class HeadlessModel(Model):
    """Define an invisible (Without views) model"""
    def _get_class_template(self):
        return """#! -*- coding: utf8 -*-
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['${class}']

class ${class}(ModelSQL):
    "${module_name}"
    __name__ = "${uri}"
${fields}
"""

    def get_xml_file(self):
        pass # We don't need xml

    def build_xml(self, *args, **kwargs):
        pass # We don't need xml
