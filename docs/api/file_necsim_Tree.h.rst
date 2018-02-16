

.. _file_necsim_Tree.h:

File Tree.h
===========



Contains the :ref:`class_Tree` class implementation as the main simulation object for spatially-implicit coalescence simulations. Provides the basis for spatially-explicit versions in :ref:`class_SpatialTree`, and protracted speciation versions in :ref:`class_ProtractedTree` and :ref:`class_ProtractedSpatialTree`. 


.. contents:: Contents
   :local:
   :backlinks: none

Definition (``necsim/Tree.h``)
------------------------------


.. toctree::
   :maxdepth: 1

   program_listing_file_necsim_Tree.h.rst



Detailed Description
--------------------

Main simulation class for performing a non-spatial neutral simulation and generating the phylogenetic tree of the individuals.
Samuel Thompson 
24/03/17
BSD-3 Licence.




Includes
--------


- ``Community.h`` (:ref:`file_necsim_Community.h`)

- ``CustomExceptions.h`` (:ref:`file_necsim_CustomExceptions.h`)

- ``DataPoint.h`` (:ref:`file_necsim_DataPoint.h`)

- ``Filesystem.h`` (:ref:`file_necsim_Filesystem.h`)

- ``Matrix.h`` (:ref:`file_necsim_Matrix.h`)

- ``NRrand.h`` (:ref:`file_necsim_NRrand.h`)

- ``SimParameters.h`` (:ref:`file_necsim_SimParameters.h`)

- ``Step.h`` (:ref:`file_necsim_Step.h`)

- ``TreeNode.h`` (:ref:`file_necsim_TreeNode.h`)

- ``sqlite3.h``



Included By
-----------


- :ref:`file_necsim_SpatialTree.h`

- :ref:`file_necsim_Metacommunity.h`

- :ref:`file_necsim_Tree.cpp`




Classes
-------


- :ref:`class_Tree`


Defines
-------


- :ref:`define_sql_ram`

