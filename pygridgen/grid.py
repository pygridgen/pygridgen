# encoding: utf-8
"""Tools for creating curvilinear grids using gridgen by Pavel Sakov"""


__docformat__ = "restructuredtext en"


import os
import sys
import ctypes

import numpy as np
from matplotlib.path import Path


def _points_inside_poly(points, verts):
    poly = Path(verts)
    return [ind for ind, p in enumerate(points) if poly.contains_point(p)]


def _approximate_erf(x):
    """
    Approximate solution to error function.

    Parameters
    ----------
    x : float

    Returns
    -------
    erf : float
        Value of the error function at ``x``

    References
    ----------
    http://en.wikipedia.org/wiki/Error_function

    """

    a = -(8 * (np.pi - 3.0) / (3.0 * np.pi * (np.pi - 4.0)))
    guts = -1 * (x ** 2) * (4.0 / np.pi + a * x * x) / (1.0 + a * x * x)
    return np.sign(x) * np.sqrt(1.0 - np.exp(guts))


class _FocusPoint(object):
    """
    Return a transformed, uniform grid, focused in the x- or
    y-direction.

    This class may be called with a uniform grid, with limits from
    [0, 1]. To create a focused grid in the ``axis`` direction centered
    about ``pos``. The output grid is also uniform from [0, 1] in both
    x and y.

    Parameters
    ----------
    pos : float
        Relative position within the grid of the focus. This must
        be in the range [0, 1]
    axis : string ('x' or 'y')
        Axis along which the grid will be focused.
    factor : float
        Amount to focus grid. Creates cell sizes that are factor
        smaller (factor > 1) or larger (factor < 1) in the focused
        region.
    extent : float
        Lateral extent of focused region.


    Returns
    -------
    foc : class
        The class may be called with vertex/node positions of a grid.
        The returned transformed grid (x, y) will be focused as per the
        parameters listed above.

    """

    def __init__(self, pos, axis, factor, extent):
        self.pos = pos
        self.axis = axis.lower()
        self.factor = factor
        self.extent = extent

        if self.pos > 1.0 or self.pos < 0:
            raise ValueError('`pos` must be within the range [0, 1]')

        if self.axis not in ['x', 'y']:
            raise ValueError("`axis` must be 'x' or 'y'")

    def _reposition_point(self, pnt):
        alpha = 1.0 - 1.0 / self.factor
        erf = _approximate_erf((pnt - self.pos) / self.extent)
        return pnt - 0.5 * (np.sqrt(np.pi) * self.extent * alpha * erf)

    def _do_focus(self, array):
        f0 = self._reposition_point(0.0)
        f1 = self._reposition_point(1.0)
        return (self._reposition_point(array) - f0) / (f1 - f0)

    def __call__(self, x, y):
        x = np.asarray(x)
        y = np.asarray(y)
        if np.any(x > 1.0) or np.any(x < 0.0):
            raise ValueError('x must be within the range [0, 1]')

        if np.any(y > 1.0) or np.any(y < 0.0):
                raise ValueError('y must be within the range [0, 1]')

        if self.axis == 'y':
            return x, self._do_focus(y)

        elif self.axis == 'x':
            return self._do_focus(x), y


class Focus(object):
    """
    Return a container for a sequence of Focus objects.

    The sequence is populated by using :meth:`~add_focus`, which defines
    a point (``xo`` or ``yo``), around which the grid is focused by a
    `factor` for the provided ``extent`` in the along the given
    ``axis``. The region of focusing will be approximately Gaussian,
    and the resolution will be increased by approximately the value of
    ``factor``.

    Calls to the object return transformed coordinates:

    .. code-block:: python

       xf, yf = foc(x, y)

    where `x` and `y` must be within [0, 1], and are typically a
    uniform, normalized grid. The focused grid will be the result of
    applying each of the focus elements in the sequence they are added
    to the series.

    Parameters
    ----------
    None

    Examples
    --------
    >>> foc = pygridgen.Focus()
    >>> foc.add_focus(0.2, axis='x', factor=3.0, extent=0.20)
    >>> foc.add_focus(0.6, axis='y', factor=5.0, extent=0.35)

    >>> x, y = np.mgrid[0:1:3j, 0:1:3j]
    >>> xf, yf = foc(x, y)

    >>> print(xf)
    [[ 0.          0.          0.        ]
     [ 0.36594617  0.36594617  0.36594617]
     [ 1.          1.          1.        ]]
    >>> print(yf)
    [[ 0.          0.62479833  1.        ]
     [ 0.          0.62479833  1.        ]
     [ 0.          0.62479833  1.        ]]

    """

    def __init__(self, *foci):
        self._focuspoints = list(foci)

    def add_focus(self, pos, axis, factor=2.0, extent=0.1):
        """
        Add a single point of focus along an axis.

        This adds a focused location to a grid and can be called multiple
        times in either the x- or y-direction.

        Parameters
        ----------
        pos : float
            Relative position within the grid of the focus. This must
            be in the range [0, 1]
        axis : string ('x' or 'y')
            Axis along which the grid will be focused.
        factor : float
            Amount to focus grid. Creates cell sizes that are factor
            smaller (factor > 1) or larger (factor < 1) in the focused
            region.
        extent : float
            Lateral extent of focused region.

        """

        self._focuspoints.append(_FocusPoint(pos, axis, factor, extent))

    def __call__(self, x, y):
        """docstring for __call__"""
        for focuspoint in self._focuspoints:
            x, y = focuspoint(x, y)
        return x, y


