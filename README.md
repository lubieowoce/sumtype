# `sumtype`
A `namedtuple`-style library for defining immutable **sum types** in Python.

The current version is `0.9`, quickly approaching `1.0`.
Suggestions and contributions are welcome! 

> *You may know **sum types** under a different name –
> they're also referred to as `tagged unions`, `enums` in Rust/Swift, and `variants` in C++.*

### A quick tour
```python
    >>> from sumtype import sumtype
    >>>
    >>> class Thing(sumtype):
    ...     def Foo(x: int, y: int): ...
    ...     def Bar(y: str, hmm: str): ...
    ...     def Zap(): ...
    ...
    >>>
```
This means that a `Thing` value can be:
- a `Foo` with two `int` fields, `x` and `y`
- a `Bar` with two `string` fields, `y` and `hmm`
- a `Zap` with no fields

You can also add your own docstring and methods in the class definition.
If you prefer `namedtuple`-style definitions, `sumtype` supports those too - see `Thing2` in `sumtype.sumtype.demo()` for an example.

#### Creating values and attribute access
```python
    >>> f, b, z = Thing.Foo(x=3, y=5),  Thing.Bar('hello', 'world'),  Thing.Zap()
    >>>
    >>> foo = Thing.Foo(x=3, y=5) # named arguments
    >>> foo
    Thing.Foo(x=3, y=5)
    >>> foo.x, foo.y;
    (3, 5)
    >>>
    >>> bar = Thing.Bar('hello', 'world') # positional arguments
    >>> bar
    Thing.Bar(y='hello', hmm='world')
    >>> bar.y,  bar.hmm
    ('hello', 'world')
    >>>
    >>> zap = Thing.Zap()
    >>> zap
    Thing.Zap()
```
They're still just different values of the same type though!
```python
    >>> all([type(foo) is Thing, type(bar) is Thing, type(zap) is Thing])
    True
```

As you can see, `sumtype` generated the constructors, a `__repr__()`, and accessors for each attribute.
(It generates many other useful methods too, demonstrated below.) 

The library is designed with efficiency in mind¹ – it uses `__slots__` for attribute storage
and generates specialized versions of all the methods for each class.
To see the generated code, do ` class Thing(sumtype, verbose=True):`.

¹ At least I like to think so ;)  I try to do my best with profiling things though!


#### Equality and hashing
```python
    >>> Thing.Foo(1,2) == Thing.Foo(1,2)
    True
    >>> Thing.Foo(1,2) == Thing.Bar('a', 'b');
    False
    >>> {foo, foo, bar, zap} == {foo, bar, zap}
    True
```

#### Pattern matching 1
```python
    >>> def do_something(val: Thing):
    ...     if val.is_Foo():
    ...         print(val.x * val.y)
    ...     elif val.is_Bar():
    ...         print('The result is', val.y, val.hmm)
    ...     elif val.is_Zap():
    ...         print('Whoosh!')
    ...     else: val.impossible() # throws an error - nice if you like having all cases covered
    ...
    >>> for val in (foo, bar, zap):
    ...     do_something(val)
    ...
    15
    The result is hello world
    Whoosh!
```

#### Pattern matching 2
```python
    >>> f = lambda val: val.match(
    ...         Foo = lambda x, y: x * y,
    ...         Zap = lambda: 999,
    ...         _   = lambda: -1 # default case
    ...     )
    >>>
    >>> [f(val) for val in (foo, bar, zap)]
    [15, -1, 999]
```

#### Updating
```python
    >>> foo;  foo.replace(x=99)
    Thing.Foo(x=3, y=5)
    Thing.Foo(x=99, y=5)
    >>>
    >>> bar;  bar.replace(y='abc', hmm='xyz')
    Thing.Bar(y='hello', hmm='world')
    Thing.Bar(y='abc', hmm='xyz')
```
Note that, like in `namedtuple`, `foo.replace(x=99)` returns a new value.

#### Value access and conversions
```python
    >>> foo.values();  foo.as_tuple();  foo.as_dict()
    (3, 5)
    ('Foo', 3, 5)
    OrderedDict([('variant', 'Foo'), ('x', 3), ('y', 5)])
    >>>
    >>> Thing.from_tuple(('Bar', 'one', 'two'))
    Thing.Bar(y='one', hmm='two')
```

#### Pickle support
```python
    >>> import pickle
    >>> vals  = [Thing.Foo(1, 2), Thing.Bar('one', 'two'), Thing.Zap()]
    >>> vals2 = pickle.loads(pickle.dumps(vals))
    >>> vals;  vals == vals2
    [Thing.Foo(x=1, y=2), Thing.Bar(y='one', hmm='two'), Thing.Zap()]
    True
```

And that's all... for now!


### Features coming in `1.0`
- Type annotations on generated constructors
- Default values
- Argument typechecking - always, or in `__debug__` mode only
- `.from_dict()`


### Possible future features

- `mypy` support.
Last time I checked, it didn't really handle metaclass-created classes - that might have changed.
Alternatively, we could provide a way to generate stub files.
- Statically generating a class definition to a file

- Dynamic alternatives to custom-generated methods –
might be useful if startup time is more important than efficiency

- An alternative implementation backed by tuples if true immutability is desired –
there's currently no way to make a `__slots__`-based implementation watertight in that aspect, though we're doing our best

- *Maybe* opt-in mutability – currently, you can use `Thing._unsafe_set_Foo_x(foo, 10)` if you want that, but that's not a nice interface
