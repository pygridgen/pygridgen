import numpy
import pandas
import seaborn

from pygridtools.viz import plot_cells


def plot_grid(grid, data_ax, cell_ax, leg_loc='lower left'):
    cell_ax.set_aspect('equal')
    plot_cells(grid.x, grid.y, ax=cell_ax, cmap='Blues', lw=0.5)
    
    data_ax.set_aspect('equal')

    data_ax.plot(grid.x.flatten(), grid.y.flatten(), 'k.', label='Grid nodes', zorder=5)
    data_ax.plot(grid.xbry, grid.ybry, '-', color='0.5', zorder=0)
    pos = numpy.nonzero(grid.beta > 0)
    neg = numpy.nonzero(grid.beta < 0)
    
    data_ax.plot(grid.xbry[pos], grid.ybry[pos], 'go', label='Positive', zorder=2, alpha=0.5)
    data_ax.plot(grid.xbry[neg], grid.ybry[neg], 'rs', label='Negative', zorder=2, alpha=0.5)
    
    if grid.ul_idx:
        data_ax.plot(grid.xbry[grid.ul_idx-1], grid.ybry[grid.ul_idx-1],
                     marker='s', markersize=10, markeredgewidth=1.5,
                     markerfacecolor='none', markeredgecolor='b',
                     linestyle='none', label='"Upper Left"', zorder=0)
    
    if leg_loc:
        data_ax.legend(numpoints=1, loc=leg_loc)

    if cell_ax.is_first_row():
        cell_ax.set_title('Final grid as cells')
        
    if data_ax.is_first_row():
        data_ax.set_title('Input data and nodes')
        
    seaborn.despine(ax=data_ax, trim=True)
    seaborn.despine(ax=cell_ax, trim=True, left=True)
    cell_ax.set_yticks([])
    

def read_boundary(example):
    df = pandas.read_table("gg_examples/xy.{}".format(example), sep='\s+').fillna(0)
    x, y, beta = df['x'].values, df['y'].values, df['b'].values
    ul_idx = numpy.nonzero(df['ul'])[0][0] + 1
    return x, y, beta, ul_idx