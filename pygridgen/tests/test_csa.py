import sys

import numpy
from matplotlib import pyplot
from matplotlib.collections import QuadMesh, PathCollection
from matplotlib.colorbar import Colorbar

import pytest
import numpy.testing as nptest

from pygridgen import utils
from pygridgen.tests import raises

from pygridgen import csa


@pytest.fixture
@utils.seed
def base_csa():
    N = 37
    xin = numpy.random.randn(N)
    yin = numpy.random.randn(N)
    zin = numpy.sin(xin**2 + yin**2) / (xin**2 + yin**2)

    return csa.CSA(xin, yin, zin)


@pytest.fixture
def xy_out():
    return numpy.mgrid[-2:2:15, -2:2:15j]


def test_CSA_caller(base_csa, xy_out):
    result = base_csa(*xy_out)
    expected = numpy.ma.MaskedArray(
        data=[[numpy.nan, -0.72197, -0.56595, -0.44383, -0.33518, -0.21754,
               -0.05890,  0.08821,  0.10263,  0.02336, -0.07648, -0.20178,
               -0.38014, -0.56006, -0.71751]],
        mask=[[True, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False]]
    )
    nptest.assert_array_almost_equal(result, expected, decimal=4)


@pytest.mark.skipif(sys.version_info < (3, 5), reason="requires python >= 3.5")
def test_CSA_plotter(base_csa, xy_out):
    fig, ax = pyplot.subplots()
    fig2, artists = base_csa.plot(*xy_out, ax=ax, mesh_opts=dict(vmin=-1, vmax=1),
                                  scatter_opts=dict(vmin=-1, vmax=1, edgecolors='none'))
    assert fig == fig2
    assert isinstance(artists, dict)
    assert sorted(list(artists.keys())) == ['colorbar', 'points', 'surface']
    assert isinstance(artists['surface'], QuadMesh)
    assert isinstance(artists['points'], PathCollection)
    assert isinstance(artists['colorbar'], Colorbar)


def test_CSA_zin_property(base_csa, xy_out):
    base_csa.zin = numpy.cos(base_csa.xin + base_csa.yin**2)
    result = base_csa(*xy_out)
    expected = numpy.ma.MaskedArray(
        data=[[numpy.nan, -0.81999, -0.68109, -0.57472, -0.47748, -0.3654 ,
               -0.18464, -0.01045, -0.01918, -0.17405, -0.3808 , -0.60488,
               -0.84598, -1.06711, -1.26715]],
        mask=[[True, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False]]
    )
    nptest.assert_array_almost_equal(result, expected, decimal=4)
