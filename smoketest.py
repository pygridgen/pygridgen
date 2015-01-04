import matplotlib.pyplot as plt
import pygridgen
x = [0, 1, 2, 1, 0]
y = [0, 0, 1, 2, 2]
beta = [1, 1, 0, 1, 1]

grid = pygridgen.grid.Gridgen(x, y, beta, shape=(10, 5))
