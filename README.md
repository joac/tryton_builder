# ![alt text](https://raw.github.com/joac/tryton_builder/master/data/logo.png "Logo")Tryton Builder

Tryton builder is a *Work in Progress* script to scaffold tryton modules:

## Example
This is the basic usage:

```python
# Imports, for base primitives
from tryton_builder import Module, Model, Field

# We create a new module
module = Module('HelloWorld')

# Two models
hello = Model('Hello', 'hello.hello')

# Add models to module
module.add_model(hello)

# Add Fields
hello.add_field(Field('Char', 'Name'))
hello.add_field(Field('Char', 'Greeting'))

# Build!!
module.build()
# Our module is placed on HelloWorld dir
```

For an extended example, look [example.py](https://github.com/joac/tryton_builder/blob/master/example.py)

## Components

Tryton builder have four objects:
 - Module
 - Model
 - Field
 - Relation 

### Module

Module represents the whole installable tryton module, that have: *dependences*,
*xml files*, *models*, and *views*. Their api give these public methods:

 *  `add_dependence` 
 *  `add_model`
 *  `build` 
 *  `build_code`
 *  `build_xml`
 *  `create_config`
 *  `create_dir`
 *  `create_init`
 *  `many2many` Build a many2many relationship, handling intermediary relation object

### Model
    Represents a row based entity of tryton

### Field
    Abstracts the code generation for different kind of Tryton Fields

### Relation
    Inherits from field, and handle relationships 

Based on the guide of [tryton wiki](http://code.google.com/p/tryton/wiki/HelloWorld)
