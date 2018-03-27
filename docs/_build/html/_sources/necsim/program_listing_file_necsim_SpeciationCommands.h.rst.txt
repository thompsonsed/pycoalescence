
.. _program_listing_file_necsim_SpeciationCommands.h:

Program Listing for File SpeciationCommands.h
=============================================

- Return to documentation for :ref:`file_necsim_SpeciationCommands.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #include <cstdio>
   
   #include "Community.h"
   #include "TreeNode.h"
   #include "SpecSimParameters.h"
   
   class SpeciationCommands
   {
   private:
       // Contains all speciation parameters
       SpecSimParameters sp;
       // Set up for the output coalescence tree
       Row<TreeNode> data;
       // Command-line arguments for parsing
       vector<string> comargs;
       // number of command-line arguments
       int argc;
   
   
   public:
       
       SpeciationCommands()
       {
           
       }
       
       void parseArgs();
   
       int applyFromComargs(int argc_in, char ** argv);
   
   };
