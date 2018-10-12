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



import sumtype as st
# import sumtype.sumtype_slots as sumtype_slots
# import sumtype.experimental.sumtype_plain_tuple as sumtype_plain_tuple

uniq = st.slots.uniq

def options_repr(options: dict) -> str:
	if not options:
		return ''
	return (
		'(' +
		', '.join('{k}={v!r}'.format(k=k, v=v) for (k, v) in options.items()) +
		')'
	)


def test_make_from_bad_spec():
	try: 
		res = st.sumtype.untyped(
			'_Underscore Space Name', [
				('Repeated', ['_a', 'as', 'b c']),
				('Repeated', ['x', 'x'])
			]
		)
	except Exception as e: res = e
	assert isinstance(res, ValueError), repr(res)
	print('Bad type spec handled OK')


def make_void_classdef(sumtype):
	class Void(sumtype, allow_zero_constructors=True):
		pass
	print("Void classdef OK")
	return Void


def make_void_call(sumtype):
	Void = sumtype('Void', [], allow_zero_constructors=True)
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



def make_thing_classdef_new(sumtype, user_options=None) -> type:
	if user_options is None: user_options = {}

	class Thing(sumtype, **user_options):
		def Foo(x: int, y: int): ...
		def Bar(y: str): ...
		def Zap(hey: float): ...
		Hop = ...
		
	print('old <Thing{}> classdef OK'.format(options_repr(user_options)))
	return Thing


def make_thing_classdef_old(sumtype, user_options=None) -> type:
	if user_options is None: user_options = {}
	class Thing(sumtype, **user_options):
		def Foo(x: int, y: int): ...
		def Bar(y: str): ...
		def Zap(hey: float): ...
		def Hop(): ...
		
	print('old <Thing{}> classdef OK'.format(options_repr(user_options)))
	return Thing


def make_thing_call(sumtype, user_options=None) -> type:
	if user_options is None: user_options = {}

	Thing = sumtype(
		'Thing', [
			('Foo', [('x', int), ('y', int)]),
			('Bar', [('y', str)]),
			('Zap', [('hey', float)]),
			('Hop', []),
		],
		**user_options
	)

	print('<Thing{}> call OK'.format(options_repr(user_options)))
	return Thing



