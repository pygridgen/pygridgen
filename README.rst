`pygridgen`
===========
.. image:: https://travis-ci.org/pygridgen/pygridgen.svg?branch=master
    :target: https://travis-ci.org/pygridgen/pygridgen
.. image:: https://coveralls.io/repos/pygridgen/pygridgen/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/pygridgen/pygridgen?branch=master


A Python interface to Pavel Sakov's `gridgen`_ library

.. _gridgen: https://github.com/sakov/gridgen-c

The full documentation for this for library is `here`_.

.. _here: https://pygridgen.github.io/pygridgen

For more detailed documentation on grid generation, manipulation, and visualization,
see the documentation for `pygridtools`_.

.. _pygridtools: https://geosyntec.github.io/pygridtools


Credits
-------
This fork of ``pygridgen`` stands on the very tall shoulders of `Robert Hetland`_ of Texas A&M University.
Many thanks to him, `Richard Signell`_, `Filipe Fernandes`_, and all of the other contributors.

.. _Robert Hetland: https://github.com/hetland
.. _Richard Signell: https://github.com/rsignell-usgs
.. _Filipe Fernandes: https://github.com/ocefpaf


Dependencies
------------

C Libraries
~~~~~~~~~~~

The following dependencies are all available via conda-forge for Linux and Mac OS:

* `nn feedstock`_
* `csa feedstock`_
* `gridgen feedstock`_
* `gridutils feedstock`_

.. _nn feedstock: https://github.com/conda-forge/nn-feedstock
.. _csa feedstock: https://github.com/conda-forge/csa-feedstock
.. _gridgen feedstock: https://github.com/conda-forge/gridgen-feedstock
.. _gridutils feedstock: https://github.com/conda-forge/gridutils-feedstock


Python
~~~~~~

Provided that all of the shared C libraries are installed, the remaining python depedencies are the following:

* numpy
* matplotlib
* pyproj (only if working with geographic coordinates)

Testing
~~~~~~~

Tests are written using the `pytest` package.
From the source tree, run them simply with by invoking ``pytest`` in a terminal.
If you're editing the source code, it helps to have `pytest-pep8` installed to check code style.

Alternatively, from the source tree you can run ``python check_pygridgen.py --strict`` to run the units tests, style checker, and doctests.

Documentation
~~~~~~~~~~~~~
Building the HTML documentation requires:

* sphinx
* sphinx_rtd_theme
* nbsphinx
* jupyter-notebook
* pandas
* seaborn
