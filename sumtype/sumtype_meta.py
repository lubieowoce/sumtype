from .sumtype_slots import sumtype as make_sumtype

# from pprint import pprint
import inspect
from collections import OrderedDict
import typing

__all__ = [
	'sumtype_meta',
]





is_variant_name = lambda name: name and name.isidentifier() and name[0].isupper()

class sumtype_meta(type):
	"""
	A metaclass wrapper for `sumtype.[untyped_]sumtype()`
	which enables the user to create sum types with a class-based syntax.
	See `sumtype.sumtype` for more.
	"""
	# creates something to hold the class namespace
	def __prepare__(typename, bases, process_class=True, **_):
		if process_class:
			# preserve variant definition order
			return OrderedDict()
		else:
			return {}

	# processes the class definition 
	def __new__(metacls, typename, bases, dct, *, process_class=True, **kwargs) -> 'Union[sumtype_meta, type]':
		"""
		Note:
			Unless it's passed `process_class=False`,
			this metaclass returns an instance of `type`, not `sumtype_meta`.
			This is so that subclasses of the created sum type won't get
			processed by `sumtype_meta` again.

			if it is passed `process_class=False`, it just forwards the call to type.__new__()
			without any processing. This is used for the `sumtype` convenience class.
		"""

		if not process_class:
			return type.__new__(metacls, typename, bases, dct)

		o_variants = dct.pop('__variants__', None)
		if o_variants is not None:
			variants_and_constructor_stubs = [
				(name, dct[name]) for name in o_variants 
			]
		else:
			variants_and_constructor_stubs = [
				(name, val) for (name, val) in dct.items()
				if is_variant_name(name) and inspect.isroutine(val)
			]

		# remove the constructor stubs from the namespace
		for (variant, _) in variants_and_constructor_stubs:
			del dct[variant]

		variant_specs = []
		for (variant, constructor_stub) in variants_and_constructor_stubs:
			hints = typing.get_type_hints(constructor_stub)
			spec = []
			for (field, _param_descr) in inspect.signature(constructor_stub).parameters.items():
				field_type = hints.get(field, typing.Any)
				spec.append((field, field_type))
			variant_specs.append((variant, spec))

		module_name = dct['__module__']


		Class = make_sumtype(typename, variant_specs, _module_name=module_name, **kwargs)


		# Append the the generated docstring to original docstring to 
		original_doc = dct.pop('__doc__', None)
		if original_doc:
			Class.__doc__ = inspect.cleandoc(original_doc) + '\n\n' + Class.__doc__

		# Insert the rest of the class dict - stuff like user-defined methods
		for (name, val) in dct.items():
			setattr(Class, name, val)

		return Class



	def __init__(metacls, typename, bases, dct, **_):
		# A dummy __init__ that swallows the keyword arguments,
		# because `type` doesn't handle them 
		pass
		