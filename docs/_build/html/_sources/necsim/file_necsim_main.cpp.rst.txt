

.. _file_necsim_main.cpp:

File main.cpp
=============



A generic simulator for spatially explicit coalescence models suitable for HPC applications. It contains all functions for running large-scale simulations backwards in time using coalescence techniques. Outputs include an SQLite database containing spatial and temporal information about tracked lineages, and allow for rebuilding of the coalescence tree. Currently, a fat-tailed dispersal kernel or normal distribution can be used for dispersal processes. 


.. contents:: Contents
   :local:
   :backlinks: none

Definition (``necsim/main.cpp``)
--------------------------------


.. toctree::
   :maxdepth: 1

   program_listing_file_necsim_main.cpp.rst



Detailed Description
--------------------

Run with -h to see full input options.
Outputs include

- habitat map file(s)
- species richness and species abundances for the supplied minimum speciation rate.
- SQL database containing full spatial data. This can be later analysed by the Speciation_Counter program for applying higher speciation rates.

Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
Based heavily on code written by James Rosindell
Contact: j.rosindell@imperial.ac.uk
Samuel Thompson
MIT Licence. 




Includes
--------


- ``SimulationTemplates.h`` (:ref:`file_necsim_SimulationTemplates.h`)

- ``SpatialTree.h`` (:ref:`file_necsim_ProtractedSpatialTree.h`)






Functions
---------


- :ref:`function_main`

