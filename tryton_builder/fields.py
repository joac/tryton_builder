# -*- coding: utf8 -*-
from .constants import VALID_FIELD_TYPES, VALID_RELATION_TYPES
from .utils import to_pep8_variable


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
