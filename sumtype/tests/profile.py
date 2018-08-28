raise NotImplementedError("Profiling {} isn't functional yet".format(__name__))


# allow this module to import the whole package
if __name__ == '__main__':

	import pathlib
	import sys
	here = pathlib.Path(__file__).resolve()
	parent_package_location = here.parents[2]
	print('Adding', str(parent_package_location), 'to sys.path to enable import\n')
	sys.path.append(str(parent_package_location))
	


def profile():

	import timeit
	from sumtype_plain_tuple import untyped_sumtype as untyped_sumtype_tuple

	Thing2 = untyped_sumtype_tuple(
	'Thing2', [
		('Foo', ('x', 'y',)),
		('Bar', ('y',)),
		('Zip', ('hey',)),
	])


	create_3_variants = """
foo = Thing.Foo(3, 5)
bar = Thing.Bar("nice")
zip = Thing.Zip(15.234)
"""
	create_3_variants_kwargs = """
foo = Thing.Foo(x=3, y=5)
bar = Thing.Bar(y="nice")
zip = Thing.Zip(hey=15.234)
"""

	access_attributes = """
x = foo.x
# y = foo.y
# y = bar.y
# z = zip.hey
"""
	unsafe_access_attributes = """
x = foo._Foo_x
# y = foo._Foo_y
# y = bar._Bar_y
# z = zip._Zip_hey
"""

	replace_all_attributes = """
foo2 = foo.replace(x=4)
# foo2 = foo.replace(x=4, y=6)
# bar2 = bar.replace(y="nicer")
# zip2 = zip.replace(hey=3.141592)
"""

	copy = """
foo2 = foo._copy()
# bar2 = bar._copy()
# zip2 = zip._copy()
"""
	# make the classes accessible to timeit
	# (they're created within `main()`, so they're not visible otherwise)
	globals()['Thing']  = Thing
	globals()['Thing2'] = Thing2

	slot_sumtype_setup  = "from __main__ import Thing"
	tuple_sumtype_setup = "from __main__ import Thing2 as Thing"


	n_timing_repetitions = 100001

	tests = (
		('slot_sumtype_create_3',          create_3_variants,        slot_sumtype_setup),
		('tuple_sumtype_create_3',         create_3_variants,        tuple_sumtype_setup),

		# ('slot_sumtype_create_3_kwargs',   create_3_variants_kwargs, slot_sumtype_setup),
		# ('tuple_sumtype_create_3_kwargs',  create_3_variants_kwargs, tuple_sumtype_setup),

		('slot_sumtype_access_all',        access_attributes,        slot_sumtype_setup +create_3_variants),
		('tuple_sumtype_access_all',       access_attributes,        tuple_sumtype_setup+create_3_variants),
		('slot_sumtype_unsafe_access_all', unsafe_access_attributes, slot_sumtype_setup +create_3_variants),

		('slot_sumtype_copy',              copy,                     slot_sumtype_setup +create_3_variants),
		('tuple_sumtype_copy',             copy,                     slot_sumtype_setup +create_3_variants),

		('slot_sumtype_replace_all_attributes',          replace_all_attributes,        slot_sumtype_setup +create_3_variants),
		('tuple_sumtype_replace_all_attributes',         replace_all_attributes,        tuple_sumtype_setup+create_3_variants),
	)
	print("Profiling")
	for (name, code, setup) in tests:
		time_usec = timeit.timeit(
			code,
			setup=setup,
			number=n_timing_repetitions
		) * 1000000 / n_timing_repetitions
		print('\t{name}:\t{time_usec:.2f} usec'.format(**locals()))


if __name__ == '__main__':
	profile()