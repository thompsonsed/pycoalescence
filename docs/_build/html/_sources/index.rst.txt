.. PyCoalescence documentation master file, created by
   sphinx-quickstart on Mon Oct 24 17:19:28 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Welcome to PyCoalescence
========================

PyCoalescence is a python package for running and analysing spatially-explicit neutral ecology simulations efficiently and easily.
Input your maps and output a simulated landscape of individuals.

There are two parts to this project. Models are run in :ref:`NECSim <Introduction_NECSim>`, built in ``c++``,
using coalescence methods. Most users will not need to use this tool directly.
:ref:`PyCoalescence <Introduction_PyCoalescence>` is an API for NECSim that aids setting up, running and
analysing models.


.. toctree::
    :maxdepth: 2

    README_PyCoalescence


.. toctree::
    :maxdepth: 2

    Exhaled/exhaled_library

Code Documentation
==================

.. toctree::
    :maxdepth: 2

    modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Version |release|

.. include:: citations.rst
