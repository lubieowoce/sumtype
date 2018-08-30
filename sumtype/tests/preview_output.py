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
	def Bar(y: str): ...
	# def Zip(hey: str): ...
	def Zip(hey): ...
	def Bop(): ...
	# ^ constructor stubs (will be filled in by sumtype)

help(Thing)

f = Thing.Foo(3, 5)
f = f.replace(y=99)
print(f.x, f.y)
