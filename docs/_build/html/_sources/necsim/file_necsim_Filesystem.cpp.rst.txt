

.. _file_necsim_Filesystem.cpp:

File Filesystem.cpp
===================



Contains routines for checking files and folder exist, opening sqlite databases safely, with support for various virtual filesystems, and checking parents of a file exist. 


.. contents:: Contents
   :local:
   :backlinks: none

Definition (``necsim/Filesystem.cpp``)
--------------------------------------


.. toctree::
   :maxdepth: 1

   program_listing_file_necsim_Filesystem.cpp.rst



Detailed Description
--------------------

Samuel Thompson 
19/07/2017
MIT Licence. Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com 




Includes
--------


- ``CustomExceptions.h`` (:ref:`file_necsim_CustomExceptions.h`)

- ``Filesystem.h`` (:ref:`file_necsim_Filesystem.h`)

- ``Logging.h`` (:ref:`file_necsim_Logging.h`)

- ``boost/filesystem.hpp``

- ``sstream``

- ``string``

- ``zconf.h``






Functions
---------


- :ref:`function_cantorPairing`

- :ref:`function_createParent`

- :ref:`function_doesExist`

- :ref:`function_doesExistNull`

- :ref:`function_getCsvLineAndSplitIntoTokens`

- :ref:`function_openSQLiteDatabase`

