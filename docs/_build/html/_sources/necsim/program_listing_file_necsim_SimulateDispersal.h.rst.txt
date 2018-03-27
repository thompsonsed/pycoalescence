
.. _program_listing_file_necsim_SimulateDispersal.h:

Program Listing for File SimulateDispersal.h
============================================

- Return to documentation for :ref:`file_necsim_SimulateDispersal.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef DISPERSAL_TEST
   #define DISPERSAL_TEST
   #ifndef PYTHON_COMPILE
   #define PYTHON_COMPILE
   #endif
   #include<string>
   #include <cstdio>
   #include <vector>
   #include <iostream>
   #include <fstream>
   #include <cmath>
   #include <stdexcept>
   #include <sqlite3.h>
   #include "Map.h"
   #include "NRrand.h"
   struct Cell
   {
       long x;
       long y;
       Cell &operator=(Cell const& c)
       = default;
   };
   
   double distanceBetween(Cell &c1, Cell &c2);
   
   class SimulateDispersal
   {
   protected:
       // The density map object
       Map<uint32_t> density_map;
       // Set to true when the size of the density map has been set
       bool has_set_size;
       // The random number generator object
       NRrand random;
       // The map file path
       string map_name;
       // The random number seed
       unsigned long seed;
       // The dispersal method
       string dispersal_method;
       // The dispersal sigma value
       double sigma;
       // The dispersal nu value (for fat-tailed dispersal kernels)
       double tau;
       // The dispersal m_probability - chance of picking from a uniform distribution (for norm-uniform dispersal kernels)
       double m_prob;
       // The maximum dispersal distance for the norm-uniform dispersal distance
       double cutoff;
       // The sqlite3 database object for storing outputs
       sqlite3 * database;
       // Vector for storing successful dispersal distances
       vector<double> distances;
       // Vector for storing the cells (for randomly choosing from)
       vector<Cell> cells;
       // The number of repeats to run the dispersal loop for
       unsigned long num_repeats;
       // The number of num_steps within each dispersal loop for the average distance travelled/
       unsigned long num_steps;
       // The maximal density value
       unsigned long max_density;
       // If true, sequentially selects dispersal probabilities, default is true
       bool is_sequential;
       // Reference number for this set of parameters in the database output
       unsigned long parameter_reference;
       // Function pointer for the landscape function
       typedef bool (SimulateDispersal::*landscape_fptr)(const double &dist, const double &angle,
                                                         const Cell &this_cell, Cell &end_cell);
       landscape_fptr getValFptr;
   public:
       SimulateDispersal()
       {
           has_set_size = false;
           sigma = 0.0;
           tau = 0.0;
           m_prob = 0.0;
           cutoff = 0.0;
           num_repeats = 0;
           num_steps = 0;
           database = nullptr;
           max_density = 0;
           seed = 0;
           is_sequential = false;
           parameter_reference = 0;
       }
       
       ~SimulateDispersal()
       {
           sqlite3_close(database);
       }
       
       void setSequential(bool bSequential);
       
       void setSizes(unsigned long x, unsigned long y);
   
       void importMaps(string map_file);
       
       void setSeed(unsigned long s)
       {
           seed = s;
           random.setSeed(s);
       }
       
       void setDispersalParameters(string dispersal_method_in, double sigma_in, double tau_in, double m_prob_in,
                                    double cutoff_in, string landscape_type);
   
       void setLandscapeType(string landscape_type);
   
       void setOutputDatabase(string out_database);
       
       void setNumberRepeats(unsigned long n);
   
       void setNumberSteps(unsigned long s);
       void storeCellList();
       
       const Cell& getRandomCell();
   
       void calculateNewPosition(const double &dist, const double &angle, const Cell &start_cell, Cell &end_cell);
   
       bool getEndPointInfinite(const double &dist, const double &angle, const Cell &this_cell, Cell &end_cell);
   
       bool getEndPointTiled(const double &dist, const double &angle, const Cell &this_cell, Cell &end_cell);
   
       bool getEndPointClosed(const double &dist, const double &angle, const Cell &this_cell, Cell &end_cell);
   
       bool getEndPoint(const double &dist, const double &angle, const Cell &this_cell, Cell &end_cell);
       
       void runMeanDispersalDistance();
   
       void runMeanDistanceTravelled();
       
       void writeDatabase(string table_name);
   
       void writeParameters(string table_name);
   
       void checkMaxParameterReference();
   
       unsigned long checkMaxIdNumber(string table_name);
   };
   
   #endif
