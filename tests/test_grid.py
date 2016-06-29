import numpy
import matplotlib.pyplot as plt

try:
    import pyproj
except ImportError:
    from mpl_toolkits.basemap import pyproj

import numpy.testing as nptest
import nose.tools as nt

import pygridgen


class _gridMixin(object):
    _options = {
        'ul_idx': 0,
        'focus': None,
        'proj': None,
        'nnodes': 14,
        'precision': 1e-12,
        'nppe': 3,
        'newton': True,
        'thin': True,
        'checksimplepoly': True,
        'verbose': False,
        'autogen': True
    }

    @nt.nottest
    def make_grid(self):
        grid = pygridgen.Gridgen(self.x, self.y, self.beta, self.shape,
                                 **self.options)

        return grid

    def test_ny(self):
        nt.assert_true(hasattr(self.grid, 'ny'))
        nt.assert_equal(self.grid.ny, self.shape[0])

    def test_nx(self):
        nt.assert_true(hasattr(self.grid, 'nx'))
        nt.assert_equal(self.grid.nx, self.shape[1])

    def test_nnodes(self):
        nt.assert_true(hasattr(self.grid, 'nnodes'))
        nt.assert_equal(self.grid.nnodes, self.options['nnodes'])

    def test_precision(self):
        nt.assert_true(hasattr(self.grid, 'precision'))
        nt.assert_equal(self.grid.precision, self.options['precision'])

    def test_nppe(self):
        nt.assert_true(hasattr(self.grid, 'nppe'))
        nt.assert_equal(self.grid.nppe, self.options['nppe'])

    def test_newton(self):
        nt.assert_true(hasattr(self.grid, 'newton'))
        nt.assert_equal(self.grid.newton, self.options['newton'])

    def test_thin(self):
        nt.assert_true(hasattr(self.grid, 'thin'))
        nt.assert_equal(self.grid.thin, self.options['thin'])

    def test_checksimplepoly(self):
        nt.assert_true(hasattr(self.grid, 'checksimplepoly'))
        nt.assert_equal(self.grid.checksimplepoly, self.options['checksimplepoly'])

    def test_verbose(self):
        nt.assert_true(hasattr(self.grid, 'verbose'))
        nt.assert_equal(self.grid.verbose, self.options['verbose'])

    def test_x(self):
        nt.assert_true(hasattr(self.grid, 'x'))
        nptest.assert_array_almost_equal(self.grid.x, self.known_x, decimal=2)

    def test_y(self):
        nt.assert_true(hasattr(self.grid, 'y'))
        nptest.assert_array_almost_equal(self.grid.y, self.known_y, decimal=2)

    def test_x_vert(self):
        nt.assert_true(hasattr(self.grid, 'x_vert'))
        nptest.assert_array_almost_equal(self.grid.x_vert, self.known_x,
                                         decimal=2)

    def test_y_vert(self):
        nt.assert_true(hasattr(self.grid, 'y_vert'))
        nptest.assert_array_almost_equal(self.grid.y_vert, self.known_y,
                                         decimal=2)

    def test_x_psi(self):
        nt.assert_true(hasattr(self.grid, 'x_psi'))
        nptest.assert_array_almost_equal(self.grid.x_psi, self.known_x_psi,
                                         decimal=2)

    def test_y_psi(self):
        nt.assert_true(hasattr(self.grid, 'y_psi'))
        nptest.assert_array_almost_equal(self.grid.y_psi, self.known_y_psi,
                                         decimal=2)

    def test_x_rho(self):
        nt.assert_true(hasattr(self.grid, 'x_rho'))
        nptest.assert_array_almost_equal(self.grid.x_rho, self.known_x_rho,
                                         decimal=2)

    def test_y_rho(self):
        nt.assert_true(hasattr(self.grid, 'y_rho'))
        nptest.assert_array_almost_equal(self.grid.y_rho, self.known_y_rho,
                                         decimal=2)

    def test_x_u(self):
        nt.assert_true(hasattr(self.grid, 'x_u'))
        nptest.assert_array_almost_equal(self.grid.x_u, self.known_x_u,
                                         decimal=2)

    def test_y_u(self):
        nt.assert_true(hasattr(self.grid, 'y_u'))
        nptest.assert_array_almost_equal(self.grid.y_u, self.known_y_u,
                                         decimal=2)

    def test_x_v(self):
        nt.assert_true(hasattr(self.grid, 'x_v'))
        nptest.assert_array_almost_equal(self.grid.x_v, self.known_x_v,
                                         decimal=2)

    def test_y_v(self):
        nt.assert_true(hasattr(self.grid, 'y_v'))
        nptest.assert_array_almost_equal(self.grid.y_v, self.known_y_v,
                                         decimal=2)

    def test_xbry(self):
        nt.assert_true(hasattr(self.grid, 'xbry'))
        nptest.assert_array_almost_equal(self.grid.xbry, self.x,
                                         decimal=2)

    def test_ybry(self):
        nt.assert_true(hasattr(self.grid, 'ybry'))
        nptest.assert_array_almost_equal(self.grid.ybry, self.y,
                                         decimal=2)


