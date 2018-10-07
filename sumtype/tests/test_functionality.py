# allow this module to import the whole package
if __name__ == '__main__':

	import pathlib
	import sys
	here = pathlib.Path(__file__).resolve()
	parent_package_location = here.parents[2]
	print('Adding', str(parent_package_location), 'to sys.path to enable import\n')
	sys.path.append(str(parent_package_location))

# test if asserts work
if __name__ == '__main__':
	try: assert False; asserts_disabled = True
	except AssertionError: asserts_disabled = False
	if asserts_disabled: raise RuntimeError("Asserts are disabled, tests won't work")



import sumtype
# import sumtype.sumtype_slots as sumtype_slots
# import sumtype.experimental.sumtype_plain_tuple as sumtype_plain_tuple

uniq = sumtype.slots.uniq

def test_make_from_bad_spec():
	try: res = sumtype.sumtype.untyped('_Underscore Space Name', [('V', ['_a', 'as', 'b c']), ('V', ['x', 'x'])])
	except Exception as e: res = e
	assert isinstance(res, ValueError), repr(res)
	print('Bad type spec handled OK')

def make_void_classdef():
	class Void(sumtype.sumtype, allow_zero_constructors=True):
		pass
	print("Void classdef OK")
	return Void


def make_void_call():
	Void = sumtype.sumtype('Void', [], allow_zero_constructors=True)
	print("Void call OK")
	return Void


def test_void(Void):
	# print(dir(Void))
	# Void has no constructors, so it can't be instantiated.
	# Mostly useless, but the fact that it works gives me a certain peace of mind about the codegen :)
	# (inspired by Haskell, just like this whole module)
	assert Void.__name__     == 'Void',        Void.__name__
	assert Void.__qualname__.endswith('Void'), Void.__qualname__
	assert Void.__module__   == __name__,      Void.__module__

	assert Void._constructors == ()
	print('All "Void" tests OK')


def make_thing_classdef() -> type:
	class Thing(sumtype.sumtype):
		def Foo(x: int, y: int): ...
		def Bar(y: str): ...
		def Zip(hey: float): ...
		Hop = ...
		
	print("Thing classdef OK")
	return Thing


def make_thing_call() -> type:
	Thing = sumtype.sumtype(
	'Thing', [
		('Foo', [('x', int), ('y', int)]),
		('Bar', [('y', str)]),
		('Zip', [('hey', float)]),
		('Hop', []),
	])

	print("Thing call OK")
	return Thing



