
.. _file_necsim_main.cpp:

File main.cpp
=============

|exhale_lsh| :ref:`Parent directory <dir_necsim>` (``necsim``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS


A generic simulator for spatially explicit coalescence models suitable for HPC applications. It contains all functions for running large-scale simulations backwards in time using coalescence techniques. Outputs include an SQLite database containing spatial and temporal information about tracked lineages, and allow for rebuilding of the coalescence tree. 
 

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

Currently, a fat-tailed dispersal kernel or normal distribution can be used for dispersal processes.
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


- ``Logger.h`` (:ref:`file_necsim_Logger.h`)

- ``Logging.h`` (:ref:`file_necsim_Logging.h`)

- ``SimulationTemplates.h`` (:ref:`file_necsim_SimulationTemplates.h`)

- ``SpatialTree.h`` (:ref:`file_necsim_ProtractedSpatialTree.h`)






Functions
---------


- :ref:`exhale_function_main_8cpp_1a0ddf1224851353fc92bfbff6f499fa97`

