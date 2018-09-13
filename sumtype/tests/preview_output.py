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

# # class Thing(sumtype, verbose=True):
# class Thing(sumtype):
# 	# def Foo(x: t.Tuple[int, str], y: int): ...
# 	def Foo(x: int, y: int): ...
# 	def Bar(y: str): ...
# 	# def Zip(hey: str): ...
# 	def Zip(hey: t.Tuple[float, float]): ...
# 	def Bop(): ...


# print('\n\n\n--------------')
# f = Thing.Foo(3, 5)
# b = Thing.Bar('abc')
# z = Thing.Zip((3.5, 6.7))
# d = Thing.Bop()

# try: res = Thing.Foo('x', 'y')
# except TypeError as e: res = e
# print(repr(res))
# print()

# print(Thing.from_tuple(('Foo', 100, 200)))
# try: res = Thing.from_tuple(('Foo', 'x', 'y'))
# except TypeError as e: res = e
# print(repr(res))
# print()

# print(repr(f.replace(x=15)))
# try: res = f.replace(x='a')
# except TypeError as e: res = e
# print(repr(res))
# print()

A = t.TypeVar('A')
class Maybe(sumtype, type_parameters=A):
	def Nothing(): ...
	def Just(val: A): ...

print(Maybe.Just.__annotations__)
print()
print(Maybe.__instancecheck__)
print(Maybe[int].__instancecheck__)
print()

def typing_props_type(x):
	print(x)
	for attr in ('__class__', '__origin__', '__args__', '__extra__', '__orig_bases__'):
		print(attr, '=', getattr(x, attr, '<not present>'))
	print()

typing_props_type(Maybe)

typing_props_type(Maybe[int])

# cls_type = Maybe[int].Just.__annotations__['_cls']
# print(cls_type)
# for attr in ('__orig_class__', '__origin__', '__args__'):
# 	print(attr, '=', getattr(cls_type, attr, '<not present>'))
# print()
	
# cls = cls_type.__args__[0]
# print(cls)
# for attr in ('__orig_class__', '__origin__', '__args__'):
# 	print(attr, '=', getattr(cls, attr, '<not present>'))
# print()

def typing_props_val(x):
	print(x)
	for attr in ('__class__', '__orig_class__'):
		print(attr, '=', getattr(x, attr, '<not present>'))
	print()
	
x = Maybe.Just(3)
typing_props_val(x)

x = Maybe[int].Just(3)
typing_props_val(x)
# x = Maybe.__dict__['Just'].__func__(object, 3)


print('Maybe[int].__instancecheck__(x):', isinstance(x, Maybe[int]))
print()
print('Maybe[str].__instancecheck__(x):', isinstance(x, Maybe[str]))
print()
print('Maybe.__instancecheck__(x):', isinstance(x, Maybe))
print()

print("Maybe.assert_type('x', {}, {})".format(x, Maybe[int]))
Maybe.assert_type('x', x, Maybe[int])
print()
print("Maybe.assert_type('x', {}, {})".format(x, Maybe[str]))
Maybe.assert_type('x', x, Maybe[str])


x = Maybe.Just((1,3))
print('isinstance(x, Maybe[t.Tuple[int, int]]):', isinstance(x, Maybe[t.Tuple[int, int]]))

# import typing
# print('*******************************')
# print()
# for name in dir(typing):
# 	val = getattr(typing, name)
# 	extra = getattr(val, '__extra__', '-')
# 	print('{:<20}: {!r}'.format(name, extra))

