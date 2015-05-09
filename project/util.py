"""Assorted Python utilities which aren't specific to the project"""

from functools import wraps
from timeit import default_timer


def timed(f):
    """Decorator to measure the runtime of a function and print it to
    stdout."""
    if hasattr(f, 'func_name'):
        name = f.func_name
    elif hasattr(f, 'im_func'):
        name = f.im_func.func_name
    else:
        name = '<unknown>'

    @wraps(f)
    def inner(*args, **kwargs):
        start = default_timer()
        rv = f(*args, **kwargs)
        taken = default_timer() - start
        print("Call to {} took {}s".format(name, taken))
        return rv

    return inner
