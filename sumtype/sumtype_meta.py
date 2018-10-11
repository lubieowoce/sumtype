from .sumtype_slots import sumtype as make_sumtype

# from pprint import pprint
import inspect
from collections import OrderedDict
import typing

__all__ = [
	'sumtype_meta',
]





is_variant_name = lambda name: name and name.isidentifier() and name[0].isupper()

def _resolve_default_options(bases: 'typing.Tuple[type, ...]') -> 'dict':
	collected_options = {}
	for base in reversed(bases): # newer options override old ones
		options = getattr(base, '_default_options_for_generated_classes', {})
		collected_options.update(options)
	return collected_options


class sumtype_meta(type):
	"""
	A metaclass wrapper for `sumtype.[untyped_]sumtype()`
	which enables the user to create sum types with a class-based syntax.
	See `sumtype.sumtype` for more.
	"""
	# creates something to hold the class namespace
	def __prepare__(typename, bases, _process_class=True, **_):
		if _process_class:
			# preserve variant definition order
			return OrderedDict()
		else:
			return {}

	# processes the class definition 
	def __new__(
			metacls, 
			typename: 'str', 
			bases: 'typing.Tuple[type, ...]', 
			dct: 'dict', 
			*, 
			_process_class: 'bool' = True, 
			 **options
		 ) -> 'typing.Union[sumtype_meta, type]':
		"""
		Note:
			Unless it's passed `_process_class=False`,
			this metaclass returns an instance of `type`, not `sumtype_meta`.
			This is so that subclasses of the created sum type won't get
			processed by `sumtype_meta` again.

			if it is passed `_process_class=False`, it just forwards the call to type.__new__()
			without any processing. This is used for the `sumtype` convenience class.
		"""
		if __debug__:
			_default_options_for_generated_classes = dct.get('_default_options_for_generated_classes')
			if _default_options_for_generated_classes:
				assert not _process_class, (
					'_default_options_for_generated_classes can only be present if _process_class=False'
				)

		if not _process_class:
			ConvenienceClass = type.__new__(metacls, typename, bases, dct)
			return ConvenienceClass


		# 'parse' the class definition to get a typespec for `make_sumtype(...)


		o_variants = dct.pop('__variants__', None)
		if o_variants is not None:
			variants_and_constructor_stubs = [
				(name, dct[name]) for name in o_variants 
			]
		else:
			variants_and_constructor_stubs = [
				(name, val) for (name, val) in dct.items()
				if is_variant_name(name) and (
					val is ... or inspect.isroutine(val)
				)
			]

		# remove the constructor stubs from the namespace
		for (variant, _) in variants_and_constructor_stubs:
			del dct[variant]

		variant_specs = []
		for (variant, constructor_stub) in variants_and_constructor_stubs:
			if inspect.isroutine(constructor_stub):
				field_spec = []
				hints = typing.get_type_hints(constructor_stub)
				for (field, _param_descr) in inspect.signature(constructor_stub).parameters.items():
					field_type = hints.get(field, typing.Any)
					field_spec.append((field, field_type))
				spec = (variant, field_spec)
			else:
				spec = (variant, []) # no arg constructor defined with `Variant = ...`
			variant_specs.append(spec)

		module_name = dct['__module__']

		all_options = _resolve_default_options(bases)
		all_options.update(options)

		GeneratedClass = make_sumtype(
			typename,
			variant_specs,
			_module_name=module_name,
			**all_options,
		)


		# Append the generated docstring to the original docstring
		original_doc = dct.pop('__doc__', None)
		if original_doc:
			GeneratedClass.__doc__ = inspect.cleandoc(original_doc) + '\n\n' + GeneratedClass.__doc__

		# Insert the rest of the class dict - stuff like user-defined methods
		for (name, val) in dct.items():
			setattr(GeneratedClass, name, val)

		return GeneratedClass



	def __init__(metacls, typename, bases, dct, **_):
		# A dummy __init__ that swallows the keyword arguments,
		# because `type` doesn't handle them 
		pass
		