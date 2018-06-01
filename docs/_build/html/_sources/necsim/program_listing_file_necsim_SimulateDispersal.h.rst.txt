
.. _program_listing_file_necsim_SimulateDispersal.h:

Program Listing for File SimulateDispersal.h
============================================

- Return to documentation for :ref:`file_necsim_SimulateDispersal.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
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
   #include "Landscape.h"
   #include "DispersalCoordinator.h"
   #include "NRrand.h"
   #include "Cell.h"
   
   
   class SimulateDispersal
   {
   protected:
       // The density map object
       Landscape density_landscape;
       // Dispersal coordinator
       DispersalCoordinator dispersal_coordinator{};
       // Stores all key simulation parameters for the Landscape object
       SimParameters  * simParameters;
       // The random number generator object
       NRrand random;
       // The random number seed
       unsigned long seed;
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
       // generation counter
       double generation;
       // If true, sequentially selects dispersal probabilities, default is true
       bool is_sequential;
       // Reference number for this set of parameters in the database output
       unsigned long parameter_reference;
   public:
       SimulateDispersal()
       {
           simParameters = nullptr;
           num_repeats = 0;
           num_steps = 0;
           database = nullptr;
           seed = 0;
           is_sequential = false;
           parameter_reference = 0;
           generation = 0.0;
       }
       
       ~SimulateDispersal()
       {
           sqlite3_close(database);
       }
       
       void setSequential(bool bSequential);
   
       void setSimulationParameters(SimParameters * sim_parameters, bool print=true);
   
       void importMaps();
   
       void setDispersalParameters();
   
       void setSeed(unsigned long s)
       {
           seed = s;
           random.wipeSeed();
           random.setSeed(s);
       }
   
       void setOutputDatabase(string out_database);
       
       void setNumberRepeats(unsigned long n);
   
       void setNumberSteps(unsigned long s);
       void storeCellList();
       
       const Cell& getRandomCell();
   
       void getEndPoint(Cell &this_cell);
       
       void runMeanDispersalDistance();
   
       void runMeanDistanceTravelled();
       
       void writeDatabase(string table_name);
   
       void writeParameters(string table_name);
   
       void checkMaxParameterReference();
   
       unsigned long checkMaxIdNumber(string table_name);
   };
   
   #endif
