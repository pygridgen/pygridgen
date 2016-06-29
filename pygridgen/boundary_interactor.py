__docformat__ = "restructuredtext en"

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

from copy import deepcopy

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from matplotlib.patches import Polygon, CirclePolygon
from matplotlib.lines import Line2D
from matplotlib.mlab import dist_point_to_segment

from .grid import Gridgen


class BoundaryInteractor(object):  # pragma: no cover
    """
    Interactive grid creation

    bry = BoundaryClick(x=[], y=[], beta=None, ax=gca(), **gridgen_options)

    The initial boundary polygon points (x and y) are
    counterclockwise, starting in the upper left corner of the
    boundary.

    Key commands:

        t : toggle visibility of verticies
        d : delete a vertex
        i : insert a vertex at a point on the polygon line

        P : set vertex as beta=1 (a Positive turn, marked with green triangle)
        M : set vertex as beta=1 (a Negative turn, marked with red triangle)
        Z : set vertex as beta=0 (no corner, marked with a black dot)
        S : set point as upper left index

        G : generate grid from the current boundary using gridgen
        T : toggle visability of the current grid

    Methods:

        bry.dump(bry_file)
            Write the current boundary informtion (bry.x, bry.y, bry.beta) to
            a pickle file bry_file.

        bry.load(bry_file)
            Read in boundary informtion (x, y, beta) from the pickle file
            bry_file.

        bry.remove_grid()
            Remove gridlines from axes.

    Attributes:
        bry.x : the X boundary points
        bry.y : the Y boundary points
        bry.verts : the verticies of the grid
        bry.grd : the CGrid object

    """

    _showverts = True
    _showbetas = True
    _showgrid = True
    _epsilon = 5  # max pixel distance to count as a vertex hit

    def _update_beta_lines(self):
        """Update m/pline by finding the points where self.beta== -/+ 1"""
        x, y = zip(*self._poly.xy)
        num_points = len(x)-1  # the first and last point are repeated

        xp = [x[n] for n in range(num_points) if self.beta[n]==1]
        yp = [y[n] for n in range(num_points) if self.beta[n]==1]
        self._pline.set_data(xp, yp)

        xm = [x[n] for n in range(num_points) if self.beta[n]==-1]
        ym = [y[n] for n in range(num_points) if self.beta[n]==-1]
        self._mline.set_data(xm, ym)

        xz = [x[n] for n in range(num_points) if self.beta[n]==0]
        yz = [y[n] for n in range(num_points) if self.beta[n]==0]
        self._zline.set_data(xz, yz)

        if len(x)-1 < self.gridgen_options['ul_idx']:
            self.gridgen_options['ul_idx'] = len(x)-1
        xs = x[self.gridgen_options['ul_idx']]
        ys = y[self.gridgen_options['ul_idx']]
        self._sline.set_data(xs, ys)

    def remove_grid(self):
        """Remove a generated grid from the BoundaryClick figure"""
        if hasattr(self, '_gridlines'):
            for line in self._gridlines:
                self._ax.lines.remove(line)
            delattr(self, '_gridlines')

    def _draw_callback(self, event):
        self._background = self._canvas.copy_from_bbox(self._ax.bbox)
        self._ax.draw_artist(self._poly)
        self._ax.draw_artist(self._pline)
        self._ax.draw_artist(self._mline)
        self._ax.draw_artist(self._zline)
        self._ax.draw_artist(self._sline)
        self._ax.draw_artist(self._line)
        self._canvas.blit(self._ax.bbox)

    def _poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self._line.get_visible()
        Artist.update_from(self._line, poly)
        self._line.set_visible(vis)  # don't use the poly visibility state

    def _get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        try:
            x, y = zip(*self._poly.xy)

            # display coords
            xt, yt = self._poly.get_transform().numerix_x_y(x, y)
            d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
            indseq = np.nonzero(np.equal(d, np.amin(d)))
            ind = indseq[0]

            if d[ind]>=self._epsilon:
                ind = None

            return ind
        except:
            # display coords
            xy = np.asarray(self._poly.xy)
            xyt = self._poly.get_transform().transform(xy)
            xt, yt = xyt[:, 0], xyt[:, 1]
            d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
            indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
            ind = indseq[0]

            if d[ind]>=self._epsilon:
                ind = None

            return ind

    def _button_press_callback(self, event):
        'whenever a mouse button is pressed'
        # if not self._showverts: return
        if event.inaxes==None: return
        if event.button != 1: return
        self._ind = self._get_ind_under_point(event)

    def _button_release_callback(self, event):
        'whenever a mouse button is released'
        # if not self._showverts: return
        if event.button != 1: return
        self._ind = None

    def _key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key=='shift': return

        if event.key=='t':
            self._showbetas = not self._showbetas
            self._line.set_visible(self._showbetas)
            self._pline.set_visible(self._showbetas)
            self._mline.set_visible(self._showbetas)
            self._zline.set_visible(self._showbetas)
            self._sline.set_visible(self._showbetas)
        elif event.key=='d':
            ind = self._get_ind_under_point(event)
            if ind is not None:
                self._poly.xy = [tup for i,tup in enumerate(self._poly.xy) \
                                 if i!=ind]
                self._line.set_data(zip(*self._poly.xy))
                self.beta = [beta for i,beta in enumerate(self.beta) \
                             if i!=ind]
        elif event.key=='p':
            ind = self._get_ind_under_point(event)
            if ind is not None:
                self.beta[ind] = 1.0
        elif event.key=='m':
            ind = self._get_ind_under_point(event)
            if ind is not None:
                self.beta[ind] = -1.0
        elif event.key=='z':
            ind = self._get_ind_under_point(event)
            if ind is not None:
                self.beta[ind] = 0.0
        elif event.key=='s':
            ind = self._get_ind_under_point(event)
            if ind is not None:
                self.gridgen_options['ul_idx'] = ind
        elif event.key=='i':
            xys = self._poly.get_transform().transform(self._poly.xy)
            p = event.x, event.y # display coords
            for i in range(len(xys)-1):
                s0 = xys[i]
                s1 = xys[i+1]
                d = dist_point_to_segment(p, s0, s1)
                if d<=self._epsilon:
                    self._poly.xy = np.array(
                        list(self._poly.xy[:i+1]) +
                        [(event.xdata, event.ydata)] +
                        list(self._poly.xy[i+1:]))
                    self._line.set_data(zip(*self._poly.xy))
                    self.beta.insert(i+1, 0)
                    break
            s0 = xys[-1]
            s1 = xys[0]
            d = dist_point_to_segment(p, s0, s1)
            if d<=self._epsilon:
                self._poly.xy = np.array(
                    list(self._poly.xy) +
                    [(event.xdata, event.ydata)])
                self._line.set_data(zip(*self._poly.xy))
                self.beta.append(0)
        elif event.key=='G' or event.key == '1':
            options = deepcopy(self.gridgen_options)
            shp = options.pop('shp')
            if self.proj is None:
                x = self.x
                y = self.y
                self.grd = Gridgen(x, y, self.beta, shp,
                                   proj=self.proj, **options)
            else:
                lon, lat = self.proj(self.x, self.y, inverse=True)
                self.grd = Gridgen(lon, lat, self.beta, shp,
                                   proj=self.proj, **options)
            self.remove_grid()
            self._showgrid = True
            gridlineprops = {'linestyle':'-', 'color':'k', 'lw':0.2}
            self._gridlines = []
            for line in self._ax._get_lines(*(self.grd.x, self.grd.y),
                                            **gridlineprops):
                self._ax.add_line(line)
                self._gridlines.append(line)
            for line in self._ax._get_lines(*(self.grd.x.T, self.grd.y.T),
                                            **gridlineprops):
                self._ax.add_line(line)
                self._gridlines.append(line)
        elif event.key=='T' or event.key == '2':
            self._showgrid = not self._showgrid
            if hasattr(self, '_gridlines'):
                for line in self._gridlines:
                    line.set_visible(self._showgrid)

        self._update_beta_lines()
        self._draw_callback(event)
        self._canvas.draw()

    def _motion_notify_callback(self, event):
        'on mouse movement'
        # if not self._showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata
        self._poly.xy[self._ind] = x, y
        if self._ind == 0:
            self._poly.xy[-1] = x, y

        x, y = zip(*self._poly.xy)
        self._line.set_data(x[:-1], y[:-1])
        self._update_beta_lines()

        self._canvas.restore_region(self._background)
        self._ax.draw_artist(self._poly)
        self._ax.draw_artist(self._pline)
        self._ax.draw_artist(self._mline)
        self._ax.draw_artist(self._zline)
        self._ax.draw_artist(self._sline)
        self._ax.draw_artist(self._line)
        self._canvas.blit(self._ax.bbox)


    def __init__(self, x, y=None, beta=None, ax=None, proj=None,
                 **gridgen_options):

        if isinstance(x, str):
            bry_dict = np.load(x)
            x = bry_dict['x']
            y = bry_dict['y']
            beta = bry_dict['beta']

        if len(x) < 4:
            raise ValueError('Boundary must have at least four points.')

        if ax is None:
            ax = plt.gca()

        self._ax = ax

        self.proj = proj

        # Set default gridgen option, and copy over specified options.
        self.gridgen_options = {'ul_idx': 0, 'shp': (32, 32)}

        for key, value in gridgen_options.iteritems():
            self.gridgen_options[key] = gridgen_options[key]

        x = list(x); y = list(y)
        if len(x) != len(y):
            raise ValueError('arrays must be equal length')

        if beta is None:
            self.beta = [0 for xi in x]
        else:
            if len(x) != len(beta):
                raise ValueError('beta must have same length as x and y')
            self.beta = list(beta)

        self._line = Line2D(x, y, animated=True,
                            ls='-', color='k', alpha=0.5, lw=1)
        self._ax.add_line(self._line)

        self._canvas = self._line.figure.canvas

        self._poly = Polygon(self.verts, alpha=0.1, fc='k', animated=True)
        self._ax.add_patch(self._poly)

        # Link in the lines that will show the beta values
        # pline for positive turns, mline for negative (minus) turns
        # otherwize zline (zero) for straight sections
        self._pline = Line2D([], [], marker='^', ms=12, mfc='g',\
                             animated=True, lw=0)
        self._mline = Line2D([], [], marker='v', ms=12, mfc='r',\
                             animated=True, lw=0)
        self._zline = Line2D([], [], marker='o', mfc='k', animated=True, lw=0)
        self._sline = Line2D([], [], marker='s', mfc='k', animated=True, lw=0)

        self._update_beta_lines()
        self._ax.add_artist(self._pline)
        self._ax.add_artist(self._mline)
        self._ax.add_artist(self._zline)
        self._ax.add_artist(self._sline)

        # get the canvas and connect the callback events
        cid = self._poly.add_callback(self._poly_changed)
        self._ind = None # the active vert

        self._canvas.mpl_connect('draw_event', self._draw_callback)
        self._canvas.mpl_connect('button_press_event',\
                                 self._button_press_callback)
        self._canvas.mpl_connect('key_press_event', self._key_press_callback)
        self._canvas.mpl_connect('button_release_event',\
                                 self._button_release_callback)
        self._canvas.mpl_connect('motion_notify_event',\
                                 self._motion_notify_callback)

    def save_bry(self, bry_file='bry.pickle'):
        f = open(bry_file, 'wb')
        bry_dict = {'x': self.x, 'y': self.y, 'beta': self.beta}
        pickle.dump(bry_dict, f, protocol=-1)
        f.close()

    def load_bry(self, bry_file='bry.pickle'):
        bry_dict = np.load(bry_file)
        x = bry_dict['x']
        y = bry_dict['y']
        self._line.set_data(x, y)
        self.beta = bry_dict['beta']
        if hasattr(self, '_poly'):
            self._poly.xy = zip(x, y)
            self._update_beta_lines()
            self._draw_callback(None)
            self._canvas.draw()

    def save_grid(self, grid_file='grid.pickle'):
        f = open(grid_file, 'wb')
        pickle.dump(self.grd, f, protocol=-1)
        f.close()

    def _get_verts(self): return zip(self.x, self.y)
    verts = property(_get_verts)
    def get_xdata(self): return self._line.get_xdata()
    x = property(get_xdata)
    def get_ydata(self): return self._line.get_ydata()
    y = property(get_ydata)


