.. pycoalescence documentation master file, created by
   sphinx-quickstart on Mon Oct 24 17:19:28 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Welcome to pycoalescence
========================

.. include:: builds.rst

**pycoalescence** is a python package for running and analysing spatially-explicit neutral ecology simulations efficiently and easily.
Input your maps and output a simulated landscape of individuals.

There are two parts to this project. Models are run in :ref:`necsim <Introduction_necsim>`, built in c++,
using coalescence methods. Most users will not need to use this tool directly.
:ref:`pycoalescence <Introduction_pycoalescence>` is an API for necsim that aids setting up, running and
analysing models.


.. toctree::
    :maxdepth: 2

    README_pycoalescence

.. toctree::
    :maxdepth: 2

    necsim/necsim_library

.. toctree::
    :maxdepth: 2
    
    README_landscapes

.. toctree::
    :maxdepth: 2

    README_merger

Code examples
=============

.. toctree::
    :maxdepth: 2

    src/examples


Code Documentation
==================

.. toctree::
    :maxdepth: 2

    modules


Indices and tables
==================

* :ref:`search`

Version |release|

.. include:: citations.rst
