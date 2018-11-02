from functools import wraps

import numpy


def requires(module, modulename):
    def outer_wrapper(function):
        @wraps(function)
        def inner_wrapper(*args, **kwargs):
            if module is None:
                raise RuntimeError(
                    "{} required for `{}`".format(modulename, function.__name__)
                )
            else:
                return function(*args, **kwargs)
        return inner_wrapper
    return outer_wrapper


def seed(func):
    """ Decorator to seed the RNG before any function. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        numpy.random.seed(0)
        return func(*args, **kwargs)
    return wrapper
