
.. _program_listing_file_necsim_Cell.cpp:

Program Listing for File Cell.cpp
=================================

- Return to documentation for :ref:`file_necsim_Cell.cpp`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #include <cmath>
   #include "Cell.h"
   
   double distanceBetweenCells(Cell &c1, Cell &c2)
   {
       return pow(pow(c1.x - c2.x, 2) + pow(c1.y - c2.y, 2), 0.5);
   }
