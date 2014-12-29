# pygridgen

A Python interface to Pavel Sakov's C-based Gridgen Orthogonal Grid
Generation Package

## Components

  + **simple GUI interface** - The GUI interface uses native matplotlib
    widgets for even more portability.
  + **arbitrary number of corners** - More corners means more complicated
    domains.  Great for domains with bays, estuaries, and other complicated
    features.
  + **a single orthogonal grid as a result** - Whites whiter!
    Brights brighter!

## Install

We are working on packaging using Bento or binstar. When that happens
it'll be very easy to install. For now, here's a *very* rough outline.
More details in [INSTALLING](INSTALLING.md)

  + cd external/nn; ./configure ; make install
  + cd external/csa; ./configure ; make install
  + cd external/gridutils; ./configure ; make install
  + cd external/gridgen; ./configure ; make shlib
  + cd pygridgen; python setup.py install

## Dependencies:
  + numpy
  + matplotlib
  + pyproj or basemap

## Examples

### Basic Example
```python

import matplotlib.pyplot as plt
import pygridgen
x = [0, 1, 2, 1, 0]
y = [0, 0, 1, 2, 2]
beta = [1, 1, 0, 1, 1]

grid = pygridgen.grid.Gridgen(x, y, beta, shape=(10, 5))

fig, ax = plt.subplots()
ax.plot(x, y, 'k-')
ax.plot(grid.x, grid.y, 'b.')
plt.show()
```
