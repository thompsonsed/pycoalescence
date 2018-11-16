
.. _program_listing_file_necsim_SimulationTemplates.h:

Program Listing for File SimulationTemplates.h
==============================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_SimulationTemplates.h>` (``necsim/SimulationTemplates.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   //
   #ifndef SIMULATIONTEMPLATES_H
   #define SIMULATIONTEMPLATES_H
   #include <string>
   #include <sstream>
   #include "Logger.h"
   #include "custom_exceptions.h"
   
   const string & getConfigFileFromCmdArgs(const vector<string> & com_args)
   {
       if(com_args.size() != 3)
       {
           stringstream ss;
           ss << "Incorrect number of command-line arguments supplied. Should be 3, got " << com_args.size() << endl;
           throw FatalException(ss.str());
       }
       else
       {
           return com_args[2];
       }
   }
   
   template <class T> void runMain(const string &config_file)
   {
       // Create our tree object that contains the simulation
       T tree;
       tree.importSimulationVariables(config_file);
       // Setup the sim
       tree.setup();
       // Detect speciation rates to apply
       bool isComplete = tree.runSimulation();
       if(isComplete)
       {
           tree.applyMultipleRates();
       }
       writeInfo("*************************************************\n");
   }
   
   #endif //SIMULATIONTEMPLATES_H
