
.. _program_listing_file_Treelist.h:

Program Listing for File Treelist.h
========================================================================================

- Return to documentation for :ref:`file_Treelist.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   // This code is a used to analyse a list of Treenode objects to generate species abundances for a given speciation rate.
   // For use within Coal_sim v3.1+
   // Author: Samuel Thompson
   // Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
   // Version 1.1
   //#include "Treenode.h"
   #ifndef TREELIST
   #define TREELIST
   
   #include <math.h>
   #include <sqlite3.h>
   #include <cstring>
   #include <cmath>
   #include <stdexcept>
   #include <string>
   # include <boost/filesystem.hpp>
   #include <boost/lexical_cast.hpp>
    #include "CustomExceptions.h"
   #include "Logging.h"
   #include "Treenode.h"
   #include "Matrix.h"
   #include "Datamask.h"
   
   using namespace std;
   using std::string;
   
   bool checkSpeciation(const long double & random_number, const long double & speciation_rate, const int & no_generations);
   
   bool doubleCompare(double d1, double d2, double epsilon);
   struct PreviousCalcPair
   {
       double speciation_rate;
       double time;
       bool fragment;
       
       PreviousCalcPair(double speciation_rate_in, double time_in, double fragment_in)
       {
           time = time_in;
           speciation_rate = speciation_rate_in;
           fragment = fragment_in;
       }
   };
   
   struct CalcPairArray
   {
       vector<PreviousCalcPair> calc_array;
       
       void push_back(double speciation_rate, double time, bool fragment)
       {
           PreviousCalcPair tmp_pair(speciation_rate, time, fragment);
           calc_array.push_back(tmp_pair);
       }
       
       bool hasPair(double speciation_rate, double time, bool fragment)
       {
           for(unsigned int i =0; i<calc_array.size(); i++)
           {
               if(doubleCompare(calc_array[i].time, time, time*0.00001) &&
                  doubleCompare(calc_array[i].speciation_rate, speciation_rate, speciation_rate*0.00001) &&
                  calc_array[i].fragment == fragment)
               {
                   return true;
               }
           }
           return false;
       }
       
       bool hasPair(double speciation_rate, double time)
       {
           return hasPair(speciation_rate, time, true);
       }
   };
   
   // A class containing the fragment limits as x,y coordinates.
   struct Fragment
   {
       // the name for the fragment (for reference purposes)
       string name;
       // coordinates for the extremes of the site
       long x_east, x_west, y_north, y_south;
       // the number of lineages in the fragment.
       unsigned long num;
       double area;
   };
   
   // Class for creating the sample matrix object for easy referencing
   
   class Samplematrix :  public Datamask
   {
   private:
       bool bIsNull;
       bool bIsFragment;
       Fragment fragment;
   public:
       Samplematrix()
       {
           bIsFragment = false;
           bIsNull = false;
       }
       
       void setIsNull(bool b)
       {
           bIsNull = b;
       }
       
       bool getIsNull()
       {
           return bIsNull;
       }
       
       bool getTestVal(unsigned long xval, unsigned long yval, long xwrap, long ywrap)
       {
           return getVal(xval, yval, xwrap, ywrap);
       }
       
       bool getMaskVal(unsigned long x1, unsigned long y1, long x_wrap, long y_wrap)
       {
           if(bIsFragment)
           {
               long x, y;
               x = x1 + (x_wrap * x_dim) + x_offset;
               y = y1 + (y_wrap * y_dim) + y_offset;
               return fragment.x_west <= x && x <= fragment.x_east && fragment.y_north <= y &&
                       y <= fragment.y_south;
           }
           if(bIsNull)
           {
               return true;
           }
           return getVal(x1, y1, x_wrap, y_wrap);
       }
       
        void setFragment(Fragment & fragment_in)
        {
               fragment = fragment_in;
   //          os << "W,E,N,S: " << fragment.x_west << ", " << fragment.x_east << ", " << fragment.y_north << ", " << fragment.y_south << endl;
               bIsFragment = true;
        }
        
        void removeFragment()
        {
            bIsFragment = false;
        }
   };
   
   
   
   
   
   class Treelist
   {
   private:
       bool bMem; // boolean for whether the database is in memory or not.
       bool bFileSet; // boolean for whether the database has been set already.
       sqlite3 * database; // stores the in-memory database connection.
       sqlite3 * outdatabase; // stores the file database connection
       bool bSqlConnection; // true if the data connection has been established.
       Row<Treenode> *nodes; // in older versions this was called list. Changed to avoid confusion with the built-in class.
       Row<unsigned int> rOut;
       double dSpecRate;
       unsigned long iSpecies;
       long double generation; // the time of interest for the simulation
       bool bSample; // checks whether the samplemask has already been imported.
       bool bDataImport; // checks whether the main sim data has been imported.
       string samplemaskfile; // stores the name of the file object for referencing.
       Samplematrix samplemask; // the samplemask object for defining the areas we want to sample from.
       vector<Fragment> fragments; // a vector of fragments for storing each fragment's coordinates.
       // the minimum speciation rate the original simulation was run with (this is read from the database SIMULATION_PARAMETERS table)
       double min_spec_rate; 
       // The dimensions of the sample grid size.
       unsigned long grid_x_size, grid_y_size;
       // The dimensions of the original sample map file
       unsigned long samplemask_x_size, samplemask_y_size, samplemask_x_offset, samplemask_y_offset;
       // Vector containing past speciation rates
       CalcPairArray past_speciation_rates;
       // Protracted speciation parameters
       bool protracted;
       double min_speciation_gen, max_speciation_gen, applied_max_speciation_gen;
   public:
       
       
       Treelist(Row<Treenode> *r):nodes(r)
       {
           bMem = false;
           dSpecRate =0;
           iSpecies =0;
           bSample = false;
           bSqlConnection = false;
           bFileSet = false;
           bDataImport = false;
           generation = 0;
           min_speciation_gen = 0.0;
           max_speciation_gen = 0.0;
           applied_max_speciation_gen = 0.0;
           protracted = false;
       }
       
       Treelist()
       {
           bMem = false;
           dSpecRate =0;
           iSpecies =0;
           bSample = false;
           bSqlConnection = false;
           bFileSet = false;
           bDataImport = false;
           generation = 0;
           min_speciation_gen = 0.0;
           max_speciation_gen = 0.0;
           applied_max_speciation_gen = 0.0;
           protracted = false;
       }
       
       ~Treelist()
       {
           nodes = nullptr;
       }
       void setList(Row<Treenode> *l);
       
       void setDatabase(sqlite3 * dbin);
       
       bool hasImportedData();
       
       double getMinimumSpeciation();
       
       void importSamplemask(string sSamplemask);
       
       unsigned long countSpecies();
       
       unsigned long calcSpecies(double s);
       
       void calcSpeciesAbundance();
       
       void resetTree();
       
       void detectDimensions(string db);
       
       void openSqlConnection(string inputfile);
       
       void internalOption();
       void importData(string inputfile);
       
       
       void importSimParameters(string file);
       
       void setProtractedParameters(double max_speciation_gen_in);
       
       void setProtractedParameters(double min_speciation_gen_in, double max_speciation_gen_in);
       
       void setProtracted(bool protracted_in);
       
       void setGeneration(long double generationin);
       ;
       
       void createDatabase(double s);
       
       bool checkRepeatSpeciation(double s, double generation, bool fragment);
       
       bool checkRepeatSpeciation(double s, double generation);
       
       bool checkRepeatSpeciation(double s);
       
       void createFragmentDatabase(const Fragment &f);
       
       void exportDatabase(string outputfile);
       
       void recordSpatial();
       
       void calcFragments(string fragment_file);
       
       void applyFragments();
       
       void getPreviousCalcs();
   };
   
   
   
   #endif
