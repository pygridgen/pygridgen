# Setting up a  Max OS X box for grid generation
(tested on Lion)

## Basics stuff
You probably need XCode and the XCode command line stuff installed.
Get XCode from the Mac App store and setup the command line tools
from within XCode or from the command line itself.

http://osxdaily.com/2014/02/12/install-command-line-tools-mac-os-x/


## Getting miniconda and creating an environment
```
$ wget http://repo.continuum.io/miniconda/Miniconda3-3.7.3-MacOSX-x86_64.sh -O miniconda.sh
$ chmod +x miniconda.sh
$ ./miniconda.sh -b
$ export PATH=/home/grid/miniconda/bin:$PATH  # you'll probably want to do this permanently
$ conda update conda
$ conda create --name=gridgen seaborn statsmodels ipython-notebook pip nose fiona shapely netcdf4 binstar --yes
$ source activate gridgen
```

### Dealing with projected data:

```
$ conda install -c https://conda.binstar.org/asmeurer pyproj --yes
```

Or for more adavanced map-related plotting:

```
$ conda install basemap --yes
```

## Cloning repos from github

```
$ mkdir sources && cd sources
$ git clone https://github.com/geosyntec/pygridgen.git
```

## Building C/C++ dependencies

`$ cd pygridgen/external`

### nearest neighbors
```
$ cd nn
$ ./configure
$ make clean
$ sudo make install
$ cd ..
```

### CSA
```
$ cd csa
$ ./configure
$ make clean
$ sudo make install
$ cd ..
```

### gridutils
```
$ cd gridutils
$ ./configure
$ make clean
$ sudo make install
$ cd ..
```

### gridgen-C
```
$ cd gridgen
$ ./configure
$ make clean
$ sudo make
$ sudo make lib
$ sudo make shlib
$ sudo make install
$ cd ..
```

## Install pygridgen
```
$ cd ~/sources/pygridgen
$ source activate gridgen
$ python setup.py install
```
