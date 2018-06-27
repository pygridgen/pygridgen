import matplotlib.pyplot as plt
import pygridgen
# define the boundary (pentagon)
x = [0, 1, 2, 1, 0, 0]
y = [0, 0, 1, 2, 2, 0]
beta = [1, 1, 0, 1, 1]
# define the focus
focus = pygridgen.grid.Focus()
focus.add_focus(0.5, 'x', factor=3, extent=0.2)
focus.add_focus(0.75, 'y', factor=5, extent=0.1)
# create the grid
grid = pygridgen.Gridgen(x, y, beta, shape=(20, 20), focus=focus)
# plot the grid
fig, ax = plt.subplots()
ax.plot(x, y, 'k-', lw=1.25, zorder=0, alpha=0.25)
ax.plot(grid.x, grid.y, 'k.', zorder=5)
plt.show()