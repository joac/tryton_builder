from tryton_builder import Module, Model, Field

module = Module('HelloWorld')

hello = Model('Hello', 'hello.hello')
bye = Model('Bye', 'hello.Bye')

module.add_model(hello)
module.add_model(bye)

hello.add_field(Field('Char', 'Name'))
hello.add_field(Field('Char', 'Greeting'))

#b.create_views()
#b.create_module()
#b.create_foo_bar()

#b.build_all()
module.build()
