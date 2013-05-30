from tryton_builder import Module, Model

module = Module('HelloWorld')

hello = Model('Hello', 'hello.hello')
bye = Model('Bye', 'hello.Bye')

module.add_model(hello)
module.add_model(bye)

#hello.add_field(Char('sdjasdjkahs'))
#hello.add_field(Char('sdjasdjkahs'))
#hello.add_field(Char('sdjasdjkahs'))
#hello.add_field(Char('sdjasdjkahs'))
#hello.add_field(Char('sdjasdjkahs'))

#b.create_views()
#b.create_module()
#b.create_foo_bar()

#b.build_all()
module.build()
