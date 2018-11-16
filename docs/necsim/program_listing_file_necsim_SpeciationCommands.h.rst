
.. _program_listing_file_necsim_SpeciationCommands.h:

Program Listing for File SpeciationCommands.h
=============================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_SpeciationCommands.h>` (``necsim/SpeciationCommands.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #include <cstdio>
   #include <memory>
   #include "Community.h"
   #include "TreeNode.h"
   #include "SpecSimParameters.h"
   
   class SpeciationCommands
   {
   private:
       // Contains all speciation current_metacommunity_parameters
       shared_ptr<SpecSimParameters> sp;
       // Command-line arguments for parsing
       vector<string> comargs;
       // number of command-line arguments
       int argc;
   
   
   public:
       
       SpeciationCommands() : sp(make_shared<SpecSimParameters>())
       {
           
       }
       
       void parseArgs();
   
       int applyFromComargs(int argc_in, char ** argv);
   
   };
