# -*- coding: utf8 -*-
import os
import shutil
from .constants import VALID_FIELD_TYPES, VALID_RELATION_TYPES
from .utils import to_pep8_variable
from .models import Model, HeadlessModel

__all__ = ['Module', 'Model', 'Field']

class Module(object):
    """Represents a Module of tryton"""

    def __init__(self, module_name, version='2.8.0'):
        self.module_name = module_name
        self.models = []
        self.version = version
        self.depends = set(['ir'])

    def add_model(self, model):
        """Adds a model to the module"""
        self.models.append(model)
        return self

    def add_dependence(self, dep):
        """Adds a dependence to the module, added to tryton.cfg"""
        self.depends.add(dep)

    def many2many(self, model_a, model_b):
        """Creates a many to many relation, tryton needs a"""
        # Create the intermediate models
        intermediate_name = "%s%s" % (model_a.class_name, model_b.class_name);
        prefix = model_a.uri.split('.')[0]
        model_uri = "%s.%s-%s" %(prefix, to_pep8_variable(model_a.class_name), to_pep8_variable(model_b.class_name))
        model = HeadlessModel(intermediate_name, model_uri)

        model.add_field(Relation('Many2One', model_a.class_name, model_a.uri))
        model.add_field(Relation('Many2One', model_b.class_name, model_b.uri))
        self.add_model(model)
        model_a.add_field(Relation(
                    'Many2Many',
                    model_b.class_name,
                    model.uri,
                    origin=to_pep8_variable(model_a.class_name),
                    target=to_pep8_variable(model_b.class_name),
                    )
                )

        model_b.add_field(Relation(
                    'Many2Many',
                    model_b.class_name,
                    model.uri,
                    origin=to_pep8_variable(model_b.class_name),
                    target=to_pep8_variable(model_a.class_name),
                    )
                )


    def create_dir(self):
        """Creates module directory"""
        if os.path.exists(self.module_name):
            shutil.rmtree(self.module_name)

        os.mkdir(self.module_name)

    def create_config(self):
        depends = 'depends:\n  %s\n' % '\n  '.join(self.depends)
        xml = 'xml:\n  %s\n' % '\n  '.join([a.get_xml_file() for a in self.models if a.get_xml_file()])
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
        if self.type == 'Many2Many':
            self.origin = kwargs['origin']
            self.target = kwargs['target']

    def get_code(self):
        """Returns Python Code for field"""

        if self.type == 'One2Many':
            return "%s = fields.%s('%s', '%s', '%s')" % (
                    self.var_name(),
                    self.type,
                    self.model,
                    to_pep8_variable(self.field),
                    self.name,
                )
        elif self.type == 'Many2Many':
            return "%s = fields.%s('%s', '%s', '%s', '%s')" % (
                    self.var_name(),
                    self.type,
                    self.model,
                    self.origin,
                    self.target,
                    self.name,
                )
        else:
            return "%s = fields.%s('%s', '%s')" % (
                    self.var_name(),
                    self.type,
                    self.model,
                    self.name,
                )


