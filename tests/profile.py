raise ImportError("Module {} isn't functional yet".format(__name__))

import sumtype.slots
import sumtype.tuple

uniq = sumtype.slots.uniq

# Void, = untyped_sumtype('Void', [], verbose=True, allow_zero_constructors=True)
# # print(dir(Void))
# print('\n\n')
# Void has no constructors, so it can't be instantiated.
# Mostly useless, but the fact that it works gives me a certain peace of mind about the codegen :)
# (inspired by Haskell, just like this whole module)

def pleple(untyped_sumtype):
	from dis import dis


	(Thing,
		Foo,
		Bar,
		Zip,
		Hop) = untyped_sumtype(
	'Thing',
	[
		('Foo', ['x', 'y',]),
		('Bar', ['y',     ]),
		('Zip', ['hey',   ]),
		('Hop', []         ),
	],
	)

	print('__name__     : ', Thing.__name__)
	print('__qualname__ : ', Thing.__qualname__)
	print('__module__   : ', Thing.__module__)
	# print('__doc__:', Thing.__doc__, sep='\n')
	# help(Thing)
	print('_positional_descriptors:', getattr(Thing, '_positional_descriptors', None))
	# print(dir(Thing))

	print()
	dis_func = Thing.match
	print('dis(%s):' % dis_func.__qualname__)
	print()
	dis(dis_func)
	print()
	
	foo = Thing.Foo(3, 5)
	bar = Thing.Bar("nice")
	zip = Thing.Zip(15.234)
	hop = Thing.Hop()


	print("Attribute access:")
	all_variant_fields = uniq( sum((Thing._variant_fields[variant] for variant in Thing._variants), ()) )

	for val in ('foo', 'bar', 'zip', 'hop'):
		val_ = eval(val)
		print("\t{}".format(val_))
		for field in all_variant_fields:
			should_work = (field in Thing._variant_fields[val_.variant])
			expr = "{val}.{field}".format(**locals())
			try:
				res = eval(expr)
				did_work = True
			except AttributeError as e:
				res = e
				did_work = False

			print(
				"\t\t{should}{did} {expr:<10}: {res!r}".format(
					expr=expr, res=res,
					should={True: '+', False: '-'}[should_work],
					did={True: '+', False: '-'}[did_work]
				)
			)

			assert should_work == did_work

			# print()
		expr = '{val}.{bad}'.format(val=val, bad=str.join('', all_variant_fields))
		try: res = eval(expr)
		except AttributeError as e: res = e
		print(
			"\t{expr:<10}: {res!r}".format(
				expr=expr, res=res,
			)
		)
		print()
		print()




	print()
	print(foo, bar, zip, hop, sep='\n')
	# Thing._variant_id.__set__(foo, 5)
	print("x==x:", foo==foo, bar==bar, zip==zip, hop==hop)
	print("V(*args) == V(*args):", Thing.Foo(3,5) == Thing.Foo(3,5))
	print("V(*args1) == V(*args2):", Thing.Foo(3,5) == Thing.Foo(0,10))
	print("X(*args) == Y(*args)", Thing.Bar(3) == Thing.Zip(3))
	print()
	foo2 = foo._copy()
	print("x, x.copy(), x is x.copy():", foo, foo2, foo is foo2, sep=', ')
	bar2 = bar._copy()
	print("x, x.copy(), x is x.copy():", bar, bar2, bar is bar2, sep=', ')
	zip2 = zip._copy()
	print("x, x.copy(), x is x.copy():", zip, zip2, zip is zip2, sep=', ')
	hop2 = hop._copy()
	print("x, x.copy(), x is x.copy():", hop, hop2, hop is hop2, sep=', ')
	bar2 = bar.replace(y="better")
	print("replace:", bar, bar2)
	print("x.is_X()", foo.is_Foo(), bar.is_Bar(), zip.is_Zip())
	print("x.is_Y()", foo.is_Bar(), bar.is_Zip(), zip.is_Foo())

	try: res = bar.replace(blah_blah_blah=5)
	except Exception as e: res = e
	print("bad replace 1:", bar, repr(res))

	try: res = bar.replace(_0=5)
	except Exception as e: res = e
	print("bad replace 2:", bar, repr(res))

	try: res = bar.replace(_variant_id=5)
	except Exception as e: res = e
	print("bad replace 2:", bar, repr(res))

	foo_ = Foo(3, 5)
	try:
		Thing._variant_id.__set__(foo_, 15)
		res = repr(foo_)
	except Exception as e:
		res = e
	print("repr of bad variant:", repr(res))

	foo_ = Foo(3, 5)
	Thing._unsafe_set_Foo_x(foo_, 10)
	print('unsafe set: Foo(3, 5) ->', foo_)
	# del foo._Foo_y
	# print(foo)

	# foo._Foo_y = 10
	# print(foo)



def profile()
	import timeit
	from sumtype_plain_tuple import untyped_sumtype as untyped_sumtype_tuple

	Thing2, *_ \
	= untyped_sumtype_tuple(
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
	main()


