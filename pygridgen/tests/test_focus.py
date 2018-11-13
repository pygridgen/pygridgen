import numpy

import numpy.testing as nptest
import pytest
from pygridgen.tests import raises

import pygridgen


def base_focus_point(axis):
    pos = 0.25
    factor = 3
    reach = 0.2
    focus = pygridgen.grid._FocusPoint(pos, axis, factor, reach)
    return focus


@pytest.fixture
def xy():
    _x = numpy.linspace(0, 1, num=10)
    _y = numpy.linspace(0, 1, num=10)
    return numpy.meshgrid(_x, _y)


def known_focused_simple(axis, xy):
    x, y = xy
    focused = numpy.array([
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.],
        [0., 0.106, 0.17, 0.222, 0.307, 0.43, 0.569, 0.712, 0.856, 1.]
    ])

    if axis == 'x':
        return focused, y
    elif axis == 'y':
        return x, focused.T


@pytest.fixture
def full_focus():
    focus = pygridgen.Focus()

    focus.add_focus(0.25, 'x', factor=3, extent=0.1)
    focus.add_focus(0.75, 'x', factor=2, extent=0.2)
    focus.add_focus(0.50, 'y', factor=2, extent=0.3)

    return focus


def test_spec_bad_axis():
    with raises(ValueError):
        pygridgen.grid._FocusPoint(0.1, 'xjunk', 2, 0.25)


@pytest.mark.parametrize('axis', ['x', 'y'])
@pytest.mark.parametrize(('x', 'y'), [
    ([1.1], [0.5]),
    ([-0.1], [0.5]),
    ([0.5], [1.1]),
    ([0.5], [-0.1])
])
def test_call_bad(axis, x, y):
    fp = base_focus_point(axis)
    with raises(ValueError):
        fp(x, y)


@pytest.mark.parametrize('axis', ['x', 'y'])
@pytest.mark.parametrize(('attr', 'known'), [
    ('pos', 0.25),
    ('factor', 3),
    ('extent', 0.20),
])
def test_pos(axis, attr, known):
    fp = base_focus_point(axis)
    assert getattr(fp, attr) == known


@pytest.mark.parametrize('axis', ['x', 'y'])
@pytest.mark.parametrize('index', [0, 1])
def test_focused_direct(xy, axis, index):
    focus_point = base_focus_point(axis)
    result = focus_point(*xy)
    known = known_focused_simple(axis, xy)

    nptest.assert_array_almost_equal(
        result[index],
        known[index],
        decimal=3
    )


def test__focuspoints(full_focus):
    assert isinstance(full_focus._focuspoints, list)
    assert len(full_focus._focuspoints) == 3


def test_add_focus_x(full_focus):
    full_focus.add_focus(0.99, 'x', factor=3, extent=0.1)
    assert len(full_focus._focuspoints), 4
    assert isinstance(full_focus._focuspoints[-1], pygridgen.grid._FocusPoint)
    assert full_focus._focuspoints[-1].pos == 0.99
    assert full_focus._focuspoints[-1].axis == 'x'


def test_add_focus_y(full_focus):
    full_focus.add_focus(0.99, 'y', factor=3, extent=0.1)
    assert len(full_focus._focuspoints), 4
    assert isinstance(full_focus._focuspoints[-1], pygridgen.grid._FocusPoint)
    assert full_focus._focuspoints[-1].pos == 0.99
    assert full_focus._focuspoints[-1].axis == 'y'


def test_full_focus_called(full_focus, xy):
    xf, yf = full_focus(*xy)

    known_focused_x = numpy.array([
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.],
        [0., 0.148, 0.248, 0.313, 0.446, 0.59, 0.711, 0.796, 0.881, 1.]
    ])

    known_focused_y = numpy.array([
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0.142, 0.142, 0.142, 0.142, 0.142, 0.142, 0.142, 0.142, 0.142, 0.142],
        [0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27, 0.27],
        [0.377, 0.377, 0.377, 0.377, 0.377, 0.377, 0.377, 0.377, 0.377, 0.377],
        [0.462, 0.462, 0.462, 0.462, 0.462, 0.462, 0.462, 0.462, 0.462, 0.462],
        [0.538, 0.538, 0.538, 0.538, 0.538, 0.538, 0.538, 0.538, 0.538, 0.538],
        [0.623, 0.623, 0.623, 0.623, 0.623, 0.623, 0.623, 0.623, 0.623, 0.623],
        [0.73, 0.73, 0.73, 0.73, 0.73, 0.73, 0.73, 0.73, 0.73, 0.73],
        [0.858, 0.858, 0.858, 0.858, 0.858, 0.858, 0.858, 0.858, 0.858, 0.858],
        [1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]
    ])

    nptest.assert_array_almost_equal(xf, known_focused_x, decimal=3)
    nptest.assert_array_almost_equal(yf, known_focused_y, decimal=3)


def test_focuspoint_to_dict():
    fp = pygridgen.grid._FocusPoint(0.25, 'x', 4, 0.5)
    fp2 = pygridgen.grid._FocusPoint(**fp.to_dict())
    assert fp.to_dict() == {'pos': 0.25, 'axis': 'x',
                            'factor': 4, 'extent': 0.5}
    assert fp.to_dict() == fp2.to_dict()


def test_focus_to_from_spec():
    fpx = pygridgen.grid._FocusPoint(0.25, 'x', 4, 0.5)
    fpy = pygridgen.grid._FocusPoint(0.33, 'y', 0.1, 0.2)
    f1 = pygridgen.grid.Focus(fpx, fpy)

    # Check that the spec dictionary returns desired results
    assert f1.to_spec() == [
        {'pos': 0.25, 'axis': 'x', 'factor': 4, 'extent': 0.5},
        {'pos': 0.33, 'axis': 'y', 'factor': 0.1, 'extent': 0.2}
    ]

    f2 = pygridgen.grid.Focus.from_spec(f1.to_spec())

    # Check that the spec dictionary returns desired results of the orignal
    # focus and the focus generated from .to_spec()
    # First check the keys are in order and then check the values
    for dict1, dict2 in zip(f1.to_spec(), f2.to_spec()):
        numpy.testing.assert_equal(dict1.keys(), dict2.keys())
        for value1, value2 in zip(dict1.values(), dict2.values()):
            assert value1 == value2
