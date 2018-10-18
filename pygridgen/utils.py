from contextlib import contextmanager
from functools import wraps

try:
    import pytest
except ImportError:  # pragma: no cover
    pytest = None


__all__ = [
    'requires',
    'raises',
]


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