class test_Grid_basic(_gridMixin):
    def setup(self):
        self.options = self._options.copy()
        self.x = [0.0, 1.0, 2.0, 1.0, 0.0]
        self.y = [0.0, 0.0, 0.5, 1.0, 1.0]
        self.beta = [1.0, 1.0, 0.0, 1.0, 1.0]
        self.shape = (10, 5)
        self.island = numpy.array([(5, 10), (10, 10), (10, 5), (5, 5)]) / 10.

        self.grid = self.make_grid()

        self.known_x = numpy.array([
            [ 1.  ,  1.12,  2.  ,  1.12,  1.  ],
            [ 0.96,  1.03,  1.17,  1.03,  0.96],
            [ 0.87,  0.91,  0.96,  0.91,  0.87],
            [ 0.77,  0.78,  0.8 ,  0.78,  0.77],
            [ 0.65,  0.65,  0.66,  0.65,  0.65],
            [ 0.52,  0.52,  0.53,  0.52,  0.52],
            [ 0.39,  0.39,  0.39,  0.39,  0.39],
            [ 0.26,  0.26,  0.26,  0.26,  0.26],
            [ 0.13,  0.13,  0.13,  0.13,  0.13],
            [ 0.  ,  0.  ,  0.  ,  0.  ,  0.  ]
        ])

        self.known_y = numpy.array([
            [ 0.  ,  0.06,  0.5 ,  0.94,  1.  ],
            [-0.  ,  0.16,  0.5 ,  0.84,  1.  ],
            [-0.  ,  0.21,  0.5 ,  0.79,  1.  ],
            [-0.  ,  0.23,  0.5 ,  0.77,  1.  ],
            [-0.  ,  0.24,  0.5 ,  0.76,  1.  ],
            [-0.  ,  0.25,  0.5 ,  0.75,  1.  ],
            [-0.  ,  0.25,  0.5 ,  0.75,  1.  ],
            [-0.  ,  0.25,  0.5 ,  0.75,  1.  ],
            [-0.  ,  0.25,  0.5 ,  0.75,  1.  ],
            [-0.  ,  0.25,  0.5 ,  0.75,  1.  ]
        ])

        self.known_x_psi = numpy.array([
            [ 1.03,  1.17,  1.03],
            [ 0.91,  0.96,  0.91],
            [ 0.78,  0.8 ,  0.78],
            [ 0.65,  0.66,  0.65],
            [ 0.52,  0.53,  0.52],
            [ 0.39,  0.39,  0.39],
            [ 0.26,  0.26,  0.26],
            [ 0.13,  0.13,  0.13]
        ])

        self.known_y_psi = numpy.array([
            [ 0.16,  0.5 ,  0.84],
            [ 0.21,  0.5 ,  0.79],
            [ 0.23,  0.5 ,  0.77],
            [ 0.24,  0.5 ,  0.76],
            [ 0.25,  0.5 ,  0.75],
            [ 0.25,  0.5 ,  0.75],
            [ 0.25,  0.5 ,  0.75],
            [ 0.25,  0.5 ,  0.75]
        ])

        self.known_x_rho = numpy.array([
            [ 1.03,  1.33,  1.33,  1.03],
            [ 0.94,  1.02,  1.02,  0.94],
            [ 0.83,  0.87,  0.87,  0.83],
            [ 0.71,  0.73,  0.73,  0.71],
            [ 0.59,  0.59,  0.59,  0.59],
            [ 0.46,  0.46,  0.46,  0.46],
            [ 0.33,  0.33,  0.33,  0.33],
            [ 0.2 ,  0.2 ,  0.2 ,  0.2 ],
            [ 0.07,  0.07,  0.07,  0.07]
        ])

        self.known_y_rho = numpy.array([
            [ 0.05,  0.3 ,  0.7 ,  0.95],
            [ 0.09,  0.34,  0.66,  0.91],
            [ 0.11,  0.36,  0.64,  0.89],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88]
        ])

        self.known_x_u = numpy.array([
            [ 1.08,  1.58,  1.08],
            [ 0.97,  1.06,  0.97],
            [ 0.85,  0.88,  0.85],
            [ 0.72,  0.73,  0.72],
            [ 0.59,  0.59,  0.59],
            [ 0.46,  0.46,  0.46],
            [ 0.33,  0.33,  0.33],
            [ 0.2 ,  0.2 ,  0.2 ],
            [ 0.07,  0.07,  0.07]
        ])

        self.known_x_v = numpy.array([
            [ 1.  ,  1.1 ,  1.1 ,  1.  ],
            [ 0.89,  0.94,  0.94,  0.89],
            [ 0.78,  0.79,  0.79,  0.78],
            [ 0.65,  0.66,  0.66,  0.65],
            [ 0.52,  0.53,  0.53,  0.52],
            [ 0.39,  0.39,  0.39,  0.39],
            [ 0.26,  0.26,  0.26,  0.26],
            [ 0.13,  0.13,  0.13,  0.13]
        ])

        self.known_y_u = numpy.array([
            [ 0.11,  0.5 ,  0.89],
            [ 0.18,  0.5 ,  0.82],
            [ 0.22,  0.5 ,  0.78],
            [ 0.24,  0.5 ,  0.76],
            [ 0.24,  0.5 ,  0.76],
            [ 0.25,  0.5 ,  0.75],
            [ 0.25,  0.5 ,  0.75],
            [ 0.25,  0.5 ,  0.75],
            [ 0.25,  0.5 ,  0.75]
        ])

        self.known_y_v = numpy.array([
            [ 0.08,  0.33,  0.67,  0.92],
            [ 0.1 ,  0.35,  0.65,  0.9 ],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88],
            [ 0.12,  0.37,  0.63,  0.88]
        ])

        self.known_mask_rho = numpy.array([
            [ 1.,  1.,  1.,  1.],
            [ 1.,  1.,  1.,  0.],
            [ 1.,  1.,  0.,  0.],
            [ 1.,  1.,  0.,  0.],
            [ 1.,  1.,  0.,  0.],
            [ 1.,  1.,  1.,  1.],
            [ 1.,  1.,  1.,  1.],
            [ 1.,  1.,  1.,  1.],
            [ 1.,  1.,  1.,  1.]
        ])

    def test_mask_poylgon(self):
        nt.assert_true(hasattr(self.grid, 'mask_polygon'))
        self.grid.mask_polygon(self.island)
        nptest.assert_array_almost_equal(
            self.known_mask_rho, self.grid.mask_rho
        )


