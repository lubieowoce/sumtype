from .sumtype_slots import sumtype as make_sumtype

# from pprint import pprint
import inspect
from collections import OrderedDict
import typing
from typing import Tuple, Union, List

__all__ = [
	'sumtype_meta',
]





is_variant_name = lambda name: name and name.isidentifier() and name[0].isupper()


def _resolve_options(user_options: dict, bases: 'Tuple[type, ...]') -> 'dict':
	options = _resolve_default_options(bases)
	options.update(user_options)
	return options


def _resolve_default_options(bases: 'Tuple[type, ...]') -> 'dict':
	"Collect all default options defined in convenience base-classes like `sumtype`"
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
			bases: 'Tuple[type, ...]', 
			dct: 'dict', 
			*, 
			_process_class: 'bool' = True, 
			 **user_options
		 ) -> 'Union[sumtype_meta, type]':
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

		options = _resolve_options(user_options, bases)

		def interpret_constructor(variant: str, constructor_stub) -> 'Tuple[str, List[Tuple[str, type]]]':
			if inspect.isroutine(constructor_stub):
				field_spec = []
				type_hints = typing.get_type_hints(constructor_stub)
				for (field, _param_descr) in inspect.signature(constructor_stub).parameters.items():
					field_type = type_hints.get(field, typing.Any)
					field_spec.append((field, field_type))
				return (variant, field_spec)
			else:
				raise TypeError(
					"Constructor stub '{variant}' must be a function, is '{constructor_stub.__class__.__qualname__}'" \
						.format(variant=variant, constructor_stub=constructor_stub)
				)
		

		if options.get('constants'):
			interpret_constructor_function = interpret_constructor

			def interpret_constructor(variant: str, constructor_stub) -> 'Tuple[str, List[Tuple[str, type]]]': 
				if constructor_stub is ...:
					return (variant, [])
				elif inspect.isroutine(constructor_stub):
					res = _variant, field_spec = interpret_constructor_function(variant, constructor_stub)
					if len(field_spec) == 0:
						raise TypeError(
							"Constructor stub '{variant}' must declare at least one field when `constants=True`\n"+
							"(Use `{variant} = ...` for variants with no fields)"
						).format(variant=variant)
					return res
				else:
					raise TypeError(
						"Constructor stub '{variant}' must be a function or `...`, is '{constructor_stub.__class__.__qualname__}'" \
							.format(variant=variant, constructor_stub=constructor_stub)
					)
			

		o_variants = dct.pop('__variants__', None)
		if o_variants is not None:
			variants_and_constructor_stubs = [
				(name, dct[name]) for name in o_variants 
			]
		else:
			variants_and_constructor_stubs = [
				(name, val) for (name, val) in dct.items()
				if is_variant_name(name)
			]

		variant_specs = [
			interpret_constructor(variant, constructor_stub) 
			for (variant, constructor_stub) in variants_and_constructor_stubs
		]

		# remove the constructor stubs from the namespace
		for (variant, _) in variants_and_constructor_stubs:
			del dct[variant]

		module_name = dct['__module__']


		GeneratedClass = make_sumtype(
			typename,
			variant_specs,
			_module_name=module_name,
			**options,
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
		