
.. _program_listing_file_necsim_main.cpp:

Program Listing for File main.cpp
=================================

- Return to documentation for :ref:`file_necsim_main.cpp`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifdef DEBUG
   #ifndef verbose
   #define verbose
   #endif
   #endif
   
   #include "Logging.h"
   #include "Logger.h"
   #include "SpatialTree.h"
   #include "SimulationTemplates.h"
   
   // #define historical_mode // not required unless you experience problems.
   // This performs a more thorough check after each move operation.
   // Currently, it will also check that the historical state value is greater than the returned value within every map cell.
   // Note that this may cause problems if the historical state is not the state with the highest number of individuals.
   
   
   
   /************************************************************
           MAIN ROUTINE AND COMMAND LINE ARG ROUTINES
   
    ************************************************************/
   
   
   
   int main(int argc, char *argv[])
   {
       logger = new Logger();
       vector<string> comargs;
       importArgs(static_cast<const unsigned int &>(argc), argv, comargs);
       const string &config_file = getConfigFileFromCmdArgs(comargs);
       runMain<SpatialTree>(config_file);
       delete logger;
       return 0;
   }
