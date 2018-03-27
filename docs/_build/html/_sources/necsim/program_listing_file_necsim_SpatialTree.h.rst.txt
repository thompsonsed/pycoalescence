
.. _program_listing_file_necsim_SpatialTree.h:

Program Listing for File SpatialTree.h
======================================

- Return to documentation for :ref:`file_necsim_SpatialTree.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   //
   #ifndef SPATIALTREE_H
   #define SPATIALTREE_H
   
   #include <cstdio>
   #include <fstream>
   #include <vector>
   #include <iostream>
   #include <string>
   #include <cstring>
   #include <cmath>
   #include <iomanip>
   #include <cmath>
   #include <ctime>
   #include <ctime>
   #include <sqlite3.h>
   #include <unistd.h>
   #include <algorithm>
   #include <stdexcept>
   //#define with_gdal
   // extra boost include - this requires the installation of boost on the system
   // note that this requires compilation with the -lboost_filesystem and -lboost_system linkers.
   #include <boost/filesystem.hpp>
   
   // include fast-csv-parser by Ben Strasser (available from https://github.com/ben-strasser/fast-cpp-csv-parser)
   // for fast file reading
   #ifdef use_csv
   #include "fast-cpp-csv-parser/csv.h"
   #endif
   
   #ifndef sql_ram
   #define sql_ram
   #endif
   
   // other includes for required files
   #include "Tree.h"
   #include "Matrix.h"
   #include "NRrand.h"
   #include "SimParameters.h"
   #include "DataPoint.h"
   #include "TreeNode.h"
   #include "SpeciesList.h"
   #include "Landscape.h"
   #include "Community.h"
   #include "Setup.h"
   #include "DispersalCoordinator.h"
   #include "ReproductionMap.h"
   #include "Logging.h"
   
   using namespace std;
   
   class SpatialTree : public virtual Tree
   {
   protected:
       // Our dispersal coordinator for getting dispersal distances and managing calls from the landscape
       DispersalCoordinator dispersal_coordinator;
       // The reproduction map object
       ReproductionMap rep_map;
       // A list of new variables which will contain the relevant information for maps and grids.
       //  strings containing the file names to be imported.
       string fine_map_input, coarse_map_input;
       string pristine_fine_map_input, pristine_coarse_map_input;
       // the time since pristine forest and the rate of change of the rainforest.
       double gen_since_pristine, habitat_change_rate;
       // the variables for the grid containing the initial individuals.
       unsigned long grid_x_size, grid_y_size;
       // The fine map variables at the same resolution as the grid.
       // the coarse map variables at a scaled resolution of the fine map.
       long fine_map_x_size, fine_map_y_size, fine_map_x_offset, fine_map_y_offset;
       long coarse_map_x_size, coarse_map_y_size, coarse_map_x_offset, coarse_map_y_offset, coarse_map_scale;
       // Landscape object containing both the coarse and fine maps for checking whether or not there is habitat at a
       // particular location.
       Landscape landscape;
       // An indexing spatial positioning of the lineages
       Matrix<SpeciesList> grid;
       // dispersal and sigma references
       double sigma, tau;
       // the cost for moving through non-habitat. 1.0 means there is no cost. 10 means that movement is 10x
       // slower through habitat.
       double dispersal_relative_cost;
       // the desired number of species we are aiming for. If it is 0, we will carry on forever.
       unsigned long desired_specnum;
       // contains the DataMask for where we should start lineages from.
       DataMask samplegrid;
   public:
       SpatialTree() : Tree()
       {
           sigma = 0.0;
           tau = 0.0;
           outdatabase = nullptr;
           gen_since_pristine = 0.0;
           habitat_change_rate = 0.0;
           grid_x_size = 0;
           grid_y_size = 0;
           fine_map_x_size = 0;
           fine_map_y_size = 0;
           fine_map_x_offset = 0;
           fine_map_y_offset = 0;
           coarse_map_x_size = 0;
           coarse_map_y_size = 0;
           coarse_map_x_offset = 0;
           coarse_map_y_offset = 0;
           coarse_map_scale = 1;
           dispersal_relative_cost = 1.0;
           desired_specnum = 1;
       }
   
       ~SpatialTree() override = default;
       void importSimulationVariables(const string &configfile) override;
   
       void parseArgs(vector<string> &comargs);
   
       void checkFolders();
   
       void setParameters() override;
   
   
       // Imports the maps using the variables stored in the class. This function must be run after the set_mapvars() in
       // order to function correctly.
       void importMaps();
   
       void importReproductionMap();
   
       unsigned long getInitialCount() override;
   
       void setupDispersalCoordinator();
   
       void setup() override;
   
       unsigned long fillObjects(const unsigned long &initial_count) override;
   
       unsigned long getIndividualsSampled(const long &x, const long &y,
                                    const long &x_wrap, const long &y_wrap, const double &current_gen);
       void removeOldPosition(const unsigned long &chosen) override;
   
       void calcMove();
   
       long double calcMinMax(const unsigned long &current);
   
       void calcNewPos(bool &coal,
                       const unsigned long &chosen,
                       unsigned long &coalchosen,
                       const long &oldx,
                       const long &oldy,
                       const long &oldxwrap,
                       const long &oldywrap);
   
       void switchPositions(const unsigned long &chosen) override;
   
       void calcNextStep() override;
   
       unsigned long estSpecnum();
   
   #ifdef pristine_mode
   
       void pristineStepChecks();
   #endif
   
   
       void incrementGeneration() override ;
   
       void updateStepCoalescenceVariables() override;
   
       void addLineages(double generation_in) override;
   
       string simulationParametersSqlInsertion() override;
   
   
       void simPause() override;
   
       void dumpMap(string pause_folder);
   
       void simResume() override;
   
       void loadGridSave();
   
       void loadMapSave();
   
       void verifyReproductionMap();
   
       void addWrappedLineage(unsigned long numstart, long x, long y);
   
       unsigned long countCellExpansion(const long &x, const long &y, const long &xwrap, const long &ywrap,
                                        const double &generationin, const bool &make_tips);
   
       void expandCell(long x, long y, long x_wrap, long y_wrap, double generation_in, unsigned long add);
   
   
   
   
   #ifdef DEBUG
   
       void validateLineages() override;
   
       void debugDispersal();
       void debugAddingLineage(unsigned long numstart, long x, long y);
   
       void runChecks(const unsigned long &chosen, const unsigned long &coalchosen) override;
   #endif
   };
   
   #endif  // SPATIALTREE_H