def test_thing(Thing):
	import builtins as b

	assert Thing.__name__     == 'Thing',         Thing.__name__
	assert Thing.__qualname__.endswith('Thing'),  Thing.__qualname__
	assert Thing.__module__   == __name__,        Thing.__module__
	
	foo = Thing.Foo(3, 5)
	bar = Thing.Bar("nice")
	zip = Thing.Zip(15.234)
	hop = Thing.Hop

	# print("Attribute access:")
	all_variant_fields = uniq( sum((Thing._variant_fields[variant] for variant in Thing._variants), ()) )

	err_msg = lambda expr, should_work, did_work, res: (
		"'{expr}' {should_str} work, but it {did_str}, giving '{res}'"\
			.format(
				should_str={True: "should", False: "shouldn't"}[should_work],
				did_str   ={True: "did", False: "didn't"}[did_work],
				**locals()
			)
	)

	for val in ('foo', 'bar', 'zip', 'hop'):
		val_ = eval(val)
		# print("\t{}".format(val_))
		for field in all_variant_fields:
			should_work = (field in Thing._variant_fields[val_.variant])
			expr = "{val}.{field}".format(**locals())
			try:
				res = eval(expr)
				did_work = True
			except AttributeError as e:
				res = e
				did_work = False

			# print(
			# 	"\t\t{should}{did} {expr:<10}: {res!r}".format(
			# 		expr=expr, res=res,
			# 		should={True: '+', False: '-'}[should_work],
			# 		did={True: '+', False: '-'}[did_work]
			# 	)
			# )

			assert should_work == did_work, err_msg(expr, should_work, did_work, res)

			# print()

		# get undeclared field
		expr = '{val}.{bad}'.format(val=val, bad=str.join('', all_variant_fields))
		try: res = eval(expr)
		except AttributeError as e: res = e
		assert isinstance(res, AttributeError), err_msg(expr, should_work=False, did_work=isinstance(res, AttributeError), res=res)
		# print(
		# 	"\t{expr:<10}: {res!r}".format(
		# 		expr=expr, res=res,
		# 	)
		# )
		# print()
		# print()



	# print()
	# print(foo, bar, zip, hop, sep='\n')
	values = (foo, bar, zip, hop)

	for x in values:
		expr = 'x == x'
		res  = eval(expr)
		assert expr, '{!r} failed for {!r}'.format(expr, x)


	args1 = ((3, 5,),  ("nice",), (15.234,), ())
	args2 = ((0, 10,), ("bad",),  (3.1415,), ())

	expr = "C(*args1) == C(*args1)"
	for (C, args1) in b.zip(Thing._constructors, args1):
		if len(args1) >= 1:
			res  = eval(expr)
			assert res, '{!r} failed for {!r}'.format(expr, (C, args1))


	expr = "C(*args1) != C(*args2) if "
	for (C, args1, args2) in b.zip(Thing._constructors, args1, args2):
		if len(args1) >= 1:
			res  = eval(expr)
			assert res, '{!r} failed for {!r}'.format(expr, (C, args1, args2))

	# doesn't work if the variants have different type specs
	# args = (3,); C1 = Thing.Bar; C2 = Thing.Zip
	# expr = "C1(*args) != C2(*args)"; res = eval(expr)
	# assert res, '{!r} failed for {!r}'.format(expr, (C1, C2, args))


	expr = 'x == x.copy()'
	for x in values:
		res = eval(expr)
		assert res, '{!r} failed for {!r}'.format(expr, x)


	expr = 'x is not x.copy()'
	for x in values:
		res = eval(expr)
		assert res, '{!r} failed for {!r}'.format(expr, x)

	# kwargs1 = ((3, 5,),  ("nice",), (15.234,), ())
	# kwargs2 = ((0, 10,), ("bad",),  (3.1415,), ())
	from collections import OrderedDict
	assert len(Thing._variant_id_fields) == len(args2), '{} !~= {}'.format(Thing._variant_id_fields, args2)
	kwargs2 = [OrderedDict(b.zip(fields, args)) for (fields, args) in b.zip(Thing._variant_id_fields, args2)]
	
	left  = 'x._constructor(**kwargs)'
	right = 'x._replace(**kwargs)'
	left_  = eval('lambda x, kwargs: '+left)
	right_ = eval('lambda x, kwargs: '+right) 
	for (x_, kwargs_) in b.zip(values, kwargs2):
		if kwargs_:
			vleft  = left_ (x_, kwargs_)
			vright = right_(x_, kwargs_)
			res = vleft == vright
			assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, (x_, kwargs_),)

	bar2 = bar.replace(y="better")
	assert bar2.y == "better", repr(bar2)


	for x in values:
		for V in Thing._variants:
			if x._variant == V:
				expr = 'x.is_{}()'.format(V)
			else:
				expr = 'not x.is_{}()'.format(V)
			res = eval(expr)
			assert res, '{!r} failed for {!r}'.format(expr, (x, V))


	expr = 'x == Thing.from_tuple(x.as_tuple())'
	for x in values:
		res = eval(expr)
		assert res, '{!r} failed for {!r}'.format(expr, x)


	expr = 'x == Thing.from_dict(x.as_dict())'
	for x in values:
		res = eval(expr)
		assert res, '{!r} failed for {!r}'.format(expr, x)


	left  = 'x'
	right = 'x.replace(**x.values_dict())'
	left_  = eval('lambda x: '+left)
	right_ = eval('lambda x: '+right) 
	for x_ in values:
		vleft  = left_ (x_)
		vright = right_(x_)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, x_,)


	left  = 'set( x.as_dict().items() )'
	right = 'set([("variant", x._variant)]) | set([(field, getattr(x, field)) for field in fields])'
	left_  = eval('lambda x, fields: '+left)
	right_ = eval('lambda x, fields: '+right) 
	for (x_, fields_) in b.zip(values, Thing._variant_id_fields):
		vleft  = left_ (x_, fields_)
		vright = right_(x_, fields_)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, (x_, fields_),)


	left  = 'x.as_tuple()'
	right = '(x.variant,) + tuple(getattr(x, field) for field in fields)'
	left_  = eval('lambda x, fields: '+left)
	right_ = eval('lambda x, fields: '+right) 
	for (x_, fields_) in b.zip(values, Thing._variant_id_fields):
		vleft  = left_ (x_, fields_)
		vright = right_(x_, fields_)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, (x_, fields_),)


	left  = 'set( x.as_dict().items() )'
	right = 'set( zip(("variant",)+fields, x.as_tuple()) )'
	left_  = eval('lambda x, fields: '+left)
	right_ = eval('lambda x, fields: '+right) 
	for (x_, fields_) in b.zip(values, Thing._variant_id_fields):
		vleft  = left_ (x_, fields_)
		vright = right_(x_, fields_)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, (x_, fields_),)


	expr = 'x.values() == x.as_tuple()[1:] == x.__getstate__()[1:]'
	for x in values:
		res = eval(expr)
		assert res, '{!r} failed for {!r}'.format(expr, x)

	expr = 'new_x == x'
	for x in values:
		x_state = x.__getstate__()
		new_x = Thing.__new__(Thing)
		new_x.__setstate__(x_state)
		res = eval(expr)
		assert res, '{!r} failed for {!r}'.format(expr, x)


	try: res = bar.replace(blah_blah_blah=5)
	except Exception as e: res = e
	# print("bad replace 1:", bar, repr(res))
	assert isinstance(res, Exception), repr(res)

	try: res = bar.replace(_0=5)
	except Exception as e: res = e
	# print("bad replace 2:", bar, repr(res))
	assert isinstance(res, Exception), repr(res)

	try: res = bar.replace(_variant_id=5)
	except Exception as e: res = e
	# print("bad replace 2:", bar, repr(res))
	assert isinstance(res, Exception), repr(res)

	foo_ = Thing.Foo(3, 5)
	try:
		Thing._variant_id.__set__(foo_, 15)
		res = repr(foo_)
	except Exception as e:
		res = e
	# print("repr of bad variant:", repr(res))
	assert isinstance(res, Exception), repr(res)

	foo_ = Thing.Foo(3, 5)
	Thing._unsafe_set_Foo_x(foo_, 10)
	# print('unsafe set: Foo(3, 5) ->', foo_)
	assert foo_.x == 10
	Thing._unsafe_set_Foo_x(foo_, 3)
	assert foo_.x == 3
	# del foo._Foo_y
	# print(foo)

	# foo._Foo_y = 10
	# print(foo)
	print('All "Thing" tests OK')


if __name__ == '__main__':
	print('Running tests')
	print()
	for Thing in (make_thing_classdef(), make_thing_call()):
		test_thing(Thing)
	print()
	for Void in (make_void_classdef(), make_void_call()):
		test_void(Void)
	print()

	test_make_from_bad_spec()