class CGrid(object):
    """
    Curvilinear Arakawa C-Grid.

    The basis for the CGrid class are two arrays defining the verticies
    of the grid in Cartesian (for geographic coordinates, see
    :class:`~CGrid_geo`). An optional mask may be defined on the cell
    centers. Other Arakawa C-grid properties, such as the locations of
    the cell centers (*rho*-points), cell edges (*u* and *v* velocity
    points), cell widths (*dx* and *dy*) and other metrics (*angle*,
    *dmde*, and *dndx*) are all calculated internally from the vertex
    points.

    Input vertex arrays may be either masked or regular numpy arrays.
    If masked arrays are used, the mask will be a combination of the
    specified mask (if given) and the masked locations.

    Parameters
    ----------
    x, y : numpy.ndarray
        Arrays of the x/y vertex/node positions

    Examples
    --------
    >>> import numpy as np
    >>> import pygridgen
    >>> x, y = np.mgrid[0.0:7.0, 0.0:8.0]
    >>> x = np.ma.masked_where((x < 3) & (y < 3), x)
    >>> y = np.ma.MaskedArray(y, x.mask)
    >>> grd = pygridgen.grid.CGrid(x, y)
    >>> print(grd.x_rho)
    [[-- -- -- 0.5 0.5 0.5 0.5]
     [-- -- -- 1.5 1.5 1.5 1.5]
     [-- -- -- 2.5 2.5 2.5 2.5]
     [3.5 3.5 3.5 3.5 3.5 3.5 3.5]
     [4.5 4.5 4.5 4.5 4.5 4.5 4.5]
     [5.5 5.5 5.5 5.5 5.5 5.5 5.5]]
    >>> print(grd.mask)
    [[ 0.  0.  0.  1.  1.  1.  1.]
     [ 0.  0.  0.  1.  1.  1.  1.]
     [ 0.  0.  0.  1.  1.  1.  1.]
     [ 1.  1.  1.  1.  1.  1.  1.]
     [ 1.  1.  1.  1.  1.  1.  1.]
     [ 1.  1.  1.  1.  1.  1.  1.]]

    """

    def __init__(self, x, y):

        # grid (verts/nodes)
        self._x = None
        self._y = None
        self._mask = None

        # subgrid masks
        self._mask_rho = None

        if np.ndim(x) != 2 and np.ndim(y) != 2:
            raise ValueError('x and y must be two dimensional')

        if np.shape(x) != np.shape(y):
            raise ValueError('x and y must be the same size.')

        if np.any(np.isnan(x)) or np.any(np.isnan(y)):
            x = np.ma.masked_where((np.isnan(x)) | (np.isnan(y)), x)
            y = np.ma.masked_where((np.isnan(x)) | (np.isnan(y)), y)

        self.x_vert = x
        self.y_vert = y

    @property
    def x(self):
        """
        x-coordinate of the grid vertices (a.k.a. nodes)
        """
        if self._x is None:
            self._x = self.x_vert
        return self._x

    @property
    def y(self):
        """
        y-coordinate of the grid vertices (a.k.a. nodes)
        """
        if self._y is None:
            self._y = self.y_vert
        return self._y

    @property
    def mask(self):
        """
        Mask for the cells (same as mask_rho)
        """
        return self.mask_rho

    @property
    def x_rho(self):
        """
        x-coordinates of cell centroids
        """
        x_rho = 0.25 * (self.x_vert[1:, 1:] + self.x_vert[1:, :-1] +
                        self.x_vert[:-1, 1:] + self.x_vert[:-1, :-1])
        return x_rho

    @property
    def y_rho(self):
        """
        y-coordinates of cell centroids
        """
        y_rho = 0.25 * (self.y_vert[1:, 1:] + self.y_vert[1:, :-1] +
                        self.y_vert[:-1, 1:] + self.y_vert[:-1, :-1])
        return y_rho

    @property
    def mask_rho(self):
        """
        Returns the mask for the cells
        """
        if self._mask_rho is None:
            mask_shape = tuple([n-1 for n in self.x_vert.shape])
            self._mask_rho = np.ones(mask_shape, dtype='d')

            # If maskedarray is given for vertices, modify the mask such that
            # non-existant grid points are masked.  A cell requires all four
            # verticies to be defined as a water point.
            if isinstance(self.x_vert, np.ma.MaskedArray):
                mask = (self.x_vert.mask[:-1,:-1] | self.x_vert.mask[1:,:-1] |
                        self.x_vert.mask[:-1,1:] | self.x_vert.mask[1:,1:])
                self._mask_rho = np.asarray(
                    ~(~np.bool_(self.mask_rho) | mask),
                    dtype='d'
                )

            if isinstance(self.y_vert, np.ma.MaskedArray):
                mask = (self.y_vert.mask[:-1,:-1] | self.y_vert.mask[1:,:-1] |
                        self.y_vert.mask[:-1,1:] | self.y_vert.mask[1:,1:])
                self._mask_rho = np.asarray(
                    ~(~np.bool_(self.mask_rho) | mask),
                    dtype='d'
                )

        return self._mask_rho

    @mask_rho.setter
    def mask_rho(self, value):
        if value.shape == self._mask_rho.shape:
            self._mask_rho = value
        else:
            raise ValueError("shapes are mismatched")

    @property
    def x_u(self):
        """
        x-coordinate of u-point (leading edge in i-direction?)
        """
        return 0.5*(self.x_vert[:-1, 1:-1] + self.x_vert[1:, 1:-1])

    @property
    def y_u(self):
        """
        y-coordinate of u-point (leading edge in i-direction?)
        """
        return 0.5*(self.y_vert[:-1, 1:-1] + self.y_vert[1:, 1:-1])

    @property
    def mask_u(self):
        """
        Mask for the u-points
        """
        return self.mask_rho[:,1:] * self.mask_rho[:,:-1]

    @property
    def x_v(self):
        """
        x-coordinate of y-point (leading edge in j-direction?)
        """
        return 0.5*(self.x_vert[1:-1, :-1] + self.x_vert[1:-1, 1:])

    @property
    def y_v(self):
        """
        y-coordinate of y-point (leading edge in j-direction?)
        """
        return 0.5*(self.y_vert[1:-1, :-1] + self.y_vert[1:-1, 1:])

    @property
    def mask_v(self):
        """
        mask for the v-points
        """
        return self.mask_rho[1:, :]*self.mask_rho[:-1, :]

    @property
    def x_psi(self):
        """
        x-coordinate of the anchor node for each cell? (upper left?)
        """
        return self.x_vert[1:-1, 1:-1]

    @property
    def y_psi(self):
        """
        y-coordinate of the anchor node for each cell? (upper left?)
        """
        return self.y_vert[1:-1, 1:-1]

    @property
    def mask_psi(self):
        """
        mask for the psi-points
        """
        mask_psi = (self.mask_rho[1:, 1:] * self.mask_rho[:-1, 1:] *
                    self.mask_rho[1:, :-1] * self.mask_rho[:-1, :-1])
        return mask_psi

    @property
    def dx(self):
        """
        dimension of cell in x-direction?
        """
        x_temp = 0.5*(self.x_vert[1:, :]+self.x_vert[:-1, :])
        y_temp = 0.5*(self.y_vert[1:, :]+self.y_vert[:-1, :])
        dx = np.sqrt(np.diff(x_temp, axis=1)**2 + np.diff(y_temp, axis=1)**2)
        return dx

    @property
    def pm(self):
        return 1.0 / self.dx

    @property
    def dy(self):
        """
        dimension of cell in y-direction?
        """
        x_temp = 0.5*(self.x_vert[:, 1:]+self.x_vert[:, :-1])
        y_temp = 0.5*(self.y_vert[:, 1:]+self.y_vert[:, :-1])
        dy = np.sqrt(np.diff(x_temp, axis=0)**2 + np.diff(y_temp, axis=0)**2)
        return dy

    @property
    def pn(self):
        return 1.0 / self.dy

    @property
    def dndx(self):
        if isinstance(self.dy, np.ma.MaskedArray):
            dndx = np.ma.zeros(self.x_rho.shape, dtype='d')
        else:
            dndx = np.zeros(self.x_rho.shape, dtype='d')

        dndx[1:-1, 1:-1] = 0.5*(self.dy[1:-1, 2:] - self.dy[1:-1, :-2])
        return dndx

    @property
    def dmde(self):
        if isinstance(self.dx, np.ma.MaskedArray):
            dmde = np.ma.zeros(self.x_rho.shape, dtype='d')
        else:
            dmde = np.zeros(self.x_rho.shape, dtype='d')

        dmde[1:-1, 1:-1] = 0.5*(self.dx[2:, 1:-1] - self.dx[:-2,1 :-1])
        return dmde

    @property
    def angle(self):
        if isinstance(self.x_vert, np.ma.MaskedArray) or \
           isinstance(self.y_vert, np.ma.MaskedArray):
            angle = np.ma.zeros(self.x_vert.shape, dtype='d')
        else:
            angle = np.zeros(self.x_vert.shape, dtype='d')

        angle_ud = np.arctan2(np.diff(self.y_vert, axis=1),
                              np.diff(self.x_vert, axis=1))
        angle_lr = np.arctan2(np.diff(self.y_vert, axis=0),
                              np.diff(self.x_vert, axis=0)) - (np.pi / 2.0)

        # domain center
        angle[1:-1, 1:-1] = 0.25 * (
            angle_ud[1:-1, 1:] + angle_ud[1:-1, :-1] +
            angle_lr[1:, 1:-1] + angle_lr[:-1, 1:-1])

        # edges
        angle[0, 1:-1] = (1.0 / 3.0) * (
            angle_lr[0, 1:-1] + angle_ud[0, 1:] + angle_ud[0, :-1]
        )
        angle[-1, 1:-1] = (1.0 / 3.0) * (
            angle_lr[-1, 1:-1] + angle_ud[-1, 1:] + angle_ud[-1, :-1]
        )

        angle[1:-1, 0] = (1.0 / 3.0) * (
            angle_ud[1:-1, 0] + angle_lr[1:, 0] + angle_lr[:-1, 0]
        )

        angle[1:-1, -1] = (1.0 / 3.0) * (
            angle_ud[1:-1, -1] + angle_lr[1:, -1] + angle_lr[:-1, -1]
        )

        #corners
        angle[0, 0] = 0.5 * (angle_lr[0, 0] + angle_ud[0, 0])
        angle[0, -1] = 0.5 * (angle_lr[0, -1] + angle_ud[0, -1])
        angle[-1, 0] = 0.5 * (angle_lr[-1, 0] + angle_ud[-1, 0])
        angle[-1, -1] = 0.5 * (angle_lr[-1, -1] + angle_ud[-1, -1])

        return angle

    @property
    def angle_rho(self):
        angle_rho = np.arctan2(
            np.diff(0.5 * (self.y_vert[1:, :] + self.y_vert[:-1, :])),
            np.diff(0.5 * (self.x_vert[1:, :] + self.x_vert[:-1, :]))
        )

        return angle_rho

    @property
    def orthogonality(self):
        """
        Calculate orthogonality error in radians
        """
        z = self.x_vert + 1j*self.y_vert

        du = np.diff(z, axis=1)
        du = (du / abs(du))[:-1 ,:]
        dv = np.diff(z, axis=0)
        dv = (dv / abs(dv))[:, :-1]
        ang1 = np.arccos(du.real*dv.real + du.imag*dv.imag)

        du = np.diff(z, axis=1)
        du = (du / abs(du))[1:, :]
        dv = np.diff(z, axis=0)
        dv = (dv / abs(dv))[:, :-1]
        ang2 = np.arccos(du.real*dv.real + du.imag*dv.imag)

        du = np.diff(z, axis=1)
        du = (du / abs(du))[:-1, :]
        dv = np.diff(z, axis=0)
        dv = (dv / abs(dv))[:, 1:]
        ang3 = np.arccos(du.real*dv.real + du.imag*dv.imag)

        du = np.diff(z, axis=1)
        du = (du / abs(du))[1:, :]
        dv = np.diff(z, axis=0)
        dv = (dv / abs(dv))[:, 1:]
        ang4 = np.arccos(du.real*dv.real + du.imag*dv.imag)

        ang = np.mean([abs(ang1), abs(ang2), abs(ang3), abs(ang4)], axis=0)
        ang = (ang - np.pi/2.0)
        return ang

    def calculate_orthogonality(self):
        """
        Should deprecate in favor of property ``orthogonality``
        """
        return self.orthogonality

    def mask_polygon(self, polyverts, mask_value=False):
        """
        Mask Cartesian points contained within the polygon defined by
        ``polyverts``.

        A cell is masked if the cell center (`x_rho`, `y_rho`) is within
        the polygon. Other sub-masks (`mask_u`, `mask_v`, and `mask_psi`)
        are updated automatically.

        A `mask_value=False` may be specified to alter the value of the
        mask set within the polygon (e.g., `mask_value=True` for water
        points)

        Parameters
        ----------
        polyverts : sequence of 2-tuples or numpy array (N, x)
            The x/y coordinates of the polygon used to mask the grid.
        mask_value : bool, optional (default = False)
            The value of the mask to be set for cells whose centroids
            are inside the polygon.

        """

        polyverts = np.asarray(polyverts)
        if polyverts.ndim != 2:
            raise ValueError('polyverts must be a 2D array, or a '
                             'similar sequence')

        if polyverts.shape[1] != 2:
            raise ValueError('polyverts must be two columns of points')

        if polyverts.shape[0] < 3:
            raise ValueError('polyverts must contain at least 3 points')

        mask = self.mask_rho.copy()
        inside = _points_inside_poly(
            np.vstack([self.x_rho.flatten(), self.y_rho.flatten()]).T,
            polyverts
        )
        if np.any(inside):
            mask.flat[inside] = mask_value

        self.mask_rho = mask


