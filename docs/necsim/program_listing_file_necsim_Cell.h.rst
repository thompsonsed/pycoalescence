
.. _program_listing_file_necsim_Cell.h:

Program Listing for File Cell.h
===============================

- Return to documentation for :ref:`file_necsim_Cell.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef CELL_H
   #define CELL_H
   
   struct Cell
   {
       long x;
       long y;
       Cell &operator=(Cell const& c)
       = default;
   
       bool operator==(Cell const&c)
       {
           return x == c.x && y == c.y;
       }
   
       bool operator!=(Cell const&c)
       {
           return !(this->operator==(c));
       }
   };
   
   
   double distanceBetweenCells(Cell &c1, Cell &c2);
   
   #endif // CELL_H
