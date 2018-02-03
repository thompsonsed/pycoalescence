
.. _program_listing_file_ReproductionMap.h:

Program Listing for File ReproductionMap.h
========================================================================================

- Return to documentation for :ref:`file_ReproductionMap.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef REPRODUCTIONMAP_H
   #define REPRODUCTIONMAP_H
   
   #include <cstring>
   #include <string>
   #include <stdio.h>
   #include <iostream>
   #include <fstream>
   
   #include "Matrix.h"
   #include "Fattaildeviate.h"
   
   
   class ReproductionMap
   {
   protected:
       // Matrix containing the relative reproduction probabilities
       Matrix<double> reproduction_map;
       // Path to the map file
       string map_file;
       // Maximum value across the map
       double max_val;
       // If true,
       bool null_map;
       // The fine map offsets and the sample map dimensions
       unsigned long offset_x, offset_y, x_dim, y_dim;
       // Function pointer for our reproduction map checker
       typedef bool (ReproductionMap::*rep_ptr)(NRrand &random_no,
                                                const unsigned long &x, const unsigned long &y,
                                                const long &xwrap, const long &ywrap);
       // once setup will contain the end check function to use for this simulation.
       rep_ptr reproductionMapChecker_fptr;
   public:
       ReproductionMap()
       {
           map_file = "none";
           max_val = 0;
           null_map = true;
       }
   
       void import(string file_name, unsigned long size_x, unsigned long size_y);
   
       void setReproductionFunction();
   
       void setOffsets(const unsigned long &x_offset, const unsigned long &y_offset,
                       const unsigned long &xdim, const unsigned long &ydim);
   
       bool rejectionSampleNull(NRrand &random_number, const unsigned long &x, const unsigned long &y, const long &xwrap,
                                const long &ywrap);
   
       bool rejectionSample(NRrand &random_number, const unsigned long &x, const unsigned long &y,
                        const long &xwrap, const long &ywrap);
   
       double getVal(const unsigned long &x, const unsigned long &y, const long &xwrap, const long &ywrap);
   
       bool hasReproduced(NRrand &random_number, const unsigned long &x, const unsigned long &y,
                          const long &xwrap, const long &ywrap);
   
       Row<double> operator[](long index)
       {
           return reproduction_map[index];
       }
   
       friend ostream& operator<<(ostream& os, ReproductionMap&r)
       {
           os << r.map_file << "\n";
           os << r.reproduction_map.GetCols() << "\n";
           os << r.reproduction_map.GetRows() << "\n";
           os << r.offset_x << "\n";
           os << r.offset_y << "\n";
           os << r.x_dim << "\n";
           os << r.y_dim << "\n";
           return os;
       }
   
       friend istream& operator>>(istream &is, ReproductionMap &r)
       {
           is.ignore();
           getline(is, r.map_file);
           unsigned long col, row;
           is >> col >> row;
           is >> r.offset_x >> r.offset_y >> r.x_dim >> r.y_dim;
           r.import(r.map_file, col, row);
           return is;
       }
   
   
   };
   
   
   #endif //REPRODUCTIONMAP_H