class CGrid_geo(CGrid):
    """Curvilinear Arakawa C-grid defined in geographic coordinates.

    For a geographic grid, the cell widths are determined by the great
    circle distances. Angles, however, are defined using the projected
    coordinates, so a projection that conserves angles must be used.
    This means typically either Mercator (projection='merc') or Lambert
    Conformal Conic (projection='lcc').

    Parameters
    ----------
    lon, lat : numpy.ndarrays
        Array of grid vertex/node positions in decimal degrees (i.e.,
        longitude and latitude).
    proj : pyproj.Proj
        A projection object that can translate ``lon`` and ``lat`` into
        Cartesian coordinates.
    use_gcdist : bool, optional (default = True)
        Toggles the use of great circle distances when computing cell
        dimensions.
    ellipse : str, optional (default = 'WGS84')
        The ellipsoid reference for ``lon`` and ``lat``,

    """

    def __init__(self, lon, lat, proj, use_gcdist=True, ellipse='WGS84'):
        try:
            import pyproj
        except ImportError:
            from mpl_toolkits.basemap import pyproj
        else:
            raise ImportError('pyproj or mpltoolkits-basemap required')

        x, y = proj(lon, lat)
        self.lon_vert = lon
        self.lat_vert = lat

        # projection information
        self.use_gcdist = use_gcdist
        self.ellipse = ellipse
        self.proj = proj
        self.geod = pyproj.Geod(ellps=self.ellipse)

        super(CGrid_geo, self).__init__(x, y)

        self.lon_rho, self.lat_rho = self.proj(self.x_rho, self.y_rho,
                                               inverse=True)
        self.lon_u, self.lat_u = self.proj(self.x_u, self.y_u, inverse=True)
        self.lon_v, self.lat_v = self.proj(self.x_v, self.y_v, inverse=True)
        self.lon_psi, self.lat_psi = self.proj(self.x_psi, self.y_psi,
                                               inverse=True)

        # coriolis frequency
        self.f = 2.0 * 7.29e-5 * np.cos(self.lat_rho * np.pi / 180.0)

    @property
    def dx(self):
        if self.use_gcdist:
            az1, az2, dx = self.geod.inv(self.lon[:,1:], self.lat[:,1:],
                                         self.lon[:,:-1], self.lat[:,:-1])
            return 0.5 * (dx[1:,:] + dx[:-1,:])
        else:
            x_temp = 0.5*(self.x_vert[1:, :]+self.x_vert[:-1, :])
            y_temp = 0.5*(self.y_vert[1:, :]+self.y_vert[:-1, :])
            dx = np.sqrt(np.diff(x_temp, axis=1)**2 + np.diff(y_temp, axis=1)**2)
            return dx

    @property
    def dy(self):
        if self.use_gcdist:
            az1, ax2, dy = self.geod.inv(self.lon[1:,:], self.lat[1:,:],
                                         self.lon[:-1,:], self.lat[:-1,:])
            return 0.5 * (dy[:,1:] + dy[:,:-1])
        else:
            x_temp = 0.5*(self.x_vert[:, 1:]+self.x_vert[:, :-1])
            y_temp = 0.5*(self.y_vert[:, 1:]+self.y_vert[:, :-1])
            dy = np.sqrt(np.diff(x_temp, axis=0)**2 + np.diff(y_temp, axis=0)**2)
            return dy

    @property
    def lon(self):
        """Shorthand for lon_vert"""
        return self.lon_vert

    @property
    def lat(self):
        """Shorthand for lat_vert"""
        return self.lat_vert

    def mask_polygon_geo(lonlat_verts, mask_value=0.0):
        lon, lat = zip(*lonlat_verts)
        x, y = proj(lon, lat, inverse=True)
        self.mask_polygon(zip(x, y), mask_value)


