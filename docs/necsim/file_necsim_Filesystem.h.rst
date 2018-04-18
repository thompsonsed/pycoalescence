

.. _file_necsim_Filesystem.h:

File Filesystem.h
=================



Contains routines for checking files and folder exist, opening sqlite databases safely, with support for various virtual filesystems, and checking parents of a file exist. 


.. contents:: Contents
   :local:
   :backlinks: none

Definition (``necsim/Filesystem.h``)
------------------------------------


.. toctree::
   :maxdepth: 1

   program_listing_file_necsim_Filesystem.h.rst



Detailed Description
--------------------

Samuel Thompson 
19/07/2017
MIT Licence. Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com 




Includes
--------


- ``sqlite3.h``

- ``string``



Included By
-----------


- :ref:`file_necsim_Community.cpp`

- :ref:`file_necsim_Filesystem.cpp`

- :ref:`file_necsim_Landscape.cpp`

- :ref:`file_necsim_LogFile.cpp`

- :ref:`file_necsim_Tree.h`

- :ref:`file_necsim_SimulateDispersal.cpp`




Functions
---------


- :ref:`function_cantorPairing`

- :ref:`function_createParent`

- :ref:`function_doesExist`

- :ref:`function_doesExistNull`

- :ref:`function_getCsvLineAndSplitIntoTokens`

- :ref:`function_openSQLiteDatabase`

