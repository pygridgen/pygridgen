from pkg_resources import resource_filename
from contextlib import contextmanager

from pygridgen.utils import requires

try:
    import pytest
except ImportError:  # pragma: no cover
    pytest = None


@requires(pytest, 'pytest')
def raises(error):
    """Wrapper around pytest.raises to support None."""
    if error:
        return pytest.raises(error)
    else:
        @contextmanager
        def not_raises():
            try:
                yield
            except Exception as e:  # pragma: no cover
                raise e
        return not_raises()


@requires(pytest, 'pytest')
def test(*args):
    options = [resource_filename('pygridgen', '')]
    options.extend(list(args))
    return pytest.main(options)


@requires(pytest, 'pytest')
def teststrict(*args):
    options = ['--pep8', '--doctest-modules'] + list(args)
    options = list(set(options))
    return test(*options)
