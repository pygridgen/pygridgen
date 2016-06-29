
Mac OS X: building from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Building ``pygridgen`` and its dependencies from source should be
pretty straight-forward. Here's a bare bones guide that was last tested
on Lion.

Basic stuff
^^^^^^^^^^^

You probably need XCode and the XCode command line stuff installed. Get
XCode from the Mac App store and setup the command line tools from
within XCode or from the command line itself.

http://osxdaily.com/2014/02/12/install-command-line-tools-mac-os-x/

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
    $ ./configure
    $ make clean
    $ sudo make install
    $ cd ..

csa
'''

::

    $ cd csa
    $ ./configure
    $ make clean
    $ sudo make install
    $ cd ..

gridutils
'''''''''

::

    $ cd gridutils
    $ ./configure
    $ make clean
    $ sudo make install
    $ cd ..

gridgen-C
'''''''''

::

    $ cd gridgen
    $ ./configure
    $ make clean
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
