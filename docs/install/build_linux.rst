
Linux: Building from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Building ``pygridgen`` and it's dependencies from source should be
pretty straight-forward. Here's a bare bones guide (assuming an Ubuntu-ish distro).

Basic linux stuff
^^^^^^^^^^^^^^^^^

::

    $ sudo apt-get update && sudo apt-get upgrade
    $ sudo apt-get autoremove libreoffice-common
    $ sudo apt-get install git vim build-essential gfortran

Getting miniconda and creating an environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
    $ chmod +x miniconda.sh
    $ ./miniconda.sh -b -p $HOME/miniconda
    $ export PATH=$HOME/miniconda/bin:$PATH
    $ conda update --yes conda
    $ conda create --name=grid python=3.5 pip nose matplotlib numpy --yes
    $ source activate grid

Dealing with projected data:
''''''''''''''''''''''''''''

::

    $ conda install --channel=IOOS pyproj --yes

Cloning dependencies from github
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ mkdir gridlibs && cd gridlibs
    $ # C libraries
    $ git clone https://github.com/sakov/nn-c.git
    $ git clone https://github.com/sakov/csa-c.git
    $ git clone https://github.com/sakov/gridutils-c.git
    $ git clone https://github.com/sakov/gridgen-c.git
    $ # python library
    $ git clone https://github.com/phobson/pygridgen.git

Building C/C++ dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^

natural neighbors
'''''''''''''''''

::

    $ cd nn
    $ ./configure && sudo make install
    $ cd ..

csa
'''

::

    $ cd csa
    $ ./configure && sudo make install
    $ cd ..

gridutils
'''''''''

::

    $ cd gridutils
    $ ./configure CFLAGS="-g -O2 -Wall -pedantic -fPIC"
    $ sudo make install
    $ cd ..

gridgen-C
'''''''''

::

    $ cd gridgen
    $ ./configure
    $ sudo make
    $ sudo make lib
    $ sudo make shlib
    $ sudo make install
    $ cd ..

Install pygridgen
^^^^^^^^^^^^^^^^^

::

    $ cd pygridgen
    $ source activate gridgen
    $ pip install .
