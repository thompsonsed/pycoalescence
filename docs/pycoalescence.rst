pycoalescence package
=====================


.. automodule:: pycoalescence
    :members:
    :undoc-members:
    :show-inheritance:

Module Contents
'''''''''''''''

.. contents::
    :depth: 4
    :local:

Key submodules
''''''''''''''

These are the most important modules for running and analysing spatially-explicit neutral models, and are most likely
to be used directly.

simulation module
-----------------

Run spatially-explicit neutral simulations on provided landscapes with support for a wide range of scenarios and
parameters. Detailed :ref:`here <performing_simulations>`.

.. automodule:: pycoalescence.simulation
    :members:
    :undoc-members:
    :show-inheritance:


coalescence_tree module
-----------------------

Generate the coalescence tree and acquire a number of biodiversity metrics for different parameter sets. Can also be
used to compare against a comparison simulation object. Detailed :ref:`here <Simulate_landscapes>`.


.. automodule:: pycoalescence.coalescence_tree
    :members:
    :undoc-members:
    :show-inheritance:

Additional submodules
'''''''''''''''''''''

All additional modules which are required for package functionality, but are unlikely to be used directly.

dispersal_simulation module
---------------------------

Simulate dispersal kernels on landscapes. Detailed :ref:`here <Simulate_landscapes>`.


.. automodule:: pycoalescence.dispersal_simulation
    :members:
    :undoc-members:
    :show-inheritance:

fragments module
----------------

Generate fragmented landscapes with specific properties. Detailed :ref:`here <Simulate_landscapes>`.


.. automodule:: pycoalescence.fragments
    :members:
    :undoc-members:
    :show-inheritance:

fragments config module
-----------------------

Generate the csv files detailing the locations of sample fragments within the landscape.

.. automodule:: pycoalescence.fragment_config
    :members:
    :undoc-members:
    :show-inheritance:

helper file
-----------

Convert older simulation parameters to new simulation parameters. Should not be required by most users.

.. automodule:: pycoalescence.helper
    :members:
    :undoc-members:
    :show-inheritance:

hpc_setup file
--------------
Compile **necsim** with a number of optimisations for running on high-performance computing systems.

.. automodule:: pycoalescence.hpc_setup
    :members:
    :undoc-members:
    :show-inheritance:

landscape file
--------------

Generate landscapes and check map file combinations.

.. automodule:: pycoalescence.landscape
    :members:
    :undoc-members:
    :show-inheritance:

map module
----------

Open tif files and detect properties and data contained using gdal. Detailed :ref:`here <Simulate_landscapes>`.

.. automodule:: pycoalescence.map
    :members:
    :undoc-members:
    :show-inheritance:

merger module
-------------

Combine simulation outputs from separate guilds. Detailed :ref:`here <merging_simulations>`.

.. automodule:: pycoalescence.merger
    :members:
    :undoc-members:
    :show-inheritance:

patched_landscape module
------------------------

Generate landscapes of interconnected patches for simulating within a spatially-explicit neutral model.
Detailed :ref:`here <generate_landscapes>`.

.. automodule:: pycoalescence.patched_landscape
    :members:
    :undoc-members:
    :show-inheritance:

setup file
----------

Compile **necsim** with default or provided compilation options.

.. automodule:: pycoalescence.setup
    :members:
    :undoc-members:
    :show-inheritance:

spatial_algorithms file
-----------------------

Simple spatial algorithms required for package functionality.

.. automodule:: pycoalescence.spatial_algorithms
    :members:
    :undoc-members:
    :show-inheritance:

sqlite_connection file
----------------------

Safely open, close and fetch data from an sqlite connection.

.. automodule:: pycoalescence.sqlite_connection
    :members:
    :undoc-members:
    :show-inheritance:

system_operations file
----------------------

Basic system-level operations required for package functionality.

.. automodule:: pycoalescence.system_operations
    :members:
    :undoc-members:
    :show-inheritance:




