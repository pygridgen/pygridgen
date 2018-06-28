import numpy as np
import matplotlib.pyplot as plt
from pygridgen import csa
xin = np.random.randn(10000)
yin = np.random.randn(10000)
zin = np.sin( xin**2 + yin**2 ) / (xin**2 + yin**2 )
xout, yout = np.mgrid[-3:3:10j, -3:3:10j]
csa_interp = csa.CSA(xin, yin, zin)
zout = csa_interp(xout, yout)
img = plt.imshow(zout)