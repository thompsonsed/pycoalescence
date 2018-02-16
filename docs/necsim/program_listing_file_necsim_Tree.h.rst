
.. _program_listing_file_necsim_Tree.h:

Program Listing for File Tree.h
===============================

- Return to documentation for :ref:`file_necsim_Tree.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef TREE_H
   #define TREE_H
   #ifndef sql_ram
   #define sql_ram
   #endif
   
   #include <sqlite3.h>
   #include "TreeNode.h"
   #include "Matrix.h"
   #include "SimParameters.h"
   #include "NRrand.h"
   #include "DataPoint.h"
   #include "Community.h"
   #include "Filesystem.h"
   #include "CustomExceptions.h"
   #include "Step.h"
   
   class Tree
   {
   protected:
       // storing the coalescence tree itself
       Row<TreeNode> data;
       // a reference for the last written point in data.
       unsigned long enddata;
       // Stores the command line parameters and parses the required information.
       SimParameters sim_parameters;
       // random number generator
       NRrand NR;
       // Storing the speciation rates for later reference.
       vector<long double> speciation_rates;
       // flag for having set the simulation seed.
       bool seeded;
       // random seed
       long long the_seed;
       // for file naming - good to know which task in a series is being executed here
       long long the_task;
       // The map file containing the times that we want to expand the model and record all lineages again.
       // If this is null, has_times_file will be false and the vector will be empty.
       string times_file;
       vector<double> reference_times;
       // Set to true if we are recording at times other than the present day.
       bool has_times_file;
       // The time variables (for timing the simulation in real time)
       time_t start, sim_start, sim_end, now, sim_finish, out_finish;
       time_t time_taken;
       // Active lineages stored as a row of datapoints
       Row<DataPoint> active;
       // Stores the point of the end of the active vector. 0 is reserved as null
       unsigned long endactive;
       // the maximum size of endactive
       unsigned long startendactive;
       // the maximum simulated number of individuals in the present day.
       unsigned long maxsimsize;
       // for create the link to the speciationcounter object which handles everything.
       Community community;
       // This might need to be updated for simulations that have large changes in maximum population size over time.
       // number of simulation num_steps
       long steps;
       // Maximum time to run for (in seconds)
       unsigned long maxtime;
       // number of generations passed,
       double generation;
       // The number of individuals per cell
       long deme;
       // The proportion of individuals to sample
       double deme_sample;
       // the speciation rate
       long double spec;
       // Path to output directory
       string out_directory;
       // sqlite3 object that stores all the data
       sqlite3 *database;
       // only set to true if the simulation has finished, otherwise will be false.
       bool sim_complete;
       // set to true when variables are imported
       bool has_imported_vars;
   // If sql database is written first to memory, then need another object to contain the in-memory database.
   #ifdef sql_ram
       sqlite3 *outdatabase;
   #endif
       // Create the step object that will be retained for the whole simulation.
       // Does not need saving on simulation pause.
       Step this_step;
       string sqloutname;
       // If true, means the command-line imports were under the (deprecated) fullmode.
       bool bFullmode;
       // If true, the simulation is to be resumed.
       bool bResume;
       // If true, a config file contains the simulation variables.
       bool bConfig;
       // If true, simulation can be resumed.
       bool has_paused, has_imported_pause;
       // Should always be false in the base class
       bool bIsProtracted;
       // variable for storing the paused sim location if files have been moved during paused/resumed simulations!
       string pause_sim_directory;
   #ifdef DEBUG
       // For debugging purposes
       unsigned long count_dispersal_fails, count_density_fails;
   #endif
   public:
       Tree() : community(&data), this_step()
       {
           has_imported_vars = false;
           enddata = 0;
           seeded = false;
           the_seed = -10;
           // set this equal to true if you want to log every 5 seconds to a logfile.
           the_task = -1;
           sqloutname = "null";
           sim_complete = false;
           time_taken = 0;  // the time taken starts at 0, unless imported from file.
           maxtime = 0;
           // Set the database to NULL pointers.
           database = nullptr;
           outdatabase = nullptr;
           has_times_file = false;
           start = 0;
           sim_start = 0;
           sim_end = 0;
           now = 0;
           sim_finish = 0;
           out_finish = 0;
           endactive = 0;
           startendactive = 0;
           maxsimsize = 0;
           steps = 0;
           generation = 0.0;
           spec = 0.0;
           deme_sample = 0.0;
           deme = 0;
           bFullmode = false;
           bResume = false;
           bConfig = true;
           has_paused = false;
           has_imported_pause = false;
           bIsProtracted = false;
           pause_sim_directory = "null";
       }
   
       virtual ~Tree()
       {
           sqlite3_close_v2(database);
   #ifdef sql_ram
           sqlite3_close_v2(outdatabase);
   #endif
       }
   
   
       virtual void importSimulationVariables(const string &configfile);
   
       void internalSetup(const SimParameters &sim_parameters_in);
   
       bool checkOutputDirectory();
   
   
       void checkSims();
   
       void checkSims(string output_dir, long seed, long task);
   
       virtual void setParameters();
   
       virtual void setProtractedVariables(double speciation_gen_min, double speciation_gen_max);
   
       bool hasPaused();
   
       vector<double> getTemporalSampling();
   
       long long getSeed();
   
       void setSeed(long long seed_in);
   
       virtual unsigned long getInitialCount();
   
       unsigned long setObjectSizes();
   
       virtual void setup();
   
       void setInitialValues();
   
       void setSimStartVariables();
   
       void printSetup();
   
       void setTimes();
   
       void determineSpeciationRates();
   
       void generateObjects();
   
       virtual unsigned long fillObjects(const unsigned long &initial_count);
   
        virtual bool runSimulation();
   
       void writeSimStartToConsole();
   
       void writeStepToConsole();
   
       virtual void incrementGeneration();
   
       void chooseRandomLineage();
   
       virtual void updateStepCoalescenceVariables();
   
       void speciation(const unsigned long &chosen);
   
       virtual void speciateLineage(const unsigned long &data_position);
       virtual void removeOldPosition(const unsigned long &chosen);
   
       virtual void switchPositions(const unsigned long &chosen);
   
       virtual void calcNextStep();
   
       virtual bool calcSpeciation(const long double &random_number,
                                   const long double &speciation_rate,
                                   const unsigned long &no_generations);
   
       void coalescenceEvent(const unsigned long &chosen, unsigned long &coalchosen);
   
       void checkTimeUpdate();
   
       virtual void addLineages(double generation_in);
   
       void checkSimSize(unsigned long req_data, unsigned long req_active);
   
   
       void makeTip(const unsigned long &tmp_active, const double &generation_in);
   
       void convertTip(unsigned long i, double generationin);
   
       bool stopSimulation();
   
       void applySpecRate(long double sr, double t);
   
       void applySpecRateInternal(long double sr, double t);
   
       Row<unsigned long> *getCumulativeAbundances();
       void setupTreeGeneration(long double sr, double t);
   
       void applySpecRate(long double sr);
   
       void applyMultipleRates();
   
       virtual bool getProtracted();
   
       virtual string getProtractedVariables();
   
       virtual double getProtractedGenerationMin();
   
       virtual double getProtractedGenerationMax();
   
   
       void sqlOutput();
   
       void outputData();
   
       void outputData(unsigned long species_richness);
   
       unsigned long sortData();
   
       void writeTimes();
   
   
       void sqlCreate();
   
       void sqlCreateSimulationParameters();
   
       virtual string simulationParametersSqlInsertion();
   
       virtual string protractedVarsToString();
   
   
       virtual void simPause();
   
       string initiatePause();
   
       void dumpMain(string pause_folder);
   
       void dumpActive(string pause_folder);
   
       void dumpData(string pause_folder);
   
       void completePause();
   
       void setResumeParameters(string pausedir, string outdir, unsigned long seed, unsigned long task,
                                unsigned long new_max_time);
   
       void setResumeParameters();
   
       virtual void loadMainSave();
   
       void loadDataSave();
   
       void loadActiveSave();
   
       void initiateResume();
   
       virtual void simResume();
   #ifdef DEBUG
   
       virtual void validateLineages();
   
       virtual void debugEndStep();
   
       void debugCoalescence();
   
       virtual void runChecks(const unsigned long &chosen, const unsigned long &coalchosen);
   
       void miniCheck(const unsigned long &chosen);
   #endif // DEBUG
   };
   
   
   #endif //TREE_H
