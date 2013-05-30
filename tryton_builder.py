# -*- coding: utf8 -*-
import os
import shutil
import ConfigParser


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

        with open('%s/config.cfg' % self.module_name, 'w') as config:
            config.write('[tryton]\nversion=%s\n' % self.version)
            config.write(depends)

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
        pattern = "    Pool.register(%s, module='%s', type='%s')\n"
        for model in self.models:
            class_name, type_ = model.get_register()
            regs += pattern % (class_name, self.module_name.lower(), type_)

        return regs

    def build(self):
        """Builds all the code"""
        self.create_dir()
        self.create_init()
        self.create_config()


class Model(object):
    """Represents a single module for tryton"""

    def __init__(self, class_name, uri, type_='model'):
        self.class_name = class_name
        self.uri = uri
        self.type = type_

    def get_import(self):
        """Return the import line for __init__.py"""
        return "from .%s import *\n" % self.class_name.lower()

    def get_register(self):
        """Return data to register the module"""
        return (self.class_name, self.type)

    def get_filename(self):
        """Returns model file"""
        return self.class_name.lower()
