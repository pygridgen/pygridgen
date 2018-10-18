from pygridgen import utils

from pygridgen.tests import raises
import pytest


@pytest.mark.parametrize(('obj', 'error'), [
    ('mod', None),
    (None, RuntimeError)
])
def test_requires(obj, error):
    with raises(error):

        @utils.requires(obj, 'obj')
        def foo():
            return 4

        assert foo() == 4