class Gridgen(CGrid):
    """
    Main class for curvilinear-orthogonal grid generation.

    Parameters
    ----------
    xbry, ybry : array-like
        One dimensional sequences of the x- and y-coordinates of the
        grid boundary.
    beta : array-like
        Turning values of each coordinate defined by ``xbry`` and
        ``ybry``. The sum of all beta values must equal 4. If you think
        about this like the right-hand rule of basic physics, positive
        turning points (+1) face up and work to close the boundary
        polygon. Negative turning points (-1) open it up (e.g., to
        define a side channel or other complexity). In between these
        points, neutral points should be assigned a value of 0.
    shape : two-tuple of ints (ny, nx)
        The number of cells that would cover the full spatial extent of
        the grid in standard C-order (i.e., rows, then columns).
    ul_idx : optional int (default = 0)
        The index of the what should be considered the upper left corner
        of the grid boundary in the ``xbry``, ``ybry``, and `beta`
        inputs. This is actually more arbitrary than it sounds. Put it
        some place convenient for you, and the algorithm will
        conceptually rotate the boundary to place this point in the
        upper left corner. Keep that in mind when specifying the shape
        of the grid.
    focus : :class:`~Focus`, optional
        A focus object to tighten/loosen the grid in certain sections.
    proj : pyproj.Proj, optional
        A pyproj projection to be used to convert lat/lon coordinates
        to a projected (Cartesian) coordinate system (e.g., UTM, state
        plane).
    nnodes : int, optional (default = 14)
        The number of nodes used in grid generation. This affects the
        precision and computation time. A rule of thumb is that this
        should be equal to or slightly larger than `-log10(precision)`.
    precision : float, optional (default = 1.0e-12)
        The precision with which the grid is generated. The default
        value is good for lat/lon coordinate (i.e., smaller magnitudes
        of boundary coordinates). You can relax this to e.g., 1e-3 when
        working in state plane or UTM grids and you'll typically get
        better performance.
    nppe : int, optional (default = 3)
        The number of points per internal edge. Lower values will
        coarsen the image.
    newton : bool, optional (default = True)
        Toggles the use of Gauss-Newton solver with Broyden update to
        determine the sigma values of the grid domains. If False simple
        iterations will be used instead.
    thin : bool, optional (default = True)
        Toggle to True when the (some portion of) the grid is generally
        narrow in one dimension compared to another.
    checksimplepoly : bool, optional (default = True)
        Toggles a check to confirm that the boundary inputs form a valid
        geometry.
    verbose : bool, optional (default = True)
        Toggles the printing of console statements to track the progress
        of the grid generation.
    autogen : bool, optional (default = True)
        Toggles the automatic generation of the grid. Set to False if
        you want to delay calling the ``generate_grid`` method.

    Example
    -------

    >>> import matplotlib.pyplot as plt
    >>> import pygridgen
    >>> # define the boundary (pentagon)
    >>> x = [0, 1, 2, 1, 0]
    >>> y = [0, 0, 1, 2, 2]
    >>> beta = [1, 1, 0, 1, 1]
    >>> # define the focus
    >>> focus = pygridgen.grid.Focus()
    >>> focus.add_focus_x(xo=0.5, factor=3, Rx=0.2)
    >>> focus.add_focus_y(yo=0.75, factor=5, Ry=0.1)
    >>> # create the grid
    >>> grid = pygridgen.Gridgen(x, y, beta, shape=(20, 20), focus=focus)
    >>> # plot the grid
    >>> fig, ax = plt.subplots()
    >>> ax.plot(x, y, 'k-')
    >>> ax.plot(grid.x, grid.y, 'b.')

    """

    def __init__(self, xbry, ybry, beta, shape, ul_idx=0, focus=None,
                 proj=None, nnodes=14, precision=1.0e-12, nppe=3,
                 newton=True, thin=True, checksimplepoly=True,
                 verbose=False, autogen=True):

        # find the gridgen-c shared library
        libgridgen_paths = [
            ('libgridgen.so', os.path.join(sys.prefix, 'lib')),
            ('libgridgen', os.path.join(sys.prefix, 'lib')),
            ('libgridgen.so', '/usr/local/lib'),
            ('libgridgen', '/usr/local/lib'),
        ]

        for name, path in libgridgen_paths:
            try:
                self._libgridgen = np.ctypeslib.load_library(name, path)
                break
            except OSError:
                pass
            else:
                print("libgridgen: attempted names/locations")
                print(libgridgen_paths)
                raise OSError('Failed to load libgridgen.')

        # initialize/set types of critical variables
        self._libgridgen.gridgen_generategrid2.restype = ctypes.POINTER(ctypes.c_void_p)
        self._libgridgen.gridnodes_getx.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        self._libgridgen.gridnodes_gety.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        self._libgridgen.gridnodes_getnce1.restype = ctypes.c_int
        self._libgridgen.gridnodes_getnce2.restype = ctypes.c_int
        self._libgridgen.gridmap_build.restype = ctypes.c_void_p

        # store the boundary, reproject if possible
        self.xbry = np.asarray(xbry, dtype='d')
        self.ybry = np.asarray(ybry, dtype='d')
        self.proj = proj
        if self.proj is not None:
            self.xbry, self.ybry = proj(self.xbry, self.ybry)

        # store and check the beta parameter
        self.beta = np.asarray(beta, dtype='d')
        if not np.isclose(self.beta.sum(), 4.0):
            raise ValueError('sum of beta must be 4.0')

        # properties
        self._sigmas = None
        self._nsigmas = None
        self._ny = shape[0]
        self._nx = shape[1]
        self._focus = focus

        # other inputs
        self.ul_idx = ul_idx
        self.nnodes = nnodes
        self.precision = precision
        self.nppe = nppe
        self.newton = newton
        self.thin = thin
        self.checksimplepoly = checksimplepoly
        self.verbose = verbose

        # initialize the gridnodes object
        self._gn = None

        # generate the grid
        if autogen:
            self.generate_grid()

    def __del__(self):
        """delete gridnode object upon deletion"""
        self._libgridgen.gridnodes_destroy(self._gn)

    @property
    def sigmas(self):
        """ Some weird intermediate value that takes a long time to the
        C code to compute with complex boundaries. """
        return self._sigmas

    @sigmas.setter
    def sigmas(self, value):
        self._sigmas = value

    @property
    def nsigmas(self):
        """ The number of sigma values. """
        return self._nsigmas

    @nsigmas.setter
    def nsigmas(self, value):
        self._nsigmas = value

    @property
    def nx(self):
        """ Number of nodes in the x-direction (columns). """
        return self._nx

    @nx.setter
    def nx(self, value):
        self._nx = value

    @property
    def ny(self):
        """ Number of nodes in the y-direction (rows). """
        return self._ny

    @ny.setter
    def ny(self, value):
        self._ny = value

    @property
    def shape(self):
        """ The shape of the overall grid (row, columns). """
        return (self.ny, self.nx)

    @property
    def focus(self):
        """ The :class:`~Focus` object associated with the grid. """
        return self._focus

    @focus.setter
    def focus(self, value):
        self._focus = value

    def generate_grid(self):
        """
        The business end of this whole thing. Collects all of the
        inputs, passes them to the gridgen-c code, and returns arrays
        of node coordinates. Unless ``autogen`` was set to False, this
        happens when the object is instantiated.

        Parameters
        ----------
        None

        """
        if self._gn is not None:
            self._libgridgen.gridnodes_destroy(self._gn)

        # number of boundary points
        nbry = len(self.xbry)

        # sigma parameter
        if self.sigmas is None:
            self.nsigmas = ctypes.c_int(0)
            self.sigmas = ctypes.c_void_p(0)

        # rectangularized domain
        nrect = ctypes.c_int(0)
        xrect = ctypes.c_void_p(0)
        yrect = ctypes.c_void_p(0)

        # focus the grid if necessary
        if self.focus is None:
            ngrid = ctypes.c_int(0)
            xgrid = ctypes.POINTER(ctypes.c_double)()
            ygrid = ctypes.POINTER(ctypes.c_double)()
        else:
            y, x =  np.mgrid[0:1:self.ny*1j, 0:1:self.nx*1j]
            xgrid, ygrid = self.focus(x, y)
            ngrid = ctypes.c_int(xgrid.size)
            xgrid = (ctypes.c_double * xgrid.size)(*xgrid.flatten())
            ygrid = (ctypes.c_double * ygrid.size)(*ygrid.flatten())

        # call the C-code to make make the grid
        self._gn = self._libgridgen.gridgen_generategrid2(
            ctypes.c_int(nbry),
            (ctypes.c_double * nbry)(*self.xbry),
            (ctypes.c_double * nbry)(*self.ybry),
            (ctypes.c_double * nbry)(*self.beta),
            ctypes.c_int(self.ul_idx),
            ctypes.c_int(self.nx),
            ctypes.c_int(self.ny),
            ngrid,
            xgrid,
            ygrid,
            ctypes.c_int(self.nnodes),
            ctypes.c_int(self.newton),
            ctypes.c_double(self.precision),
            ctypes.c_int(self.checksimplepoly),
            ctypes.c_int(self.thin),
            ctypes.c_int(self.nppe),
            ctypes.c_int(self.verbose),
            ctypes.byref(self.nsigmas),
            ctypes.byref(self.sigmas),
            ctypes.byref(nrect),
            ctypes.byref(xrect),
            ctypes.byref(yrect)
        )

        # x-positions
        x = self._libgridgen.gridnodes_getx(self._gn)
        x = np.asarray([x[0][i] for i in range(self.ny*self.nx)])
        x.shape = (self.ny, self.nx)

        # y-positions
        y = self._libgridgen.gridnodes_gety(self._gn)
        y = np.asarray([y[0][i] for i in range(self.ny*self.nx)])
        y.shape = (self.ny, self.nx)

        # mask out invalid values
        if np.any(np.isnan(x)) or np.any(np.isnan(y)):
            x = np.ma.masked_where(np.isnan(x), x)
            y = np.ma.masked_where(np.isnan(y), y)

        super(Gridgen, self).__init__(x, y)



