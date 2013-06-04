# -*- coding: utf8 -*-
import os
import shutil
from string import Template
from xml_utils import (
        CDATAWrapper,
        Document,
        Field as XMLField,
        FormView,
        MenuItem,
        Record,
        TreeView,
        )

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
        #FIXME append xml handling
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
        #FIXME build import strings here
        imports = ''
        for model in self.models:
            imports += model.get_import()
        return imports

    def _obtain_registers(self):
        regs = '\n\ndef register():\n'
        pattern = "    Pool.register(%s, module='%s', type_='%s')\n"
        for model in self.models:
            class_name, type_ = model.get_register()
            regs += pattern % (class_name, self.module_name.lower(), type_)

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
    # FIXME put fields here
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
        #Menu item
        doc.add(MenuItem('%s %s' % (module_name, self.class_name)))
        #Tree View
        r = Record('ir.ui.view', '%s_view_tree' % self.class_name.lower())
        doc.add(r)
        r.add(XMLField('model', value=self.uri))
        r.add(XMLField('type', value='tree'))

        container = XMLField('arch', {'type': 'xml'})
        cdata = CDATAWrapper()
        container.add(cdata)
        r.add(container)
        tree = TreeView(self.class_name)
        cdata.add(tree)
        for field in self.fields:
            tree.add(XMLField(field.var_name()))

        doc.write_xml("%s/%s.xml" % (module_name, self.class_name.lower()))

    def _code_for_fields(self):
        """Creates the block for fields"""
        code = ''
        for field in self.fields:
            code += indent(field.get_code()) + '\n'
        return code

    def add_field(self, field):
        self.fields.append(field)


class Field(object):
    """Represents a generic field of tryton"""

    def __init__(self, type_, name, *kwargs):
        """Parametrize a new field"""
        self.type = type_
        self.name = name

    def get_code(self):
        """Returns code for field"""
        return "%s = fields.%s('%s')" % (
                self.var_name(),
                self.type,
                self.name
                )
    def var_name(self):
        return to_pep8_variable(self.name)


