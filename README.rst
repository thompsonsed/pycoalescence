pycoalescence overview
======================

*A package for coalescence-based spatially explicit neutral ecology simulations*

|Documentation|_ |Binder|_ |CondaV|_ |CondaPlatform|_ |PyPiV|_ |PyPiLinux|_ |License|_


.. |Documentation| image:: https://img.shields.io/readthedocs/pycoalescence/latest.svg?label=documentation
.. _Documentation: https://pycoalescence.readthedocs.io

.. |Binder| image:: https://img.shields.io/badge/examples-launch-579ACA.svg?logo=data:image/png;base64,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
.. _Binder: https://mybinder.org/v2/gh/thompsonsed/pycoalescence_examples/master?filepath=%2Fhome%2Fpycoalescence_examples%2F

.. |CondaV| image:: https://img.shields.io/conda/vn/conda-forge/pycoalescence.svg?label=conda
.. _CondaV: https://anaconda.org/conda-forge/pycoalescence

.. |CondaPlatform| image:: https://img.shields.io/conda/pn/conda-forge/pycoalescence?label=conda
.. _CondaPlatform: https://anaconda.org/conda-forge/pycoalescence

.. |PyPiV| image:: https://img.shields.io/pypi/v/pycoalescence.svg
.. _PyPiV: https://badge.fury.io/py/pycoalescence

.. |License| image:: https://img.shields.io/pypi/l/pycoalescence
.. _License: https://opensource.org/licenses/MIT

.. |PyPiLinux| image:: https://img.shields.io/circleci/project/github/thompsonsed/pycoalescence.svg?label=Linux&logo=circleci
.. _PyPiLinux: https://circleci.com/github/thompsonsed/pycoalescence


Introduction
~~~~~~~~~~~~

pycoalescence is a Python package for spatially explicit coalescence neutral simulations. pycoalescence provides a
pythonic interface for setting up, running and analysing spatially explicit neutral simulations. Simulations themselves
are performed in C++ using `necsim <https://pycoalescence.readthedocs.io/en/release/necsim/necsim_library.html>`__ for
excellent performance, whilst the Python interface provides a simple solution for setting up and analysing simulations.

For full documentation please see `here <https://pycoalescence.readthedocs.io/en/release/>`__.

For R users, there is a sister package with (mostly) equivalent functionality, which can be found `here <https://github.com/thompsonsed/rcoalescence.git>`__.


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

-  Python version 2 >= 2.7.9 or 3 >= 3.6.1 (although earlier versions may work)
-  C++ compiler (such as GNU g++) with C++14 support.
-  The SQLite library available `here <https://www.sqlite.org/download.html>`__ (comes included with Python). Requires
   both C++ and Python installations.
-  The Boost library for C++ available `here <https://www.boost.org>`__.
-  Numerical Python (``numpy``) package (``pip install numpy``).
-  The gdal library for both Python and C++ (`available here <https://www.gdal.org/>`__) including development options.
   Both the Python package and C++ binaries are required; installation differs between systems, so view the gdal
   documentation for more help installing gdal properly.
- The `proj library <https://proj.org/install.html>`__ for converting between coordinate systems.

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
   file set-ups can be provided using ``set_map_files()`` can also be
   used to customise parameters, instead of detecting from the provided
   tif files.
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

   -  list of speciation rates to apply
   -  T/F of recording full spatial data
   -  either a csv file containing fragment data, or T/F for whether
      fragments should be calculated from squares of continuous habitat.
   -  [optional] a sample file to specify certain cells to sample from
   -  [optional] a config file containing the temporal sampling points
      desired.

-  ``apply()`` performs the analysis. This can be extremely RAM and
   time-intensive for large simulations. The calculations will be stored
   in extra tables within the same SQL file as originally specified.

-  ``get_species_richness()`` or other equivalent functions to obtain the
   required metrics of biodiversity.


Contacts
~~~~~~~~

Author: Samuel Thompson

Contact: samuel.thompson14@imperial.ac.uk - thompsonsed@gmail.com

Institution: Imperial College London and National University of
Singapore

This project is released under MIT licence. See file **LICENSE.txt** or
go to `here <https://opensource.org/licenses/MIT>`__ for full license
details.