def rho_to_vert(xr, yr, pm, pn, ang):  # pragma: no cover
    """ Possibly converts centroids to nodes """
    Mp, Lp = xr.shape
    x = empty((Mp+1, Lp+1), dtype='d')
    y = empty((Mp+1, Lp+1), dtype='d')
    x[1:-1, 1:-1] = 0.25*(xr[1:,1:]+xr[1:,:-1]+xr[:-1,1:]+xr[:-1,:-1])
    y[1:-1, 1:-1] = 0.25*(yr[1:,1:]+yr[1:,:-1]+yr[:-1,1:]+yr[:-1,:-1])

    # east side
    theta = 0.5*(ang[:-1,-1]+ang[1:,-1])
    dx = 0.5*(1.0/pm[:-1,-1]+1.0/pm[1:,-1])
    dy = 0.5*(1.0/pn[:-1,-1]+1.0/pn[1:,-1])
    x[1:-1,-1] = x[1:-1,-2] + dx*np.cos(theta)
    y[1:-1,-1] = y[1:-1,-2] + dx*np.sin(theta)

    # west side
    theta = 0.5*(ang[:-1,0]+ang[1:,0])
    dx = 0.5*(1.0/pm[:-1,0]+1.0/pm[1:,0])
    dy = 0.5*(1.0/pn[:-1,0]+1.0/pn[1:,0])
    x[1:-1,0] = x[1:-1,1] - dx*np.cos(theta)
    y[1:-1,0] = y[1:-1,1] - dx*np.sin(theta)

    # north side
    theta = 0.5*(ang[-1,:-1]+ang[-1,1:])
    dx = 0.5*(1.0/pm[-1,:-1]+1.0/pm[-1,1:])
    dy = 0.5*(1.0/pn[-1,:-1]+1.0/pn[-1,1:])
    x[-1,1:-1] = x[-2,1:-1] - dy*np.sin(theta)
    y[-1,1:-1] = y[-2,1:-1] + dy*np.cos(theta)

    # here we are now going to the south side..
    theta = 0.5*(ang[0,:-1]+ang[0,1:])
    dx = 0.5*(1.0/pm[0,:-1]+1.0/pm[0,1:])
    dy = 0.5*(1.0/pn[0,:-1]+1.0/pn[0,1:])
    x[0,1:-1] = x[1,1:-1] + dy*np.sin(theta)
    y[0,1:-1] = y[1,1:-1] - dy*np.cos(theta)

    #Corners
    x[0,0] = 4.0*xr[0,0]-x[1,0]-x[0,1]-x[1,1]
    x[-1,0] = 4.0*xr[-1,0]-x[-2,0]-x[-1,1]-x[-2,1]
    x[0,-1] = 4.0*xr[0,-1]-x[0,-2]-x[1,-1]-x[1,-2]
    x[-1,-1] = 4.0*xr[-1,-1]-x[-2,-2]-x[-2,-1]-x[-1,-2]

    y[0,0] = 4.0*yr[0,0]-y[1,0]-y[0,1]-y[1,1]
    y[-1,0] = 4.0*yr[-1,0]-y[-2,0]-y[-1,1]-y[-2,1]
    y[0,-1] = 4.0*yr[0,-1]-y[0,-2]-y[1,-1]-y[1,-2]
    y[-1,-1] = 4.0*yr[-1,-1]-y[-2,-2]-y[-2,-1]-y[-1,-2]

    return x, y


