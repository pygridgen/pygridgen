from pkg_resources import resource_filename

import pygridgen
from .utils import requires

try:
    import pytest
except ImportError:
    pytest = None


@requires(pytest, 'pytest')
def test(*args):
    options = [resource_filename('pygridgen', '')]
    options.extend(list(args))
    return pytest.main(options)


@requires(pytest, 'pytest')
def teststrict(*args):
    options = [
        resource_filename('pygridgen', ''),
        '--pep8', '--mpl', '--doctest-modules',
        *list(args)
    ]
    options = list(set(options))
    return pytest.main(options)
    return pytest.main(options)
