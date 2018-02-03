
.. _program_listing_file_Tree.h:

Program Listing for File Tree.h
========================================================================================

- Return to documentation for :ref:`file_Tree.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   //
   #ifndef TREE
   #define TREE
   
   /************************************************************
                                                   INCLUDES
    ************************************************************/
   // standard includes
   #include <stdio.h>
   #include <fstream>
   #include <vector>
   #include <iostream>
   #include <string>
   #include <cstring>
   #include <math.h>
   #include <iomanip>
   #include <cmath>
   #include <time.h>
   #include <ctime>
   #include <sqlite3.h>
   #include <string>
   //# include <sqlite.h>
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
   
   //#define use_csv // for integration with the matrix header file
   //#include "fast-cpp-csv-parser/csv.h"
   //#define record_space // tells the compiler whether to include the routines for outputting full spatial data of
   //lineages. Usually this will not be required.
   
   // this uses the RAM for the storage of the active SQL database.
   // If the RAM requirements get too huge, comment this out to instead write directly to disc.
   // For HPC systems, it is recommended to use this option as write speeds are generally fast and large simulations don't
   // have a linear increase in the SQL database size (at least in RAM).
   #define sql_ram
   
   // other includes for required files
   #include "Matrix.h"
   #include "Fattaildeviate.h"
   #include "Datapoint.h"
   #include "Treenode.h"
   #include "SpeciesList.h"
   #include "Map.h"
   #include "Treelist.h"
   #include "ConfigFileParser.h"
   #include "Setup.h"
   #include "Logging.h"
   #include "DispersalCoordinator.h"
   #include "Step.h"
   #include "ReproductionMap.h"
   
   using namespace std;
   
   /************************************************************
                                                   MAIN TREE OBJECT
    ************************************************************/
   
   class Tree
   {
   #ifdef DEBUG
   private:
       unsigned long count_dispersal_fails, count_density_fails;
   #endif
       // declare protected variables
   protected:
       // storing the coalescence tree itself
       Row<Treenode> data;
   #ifdef DEBUG
       ofstream logfile;
   #endif
       unsigned long enddata;
       // for storing the command line parameters and parsing the required information.
       SimParameters sim_parameters;
       // random number generator
       NRrand NR;
       // Our dispersal coordinator for getting dispersal distances and managing calls from the forestmap
       DispersalCoordinator dispersal_coordinator;
       // The reproduction map object
       ReproductionMap rep_map;
       // Storing the speciation rates for later reference.
       vector<double> speciation_rates;
       bool seeded;
       // random seed
       long long the_seed;
   
       // for general debugging use
       //  bool debug;
   
       // for enabling the logging mode
       bool log_all;
       // note: in earlier versions I had the minspecsetup variable here
       // I've removed it because this version implements speciation as it goes rather than on the tree later
       // I've also removed sim_counter which recorded the number of repeat simulations
       // because each job will be 1 simulation in this implementation
   
       // for file naming - good to know which task in a series is being executed here
       long long the_task;
   
       // The map file containing the times that we want to expand the model and record all lineages again.
       // If this is null, bAutocorrel will be false and the vector will be empty.
       string autocorrel_file;
       vector<double> autocorrel_times;
       // Set to true if we are recording at times other than the present day.
       bool bAutocorrel;
       // tmp debugging
       // A list of new variables which will contain the relevant information for maps and grids.
       //  strings containing the file names to be imported.
       string finemapinput, coarsemapinput, outdirectory;  
       // variable for storing the paused sim location if files have been moved during paused/resumed simulations!
       string pause_sim_directory; 
       string pristinefinemapinput, pristinecoarsemapinput;
       // the time since pristine forest and the rate of change of the rainforest.
       double dPristine, dForestTransform;  
       // the variables for the grid containing the initial individuals.
       unsigned long gridxsize, gridysize;
       // The fine map variables at the same resolution as the grid.
       // the coarse map variables at a scaled resolution of the fine map.
       long finemapxsize, finemapysize, finemapxoffset, finemapyoffset;  
       long coarsemapxsize, coarsemapysize, coarsemapxoffset, coarsemapyoffset, coarsemapscale;  
       // Used to check whether the map variables have already been imported.
       bool varimport;  
       // New private vectors
       // The time variables (for timing the simulation in real time)
       time_t start, sim_start, sim_end, now, sim_finish, out_finish;
       time_t time_taken;
       // Map object containing both the coarse and fine maps for checking whether or not there is forest at a particular
       // location.
       Map forestmap;
       // An indexing spread for the lineages
       Matrix<SpeciesList> grid;
       // Active lineages stored as a row of datapoints
       Row<Datapoint> active;
       // Stores the point of the end of the active vector. 0 is reserved as null
       unsigned long endactive; 
       // the maximum size of endactive
       unsigned long startendactive;  
       // the maximum simulated number of individuals in the present day.
       unsigned long maxsimsize;  
       // This might need to be updated for simulations that have large changes in maximum population size over time.
       // number of simulation steps
       long steps;
       // Maximum time to run for (in seconds)
       unsigned long maxtime;
       // number of generations passed, dispersal and sigma references
       double generation, sigma, tau, deme_sample;
       // the speciation rate
       long double spec;
       // the cost for moving through non-forest. 1.0 means there is no cost. 10 means that movement is 10x
       // slower through forest.
       double dispersal_relative_cost;  
       // The number of individuals per cell
       long deme;
       // the desired number of species we are aiming for. If it is 0, we will carry on forever.
       unsigned long desired_specnum;  
       // sqlite3 object that stores all the data
       sqlite3 *database;
   // If sql database is written first to memory, then need another object to contain the in-memory database.
   #ifdef sql_ram
       sqlite3 *outdatabase;
   #endif
       string sqloutname;
       // for create the link to the speciationcounter object which handles everything.
       Treelist tl;  
       // contains the Datamask for where we should start lineages from.
       Datamask samplegrid;  
        // only set to true if the simulation has finished, otherwise will be false.
       bool sim_complete; 
       
       // THESE VARIABLES DON'T NEED TO BE SAVED ON PAUSE/RESUME
       // Create the step object that will be retained for the whole simulation.
       Step this_step; 
       // If true, means the command-line imports were under the (deprecated) fullmode.
       bool bFullmode; 
       // If true, the simulation is to be resumed.
       bool bResume; 
       // If true, a config file contains the simulation variables.
       bool bConfig; 
       // If true, simulation can be resumed.
       bool bPaused, bPausedImport;
       
       // Should always be false in the base class
       bool bIsProtracted; 
   public:
       // constructor
       Tree() : tl(&data)
       {
           enddata = 0;
           seeded = false;
           the_seed = -10;
           log_all = true;  // set this equal to true if you want to log every 5 seconds to a logfile.
           the_task = -1;
           varimport = false;
           sqloutname = "null";
           sim_complete = false;
           time_taken = 0;  // the time taken starts at 0, unless imported from file.
           maxtime = 0;
           sigma = 0.0;
           tau = 0.0;
           // Set the databases to NULL pointers.
           database = nullptr;
           outdatabase = nullptr;
           bFullmode = false;
           bResume = false;
           bConfig = false;
           bPaused = false;
           bPausedImport = false;
           bIsProtracted = false;
       }
       
       ~Tree()
       {
           sqlite3_close_v2(database);
           sqlite3_close_v2(outdatabase);
       }
       
       void importSimulationVariables(vector<string> & comargs);
       
       void importSimulationVariables(string config_file);
       
       void parseArgs(vector<string> & comargs);
       
       void checkFolders();
       
       void checkSims();
       
       void checkSims(string output_dir, long seed, long task);
       
       void setParameters();
   
       vector<double> getTemporalSampling();
   
       // Imports the maps using the variables stored in the class. This function must be run after the set_mapvars() in
       // order to function correctly.
       void importMaps();
   
       long long getSeed();
   
       void setSeed(long long theseedin);
   
       bool getbPaused();
       
       vector<long> randomList(long maxnum, long numnum);
   
       unsigned long setObjectSizes();
   
       void setupDispersalCoordinator();
       
   
       void setup();
       
       void removeOldPos(const unsigned long &chosen);
   
       void calcMove(Step &this_step);
   
       
       //
       //
       long double calcMinMax(const unsigned long &current);
   
       void coalescenceEvent(const unsigned long &chosen, unsigned long &coalchosen);
   
       //
       //
       void calcNewPos(bool &coal,
                       const unsigned long &chosen,
                       unsigned long &coalchosen,
                       const long &oldx,
                       const long &oldy,
                       const long &oldxwrap,
                       const long &oldywrap);
   
       void switchPositions(const unsigned long chosen);
   
       void speciation(const unsigned long &chosen);
       
       virtual bool calcSpeciation(const long double & random_number, const long double & speciation_rate, const int & no_generations);
       
       unsigned long estSpecnum();
   
       void runChecks(const unsigned long &chosen, const unsigned long &coalchosen);
   
       void validationCheck(const unsigned long &chosen, int o, const unsigned long &current, const bool &coal);
   
       void checkSimSize(unsigned long req_data, unsigned long req_active);
   
       void writeSimStartToConsole();
       
       void setSimStartVariables();
       
   #ifdef verbose
   
       void writeStepToConsole();
   #endif
       
   #ifdef pristine_mode
   
       void pristineStepChecks();
   #endif
       
       void checkMapUpdate();
       
       void chooseRandomLineage();
       
   #ifdef DEBUG
   
       void debugCoalescence();
   
       void debugDispersal();
       
       void debugEndStep();
   #endif
   
       bool runSimulation();
       
       
       bool stopSimulation();
       
       void expandMap(double generationin);
   
       unsigned long sortData();
   
       void outputData();
       void outputData(unsigned long species_richness);
   
       void writeTimes();
       
       virtual void setProtractedVariables(double speciation_gen_min, double speciation_gen_max);
       
       virtual string getProtractedVariables();
       
       virtual double getProtractedGenerationMin();
       
       virtual double getProtractedGenerationMax();
       
       void simPause();
   
       void setResumeParameters(string pausedir, string outdir, unsigned long seed, unsigned long task, unsigned long new_max_time);
       
       void setResumeParameters();
       virtual void loadMainSave();
   
       void loadDataSave();
   
       void loadActiveSave();
   
       void loadGridSave();
   
       void loadMapSave();
   
       void simResume();
   
       void sqlCreate();
       
       virtual string protractedVarsToString();
       
       void sqlOutput();
   
       void applySpecRate(double sr, double t);
   
       void applySpecRate(double sr);
       
       void applyMultipleRates();
       
       
       void determineSpeciationRates();
   
       void verifyReproductionMap();
   
       void addWrappedLineage(unsigned long numstart, long x, long y);
   
       void convertTip(unsigned long i, double generationin);
   
       unsigned long countCellExpansion(const long &x, const long &y, const long &xwrap, const long &ywrap,
                                        const double &generationin, const bool &make_tips);
   
       void expandCell(long x, long y, long xwrap, long ywrap, double generationin, unsigned long add);
   
       void makeTip(const unsigned long &tmp_active, const double &generationin);
   
   
       void validateLineages();
   
   #ifdef DEBUG
   
       void debugAddingLineage(unsigned long numstart, long x, long y);
   #endif
   };
   
   #endif  // TREE