def uvp_masks(rmask):  # pragma: no cover
    """
    return u-, v-, and psi-masks based on input rho-mask

    Parameters
    ----------

    rmask : ndarray
        mask at CGrid rho-points

    Returns
    -------
    (umask, vmask, pmask) : ndarrays
        masks at u-, v-, and psi-points

    """
    rmask = np.asarray(rmask)
    if rmask.ndim != 2:
        raise ValueError('rmask must be a 2D array')

    if not np.all((rmask == 0) | (rmask ==1 )):
        raise ValueError('rmask array must contain only ones and zeros.')

    umask = rmask[:, :-1] * rmask[:, 1:]
    vmask = rmask[:-1, :] * rmask[1:, :]
    pmask = rmask[:-1, :-1] * rmask[:-1, 1:] * rmask[1:, :-1] * rmask[1:, 1:]

    return umask, vmask, pmask


if __name__ == '__main__':  # pragma: no cover
    import matplotlib.pyplot as plt

    geographic = False
    if geographic:
        from mpl_toolkits.basemap import Basemap
        proj = Basemap(projection='lcc',
                       resolution='i',
                       llcrnrlon=-72.0,
                       llcrnrlat= 40.0,
                       urcrnrlon=-63.0,
                       urcrnrlat=47.0,
                       lat_0=43.0,
                       lon_0=-62.5)

        lon = (-71.977385177601761, -70.19173825913137,
               -63.045075098584945,-64.70104074097425)
        lat = (42.88215610827428, 41.056141745853786,
               44.456701607935841, 46.271758064353897)
        beta = [1.0, 1.0, 1.0, 1.0]

        grd = Gridgen(lon, lat, beta, (32, 32), proj=proj)

        for seg in proj.coastsegs:
            grd.mask_polygon(seg)

        plt.pcolor(grd.x, grd.y, grd.mask)
        plt.show()
    else:
        x = [0.2, 0.85, 0.9, 0.82, 0.23]
        y = [0.2, 0.25, 0.5, 0.82, .83]
        beta = [1.0, 1.0, 0.0, 1.0, 1.0]

        grd = Gridgen(x, y, beta, (32, 32), verbose=False)

        print(grd.x)

        # ax = plt.subplot(111)
        # BoundaryInteractor(x, y, beta)
        # plt.show()
