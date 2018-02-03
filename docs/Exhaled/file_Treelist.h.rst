

.. _file_Treelist.h:

File Treelist.h
========================================================================================



Contains the :ref:`class_Treelist` object, which is used for reconstructing the coalescence tree after simulations are complete. The primary file used by :ref:`file_Treelist.cpp` and :ref:`file_SpeciationCounter.cpp`. 


.. contents:: Contents
   :local:
   :backlinks: none

Definition (``Treelist.h``)
----------------------------------------------------------------------------------------


.. toctree::
   :maxdepth: 1

   program_listing_file_Treelist.h.rst



Detailed Description
----------------------------------------------------------------------------------------

Samuel Thompson 
31/08/16
1.1 For use with Coal_sim 3.1 and above. 
BSD-3 Licence. 




Includes
----------------------------------------------------------------------------------------


- ``CustomExceptions.h`` (:ref:`file_CustomExceptions.h`)

- ``Datamask.h`` (:ref:`file_Datamask.h`)

- ``Logging.h`` (:ref:`file_Logging.h`)

- ``Matrix.h`` (:ref:`file_Matrix.h`)

- ``Treenode.h`` (:ref:`file_Treenode.h`)

- ``boost/filesystem.hpp``

- ``boost/lexical_cast.hpp``

- ``cmath``

- ``cstring``

- ``math.h``

- ``sqlite3.h``

- ``stdexcept``

- ``string``



Included By
----------------------------------------------------------------------------------------


- :ref:`file_ApplySpec.h`

- :ref:`file_Tree.h`

- :ref:`file_Treelist.cpp`




Classes
----------------------------------------------------------------------------------------


- :ref:`struct_CalcPairArray`

- :ref:`struct_Fragment`

- :ref:`struct_PreviousCalcPair`

- :ref:`class_Samplematrix`

- :ref:`class_Treelist`


Functions
----------------------------------------------------------------------------------------


- :ref:`function_checkSpeciation`

- :ref:`function_doubleCompare`