class edit_mask_mesh(object):  # pragma: no cover

    def _on_key(self, event):
        if event.key == 'e':
            self._clicking = not self._clicking
            plt.title('Editing %s -- click "e" to toggle' % self._clicking)
            plt.draw()

    def _on_click(self, event):
        x, y = event.xdata, event.ydata
        if event.button==1 and event.inaxes is not None and self._clicking == True:
            d = (x-self._xc)**2 + (y-self._yc)**2
            if isinstance(self.xv, np.ma.MaskedArray):
                idx = np.argwhere(d[~self._xc.mask] == d.min())
            else:
                idx = np.argwhere(d.flatten() == d.min())
            self._mask[idx] = float(not self._mask[idx])
            i, j = np.argwhere(d == d.min())[0]
            self.mask[i, j] = float(not self.mask[i, j])
            self._pc.set_array(self._mask)
            self._pc.changed()
            plt.draw()

    def __init__(self, xv, yv, mask, **kwargs):
        if xv.shape != yv.shape:
            raise ValueError('xv and yv must have the same shape')
        for dx, dq in zip(xv.shape, mask.shape):
             if dx != dq+1:
                raise ValueError('xv and yv must be cell verticies '
                                 '(i.e., one cell bigger in each dimension)')

        self.xv = xv
        self.yv = yv

        self.mask = mask

        land_color = kwargs.pop('land_color', (0.6, 1.0, 0.6))
        sea_color = kwargs.pop('sea_color', (0.6, 0.6, 1.0))

        cm = plt.matplotlib.colors.ListedColormap([land_color, sea_color],
                                                 name='land/sea')
        self._pc = plt.pcolor(xv, yv, mask, cmap=cm, vmin=0, vmax=1, **kwargs)
        self._xc = 0.25*(xv[1:,1:]+xv[1:,:-1]+xv[:-1,1:]+xv[:-1,:-1])
        self._yc = 0.25*(yv[1:,1:]+yv[1:,:-1]+yv[:-1,1:]+yv[:-1,:-1])

        if isinstance(self.xv, np.ma.MaskedArray):
            self._mask = mask[~self._xc.mask]
        else:
            self._mask = mask.flatten()

        plt.connect('button_press_event', self._on_click)
        plt.connect('key_press_event', self._on_key)
        self._clicking = False
        plt.title('Editing %s -- click "e" to toggle' % self._clicking)
        plt.draw()
