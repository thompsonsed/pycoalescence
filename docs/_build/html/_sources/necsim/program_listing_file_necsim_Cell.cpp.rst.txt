
.. _program_listing_file_necsim_Cell.cpp:

Program Listing for File Cell.cpp
=================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_Cell.cpp>` (``necsim/Cell.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #include <cmath>
   #include "Cell.h"
   
   double distanceBetweenCells(Cell &c1, Cell &c2)
   {
       return pow(pow(c1.x - c2.x, 2) + pow(c1.y - c2.y, 2), 0.5);
   }
