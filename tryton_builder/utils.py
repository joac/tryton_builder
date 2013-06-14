#! -*- coding: utf8 -*-
def indent(string, level=1):
    """Indents a piece of code, adding multiples of 4 spaces"""
    spaces = ' ' * (level * 4)
    return "%s%s" % (spaces, string)


def to_pep8_variable(string):
    """Format a string as a correct pep8 name"""
    return string.replace(' ', '_').replace('-', '_').lower()

