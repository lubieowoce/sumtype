# `sumtype`
A `namedtuple`-style library for defining immutable **sum types** in Python. ([Get it on PyPI](https://pypi.org/project/sumtype/))

> *You may know **sum types** under a different name –
> they're also referred to as `tagged unions`, `enums` in Rust/Swift, and `variants` in C++. 
> If you haven't heard about them yet, [here's](https://chadaustin.me/2015/07/sum-types/) a nice introduction.*

The current version is `0.10.0`, quickly approaching `1.0`.
The library supports Python 3.x.
The core code has lived in various `utils` folders for about a year,
before I got tired of copying it around and decided to release it as an independent package.
(see also: [Should I use it?](https://github.com/lubieowoce/sumtype#should-i-use-it))

Suggestions, feedback and contributions are very welcome!



## A quick tour
```python
>>> from sumtype import sumtype
>>> from typing import Tuple
>>>
>>> class Thing(sumtype):
...     def Foo(x: int, y: int): ...
...     def Bar(y: str, hmm: Tuple[str, str]): ...
...     Zap = ...
...
>>>
```
This means that a `Thing` value can be one of three variants:
- a `Foo` with two `int` fields, `x` and `y`
- a `Bar` with a `str` field `y` and a `Tuple[str, str]` field `hmm`
- a `Zap` with no fields

If type annotations are provided, the constructors will typecheck the arguments (see [Typechecking](https://github.com/lubieowoce/sumtype#typechecking))
You can also add your own docstring and methods in the class definition.
If you prefer `namedtuple`-style definitions, `sumtype` supports those too - see `Thing2` in `sumtype.sumtype.demo()` for an example.

#### Creating values and attribute access
```python
>>> foo = Thing.Foo(x=3, y=5)  # named arguments
>>> bar = Thing.Bar('hello', ('wo', 'rld'))  # positional arguments
>>> zap = Thing.Zap()
```
Note that they're still just different values of the same type, not subclasses:
```python
>>> type(foo) is Thing  and  type(bar) is Thing  and  type(zap) is Thing
True
```

Every specified field gets an accessor:
```python
>>> foo.x, foo.y;
(3, 5)
>>> bar.y,  bar.hmm
('hello', ('wo', 'rld'))
```
...with checks if the access is valid and descriptive error messages:
```python
>>> Thing.Zap().hmm  # only `Bar`s have a `hmm` field
Traceback (most recent call last):
  ...
AttributeError: Incorrect 'Thing' variant: Field 'hmm' not declared in variant 'Zap'...
>>>
>>> Thing.Foo(x=1, y=2).blah_blah_blah  # no variant has a `blah_blah_blah` field 
Traceback (most recent call last):
  ...
AttributeError: Unknown attribute: Field 'blah_blah_blah' not declared in any variant of 'Thing'...
```

The values also have a nice `__repr__()`:
```python
>>> foo; bar; zap
Thing.Foo(x=3, y=5)
Thing.Bar(y='hello', hmm=('wo', 'rld'))
Thing.Zap()
```

The library is designed with efficiency in mind¹ – it uses `__slots__` for attribute storage
and generates specialized versions of all the methods for each class.
To see the generated code, do ` class Thing(sumtype, verbose=True):`.

¹ At least I like to think so ;)  I try to do my best with profiling things though!


## Features

### Typechecking

`sumtype` uses [`typeguard`](https://github.com/agronholm/typeguard) to typecheck the fields:
```python
>>> # Foo(x: int, y: int) -> Thing
>>> Thing.Foo(x=1, y=2)
Thing.Foo(x=1, y=2)
>>> Thing.Foo(x='should be an int', y=2)
Traceback (most recent call last):
  ...
TypeError: type of argument "x" must be int; got str instead
```
`typing` annotations are supported too:
```python
>>> # Bar(y: str, hmm: Tuple[str, str]) -> Thing
>>> Thing.Bar(y='a', hmm=('b', 'c'))
Thing.Bar(y='a', hmm=('b', 'c'))
>>> Thing.Bar(y='a', hmm=(1, 2))
Traceback (most recent call last):
  ...
TypeError: type of argument "hmm"[0] must be str; got int instead
```
[`typeguard`](https://github.com/agronholm/typeguard) supports all `typing` constructs (`Tuple`, `List`, `Dict`, `Union`, etc).
(See their [README](https://github.com/agronholm/typeguard/blob/master/README.rst) for a full list)
However, as of `2.2.2` it doesn't support user-defined generic classes, so for a field like `z: UserDefinedList[float]`, `typeguard` will not check
if the contents are actually `floats`. 
This also prevents us from defining generic sumtypes (e.g. `ConsList[A]`, `Maybe[A]`, `Either[A, B]`), but I'm working on resolving this issue.

Typechecking can be controlled with the `typecheck` argument: `class Thing(sumtype, typecheck='always'|'debug'|'never'):`.
The default mode is `'always'`
Fields with no annotations will not be typechecked, and you can mix annotated and non-annotated fields in a definition.


### Equality and hashing
```python
>>> Thing.Foo(1,2) == Thing.Foo(1,2)
True
>>> Thing.Foo(1,2) == Thing.Bar('a', ('b', 'c'));
False
>>> {foo, foo, bar, zap} == {foo, bar, zap}
True
```
`__eq__` and `__hash__` pay attention to variant - even if we had a variant `Moo(x: int, y: int)`,
`Foo(1,2) != Moo(1,2)` and `hash(Foo(1,2)) != hash(Moo(1,2))`.

> **Note**: *Just like tuples, `sumtypes` `__eq__`/`__hash__` work by `__eq__`ing/`__hash__`ing the values inside,
so the values must all implement the relevant method for it to work.*


### Modifying values
```python
>>> foo;  foo.replace(x=99)
Thing.Foo(x=3, y=5)
Thing.Foo(x=99, y=5)
>>>
>>> bar;  bar.replace(y='abc', hmm=('d', 'e'))
Thing.Bar(y='hello', hmm=('wo', 'rld'))
Thing.Bar(y='abc', hmm=('d', 'e'))
```
`foo.replace(x=99)` returns a new value, just like in `namedtuple`. 
`.replace` behaves just like the constructors w.r.t. typechecking.

> **Note**: *`replace` and all the other methods have underscored aliases (`_replace`).
So even if you have a field called `replace`, you can still use `my_value._replace(x=15)`.*


### Pattern matching
##### Statement form:
```python
>>> def do_something(val: Thing):
...     if val.is_Foo():
...         print(val.x * val.y)
...     elif val.is_Bar():
...         print('The result is', val.y, ''.join(val.hmm))
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
##### Expression form:
```python
>>> [ val.match(
...      Foo = lambda x, y: x*y, 
...      Zap = lambda: 999,
...      _   = lambda: -1 # default case
...   )
...  for val in (foo, bar, zap)]
[15, -1, 999]
```


### Conversions between `sumtypes` and standard types
To...
```python
>>> foo.values();  foo.values_dict();
(3, 5)
OrderedDict([('x', 3), ('y', 5)])
```
```python
>>> foo.as_tuple();  foo.as_dict()
('Foo', 3, 5)
OrderedDict([('variant', 'Foo'), ('x', 3), ('y', 5)])
```
...and from
```python
>>> Thing.from_tuple(('Foo', 10, 15));  Thing.from_dict({'variant':'Foo', 'x': 10, 'y': 15})
Thing.Foo(x=10, y=15)
Thing.Foo(x=10, y=15)
```
Also, `x == Thing.from_tuple(x.as_tuple())` and `x == Thing.from_dict(x.as_dict())`.


### Pickle support
```python
>>> import pickle
>>> vals  = [Thing.Foo(1, 2), Thing.Bar('one', ('two', 'three')), Thing.Zap()]
>>> vals2 = pickle.loads(pickle.dumps(vals))
>>> vals;  vals == vals2
[Thing.Foo(x=1, y=2), Thing.Bar(y='one', hmm=('two', 'three')), Thing.Zap()]
True
```

There's also tests in `sumtype.tests` to ensure that it all works correctly.
And that's everything... for now!


## Features planned for in `1.0`
- Defining generic sumtypes like `Maybe[A]`/`Either[A, B]` in a typesafe way

## Should I use it?
Yeah! I didn't just build this library because I thought it'd be nice –
I'm using it heavily in an app I'm developing and a few smaller projects.
Saying that it's battle-tested is a bit much, but it's getting there.


## Possible future features
- Default values

- `mypy` support.
Unfortunately, last time I checked, `mypy` didn't handle metaclass-created classes too well, but that might have changed.
Alternatively, we could provide a way to generate `mypy` stub files. Also, right now there's no way to tell `mypy` that
the return type of accessors depend on the variant – `Union[a, b]` is close, but `mypy` will complain that not all cases
are handled even if they are.

- Statically generating a class definition to a file

- Dynamic alternatives to custom-generated methods –
might be useful if startup time is more important than efficiency

- An alternative implementation backed by tuples if true immutability is desired –
there's currently no way to make a `__slots__`-based implementation watertight in that aspect, I'm doing my best.

- **Maybe** opt-in mutability – currently, you can use `Thing._unsafe_set_Foo_x(foo, 10)` if you want that, but that's not a nice interface