def test_thing(Thing, user_options=None):
	if user_options is None: user_options = {}
	# inclusion test works on items, not dicts
	assert is_subdict(user_options, Thing._options), (
		repr((user_options, Thing._options))
	)
	options = Thing._options

	import builtins as b

	assert Thing.__name__     == 'Thing',         Thing.__name__
	assert Thing.__qualname__.endswith('Thing'),  Thing.__qualname__
	assert Thing.__module__   == __name__,        Thing.__module__
	
	foo = Thing.Foo(3, 5)
	bar = Thing.Bar("nice")
	zap = Thing.Zap(15.234)
	hop = Thing.Hop if options.get('constants') else Thing.Hop()

	# print("Attribute access:")
	all_variant_fields = uniq( sum((Thing._variant_fields[variant] for variant in Thing._variants), ()) )

	err_msg = lambda expr, should_work, did_work, res: (
		"'{expr}' {should_str} work, but it {did_str}, giving '{res}'" \
			.format(
				should_str={True: "should", False: "shouldn't"}[should_work],
				did_str   ={True: "did", False: "didn't"}[did_work],
				**locals()
			)
	)

	eval = b.eval
	for val in ('foo', 'bar', 'zap', 'hop'):
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
		assert isinstance(res, AttributeError), \
			err_msg(expr, should_work=False, did_work=isinstance(res, AttributeError), res=res)
		# print(
		# 	"\t{expr:<10}: {res!r}".format(
		# 		expr=expr, res=res,
		# 	)
		# )
		# print()
		# print()



	# print()
	# print(foo, bar, zap, hop, sep='\n')
	values = (foo, bar, zap, hop)

	for x in values:
		expr = 'x == x'
		res  = eval(expr)
		assert expr, '{!r} failed for {!r}'.format(expr, x)


	variant_args1 = ((3, 5,),  ("nice",), (15.234,), None if options.get('constants') else ())
	variant_args2 = ((0, 10,), ("bad",),  (3.1415,), None if options.get('constants') else ())

	expr = "C(*args1) == C(*args1)"
	for (C, args1) in b.zip(Thing._constructors, variant_args1):
		if args1 is not None:
			res  = eval(expr)
			assert res, '{!r} failed for {!r}'.format(expr, (C, args1))


	expr = "C(*args1) != C(*args2)"
	for (C, args1, args2) in b.zip(Thing._constructors, variant_args1, variant_args2):
		if args1 is not None and len(args1) >= 1:
			res  = eval(expr)
			assert res, '{!r} failed for {!r}'.format(expr, (C, args1, args2))

	# doesn't work if the variants have different type specs
	# args = (3,); C1 = Thing.Bar; C2 = Thing.Zap
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
	assert len(Thing._variant_id_fields) == len(variant_args2), \
		'{} !~= {}'.format(Thing._variant_id_fields, variant_args2)
	variant_kwargs2 = [
		OrderedDict(b.zip(fields, args2)) if args2 is not None else None
		for (fields, args2) in b.zip(Thing._variant_id_fields, variant_args2)
	]
	
	# import inspect
	# def eval(s):
	# 	print('eval({!r})'.format(s))
	# 	frame = inspect.currentframe().f_back
	# 	globs, locs = frame.f_globals, frame.f_locals
	# 	return b.eval(s, globs, locs)

	left  = 'x._constructor(**kwargs2)'
	right = 'x._replace(**kwargs2)'
	for (x, kwargs2) in b.zip(values, variant_kwargs2):
		if kwargs2 is not None:
			vleft  = eval(left)
			vright = eval(right)
			res = vleft == vright
			assert res, \
				'\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'\
					.format(left, vleft, right, vright, (x, kwargs2),)

	# eval = b.eval

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
	for x_ in values:
		vleft  = eval(left)
		vright = eval(right)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, x_,)

	left = 'set( x.as_dict().items() )'
	right = 'set([("variant", x._variant)]) | set([(field, getattr(x, field)) for field in fields])'
	for (x, fields) in b.zip(values, Thing._variant_id_fields):
		vleft  = eval('lambda x, fields: '+ left )(x, fields)
		vright = eval('lambda x, fields: '+ right)(x, fields)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, (x, fields),)


	left  = 'x.as_tuple()'
	right = '(x.variant,) + tuple(getattr(x, field) for field in fields)'
	for (x, fields) in b.zip(values, Thing._variant_id_fields):
		vleft  = eval('lambda x, fields: '+left)(x, fields)
		vright = eval('lambda x, fields: '+right)(x, fields)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, (x, fields),)


	left  = 'set( x.as_dict().items() )'
	right = 'set( zip(("variant",)+fields, x.as_tuple()) )'
	for (x, fields) in b.zip(values, Thing._variant_id_fields):
		vleft  = eval(left)
		vright = eval(right)
		res = vleft == vright
		assert res, '\n{!r}\n  -> {!r}\n and \n{!r}\n  -> {!r}\n failed equality test on {!r}'.format(left, vleft, right, vright, (x, fields),)


	expr = 'x.values() == x.as_tuple()[1:] == x.__getstate__()[1:]'
	for x in values:
		res = eval(expr)
		assert res, '{!r} failed for {!r}'.format(expr, x)

	body = [
		'x_state = x.__getstate__()',
		'new_x = Thing.__new__(Thing)',
		'new_x.__setstate__(x_state)',
		'new_x == x'
	]
	for x in values:
		body[-1] = 'res = '+body[-1]
		exec('\n'.join(body))
		assert res, '{!r} failed for {!r}'.format(body, x)


	try: res = bar.replace(blah_blah_blah=5)
	except AttributeError as e: res = e
	# print("bad replace 1:", bar, repr(res))
	assert isinstance(res, AttributeError), repr(res)

	try: res = bar.replace(_0=5)
	except TypeError as e: res = e
	# print("bad replace 2:", bar, repr(res))
	assert isinstance(res, TypeError), repr(res)

	try: res = bar.replace(_variant_id=5)
	except TypeError as e: res = e
	# print("bad replace 2:", bar, repr(res))
	assert isinstance(res, TypeError), repr(res)

	foo_ = Thing.Foo(3, 5)
	Thing._variant_id.__set__(foo_, 15)
	try:
		res = repr(foo_)
	except RuntimeError as e:
		res = e
	# print("repr of bad variant:", repr(res))
	assert isinstance(res, RuntimeError), repr(res)

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


def is_subdict(a: dict, b: dict) -> bool:
	 return all(
	 	k in b  and  b[k] == v
		for k, v in a.items()
	)



if __name__ == '__main__':
	print('Running tests')
	print()
	for user_options in (dict(), dict(constants=True), dict(constants=False)):
		for sumtype in (st.sumtype, st.future.sumtype):
			for make_thing in (make_thing_classdef_old, make_thing_classdef_new, make_thing_call):
				Thing = make_thing(sumtype, user_options)
				err_msg = '{} ~> <Thing{}>'.format(
					sumtype.__module__+'.'+sumtype.__name__,
					options_repr(user_options)
				)
				try:
					test_thing(Thing, user_options)
				except Exception as e:
					e2 = e.__class__(err_msg)
					raise e2 from e
				else:
					print(
						'All {} ~> <Thing{}> tests OK'.format(
							sumtype.__module__+'.'+sumtype.__name__,
							options_repr(user_options)
						)
					)
					# print(Thing._options )
			print()

	for sumtype in (st.sumtype, st.future.sumtype):
		for Void in (make_void_classdef(sumtype), make_void_call(sumtype)):
			try:
				test_void(Void)
			except Exception as e:
				e2 = e.__class__(
					'{} ~> <Void>'.format(
						sumtype.__module__+'.'+sumtype.__name__,
					)
				)
				raise e2 from e
			else:
				print(
					'All {} ~> <Void> tests OK'.format(
						sumtype.__module__+'.'+sumtype.__name__,
					)
				)

	print()

	test_make_from_bad_spec()

