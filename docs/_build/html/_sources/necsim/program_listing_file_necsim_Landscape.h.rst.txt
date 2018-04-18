
.. _program_listing_file_necsim_Landscape.h:

Program Listing for File Landscape.h
====================================

- Return to documentation for :ref:`file_necsim_Landscape.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #ifndef LANDSCAPE_H
   #define LANDSCAPE_H
   
   # include <string>
   # include <cstdio>
   # include <vector>
   # include <iostream>
   # include <fstream>
   # include <cmath>
   # include <stdexcept>
   # include <boost/filesystem.hpp>
   
   #include "Map.h"
   #include "DataMask.h"
   #include "SimParameters.h"
   
   using namespace std;
   
   uint32_t importToMapAndRound(string map_file, Map<uint32_t> &map_in, unsigned long map_x,
                                unsigned long map_y, unsigned long scalar);
   
   class Landscape
   {
   protected:
       // The map files which are read in (or generated if running with "null" as the map file".
       // historical maps are meant for before any deforestation occured, whereas the other maps are intended for modern day maps.
       // A linear transformation from modern to historical maps is used, approaching the habitat_change_rate variable times the difference between the historical and modern maps.
       // Once the gen_since_historical number of generations has been reached, the map will jump to the historical condition.
       // the finer grid for the area around the sample area.
       Map<uint32_t> fine_map;
       // the historical finer map.
       Map<uint32_t> historical_fine_map;
       // the coarser grid for the wider zone.
       Map<uint32_t> coarse_map;
       // the historical coarser map.
       Map<uint32_t> historical_coarse_map;
       // for importing and storing the simulation set-up options.
       SimParameters * mapvars;
       // the minimum values for each dimension for offsetting.
       long fine_x_min{}, fine_y_min{}, coarse_x_min{}, coarse_y_min{};
       // the maximum values for each dimension for offsetting.
       long fine_x_max{}, fine_y_max{}, coarse_x_max{}, coarse_y_max{};
       // the offsetting of the map in FINE map units.
       long fine_x_offset{}, fine_y_offset{}, coarse_x_offset{}, coarse_y_offset{};
       // the scale of the coarse map compared with the smaller map.
       unsigned long scale{};
       // the length of the grid where the species start.
       long x_dim{};
       // the height of the grid where the species start.
       long y_dim{};
       unsigned long deme{};
       // for checking that the dimensions have been set before attempting to import the maps.
       bool check_set_dim;
       // for setting the movement cost through forest.
       double dispersal_relative_cost{};
       // the last time the map was updated, in generations.
       double update_time{};
       // the rate at which the habitat transforms from the modern forest map to the historical habitat map.
       // A value of 1 will give a smooth curve from the present day to historical habitat.
       double habitat_change_rate{};
       // the number of generations at which point the habitat becomes entirely historical.
       double gen_since_historical{};
       // the time the current map was updated.
       double current_map_time;
       // checks whether the simulation has already been set to the historical state.
       bool is_historical;
       // flag of whether the simulation has a historical state or not.
       bool has_historical;
       // the maximum value for habitat
       unsigned long habitat_max;
       // the maximum value on the fine map file
       unsigned long fine_max;
       // the maximum value on the coarse map file
       unsigned long coarse_max;
       // the maximum value on the historical fine map file
       unsigned long historical_fine_max;
       // the maximum value on the historical coarse map file
       unsigned long historical_coarse_max;
       // if true, dispersal is possible from anywhere, only the fine map spatial structure is preserved
       string landscape_type;
       string NextMap;
       // If this is false, there is no coarse map defined, so ignore the boundaries.
       bool has_coarse;
       // the number of updates to have occured.
       unsigned int nUpdate{};
   
       // Typedef for single application of the infinite landscape verses bounded landscape.
       typedef unsigned long (Landscape::*fptr)(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                                const double &dCurrentGen);
   
       fptr getValFunc;
   public:
       Landscape()
       {
           mapvars = nullptr;
           check_set_dim = false; // sets the check to false.
           is_historical = false;
           current_map_time = 0;
           habitat_max = 1;
           getValFunc = nullptr;
           has_coarse = false;
           has_historical = false;
           landscape_type = "closed";
           fine_max = 0;
           coarse_max = 0;
           historical_fine_max = 0;
           historical_coarse_max = 0;
       }
   
       unsigned long getHabitatMax();
   
       bool hasHistorical();
       void setDims(SimParameters * mapvarsin);
   
   
       bool checkMapExists();
   
       void calcFineMap();
   
       void calcHistoricalFineMap();
   
       void calcCoarseMap();
   
       void calcHistoricalCoarseMap();
   
       void setTimeVars(double gen_since_historical_in, double habitat_change_rate_in);
   
       void calcOffset();
   
       bool checkAllDimensionsZero();
   
       void calculateOffsetsFromMaps();
   
       void calculateOffsetsFromParameters();
   
       void validateMaps();
   
       void updateMap(double generation);
   
       void doUpdate();
       void resetHistorical();
   
       bool isHistorical()
       {
           if(has_historical)
           {
               return is_historical;
           }
           return true;
       }
   
       void setHistorical(const bool &historical_in)
       {
           is_historical = historical_in;
       }
   
       double getHistorical()
       {
           return gen_since_historical;
       }
   
       string getLandscapeType()
       {
           return landscape_type;
       }
   
       void checkHistorical(double generation)
       {
           if(has_historical)
           {
               if(generation >= gen_since_historical)
               {
                   is_historical = true;
               }
           }
       }
   
       void setLandscape(string is_infinite);
   
       unsigned long getVal(const double &x, const double &y,
                            const long &xwrap, const long &ywrap, const double &current_generation);
   
       unsigned long getValCoarse(const double &xval, const double &yval, const double &current_generation);
   
       unsigned long getValFine(const double &xval, const double &yval, const double &current_generation);
   
       unsigned long getValFinite(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                  const double &current_generation);
   
       unsigned long getValInfinite(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                    const double &current_generation);
   
       unsigned long getValCoarseTiled(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                       const double &current_generation);
   
       unsigned long getValFineTiled(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                     const double &current_generation);
   
       unsigned long convertSampleXToFineX(const unsigned long &x, const long &xwrap);
   
       unsigned long convertSampleYToFineY(const unsigned long &y, const long &ywrap);
   
       void convertFineToSample(long &x, long &xwrap, long &y, long &ywrap);
   
       unsigned long getInitialCount(double dSample, DataMask &samplemask);
   
       SimParameters * getSimParameters();
   
       bool checkMap(const double &x, const double &y, const long &xwrap, const long &ywrap, const double generation);
   
       bool checkFine(const double &x, const double &y, const long &xwrap, const long &ywrap);
   
       void convertCoordinates(double &x, double &y, long &xwrap, long &ywrap);
   
       unsigned long runDispersal(const double &dist, const double &angle, long &startx, long &starty, long &startxwrap,
                                  long &startywrap, bool &disp_comp, const double &generation);
   
       friend ostream &operator<<(ostream &os, const Landscape &r)
       {
           os << r.fine_x_min << "\n" << r.fine_x_max << "\n" << r.coarse_x_min << "\n"
              << r.coarse_x_max;
           os << "\n" << r.fine_y_min << "\n" << r.fine_y_max << "\n" << r.coarse_y_min << "\n" << r.coarse_y_max << "\n";
           os << r.fine_x_offset << "\n" << r.fine_y_offset << "\n" << r.coarse_x_offset << "\n" << r.coarse_y_offset
              << "\n";
           os << r.scale << "\n" << r.x_dim << "\n" << r.y_dim << "\n" << r.deme << "\n" << r.check_set_dim << "\n"
              << r.dispersal_relative_cost << "\n";
           os << r.update_time << "\n" << r.habitat_change_rate << "\n" << r.gen_since_historical << "\n"
              << r.current_map_time << "\n"
              << r.is_historical << "\n";
           os << r.NextMap << "\n" << r.nUpdate << "\n" << r.landscape_type << "\n" << r.fine_max << "\n"
              << r.coarse_max << "\n";
           os << r.historical_fine_max << "\n" << r.historical_coarse_max << "\n" << r.habitat_max << "\n"
              << r.has_coarse << "\n" << r.has_historical << "\n";
           return os;
       }
   
       friend istream &operator>>(istream &is, Landscape &r)
       {
           is >> r.fine_x_min;
           is >> r.fine_x_max >> r.coarse_x_min;
           is >> r.coarse_x_max >> r.fine_y_min >> r.fine_y_max;
           is >> r.coarse_y_min >> r.coarse_y_max;
           is >> r.fine_x_offset >> r.fine_y_offset >> r.coarse_x_offset >> r.coarse_y_offset >> r.scale >> r.x_dim
              >> r.y_dim
              >> r.deme >> r.check_set_dim >> r.dispersal_relative_cost;
           is >> r.update_time >> r.habitat_change_rate >> r.gen_since_historical >> r.current_map_time >> r.is_historical;
           getline(is, r.NextMap);
           is >> r.nUpdate;
           is >> r.landscape_type;
           is >> r.fine_max >> r.coarse_max;
           is >> r.historical_fine_max >> r.historical_coarse_max;
           is >> r.habitat_max >> r.has_coarse >> r.has_historical;
           r.setLandscape(r.mapvars->landscape_type);
           r.calcFineMap();
           r.calcCoarseMap();
           r.calcHistoricalFineMap();
           r.calcHistoricalCoarseMap();
           r.recalculateHabitatMax();
           return is;
       }
   
       string printVars();
   
       void clearMap();
   
       void recalculateHabitatMax();
   
   };
   
   #endif // LANDSCAPE_H
    
