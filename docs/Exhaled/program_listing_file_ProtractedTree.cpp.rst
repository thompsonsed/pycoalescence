
.. _program_listing_file_ProtractedTree.cpp:

Program Listing for File ProtractedTree.cpp
========================================================================================

- Return to documentation for :ref:`file_ProtractedTree.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   //
   #include "ProtractedTree.h"
   
   
   bool ProtractedTree::calcSpeciation(const long double & random_number, const long double & speciation_rate, const int & no_generations)
   {
       if(generation < speciation_generation_min)
       {
           return false;
       }
       if(generation > speciation_generation_max)
       {
           return true;
       }
       return checkSpeciation(random_number, speciation_rate, no_generations);
   }
   
   void ProtractedTree::setProtractedVariables(double speciation_gen_min_in, double speciation_gen_max_in)
   {
       speciation_generation_min = speciation_gen_min_in;
       speciation_generation_max = speciation_gen_max_in;
   }
   
   string ProtractedTree::getProtractedVariables()
   {
       stringstream ss;
       ss << speciation_generation_min << "\n" << speciation_generation_max << "\n";
       return ss.str();
   }
   
   double ProtractedTree::getProtractedGenerationMin()
   {
       return speciation_generation_min;
   }
   
   double ProtractedTree::getProtractedGenerationMax()
   {
       return speciation_generation_max;
   }
   
   string ProtractedTree::protractedVarsToString()
   {
       string tmp = "1 , " + to_string(speciation_generation_min) + ", " + to_string(speciation_generation_max);
       return tmp;
   }
   
   
   int runMainProtracted(int argc, vector<string> argv)
   {
       // Create our SimSetup object
       // This performs some basic checks to make sure that our simulation parameters make sense
       // It also outputs the information if the user requests help or runs with incorrect options.
   #ifndef verbose
       // Open our file for logging outputs
       openLogFile(false);
   #endif
       // Parse our arguments
       vector<string> comargs;
       comargs = argv;
       // Create our tree object that contains the simulation
       ProtractedTree tree;
       tree.importSimulationVariables(comargs);
       // Setup the sim
       tree.setup();
       // Detect speciation rates to apply
       bool isComplete = tree.runSimulation();
       if(isComplete)
       {
           tree.applyMultipleRates();
       }
   #ifndef verbose
       fclose(stdout);
   #endif
       write_cout("*************************************************\n");
       return 0;
   }
