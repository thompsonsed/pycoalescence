
.. _program_listing_file_Map.h:

Program Listing for File Map.h
========================================================================================

- Return to documentation for :ref:`file_Map.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details
   #ifndef MAP
   #define MAP
   
   # include <string>
   # include <stdio.h>
   #include <vector>
   # include <iostream>
   # include <fstream>
   # include <math.h>
   # include <stdexcept>
   # include "ConfigFileParser.h"
   # include <boost/filesystem.hpp>
   
   #include "Matrix.h"
   #include "Logging.h"
   # include "Datamask.h"
   #include "SimParameters.h"
   
   //#include <Setup.h>
   //# include "Fattaildeviate.cpp"
   using namespace std;
   
   
   /************************************************************
                       MAP OBJECT
    ************************************************************/
   // Object containing both the maps (the coarse and fine version) and routines for easy setting up and switching between the different coordinate systems.
   class Map
   {
   protected:
       // The map files which are read in (or generated if running with "null" as the map file".
       // Pristine maps are meant for before any deforestation occured, whereas the other maps are intended for modern day maps.
       // A linear transformation from modern to pristine maps is used, approaching the dForestTransform variable times the difference between the pristine and modern maps.
       // Once the dPristine number of generations has been reached, the map will jump to the pristine condition.
       Matrix<uint32_t> fine_map; // the finer grid for the area around the sample area.
       Matrix<uint32_t> pristine_fine_map; // the pristine finer map.
       Matrix<uint32_t> coarse_map; // the coarser grid for the wider zone.
       Matrix<uint32_t> pristine_coarse_map; // the pristine coarser map.
       SimParameters mapvars; // for importing and storing the simulation set-up options.
       long finexmin, fineymin, coarsexmin, coarseymin; // the minimum values for each dimension for offsetting.
       long finexmax, fineymax, coarsexmax, coarseymax; // the maximum values for each dimension for offsetting.
       long finexoffset, fineyoffset, coarsexoffset, coarseyoffset; // the offsetting of the map in FINE map units.
       unsigned long scale; // the scale of the coarse map compared with the smaller map.
       long xdim; // the length of the grid where the species start.
       long ydim; // the height of the grid where the species start.
       unsigned long deme;
       bool checksetdim; // for checking that the dimensions have been set before attempting to import the maps.
       double dispersal_relative_cost; // for setting the movement cost through forest.
   
       double dUpdateTime; // the last time the map was updated, in generations.
       double dForestTransform; // the rate at which the forest transforms from the modern forest map to the pristine forest map. A value of 1 will give a smooth curve from the present day to pristine forest.
       double dPristine; // the number of generations at which point the forest becomes entirely pristine.
       double dCurrent; // the time the current map was updated.
       bool bPristine; // checks whether the simulation has already been set to the pristine state.
       bool hasPristine; // flag of whether the simulation has a pristine state or not.
       unsigned long iForestMax; // the maximum value for forest
       unsigned long iFineForestMax; // the maximum value on the fine map file
       unsigned long iCoarseForestMax; // the maximum value on the coarse map file
       unsigned long iPristineFineForestMax; // the maximum value on the pristine fine map file
       unsigned long iPristineCoarseForestMax; // the maximum value on the pristine coarse map file
       string landscape_type; // if true, dispersal is possible from anywhere, only the fine map spatial structure is preserved
       string NextMap;
       bool bCoarse; // If this is false, there is no coarse map defined, so ignore the boundaries.
       unsigned int nUpdate; // the number of updates to have occured.
       // Typedef for single application of the infinite landscape verses bounded landscape.
       typedef unsigned long (Map::*fptr)(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                          const double &dCurrentGen);
   
       fptr getValFunc;
   public:
       Map()
       {
           checksetdim = false; // sets the check to false.
           bPristine = false;
           dCurrent = 0;
           iForestMax = 1;
           getValFunc = nullptr;
           bCoarse = false;
           hasPristine = false;
           landscape_type = "closed";
           iFineForestMax = 0;
           iCoarseForestMax = 0;
           iPristineFineForestMax = 0;
           iPristineCoarseForestMax = 0;
       }
   
       string printForestMax()
       {
           stringstream ss;
           ss << "max, fine, coarse, pfine, pcoarse: " << iForestMax << "," << iFineForestMax;
           ss << ", " << iCoarseForestMax << ", " << iPristineFineForestMax << ", " << iPristineCoarseForestMax << endl;
           return ss.str();
       }
   
       unsigned long getForestMax();
   
       void setDims(SimParameters mapvarsin);
   
       bool checkMapExists();
   
       /********************************************
        * CALC MAP FUNCTIONS
        ********************************************/
   
       void calcFineMap();
   
       void calcPristineFineMap();
   
       void calcCoarseMap();
   
       void calcPristineCoarseMap();
   
       // Map setters
       void setTimeVars(double dPristinein, double dForestTransformin);
   
   
       void calcOffset();
       /********************************************
        * VALIDATE MAPS
        ********************************************/
   
       void validateMaps();
   
       /********************************************
        * CHANGE MAP FUNCTIONS
        ********************************************/
   
       void updateMap(double generation);
   
       bool isPristine()
       {
           if(hasPristine)
           {
               return bPristine;
           }
           return true;
       }
   
       void setPristine(const bool &bPristinein)
       {
           bPristine = bPristinein;
       }
   
       double getPristine()
       {
           return dPristine;
       }
   
       string getLandscapeType()
       {
           return landscape_type;
       }
   
       void checkPristine(double generation)
       {
           if(hasPristine)
           {
               if(generation >= dPristine)
               {
                   bPristine = true;
               }
           }
       }
       // 
       /********************************************
        * GET VAL FUNCTIONS
        ********************************************/
   
   
       // Function for getting the val at a particular coordinate from either the coarse or fine map
       // altered to use the current generation as well to determine the value.
   
   
       void setLandscape(string is_infinite);
   
       unsigned long
       getVal(const double &x, const double &y, const long &xwrap, const long &ywrap, const double &dCurrentGen);
   
       unsigned long getValCoarse(const double &xval, const double &yval, const double &dCurrentGen);
   
       unsigned long getValFine(const double &xval, const double &yval, const double &dCurrentGen);
   
       unsigned long
       getValFinite(const double &x, const double &y, const long &xwrap, const long &ywrap, const double &dCurrentGen);
   
   
       unsigned long
       getValInfinite(const double &x, const double &y, const long &xwrap, const long &ywrap, const double &dCurrentGen);
   
   
       unsigned long getValCoarseTiled(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                       const double &dCurrentGen);
   
   
       unsigned long getValFineTiled(const double &x, const double &y, const long &xwrap, const long &ywrap,
                                     const double &dCurrentGen);
   
       unsigned long convertSampleXToFineX(const unsigned long &x, const long &xwrap);
   
       unsigned long convertSampleYToFineY(const unsigned long &y, const long &ywrap);
   
       void convertFineToSample(long &x, long &xwrap, long &y, long &ywrap);
   
   
       unsigned long getInitialCount(double dSample, Datamask &samplemask);
   
       SimParameters getSimParameters();
   
       /********************************************
        * CHECK MAP FUNCTIONS
        ********************************************/
       bool checkMap(const double &x, const double &y, const long &xwrap, const long &ywrap, const double generation);
   
   
       bool checkFine(const double &x, const double &y, const long &xwrap, const long &ywrap);
   
   
       void convertCoordinates(double &x, double &y, long &xwrap, long &ywrap);
   
       /********************************************
        * MAIN DISPERSAL FUNCTION
        ********************************************/
       unsigned long runDispersal(const double &dist, const double &angle, long &startx, long &starty, long &startxwrap,
                                  long &startywrap, bool &disp_comp, const double &generation);
   
   
       friend ostream &operator<<(ostream &os, const Map &r)
       {
           os << r.mapvars << "\n" << r.finexmin << "\n" << r.finexmax << "\n" << r.coarsexmin << "\n" << r.coarsexmax;
           os << "\n" << r.fineymin << "\n" << r.fineymax << "\n" << r.coarseymin << "\n" << r.coarseymax << "\n";
           os << r.finexoffset << "\n" << r.fineyoffset << "\n" << r.coarsexoffset << "\n" << r.coarseyoffset << "\n";
           os << r.scale << "\n" << r.xdim << "\n" << r.ydim << "\n" << r.deme << "\n" << r.checksetdim << "\n"
              << r.dispersal_relative_cost << "\n";
           os << r.dUpdateTime << "\n" << r.dForestTransform << "\n" << r.dPristine << "\n" << r.dCurrent << "\n"
              << r.bPristine << "\n";
           os << r.NextMap << "\n" << r.nUpdate << "\n" << r.landscape_type << "\n" << r.iFineForestMax << "\n"
              << r.iCoarseForestMax << "\n";
           os << r.iPristineFineForestMax << "\n" << r.iPristineCoarseForestMax << "\n" << r.iForestMax << "\n"
              << r.bCoarse << "\n" << r.hasPristine << "\n";
           return os;
       }
   
       friend istream &operator>>(istream &is, Map &r)
       {
           //double temp1,temp2;
           //is << m.numRows<<" , "<<m.numCols<<" , "<<endl;
           is >> r.mapvars >> r.finexmin;
           is >> r.finexmax >> r.coarsexmin;
           is >> r.coarsexmax >> r.fineymin >> r.fineymax;
           is >> r.coarseymin >> r.coarseymax;
           is >> r.finexoffset >> r.fineyoffset >> r.coarsexoffset >> r.coarseyoffset >> r.scale >> r.xdim >> r.ydim
              >> r.deme >> r.checksetdim >> r.dispersal_relative_cost;
           is >> r.dUpdateTime >> r.dForestTransform >> r.dPristine >> r.dCurrent >> r.bPristine;
           getline(is, r.NextMap);
           is >> r.nUpdate;
           is >> r.landscape_type;
           is >> r.iFineForestMax >> r.iCoarseForestMax;
           is >> r.iPristineFineForestMax >> r.iPristineCoarseForestMax;
           is >> r.iForestMax >> r.bCoarse >> r.hasPristine;
   //      r.mapvars.setPristine(r.nUpdate);
           r.setLandscape(r.mapvars.landscape_type);
           r.calcFineMap();
           r.calcCoarseMap();
           r.calcPristineFineMap();
           r.calcPristineCoarseMap();
           r.recalculateForestMax();
           return is;
       }
   
       string printVars();
   
       void clearMap();
   
       void recalculateForestMax();
   
   };
   
   #endif
    
