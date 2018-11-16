
.. _program_listing_file_necsim_ActivityMap.h:

Program Listing for File ActivityMap.h
======================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_ActivityMap.h>` (``necsim/ActivityMap.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef ACTIVITYMAP_H
   #define ACTIVITYMAP_H
   
   #include <cstring>
   #include <string>
   #include <cstdio>
   #include <iostream>
   #include <fstream>
   #include <memory>
   #include "Map.h"
   #include "NRrand.h"
   
   class ActivityMap
   {
   protected:
       // Matrix containing the relative activity probabilities
       Map<double> activity_map;
       // Path to the map file
       string map_file;
       // Maximum value across the map
       double max_val;
       // If true,
       bool null_map;
       // The fine map offsets and the sample map dimensions
       unsigned long offset_x, offset_y, x_dim, y_dim;
       // Random number generator
       shared_ptr<NRrand> random;
   
       // Function pointer for our reproduction map checker
       typedef bool (ActivityMap::*rep_ptr)(const unsigned long &x, const unsigned long &y, const long &xwrap,
                                            const long &ywrap);
   
       // once setup will contain the end check function to use for this simulation.
       rep_ptr activity_map_checker_fptr;
   public:
       ActivityMap() : activity_map(), offset_x(0), offset_y(0), x_dim(0), y_dim(0), random(make_shared<NRrand>()),
                       activity_map_checker_fptr(nullptr)
       {
           map_file = "none";
           max_val = 0;
           null_map = true;
       }
   
       bool isNull();
   
       void import(string file_name, unsigned long size_x, unsigned long size_y, shared_ptr<NRrand> random_in);
   
       void setActivityFunction();
   
       void setOffsets(const unsigned long &x_offset, const unsigned long &y_offset,
                       const unsigned long &xdim, const unsigned long &ydim);
   
       bool rejectionSampleNull(const unsigned long &x, const unsigned long &y, const long &xwrap, const long &ywrap);
   
       bool rejectionSample(const unsigned long &x, const unsigned long &y, const long &xwrap, const long &ywrap);
   
       double getVal(const unsigned long &x, const unsigned long &y, const long &xwrap, const long &ywrap);
   
       bool actionOccurs(const unsigned long &x, const unsigned long &y, const long &xwrap, const long &ywrap);
   
       void standardiseValues();
   
       Row<double> operator[](long index)
       {
           return activity_map[index];
       }
   
       ActivityMap &operator=(const ActivityMap &rm)
       {
           this->activity_map = rm.activity_map;
           this->map_file = rm.map_file;
           this->max_val = rm.max_val;
           this->null_map = rm.null_map;
           this->offset_x = rm.offset_x;
           this->offset_y = rm.offset_y;
           this->x_dim = rm.x_dim;
           this->y_dim = rm.y_dim;
           this->activity_map_checker_fptr = rm.activity_map_checker_fptr;
           return *this;
       }
   
       friend ostream &operator<<(ostream &os, ActivityMap &r)
       {
           os << r.map_file << "\n";
           os << r.activity_map.getCols() << "\n";
           os << r.activity_map.getRows() << "\n";
           os << r.offset_x << "\n";
           os << r.offset_y << "\n";
           os << r.x_dim << "\n";
           os << r.y_dim << "\n";
           return os;
       }
   
       friend istream &operator>>(istream &is, ActivityMap &r)
       {
           is.ignore();
           getline(is, r.map_file);
           unsigned long col, row;
           is >> col >> row;
           is >> r.offset_x >> r.offset_y >> r.x_dim >> r.y_dim;
           r.import(r.map_file, col, row, shared_ptr<NRrand>());
           return is;
       }
   
   };
   
   #endif //ACTIVITYMAP_H
