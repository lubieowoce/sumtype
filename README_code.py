# A quick demo

from sumtype import sumtype

class Thing(sumtype):
    def Foo(x: int, y: int): ...
    def Bar(y: str, hmm: str): ...
    def Zap(): ...


foo = Thing.Foo(x=3, y=5) # named
foo
foo.x;  foo.y;

bar = Thing.Bar('hello', 'world') # positional
bar
bar.y;  bar.hmm

zap = Thing.Zap()
zap

[type(foo), type(bar), type(zap)] # they're different variants of the same type!


# Automatic equality and hashing

foo == foo; foo == bar;
{foo, bar, bar, zap}


# Pattern matching

def do_something(val: Thing):
    if val.is_Foo():
        print(val.x * val.y)
    elif val.is_Bar():
        print('The result is', val.y, val.hmm)
    elif val.is_Zap():
        print('Whoosh!')
    else: val.impossible() # throws an error - nice if you like having all cases covered

for val in (foo, bar, zap):
    do_something(val)


# Pattern matching 2

f = lambda val: val.match(
        Foo = lambda x, y: x * y,
        Zap = lambda: 999,
        _   = lambda: -1 # default case
    )

[f(val) for val in (foo, bar, zap)]


# Updating

foo;  foo.replace(x=5)
bar;  bar.replace(y='abc', hmm='xyz')


# Value access and conversions

foo.values();  foo.as_tuple();  foo.as_dict()
Thing.from_tuple(('Bar', 'one', 'two'))


# Pickle support

import pickle
vals  = [Thing.Foo(1, 2), Thing.Bar('one', 'two'), Thing.Zap()]
vals2 = pickle.loads(pickle.dumps(vals))
vals;  vals == vals2
