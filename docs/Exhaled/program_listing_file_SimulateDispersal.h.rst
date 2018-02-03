
.. _program_listing_file_SimulateDispersal.h:

Program Listing for File SimulateDispersal.h
========================================================================================

- Return to documentation for :ref:`file_SimulateDispersal.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef DISPERSAL_TEST
   #define DISPERSAL_TEST
   #ifndef PYTHON_COMPILE
   #define PYTHON_COMPILE
   #endif
   #include <string>
   #include <stdio.h>
   #include <vector>
   #include <iostream>
   #include <fstream>
   #include <math.h>
   #include <stdexcept>
   #include <sqlite3.h>
   #include "Matrix.h"
   #include "CustomExceptions.h"
   #include "Fattaildeviate.h"
   
   struct Cell
   {
       unsigned long x;
       unsigned long y;
   };
   
   class SimulateDispersal
   {
   protected:
       // The density map object
       Matrix<unsigned long> density_map;
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
       // The number of repeats
       unsigned long num_repeats;
       // The maximal density value
       unsigned short max_density;
       // If true, sequentially selects dispersal probabilities, default is true
       bool is_sequential;
       // Function pointer for the landscape function
       typedef bool (SimulateDispersal::*landscape_fptr)(double dist, double angle, Cell &this_cell);
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
           database = nullptr;
           max_density = 0;
           seed = 0;
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
       
       void storeCellList();
       
       const Cell& getRandomCell();
   
       bool getEndPointInfinite(double dist, double angle, Cell &this_cell);
   
       bool getEndPointTiled(double dist, double angle, Cell &this_cell);
   
       bool getEndPointClosed(double dist, double angle, Cell &this_cell);
   
       bool getEndPoint(double dist, double angle, Cell &this_cell);
       
       void runDispersal();
       
       void writeDatabase();
   
   
   };
   
   #endif
