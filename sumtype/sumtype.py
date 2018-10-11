from typing import Tuple

from .sumtype_meta import sumtype_meta, _resolve_default_options
from .sumtype_slots import sumtype         as make_sumtype
from .sumtype_slots import untyped_sumtype as make_untyped_sumtype
__all__ = ['sumtype']

import sys
from warnings import warn


class sumtype(metaclass=sumtype_meta, _process_class=False):
	"""The main user-facing API of this package.
	
	This class is just a wrapper around stuff defined inside -
	see "Implemetation Notes" below for more. 
	
	## Usage

	### In a normal class definition:

		class Thing(sumtype):
			def Variant1(x: int, y: str): ...
			def Variant2(y: str, z: str, w: str): ...
			<... more stuff>

	Think of `def Foo(x: int, y: int): ...` as a constructor stub.
	Note that those are literal Python ellipses (`...`), not elided code -
	`sumtype` will generate the constructors,
	it's just a relatively convenient syntax for declaring variants.
	(If you like Haskell, think 'GADT syntax')

	You can pass keyword arguments to `sumtype()` like so:

		class Thing(sumtype, verbose=True):
			def Foo(x: int, y: int): ...
			def Bar(y: str): ...
			def Zip(hey: str): ...
			def Bop(): ...



	### namedtuple-style (as a factory function):

		Thing = sumtype('Thing', [('Variant1', [('x', int), ('y', str)]), ('Variant2', [...])])
		Thing = sumtype.untyped('Thing', [('Variant1', ['x', 'y']), ('Variant2', [...])])

	You can easily get the constructors in your local scope as well:

		Thing, Variant1, Variant2 = sumtype.with_constructors('Thing', [('Variant1', [('x', int), ('y', str)]), ('Variant2', [...])])
		Thing, Variant1, Variant2 = sumtype.untyped_with_constructors('Thing', [('Variant1', ['x', 'y']), ('Variant2', [...])])

	...but that might get removed in a future release -
	it's mostly here because a large codebase of mine used that form.
	Consider using
		T = sumtype('T', ...)
		Variant1, Variant2 = T._constructors
	instead.


	## Implementation notes

	This class is just a wrapper around `sumtype_meta.sumtype_meta`
	(which in turn wraps `sumtype_slots.sumtype(...)/untyped_sumtype(...)`).

	It has to be a class for the users to be able to write
		class Thing(sumtype):
			def Variant1(x: int, y: str): ...
			def Variant2(...): ...
			...
	instead of
		class Thing(metaclass=sumtype_meta):

	Its only role is to 'forward' the metaclass to `Thing` -
	it won't actually be added to `Thing.__mro__`.

	The `_process_class=False` metaclass keyword argument is necessary,
	because without it, `sumtype_meta` would turn it into variant class with no variants,
	which is an instance of `type`, not `sumtype_meta`,
	and the metaclass wouldn't be 'forwarded' to `Thing`.
	"""
	_options_for_generated_classes = {}

	# READERS: There's a bunch of stuff about '_module_name' here,
	# because we need to give the generated classes the __module__ that they were
	# defined in. It's not key to understand how this all works,
	# but if you want to, check out `namedtuple`'s source for a simpler example.

	# HACKY
	# (because, well, that's not what __new__ is supposed to do)
	def __new__(cls, typename, variant_names_and_specs, **user_options) -> type:
		"""A wrapper around `sumtype_slots.sumtype()`
		to support namedtuple-style definitions:
			T = sumtype('T', ...)
		See `help(sumtype)` for more.
		"""
		options = _resolve_default_options(cls.mro())
		options.update(user_options)
		options['_module_name'] = get_callers_module_if_necessary_or_warn(options, typename)
		return make_sumtype(typename, variant_names_and_specs, **options)

	# swallow the arguments passed to __new__()
	def __init__(cls, typename, variant_names_and_specs, **user_options): pass
		
	@classmethod
	def with_constructors(cls, typename, variant_names_and_specs, **user_options) -> Tuple[type, ...]:
		"""A wrapper around `sumtype_slots.sumtype()`
		to support namedtuple-style definitions:
			T, V1, V2 = sumtype.with_constructors('T', [('V1', [...]), ('V2', [...])]
		See `help(sumtype)` for more.
		"""
		options = _resolve_default_options(cls.mro())
		options.update(user_options)
		options['_module_name'] = get_callers_module_if_necessary_or_warn(options, typename)
		t = make_sumtype(typename, variant_names_and_specs, **options)
		return (t,) + t._constructors
		
	@classmethod
	def untyped(cls, typename, variant_names_and_specs, **user_options) -> type:
		"""A wrapper around `sumtype_slots.untyped_sumtype()`
		to support namedtuple-style definitions:
			T = sumtype.untyped('T', ...)
		See `help(sumtype)` for more.
		"""
		options = _resolve_default_options(cls.mro())
		options.update(user_options)
		options['_module_name'] = get_callers_module_if_necessary_or_warn(options, typename)
		return make_untyped_sumtype(typename, variant_names_and_specs, **options)

	@classmethod
	def untyped_with_constructors(cls, typename, variant_names_and_specs, **user_options) -> Tuple[type, ...]:
		"""A wrapper around `sumtype_slots.untyped_sumtype()`
		to support namedtuple-style definitions:
			T, V1, V2 = sumtype.untyped_with_constructors('T', [('V1', [...]), ('V2', [...])]
		See `help(sumtype)` for more.
		"""
		"A wrapper around `sumtype_slots.make_untyped_sumtype().`"
		options = _resolve_default_options(cls.mro())
		options.update(user_options)
		options['_module_name'] = get_callers_module_if_necessary_or_warn(options, typename)
		t = make_untyped_sumtype(typename, variant_names_and_specs, **options)
		return (t,) + t._constructors



