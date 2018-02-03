

.. _file_Matrix.h:

File Matrix.h
========================================================================================



Contains a template for a matrix with all the basic matrix operations overloaded. 


.. contents:: Contents
   :local:
   :backlinks: none

Definition (``Matrix.h``)
----------------------------------------------------------------------------------------


.. toctree::
   :maxdepth: 1

   program_listing_file_Matrix.h.rst



Detailed Description
----------------------------------------------------------------------------------------

James Rosindell 
31/08/16
1.2 
BSD-3 Licence.
Created with large usage of  href = "http://www.devarticles.com/c/a/Cplusplus/Operator-Overloading-in-C-plus/1"> this website . There are two distinct classes, :ref:`template_class_Row` and :ref:`template_class_Matrix`. Most operations are low-level, but some higher level functions remain, such as importCsv().
Modified to include additional functionality by Samuel Thompson (Imperial College London).
Contact: thompsonsed@gmail.com
UPDATES:


- version 1.1 fixed memory leak in matrix
- version 1.11 also changed policy for acessing invalid areas of the matrix to periodic
- version 1.12 added :ref:`template_class_Row` ifstream and ostream operators, removed debugging code
- version 1.2 added .tif import support 




Includes
----------------------------------------------------------------------------------------


- ``Logging.h`` (:ref:`file_Logging.h`)

- ``assert.h``

- ``cstdlib``

- ``cstring``

- ``fstream``

- ``iostream``

- ``sstream``

- ``stdexcept``

- ``stdint.h``

- ``stdio.h``



Included By
----------------------------------------------------------------------------------------


- :ref:`file_Treelist.h`

- :ref:`file_Datamask.h`

- :ref:`file_Tree.h`

- :ref:`file_Map.h`

- :ref:`file_DispersalCoordinator.h`

- :ref:`file_ReproductionMap.h`

- :ref:`file_SimulateDispersal.h`




Classes
----------------------------------------------------------------------------------------


- :ref:`template_class_Matrix`

- :ref:`template_class_Row`


Defines
----------------------------------------------------------------------------------------


- :ref:`define_MATRIX`

- :ref:`define_null`

- :ref:`define_version1_11`


Variables
----------------------------------------------------------------------------------------


- :ref:`variable_gdal_data_sizes`

