# Imports, for base primitives
from tryton_builder import Module, Model, Field

# We create a new module
module = Module('HelloWorld')

# Two models
hello = Model('Hello', 'hello.hello')
bye = Model('Bye', 'hello.Bye')

# Add models to module
module.add_model(hello)
module.add_model(bye)

# Add Fields
hello.add_field(Field('Char', 'Name'))
hello.add_field(Field('Char', 'Greeting'))

# Build!!
module.build()
# Our module is placed on HelloWorld dir
