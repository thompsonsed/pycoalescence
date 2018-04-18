

.. _file_necsim_Metacommunity.h:

File Metacommunity.h
====================



Generates a neutral metacommunity. 


.. contents:: Contents
   :local:
   :backlinks: none

Definition (``necsim/Metacommunity.h``)
---------------------------------------


.. toctree::
   :maxdepth: 1

   program_listing_file_necsim_Metacommunity.h.rst



Detailed Description
--------------------

Generates a metacommunity using spatially-implicit neutral simulations, which is used to draw individuals from a community.
Samuel Thompson
MIT Licence. Individuals will be drawn from the metacommunity for each speciation event, instead of creating a new species each time. The metacommunity itself is generated using spatially-implicit neutral simulations.
Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com



Includes
--------


- ``Community.h`` (:ref:`file_necsim_Community.h`)

- ``NRrand.h`` (:ref:`file_necsim_NRrand.h`)

- ``SpecSimParameters.h`` (:ref:`file_necsim_SpecSimParameters.h`)

- ``Tree.h`` (:ref:`file_necsim_ProtractedSpatialTree.h`)

- ``set``

- ``sqlite3.h``

- ``string``



Included By
-----------


- :ref:`file_necsim_Metacommunity.cpp`




Classes
-------


- :ref:`class_Metacommunity`

