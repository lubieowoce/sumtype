# allow this module to import the whole package
if __name__ == '__main__':
	import pathlib
	import sys
	here = pathlib.Path(__file__).resolve()
	parent_package_location = here.parents[2]
	print('Adding', str(parent_package_location), 'to sys.path to enable import\n')
	sys.path.append(str(parent_package_location))

import typing as t
from sumtype import sumtype

# class Thing(sumtype, verbose=True):
class Thing(sumtype):
	# def Foo(x: t.Tuple[int, str], y: int): ...
	def Foo(x: int, y: int): ...
	def Bar(y: t.List[str]): ...
	# def Zip(hey: str): ...
	def Zip(hey: t.Tuple[float, float]): ...
	def Bop(): ...


print('\n\n\n--------------')
f = Thing.Foo(3, 5)
b = Thing.Bar(['abc', 'def'])
z = Thing.Zip((3.5, 6.7))
d = Thing.Bop()


try: res = Thing.Foo('x', 'y')
except TypeError as e: res = e
print(repr(res))
print()

# res = Thing.Bar([1, 2, '3'])
try: res = Thing.Bar([1, 2, '3'])
except TypeError as e: res = e
print(repr(res))
print()

try: res = Thing.Zip(('x', 'y'))
except TypeError as e: res = e
print(repr(res))
print()

print(Thing.from_tuple(('Foo', 100, 200)))
try: res = Thing.from_tuple(('Foo', 'x', 'y'))
except TypeError as e: res = e
print(repr(res))
print()

print(repr(f.replace(x=15)))
try: res = f.replace(x='a')
except TypeError as e: res = e
print(repr(res))
print()