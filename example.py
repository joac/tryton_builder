# Imports, for base primitives
from tryton_builder import Module, Model, Field, Relation

# We create a new module
module = Module('HelloWorld')

# Add a module dependence
module.add_dependence('party')

# Two models
hello = Model('Hello', 'hello.hello')
bye = Model('Bye', 'bye.bye')

# Add models to module
module.add_model(hello)
module.add_model(bye)

# Add Fields
hello.add_field(Field('Char', 'Name'))
hello.add_field(Field('Char', 'Greeting'))
hello.add_field(Field('Boolean', 'Is Happy'))
hello.add_field(Field('Date', 'Birthdate'))
hello.add_field(Field('Time', 'Wake Up Time'))
hello.add_field(Field('Binary', 'Some File'))

# Add Relation with party module
hello.add_field(Relation('Many2One', 'Party', 'party.party'))

# Fields for Bye module
bye.add_field(Field('Char', 'Name'))
bye.add_field(Field('Selection', 'Season', options=[
    'Summer', 'Autumn', 'Winter', 'Spring'
    ]))
bye.add_field(Field('Boolean', 'Is painfull'))
bye.add_field(Field('DateTime', 'Date'))
bye.add_field(Field('Text', 'Log'))

# Creates a Many2Many Relationship
module.many2many(hello, bye)

# Build!!
module.build()
# Our module is placed on HelloWorld dir
