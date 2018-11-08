
.. _program_listing_file_necsim_SpatialTree.h:

Program Listing for File SpatialTree.h
======================================

- Return to documentation for :ref:`file_necsim_SpatialTree.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
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
   
   #ifndef WIN_INSTALL
   
   #include <unistd.h>
   
   #endif
   
   #include <algorithm>
   #include <stdexcept>
   #include <memory>
   //#define with_gdal
   // extra boost include - this requires the installation of boost on the system
   // note that this requires compilation with the -lboost_filesystem and -lboost_system linkers.
   #include <boost/filesystem.hpp>
   
   // include fast-csv-parser by Ben Strasser (available from https://github.com/ben-strasser/fast-cpp-csv-parser)
   // for fast file reading
   
   #ifdef use_csv
   #include "fast-cpp-csv-parser/csv.h"
   #endif
   
   //#ifndef sql_ram
   //#define sql_ram
   //#endif
   
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
   #include "setup.h"
   #include "DispersalCoordinator.h"
   #include "ActivityMap.h"
   #include "Logger.h"
   
   using namespace std;
   
   class SpatialTree : public virtual Tree
   {
   protected:
       // Our dispersal coordinator for getting dispersal distances and managing calls from the landscape
       DispersalCoordinator dispersal_coordinator;
       // Death probability values across the landscape
       shared_ptr<ActivityMap> death_map;
       // Reproduction probability values across the landscape
       shared_ptr<ActivityMap> reproduction_map;
       // A species_id_list of new variables which will contain the relevant information for maps and grids.
       //  strings containing the file names to be imported.
       string fine_map_input, coarse_map_input;
       string historical_fine_map_input, historical_coarse_map_input;
       // Landscape object containing both the coarse and fine maps for checking whether or not there is habitat at a
       // particular location.
       shared_ptr<Landscape> landscape;
       // An indexing spatial positioning of the lineages
       Matrix<SpeciesList> grid;
       unsigned long desired_specnum;
       // contains the DataMask for where we should start lineages from.
       DataMask samplegrid;
   public:
       SpatialTree() : Tree(), dispersal_coordinator(), death_map(make_shared<ActivityMap>()),
                       reproduction_map(make_shared<ActivityMap>()),
                       fine_map_input("none"), coarse_map_input("none"), historical_fine_map_input("none"),
                       historical_coarse_map_input("none"), landscape(make_shared<Landscape>()),
                       grid(), desired_specnum(1), samplegrid()
       {
   
       }
   
       ~SpatialTree() override = default;
   
       void runFileChecks() override;
   
       void parseArgs(vector<string> &comargs);
   
       void checkFolders();
   
       void setParameters() override;
   
   
       // Imports the maps using the variables stored in the class. This function must be run after the set_mapvars() in
       // order to function correctly.
       void importMaps();
   
       void importActivityMaps();
   
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
   
   #ifdef historical_mode
   
       void historicalStepChecks();
   #endif
   
       void incrementGeneration() override;
   
       void updateStepCoalescenceVariables() override;
   
       void addLineages(double generation_in) override;
   
       string simulationParametersSqlInsertion() override;
   
       void simPause() override;
   
       void dumpMap(shared_ptr<ofstream> out);
   
       void dumpGrid(shared_ptr<ofstream> out);
   
       void simResume() override;
   
       void loadGridSave(shared_ptr<ifstream> in1);
   
       void loadMapSave(shared_ptr<ifstream> in1);
   
       void verifyActivityMaps();
   
       void addWrappedLineage(unsigned long numstart, long x, long y);
   
       unsigned long countCellExpansion(const long &x, const long &y, const long &xwrap, const long &ywrap,
                                        const double &generationin, vector<TreeNode> &data_added);
   
       void expandCell(long x, long y, long x_wrap, long y_wrap, double generation_in, unsigned long add,
                       vector<TreeNode> &data_added, vector<DataPoint> &active_added);
   
   #ifdef DEBUG
   
       void validateLineages() override;
   
       void debugDispersal();
   
       void debugAddingLineage(unsigned long numstart, long x, long y);
   
       void runChecks(const unsigned long &chosen, const unsigned long &coalchosen) override;
   
   #endif
   };
   
   #endif  // SPATIALTREE_H
