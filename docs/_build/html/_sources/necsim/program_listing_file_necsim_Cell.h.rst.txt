
.. _program_listing_file_necsim_Cell.h:

Program Listing for File Cell.h
===============================

- Return to documentation for :ref:`file_necsim_Cell.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef CELL_H
   #define CELL_H
   
   struct Cell
   {
       long x;
       long y;
       Cell &operator=(Cell const& c)
       = default;
   };
   
   #endif // CELL_H