# Ugly, but saves copy-pasting it a bunch of times.
def get_callers_module_if_necessary_or_warn(options, typename) -> str:
	# `untyped_sumtype` relies on sys._getframe to inspect the caller's frame and
	# get the right module name. That won't work if `sumtype` calls it,
	# since the caller's frame will be located in this module.
	# So we have to get the module name here, and pass it down.				 
	# We could just walk the callstack upwards until we find a module
	# that's outside this package, but AFAIK that's expensive.

	_module_name = options.get('_module_name', None)
	if _module_name is None:
		try:
			_module_name = sys._getframe(2).f_globals.get('__name__', '__main__') # 2 frames up - first the function that called it, then for the actual caller
		except (AttributeError, ValueError):
			warn(RuntimeWarning("Cannot access the caller's module name - pickle will likely have trouble unpickling {} objects".format(typename)))
			_module_name = '<generated by sumtype>'

	return _module_name



def demo():
	# create a class like this...
	class Thing(sumtype):
		def Foo(x: int, y: int): ...
		def Bar(y: str): ...
		def Zip(hey: str): ...
		Bop = ...
		# ^ constructor stubs (will be filled in by sumtype)

		__doc__ = """
		There are many kinds of things,
		so we need a whole bunch of variants.
		"""
		# ^ The docstring could be at the top in its normal form,
		# but it's nicer to have the constructors on top

		def my_method(thing, n: int) -> int:
			"Does stuff, and will be included in the generated class!"
			if thing.is_Foo():
				return thing.x + n*thing.y
			elif thing.is_Bar():
				return n + len(thing.y)
			else:
				return n

		@classmethod
		def make_something(cls):
			return cls.Zip('hello')

	# help(Thing)
	# print()

	f = Thing.Foo(3, 5)
	print(f)
	print(f, '.my_method(5) -> ', f.my_method(5), sep='')
	print()
	b = Thing.Bar("nice")
	print(b)
	print(b, '.my_method(5) -> ', b.my_method(5), sep='')
	print()
	print('Thing.make_something() -> ', Thing.make_something(), sep='')
	print()

	# ... or like this ... 
	Thing2 = sumtype.untyped(
	'Thing2',
	[
		('Foo', ['x', 'y',]),
		('Bar', ['y',     ]),
		('Zip', ['hey',   ]),
		('Hop', []         ),
	],
	)
	print()
	assert Thing2.__module__ == __name__, "Module name setting is broken: expected {!r}, got {!r}".format(__name__, Thing2.__module__)

	# ... or like this
	Thing3 = sumtype(
	'Thing',
	[
		('Foo', [('x',   object), ('y', object),]),
		('Bar', [('y',   object)]),
		('Zip', [('hey', object)]),
		('Hop', []),
	],
	)



if __name__ == '__main__':
	demo()



# An experimental Haskell-like syntax, probably won't be used but hey
#
# class TypeSpec:
#   def __init__(spec, name, variants=()):
#      spec.name = name
#      spec.variants = variants
#
#   def add_variant(spec, variant_tuple):
#	  variant, *fields = variant_tuple
#	  fields = tuple(fields)
#     return TypeSpec(spec.name,  spec.variants + (variant, fields))
#		
#   def __repr__(spec):
#     return spec.name+' - '+' | '.join(v+repr(tuple(fs)) for (v, *fs) in spec.variants)
#
#   __sub__ = add_variant
#   __or__  = add_variant
#	
#	def __iter__(spec): return ((spec.name, spec.variants))
#
# data = TypeSpec


# Thing = untyped_union(
# *data('Thing') - ('Foo', 'x', 'y')
#                | ('Bar', 'y')
#                | ('Zip', 'hey')
#                | ('Bop',)
# ) 
