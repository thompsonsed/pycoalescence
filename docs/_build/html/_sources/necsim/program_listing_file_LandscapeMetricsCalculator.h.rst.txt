
.. _program_listing_file_LandscapeMetricsCalculator.h:

Program Listing for File LandscapeMetricsCalculator.h
=====================================================

- Return to documentation for :ref:`file_LandscapeMetricsCalculator.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #include<algorithm>
   #include <vector>
   #include <numeric>
   #include "necsim/Map.h"
   #include "necsim/Cell.h"
   #ifndef MEAN_DISTANCE_MEANDISTANCECALCULATOR_H
   #define MEAN_DISTANCE_MEANDISTANCECALCULATOR_H
   
   using namespace std;
   
   class LandscapeMetricsCalculator : public Map<double>
   {
       vector<Cell> all_cells;
   public:
   
       double calculateMNN();
   
       void checkMinDistance(Cell &home_cell, const long &x, const long &y, double & min_distance);
   
       double findNearestNeighbourDistance(const long & row, const long & col);
   
       void createCellList();
   
       double calculateClumpiness();
   
       unsigned long calculateNoAdjacencies();
   
       double calculateMinPerimeter();
   
   };
   
   #endif //MEAN_DISTANCE_MEANDISTANCECALCULATOR_H
