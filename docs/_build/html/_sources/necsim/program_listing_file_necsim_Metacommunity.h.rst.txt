
.. _program_listing_file_necsim_Metacommunity.h:

Program Listing for File Metacommunity.h
========================================

- Return to documentation for :ref:`file_necsim_Metacommunity.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef SPECIATIONCOUNTER_METACOMMUNITY_H
   #define SPECIATIONCOUNTER_METACOMMUNITY_H
   
   #include <string>
   #include <sqlite3.h>
   #include <set>
   #include "Community.h"
   #include "Tree.h"
   #include "NRrand.h"
   #include "SpecSimParameters.h"
   
   using namespace std;
   class Metacommunity : public virtual Community
   {
   protected:
       // The number of individuals in the metacommunity
       unsigned long community_size;
       // The speciation rate used for creation of the metacommunity
       long double speciation_rate;
       // Simulation seed and task (read from the output database or set to 1)
       unsigned long seed;
       unsigned long task;
       bool parameters_checked;
       Row<unsigned long> * metacommunity_cumulative_abundances;
       NRrand random;
       Tree metacommunity_tree;
   public:
   
       Metacommunity();
   
       ~Metacommunity() override = default;
   
       void setCommunityParameters(unsigned long community_size_in, long double speciation_rate_in);
   
       void checkSimulationParameters();
   
       void addSpecies(unsigned long &species_count, TreeNode *tree_node, set<unsigned long> &species_list) override;
   
       void createMetacommunityNSENeutralModel();
   
       unsigned long selectLineageFromMetacommunity();
   
       void applyNoOutput(SpecSimParameters *sp) override ;
   
   
   };
   
   
   #endif //SPECIATIONCOUNTER_METACOMMUNITY_H
