# allow this module to import the whole package
if __name__ == '__main__':

	import pathlib
	import sys
	here = pathlib.Path(__file__).resolve()
	parent_package_location = here.parents[2]
	print('Adding', str(parent_package_location), 'to sys.path to enable import\n')
	sys.path.append(str(parent_package_location))


from typing import Tuple
from sumtype import sumtype

import hypothesis
from hypothesis import (
	given, infer,
)
from hypothesis.strategies import (
	builds, just, one_of, from_type,
)

class Thing(sumtype):
    def Foo(x: int, y: int): ...
    def Bar(y: str, hmm: Tuple[str, str]): ...
    def Zap(): ...


def unwrap_constructor(ctr):
	try:
		return ctr.__func__.__wrapped__ # unwrap @classmethod and @typechecked
	except AttributeError:
		return ctr.__func__ # 0-argument constructors aren't wrapped with @typechecked


def sumtype_strategy(Class):
	return one_of(builds(unwrap_constructor(ctr), _cls=just(Thing)) for ctr in Class._constructors)



Thing_strategy = sumtype_strategy(Thing)
hypothesis.strategies.register_type_strategy(Thing, Thing_strategy)

# for _ in range(40):
# 	val = Thing_strategy.example()
# 	s = repr(val).encode('ascii', errors='replace').decode('ascii') # printing unicode chars is not great on Windows
# 	print(s)


@given(x=infer)
def test_as_tuple_from_tuple_identity(x: Thing):
	assert x == x.__class__.from_tuple(x.as_tuple())


if __name__ == '__main__':
	test_as_tuple_from_tuple_identity()
