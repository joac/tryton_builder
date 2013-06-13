# -*- coding: utf8 -*-
import os
import shutil
from string import Template
from xml_utils import (
        CDATAWrapper,
        Document,
        Field as XMLField,
        FormView,
        Label,
        MenuItem,
        Record,
        TreeView,
        )

# Define valid trytond field types
VALID_FIELD_TYPES = [
    'Boolean',
    'Integer',
    'BigInteger',
    'Char',
    'Sha',
    'Text',
    'Float',
    'Numeric',
    'Date',
    'DateTime',
    'Time',
    'Binary',
    'Selection',
    'Reference',
#   'Function', not suported yet!
]

VALID_RELATION_TYPES = [
#   'One2One',
   'Many2One',
   'One2Many',
#   'Many2Many',
]

__all__ = ['Module', 'Model', 'Field']

def indent(string, level=1):
    """Indents a piece of code, adding multiples of 4 spaces"""
    spaces = ' ' * (level * 4)
    return "%s%s" % (spaces, string)


def to_pep8_variable(string):
    """Format a string as a correct pep8 name"""
    return string.replace(' ', '_').replace('-', '_').lower()


class Module(object):

    def __init__(self, module_name, version='2.8.0'):

        self.module_name = module_name
        self.models = []
        self.version = version
        self.depends = ['ir']

    def add_model(self, model):
        self.models.append(model)

    def create_dir(self):
        """Creates module directory"""
        if os.path.exists(self.module_name):
            shutil.rmtree(self.module_name)

        os.mkdir(self.module_name)

    def create_config(self):
        depends = 'depends:\n  %s\n' % '\n  '.join(self.depends)
        xml = 'xml:\n  %s\n' % '\n  '.join([a.get_xml_file() for a in self.models])
        with open('%s/tryton.cfg' % self.module_name, 'w') as config:
            config.write('[tryton]\nversion=%s\n' % self.version)
            config.write(depends)
            config.write(xml)

    def create_init(self):
        """Creates de __init__.py for the module"""

        with open('%s/__init__.py' % self.module_name, 'w') as file:
            file.write("from trytond.pool import Pool\n")
            file.write(self._obtain_imports())
            file.write(self._obtain_registers())

    def _obtain_imports(self):
        """Obtain imports for all models"""
        imports = ''
        for model in self.models:
            imports += model.get_import()
        return imports

    def _obtain_registers(self):
        regs = '\n\ndef register():\n'
        pattern = "    Pool.register(%s, module='%s', type_='%s')\n"
        class_names = []

        for model in self.models:
            class_name, type_ = model.get_register()
            class_names.append(class_name)

        regs += pattern % (', '.join(class_names), self.module_name, type_)

        return regs

    def build_code(self):
        """Build code files for every model in module"""
        for model in self.models:
            contents = model.build_class(self.module_name)
            with open('%s/%s.py' % (self.module_name, model.class_name.lower()), 'w') as code_file:
                code_file.write(contents)

    def build_xml(self):
        """Builds xml for all models in module"""
        for model in self.models:
            model.build_xml(self.module_name)

    def build(self):
        """Builds all the code"""
        self.create_dir()
        self.create_init()
        self.create_config()
        self.build_code()
        self.build_xml()


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

    def build_class(self, module_name):
        """Return code of the object"""
        template = Template(
"""#! -*- coding: utf8 -*-
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['${class}']

class ${class}(ModelSQL, ModelView):
    "${module_name}"
    __name__ = "${uri}"
${fields}
""")

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


class Field(object):
    """Represents a generic field of tryton"""

    def __init__(self, type_, name, **kwargs):
        """Parametrize a new field"""
        assert type_ in VALID_FIELD_TYPES
        if 'options' in kwargs:
                self.options = kwargs['options']
        self.type = type_
        self.name = name

    def build_options(self):
        """Builds an options list of this form:
            [('db_choice','show_value'), (etc...)]
            """
        out = '['
        for option in self.options:
            out += "('%s', '%s'), " % (to_pep8_variable(option), option)
        out += ']'
        return out

    def get_code(self):
        """Returns code for field"""
        if self.type == 'Selection':
            #First Field of selection are the options
            return "%s = fields.%s(%s, '%s')" % (
                    self.var_name(),
                    self.type,
                    self.build_options(),
                    self.name
                )

        else:

            return "%s = fields.%s('%s')" % (
                    self.var_name(),
                    self.type,
                    self.name
                )

    def var_name(self):
        return to_pep8_variable(self.name)



class Relation(Field):
    """Represents a generic relation field"""

    def __init__(self, type_, name, model, **kwargs):
        """Parametrize a new field"""
        assert type_ in VALID_RELATION_TYPES
        self.type = type_
        self.name = name
        self.model = model
        if self.type == 'One2Many':
            self.field = kwargs['field']

    def get_code(self):
        """Returns Python Code for field"""

        if self.type == 'One2Many':
            return "%s = fields.%s('%s', '%s', '%s')" % (
                    self.var_name(),
                    self.type,
                    self.model,
                    self.name,
                    self.field,
                )
        else:
            return "%s = fields.%s('%s', '%s')" % (
                    self.var_name(),
                    self.type,
                    self.model,
                    self.name,
                )


