# `sumtype`
A `namedtuple`-style library for defining immutable **sum types** in Python.
The current version is `0.9`, quickly approaching `1.0`.

**Sum types** are also known as `tagged unions`, `enums` in `Rust`/`Swift`, and `variants` in `C++`).

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
This means that a value of `Thing` can be:
- a `Foo` containing two ints
- a `Bar` containing two strings
- a `Zap`, which contains nothing.

You can also add your own docstring and methods in the class definition.
If you prefer `namedtuple`-style definitions, `sumtype` supports those too - see `Thing2` in `sumtype.sumtype.demo()` for an example.

#### Creating values and attribute access
```python
    >>> foo = Thing.Foo(x=3, y=5) # named arguments
    >>> foo
    Thing.Foo(x=3, y=5)
    >>> foo.x;  foo.y;
    3
    5
    >>>
    >>> bar = Thing.Bar('hello', 'world') # positional arguments
    >>> bar
    Thing.Bar(y='hello', hmm='world')
    >>> bar.y;  bar.hmm
    'hello'
    'world'
    >>>
    >>> zap = Thing.Zap()
    >>> zap
    Thing.Zap()
```
They're still just different values of the same type though!
```python
    >>> [type(foo), type(bar), type(zap)]
    [<class '__main__.Thing'>, <class '__main__.Thing'>, <class '__main__.Thing'>]
```

As you can see, `sumtype` generated the constructors, a `__repr__()`, and accessors for each attributes.
(It generates many other useful methods too! See below for more.) 

The library is designed for efficiency - it uses `__slots__` for attribute storage
and generates specialized versions of all the methods for each class.
To see the generated code, do
```python
>>> class Thing(sumtype, verbose=True)
... 	... 
```

#### Equality and hashing
```python
    >>> Thing.Foo(1,2) == Thing.Foo(1,2)
    True
    >>> Thing.Foo(1,2) == Thing.Bar('a', 'b');
    False
    >>> {foo, bar, bar, zap}
    {Thing.Bar(y='hello', hmm='world'), Thing.Foo(x=3, y=5), Thing.Zap()}
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

#### Updating (without modifying in-place)
```python
    >>> foo;  foo.replace(x=99)
    Thing.Foo(x=3, y=5)
    Thing.Foo(x=5, y=99)
    >>>
    >>> bar;  bar.replace(y='abc', hmm='xyz')
    Thing.Bar(y='hello', hmm='world')
    Thing.Bar(y='abc', hmm='xyz')
```

#### Value access and conversions
```python
    >>> foo.values();  foo.as_tuple();  foo.as_dict()
    (3, 5)
    ('Foo', 3, 5)
    {'variant': 'Foo', 'y': 5, 'x': 3}
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

### Features planned for `1.0`
- Argument typechecking - always, or in __debug__ mode only
- Default values

### Possible features
- Provide alternative dynamic alternatives to custom-generated methods --
might be useful if startup time is more important than efficiency
- An alternative implementation backed by tuples if true immutability is desired
- Support opt-in mutability