class test_Grid_with_focus(_gridMixin):
    def setup(self):
        self.options = self._options.copy()
        self.x = [0.0, 1.0, 2.0, 1.0, 0.0]
        self.y = [0.0, 0.0, 0.5, 1.0, 1.0]
        self.beta = [1.0, 1.0, 0.0, 1.0, 1.0]
        self.shape = (9, 9)

        focus = pygridgen.Focus()
        focus.add_focus(0.50, 'x', factor=2.0, extent=3.0)
        focus.add_focus(0.75, 'y', factor=0.5, extent=2.0)
        self.options.update({'ul_idx': 0, 'focus': focus})

        self.grid = self.make_grid()

        self.known_x = numpy.array([
            [ 1.  ,  1.04,  1.12,  1.27,  2.  ,  1.27,  1.12,  1.04,  1.  ],
            [ 0.95,  0.97,  1.02,  1.1 ,  1.15,  1.1 ,  1.02,  0.97,  0.95],
            [ 0.86,  0.87,  0.89,  0.92,  0.93,  0.92,  0.89,  0.87,  0.86],
            [ 0.73,  0.74,  0.75,  0.76,  0.76,  0.76,  0.75,  0.74,  0.73],
            [ 0.59,  0.59,  0.6 ,  0.6 ,  0.6 ,  0.6 ,  0.6 ,  0.59,  0.59],
            [ 0.45,  0.45,  0.45,  0.45,  0.45,  0.45,  0.45,  0.45,  0.45],
            [ 0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ],
            [ 0.15,  0.15,  0.15,  0.15,  0.15,  0.15,  0.15,  0.15,  0.15],
            [ 0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.  ]
        ])

        self.known_y = numpy.array([
            [ 0.  ,  0.02,  0.06,  0.14,  0.5 ,  0.86,  0.94,  0.98,  1.  ],
            [-0.  ,  0.07,  0.16,  0.3 ,  0.5 ,  0.7 ,  0.84,  0.93,  1.  ],
            [-0.  ,  0.1 ,  0.21,  0.35,  0.5 ,  0.65,  0.79,  0.9 ,  1.  ],
            [-0.  ,  0.12,  0.24,  0.37,  0.5 ,  0.63,  0.76,  0.88,  1.  ],
            [-0.  ,  0.12,  0.25,  0.37,  0.5 ,  0.63,  0.75,  0.88,  1.  ],
            [-0.  ,  0.12,  0.25,  0.37,  0.5 ,  0.63,  0.75,  0.88,  1.  ],
            [-0.  ,  0.13,  0.25,  0.38,  0.5 ,  0.62,  0.75,  0.87,  1.  ],
            [-0.  ,  0.13,  0.25,  0.38,  0.5 ,  0.62,  0.75,  0.87,  1.  ],
            [-0.  ,  0.13,  0.25,  0.38,  0.5 ,  0.62,  0.75,  0.87,  1.  ]
        ])

        self.known_x_psi = numpy.array([
            [ 0.97,  1.02,  1.1 ,  1.15,  1.1 ,  1.02,  0.97],
            [ 0.87,  0.89,  0.92,  0.93,  0.92,  0.89,  0.87],
            [ 0.74,  0.75,  0.76,  0.76,  0.76,  0.75,  0.74],
            [ 0.59,  0.6 ,  0.6 ,  0.6 ,  0.6 ,  0.6 ,  0.59],
            [ 0.45,  0.45,  0.45,  0.45,  0.45,  0.45,  0.45],
            [ 0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ],
            [ 0.15,  0.15,  0.15,  0.15,  0.15,  0.15,  0.15]
        ])

        self.known_y_psi = numpy.array([
            [ 0.07,  0.16,  0.3 ,  0.5 ,  0.7 ,  0.84,  0.93],
            [ 0.1 ,  0.21,  0.35,  0.5 ,  0.65,  0.79,  0.9 ],
            [ 0.12,  0.24,  0.37,  0.5 ,  0.63,  0.76,  0.88],
            [ 0.12,  0.25,  0.37,  0.5 ,  0.63,  0.75,  0.88],
            [ 0.12,  0.25,  0.37,  0.5 ,  0.63,  0.75,  0.88],
            [ 0.13,  0.25,  0.38,  0.5 ,  0.62,  0.75,  0.87],
            [ 0.13,  0.25,  0.38,  0.5 ,  0.62,  0.75,  0.87]
        ])

        self.known_x_rho = numpy.array([
            [ 0.99,  1.04,  1.13,  1.38,  1.38,  1.13,  1.04,  0.99],
            [ 0.91,  0.94,  0.98,  1.02,  1.02,  0.98,  0.94,  0.91],
            [ 0.8 ,  0.81,  0.83,  0.84,  0.84,  0.83,  0.81,  0.8 ],
            [ 0.66,  0.67,  0.68,  0.68,  0.68,  0.68,  0.67,  0.66],
            [ 0.52,  0.52,  0.52,  0.53,  0.53,  0.52,  0.52,  0.52],
            [ 0.37,  0.37,  0.37,  0.37,  0.37,  0.37,  0.37,  0.37],
            [ 0.22,  0.22,  0.22,  0.22,  0.22,  0.22,  0.22,  0.22],
            [ 0.07,  0.07,  0.07,  0.07,  0.07,  0.07,  0.07,  0.07]
        ])

        self.known_y_rho = numpy.array([
            [ 0.02,  0.08,  0.16,  0.36,  0.64,  0.84,  0.92,  0.98],
            [ 0.04,  0.14,  0.26,  0.41,  0.59,  0.74,  0.86,  0.96],
            [ 0.05,  0.17,  0.29,  0.43,  0.57,  0.71,  0.83,  0.95],
            [ 0.06,  0.18,  0.3 ,  0.43,  0.57,  0.7 ,  0.82,  0.94],
            [ 0.06,  0.19,  0.31,  0.44,  0.56,  0.69,  0.81,  0.94],
            [ 0.06,  0.19,  0.31,  0.44,  0.56,  0.69,  0.81,  0.94],
            [ 0.06,  0.19,  0.31,  0.44,  0.56,  0.69,  0.81,  0.94],
            [ 0.06,  0.19,  0.31,  0.44,  0.56,  0.69,  0.81,  0.94]
        ])

        self.known_x_u = numpy.array([
            [ 1.  ,  1.07,  1.19,  1.57,  1.19,  1.07,  1.  ],
            [ 0.92,  0.96,  1.01,  1.04,  1.01,  0.96,  0.92],
            [ 0.8 ,  0.82,  0.84,  0.85,  0.84,  0.82,  0.8 ],
            [ 0.66,  0.67,  0.68,  0.68,  0.68,  0.67,  0.66],
            [ 0.52,  0.52,  0.53,  0.53,  0.53,  0.52,  0.52],
            [ 0.37,  0.37,  0.37,  0.38,  0.37,  0.37,  0.37],
            [ 0.22,  0.22,  0.22,  0.22,  0.22,  0.22,  0.22],
            [ 0.07,  0.07,  0.07,  0.07,  0.07,  0.07,  0.07]
        ])

        self.known_x_v = numpy.array([
            [ 0.96,  1.  ,  1.06,  1.12,  1.12,  1.06,  1.  ,  0.96],
            [ 0.86,  0.88,  0.9 ,  0.92,  0.92,  0.9 ,  0.88,  0.86],
            [ 0.73,  0.74,  0.75,  0.76,  0.76,  0.75,  0.74,  0.73],
            [ 0.59,  0.6 ,  0.6 ,  0.6 ,  0.6 ,  0.6 ,  0.6 ,  0.59],
            [ 0.45,  0.45,  0.45,  0.45,  0.45,  0.45,  0.45,  0.45],
            [ 0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ,  0.3 ],
            [ 0.15,  0.15,  0.15,  0.15,  0.15,  0.15,  0.15,  0.15]
        ])

        self.known_y_u = numpy.array([
            [ 0.04,  0.11,  0.22,  0.5 ,  0.78,  0.89,  0.96],
            [ 0.09,  0.19,  0.32,  0.5 ,  0.68,  0.81,  0.91],
            [ 0.11,  0.23,  0.36,  0.5 ,  0.64,  0.77,  0.89],
            [ 0.12,  0.24,  0.37,  0.5 ,  0.63,  0.76,  0.88],
            [ 0.12,  0.25,  0.37,  0.5 ,  0.63,  0.75,  0.88],
            [ 0.13,  0.25,  0.37,  0.5 ,  0.63,  0.75,  0.87],
            [ 0.13,  0.25,  0.38,  0.5 ,  0.62,  0.75,  0.87],
            [ 0.13,  0.25,  0.38,  0.5 ,  0.62,  0.75,  0.87]
        ])

        self.known_y_v = numpy.array([
            [ 0.04,  0.12,  0.23,  0.4 ,  0.6 ,  0.77,  0.88,  0.96],
            [ 0.05,  0.16,  0.28,  0.42,  0.58,  0.72,  0.84,  0.95],
            [ 0.06,  0.18,  0.3 ,  0.43,  0.57,  0.7 ,  0.82,  0.94],
            [ 0.06,  0.18,  0.31,  0.44,  0.56,  0.69,  0.82,  0.94],
            [ 0.06,  0.19,  0.31,  0.44,  0.56,  0.69,  0.81,  0.94],
            [ 0.06,  0.19,  0.31,  0.44,  0.56,  0.69,  0.81,  0.94],
            [ 0.06,  0.19,  0.31,  0.44,  0.56,  0.69,  0.81,  0.94]
        ])


