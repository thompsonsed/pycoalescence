pycoalescence overview
======================

*A package for coalescence-based spatially explicit neutral ecology simulations*


.. list-table::
    :widths: auto
    :align: center
    :header-rows: 1

    * - Documentation
      - Examples
      - Conda version
      - PyPi version
    * - |Documentation|_
      - |Binder|_
      - |CondaV|_
      - |PyPiV|_

|

.. list-table::
    :widths: auto
    :align: center
    :header-rows: 1

    * - Windows
      - macOS
      - Linux
    * - |AppVeyorWin|_
      - |TravisCI|_
      - |CircleCI|_

.. |Documentation| image:: https://readthedocs.org/projects/pip/badge/?version=latest&style=flat
.. _Documentation: https://pycoalescence.readthedocs.io

.. |Binder| image:: https://mybinder.org/badge.svg
.. _Binder: https://mybinder.org/v2/gh/thompsonsed/pycoalescence_examples/master?filepath=%2Fhome%2Fpycoalescence_examples%2F

.. |CondaV| image:: https://img.shields.io/conda/vn/conda-forge/pycoalescence.svg
.. _CondaV: https://anaconda.org/conda-forge/pycoalescence

.. |PyPiV| image:: https://badge.fury.io/py/pycoalescence.svg
.. _PyPiV: https://badge.fury.io/py/pycoalescence

.. |CircleCI| image:: https://circleci.com/bb/thompsonsed/pycoalescence.svg?style=svg
.. _CircleCI: https://circleci.com/bb/thompsonsed/pycoalescence

.. |TravisCI| image:: https://travis-ci.org/pycoalescence/pycoalescence-ci.svg?branch=master
.. _TravisCI: https://travis-ci.org/pycoalescence/pycoalescence-ci

.. |AppVeyorWin| image:: https://ci.appveyor.com/api/projects/status/3qex6in9w1384f57/branch/master?svg=true
.. _AppVeyorWin: https://ci.appveyor.com/project/thompsonsed1992/pycoalescence-ci



Introduction
~~~~~~~~~~~~

pycoalescence is a Python package for spatially explicit coalescence neutral simulations. pycoalescence provides a
pythonic interface for setting up, running and analysing spatially explicit neutral simulations. Simulations themselves
are performed in C++ using `necsim <https://pycoalescence.readthedocs.io/en/release/necsim/necsim_library.html>`__ for
excellent performance, whilst the Python interface provides a simple solution for setting up and analysing simulations.

For full documentation please see `here <https://pycoalescence.readthedocs.io/en/release/>`__.

Installation
~~~~~~~~~~~~
Usage of conda is recommended to aid handling installation of dependencies.

Installation is available through pip, conda or a manual installation. For full installation instructions, see
`here <https://pycoalescence.readthedocs.io/en/release/README_pycoalescence.html#installation>`__.

Currently, pip is supported on Mac OS X and Linux and conda is supported on Mac OS X, Linux and Windows.

Using pip, make sure all the prerequisites are installed and run ``pip install pycoalescence``.

If you cannot install via pip, download the tar ball and run ``python setup.py install``. The package can also be
installed locally, (i.e not to the virtual or system environment) using ``python installer.py`` in the module directory.
Either method requires all dependencies have been installed. By default, .o files are compiled to lib/obj and the .so
or .dylib file is compiled to the necsim directory.

Make sure compilation is performed under the same Python version simulations will be performed in.

Requirements
~~~~~~~~~~~~

Essential
^^^^^^^^^

-  Python version 2 >= 2.7.9 or 3 >= 3.6.1 (although earlier version may work)
-  C++ compiler (such as GNU g++) with C++14 support.
-  The SQLite library available `here <https://www.sqlite.org/download.html>`__ (comes included with Python). Requires
   both C++ and Python installations.
-  The Boost library for C++ available `here <https://www.boost.org>`__.
-  Numerical Python (``numpy``) package (``pip install numpy``).
-  The gdal library for both Python and C++ (`available here <https://www.gdal.org/>`__) including development options.
   Both the Python package and C++ binaries are required; installation differs between systems, so view the gdal
   documentation for more help installing gdal properly.

Recommended
^^^^^^^^^^^

-  Scipy package for generating fragmented landscapes
   (``pip install scipy``).

-  Matplotlib package for plotting fragmented landscapes
   (``pip install matplotlib``).

Optional
^^^^^^^^

-  For work involving large csv files, the fast-cpp-csv-parser by Ben Strasser, available
   `here <https://github.com/ben-strasser/fast-cpp-csv-parser>`__ can be used. This provides much faster csv read and
   write capabilities and is probably essential for larger-scale simulations, but not necessary if your simulations are
   small or you are intending to use *.tif* files (the recommended method). The folder
   *fast-cpp-csv-parser/* should be in the same directory as your **necsim** C++ header files (the lib/necsim directory)
   and requires manual installation.

.. note:: fast-cpp-csv-parser is no longer tested with updated versions of that package, but should still be functional.

Basic Usage
~~~~~~~~~~~

The Simulation class contains most of the operations required for
setting up a coalescence simulation. The important set up functions are:

-  ``set_simulation_parameters()`` sets a variety of key simulation
   variables, including the seed, output directory, dispersal parameters
   and speciation rate.
-  ``set_map()`` is used to specify a map file to use. More complex map
   file set-ups can be provided using ``set_map_files``.
   ``set_map_parameters()`` can also be used to customise parameters,
   instead of detecting from the provided tif files.
-  ``set_speciation_rates()`` takes a list of speciation rates to apply
   at the end of the simulation. This is optional.
-  ``run()`` checks and starts the simulation, writing to the output
   database upon successful completion. This stage can take an extremely
   long time (up to tens of hours) depending on the size of the
   simulation and the dispersal variables. Upon completion, an SQL file
   will have been created containing the coalescence tree.

The CoalescenceTree class also contains some basic analysis abilities,
such as applying additional speciation rates post-simulation, or
calculating species abundances for fragments within the main simulation.

The basic procedure for this procedure is

-  ``set_database()`` to provide the path to the completed simulation
   database
-  ``set_speciation_parameters()`` which takes as arguments

   -  T/F of recording full spatial data
   -  either a csv file containing fragment data, or T/F for whether
      fragments should be calculated from squares of continuous habitat.
   -  list of speciation rates to apply
   -  [optional] a sample file to specify certain cells to sample from
   -  [optional] a config file containing the temporal sampling points
      desired.

-  ``apply()`` performs the analysis. This can be extremely RAM and
   time-intensive for large simulations. The calculations will be stored
   in extra tables within the same SQL file as originally specified.

-  ``get_species_richness()`` or other equivalent functions to obtain the
   required metrics of biodiversity.


CONTACTS
~~~~~~~~

Author: Samuel Thompson

Contact: samuelthompson14@imperial.ac.uk - thompsonsed@gmail.com

Institution: Imperial College London and National University of
Singapore

This project is released under MIT licence. See file **LICENSE.txt** or
go to `here <https://opensource.org/licenses/MIT>`__ for full license
details.
