# encoding: utf-8
'''
PYGRIDGEN is a tool for building curvilinear grids.

PYGRIDGEN is based on Pavel Sakov's gridgen c-library, with python capabilities
added through ctypes.  There is also an interactive boundary creator that can be
used for making grids.

(c) Rob Hetland, 2012

Released under an MIT license.

'''

from .grid import *
from .csa import *
from .boundary_interactor import *

__authors__ = ['Robert Hetland <hetland@tamu.edu>',
               'Rich Signell <rsignell@gmail.com']

__version__ = '0.1.0'