class test_Grid_with_proj(_gridMixin):
    def setup(self):
        self.options = self._options.copy()
        self.x = [-122.7, -122.5, -122.1, -121.7, -122.1, -122.3]
        self.y = [44.5, 45.0, 45.5, 45.5, 45.0, 44.5]
        self.beta = [1.0, 1.0, 0.0, 0.0, 1.0, 1.0]
        self.shape = (10, 4)

        utm10 = pyproj.Proj(proj='utm', zone=10, ellps='WGS84')
        self.options.update({'ul_idx': 2, 'proj': utm10})

        self.grid = self.make_grid()

        self.known_x = numpy.array([
            [ 523849.33,  537634.03,  547839.75,  555648.45],
            [ 526581.75,  538098.95,  548230.37,  556959.19],
            [ 528706.88,  539280.4 ,  549285.71,  558586.48],
            [ 530680.14,  540779.61,  550703.53,  560332.94],
            [ 532573.13,  542376.34,  552276.84,  562147.52],
            [ 534399.75,  543920.09,  553868.86,  564017.21],
            [ 536134.21,  545225.84,  555367.56,  565953.24],
            [ 537693.4 ,  545930.59,  556686.9 ,  567971.74],
            [ 538892.32,  545175.68,  557971.63,  569945.95],
            [ 539407.65,  541507.67,  553438.74,  570933.77]
        ])

        self.known_y = numpy.array([
            [ 4927452.94,  4927537.26,  4927599.69,  4927647.45],
            [ 4937221.02,  4935113.05,  4933970.41,  4932423.55],
            [ 4944818.07,  4942360.57,  4940479.26,  4938353.08],
            [ 4951872.24,  4949330.44,  4947109.6 ,  4944716.87],
            [ 4958639.43,  4956134.07,  4953832.9 ,  4951328.87],
            [ 4965169.39,  4962831.75,  4960667.24,  4958141.67],
            [ 4971369.87,  4969442.43,  4967703.75,  4965196.22],
            [ 4976943.77,  4975952.38,  4975210.77,  4972551.26],
            [ 4981229.76,  4982185.84,  4984280.65,  4979744.91],
            [ 4983071.99,  4986864.71,  5008412.78,  4983344.35]
        ])

        self.known_x_psi = numpy.array([
            [ 538098.95,  548230.37],
            [ 539280.4 ,  549285.71],
            [ 540779.61,  550703.53],
            [ 542376.34,  552276.84],
            [ 543920.09,  553868.86],
            [ 545225.84,  555367.56],
            [ 545930.59,  556686.9 ],
            [ 545175.68,  557971.63]
        ])

        self.known_y_psi = numpy.array([
            [ 4935113.05,  4933970.41],
            [ 4942360.57,  4940479.26],
            [ 4949330.44,  4947109.6 ],
            [ 4956134.07,  4953832.9 ],
            [ 4962831.75,  4960667.24],
            [ 4969442.43,  4967703.75],
            [ 4975952.38,  4975210.77],
            [ 4982185.84,  4984280.65]
        ])

        self.known_x_rho = numpy.array([
            [ 531541.02,  542950.78,  552169.44],
            [ 533166.99,  543723.86,  553265.44],
            [ 534861.76,  545012.31,  554727.16],
            [ 536602.3 ,  546534.08,  556365.21],
            [ 538317.33,  548110.53,  558077.61],
            [ 539919.98,  549595.59,  559801.72],
            [ 541246.01,  550802.72,  561494.86],
            [ 541923.  ,  551441.2 ,  563144.06],
            [ 541245.83,  549523.43,  563072.52]
        ])

        self.known_y_rho = numpy.array([
            [ 4931831.07,  4931055.1 ,  4930410.27],
            [ 4939878.18,  4937980.82,  4936306.57],
            [ 4947095.33,  4944819.97,  4942664.7 ],
            [ 4953994.04,  4951601.75,  4949247.06],
            [ 4960693.66,  4958366.49,  4955992.67],
            [ 4967203.36,  4965161.29,  4962927.22],
            [ 4973427.11,  4972077.33,  4970165.5 ],
            [ 4979077.94,  4979407.41,  4977946.9 ],
            [ 4983338.07,  4990436.  ,  4988945.67]
        ])

        self.known_x_u = numpy.array([
            [ 537866.49,  548035.06],
            [ 538689.67,  548758.04],
            [ 540030.  ,  549994.62],
            [ 541577.97,  551490.18],
            [ 543148.21,  553072.85],
            [ 544572.97,  554618.21],
            [ 545578.22,  556027.23],
            [ 545553.13,  557329.27],
            [ 543341.67,  555705.19]
        ])

        self.known_x_v = numpy.array([
            [ 532340.35,  543164.66,  552594.78],
            [ 533993.64,  544283.05,  553936.1 ],
            [ 535729.88,  545741.57,  555518.23],
            [ 537474.73,  547326.59,  557212.18],
            [ 539159.92,  548894.47,  558943.03],
            [ 540680.03,  550296.7 ,  560660.4 ],
            [ 541812.  ,  551308.74,  562329.32],
            [ 542034.  ,  551573.65,  563958.79]
        ])

        self.known_y_u = numpy.array([
            [ 4931325.16,  4930785.05],
            [ 4938736.81,  4937224.83],
            [ 4945845.51,  4943794.43],
            [ 4952732.25,  4950471.25],
            [ 4959482.91,  4957250.07],
            [ 4966137.09,  4964185.49],
            [ 4972697.41,  4971457.26],
            [ 4979069.11,  4979745.71],
            [ 4984525.28,  4996346.71]
        ])

        self.known_y_v = numpy.array([
            [ 4936167.04,  4934541.73,  4933196.98],
            [ 4943589.32,  4941419.92,  4939416.17],
            [ 4950601.34,  4948220.02,  4945913.24],
            [ 4957386.75,  4954983.48,  4952580.89],
            [ 4964000.57,  4961749.5 ,  4959404.45],
            [ 4970406.15,  4968573.09,  4966449.98],
            [ 4976448.08,  4975581.57,  4973881.01],
            [ 4981707.8 ,  4983233.25,  4982012.78]
        ])

    def test_xbry(self):
        projx, projy = self.grid.proj(self.x, self.y)
        nt.assert_true(hasattr(self.grid, 'xbry'))
        nptest.assert_array_almost_equal(
            self.grid.xbry,
            projx,
            decimal=2
        )

    def test_ybry(self):
        projx, projy = self.grid.proj(self.x, self.y)
        nt.assert_true(hasattr(self.grid, 'ybry'))
        nptest.assert_array_almost_equal(
            self.grid.ybry,
            projy,
            decimal=2
        )


class test_Grid_autogenFalse_Called(test_Grid_basic):

    @nt.nottest
    def make_grid(self):
        self.options.update({'autogen': False})
        grid = pygridgen.Gridgen(self.x, self.y, self.beta, self.shape,
                                 **self.options)

        grid.generate_grid()
        return grid



class test_Grid_regenerate(test_Grid_with_focus):
    '''Tests grid regenerate with tweaks parameters (properties)

    Starts off with the same parameters as ``test_Grid_with_focus``, but
    ignores focus and initial generates as grid with a different shape. Then
    the grid's ``nx``, ``ny``, and ``focus`` properties are set to their
    correct values and the grid is regenerated. All of the original
    ``test_Grid_with_focus`` tests are then run.

    '''
    @nt.nottest
    def make_grid(self):
        focus = self.options.pop('focus')

        grid = pygridgen.Gridgen(self.x, self.y, self.beta, (5, 5),
                                 focus=None, **self.options)

        grid.ny = self.shape[0]
        grid.nx = self.shape[1]
        grid.focus = focus
        grid.generate_grid()

        return grid
