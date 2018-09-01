# inspired by an older `sumtypes` module (https://pypi.org/project/sumtypes/)
# which let you define functions like this:
#
# @match(Thing)
# class get_number:
#     def Foo(x, y): return x
#     def Bar(s):    return len(s)
#     ...


# allow this module to import the whole package
if __name__ == '__main__':
    import pathlib
    import sys
    here = pathlib.Path(__file__).resolve()
    parent_package_location = here.parents[2]
    print('Adding', str(parent_package_location), 'to sys.path to enable import\n')
    sys.path.append(str(parent_package_location))

from sumtype import sumtype




import inspect

_NO_VALUE = object()


class match:
    """ A hack to get pseudo-pattern matching through a with-statement
    It's here just for fun, I wouldnt't recommend actually using it.
    Usage:

    >>> class Thing(sumtype):
    ...    def Foo(x: int, y: int): ...
    ...    def Bar(y: str): ...
    ...    def Zip(hey: str): ...
    ...    def Bop(): ...
    ...
    >>> 
    >>> def stuff(val: Thing, boop):
    ...     with match(val):
    ...         def Foo(x, y): z=15; print('F', x+y+z)
    ...         def Bar(y):    print('B', len(y))
    ...         def _():       print('_', boop)
    ... 
    >>> stuff(Thing.Foo(10, 11), -1)
    F 36
    >>> stuff(Thing.Bar('beep'), -1)
    B 4
    >>> stuff(Thing.Bop(), -1)
    _ -1

    """
    def __init__(m, val):
        m.val = val
        outer_locals = inspect.currentframe().f_back.f_locals
        # print('before:')
        # pprint(outer_locals)
        m.prev_val_of_case    = outer_locals.get(val.variant, _NO_VALUE)
        m.prev_val_of_default = outer_locals.get('_',         _NO_VALUE)

    def __enter__(m):
        return m.val

    def __exit__(m, exc_type, exc_val, exc_tb):
        # try find a newly defined matching case function in the outer locals 
        val = m.val
        outer_locals = inspect.currentframe().f_back.f_locals
        # print('after:')
        # pprint(outer_locals)
        current_val_of_case    = outer_locals.get(val.variant, _NO_VALUE)
        if current_val_of_case is not m.prev_val_of_case:
            assert current_val_of_case is not _NO_VALUE
            # a matching case was defined in the body
            res = current_val_of_case(*val._values())
        else:
            # no matching case was defined in the body
            current_val_of_default = outer_locals.get('_', _NO_VALUE)
            if current_val_of_default is not m.prev_val_of_default:
                # a default case was defined in the body
                res = current_val_of_default()
            else:
                # no default case was defined in the body
                raise RuntimeError("match: No pattern for {}".format(val))


if __name__ == '__main__':
    class Thing(sumtype):
        def Foo(x: int, y: int): ...
        def Bar(y: str): ...
        def Zip(hey: str): ...
        def Bop(): ...


    def stuff(val: Thing, boop):
        with match(val):
            def Foo(x, y): z=15; print('F', x+y+z)
            def Bar(y):    print('B', len(y))
            def _():       print('_', boop)

    stuff(Thing.Foo(10, 11), -1)
    stuff(Thing.Bar('beep'), -1)
    stuff(Thing.Bop(), -1)