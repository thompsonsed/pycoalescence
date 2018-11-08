
.. _program_listing_file_necsim_Metacommunity.h:

Program Listing for File Metacommunity.h
========================================

- Return to documentation for :ref:`file_necsim_Metacommunity.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef SPECIATIONCOUNTER_METACOMMUNITY_H
   #define SPECIATIONCOUNTER_METACOMMUNITY_H
   
   #include <string>
   #include <sqlite3.h>
   #include <set>
   #include <memory>
   #include "Community.h"
   #include "Tree.h"
   #include "NRrand.h"
   #include "SpecSimParameters.h"
   #include "SpeciesAbundancesHandler.h"
   
   using namespace std;
   
   class Metacommunity : public virtual Community
   {
   protected:
       // Simulation seed and task (read from the output database or set to 1)
       unsigned long seed;
       unsigned long task;
       bool parameters_checked;
       shared_ptr<SpeciesAbundancesHandler> species_abundances_handler;
       shared_ptr<NRrand> random;
       unique_ptr<Tree> metacommunity_tree;
   public:
   
       Metacommunity();
   
       ~Metacommunity() override = default;
   
       void setCommunityParameters(shared_ptr<MetacommunityParameters> metacommunity_parameters);
   
       void checkSimulationParameters();
   
       void addSpecies(unsigned long &species_count, TreeNode *tree_node, set<unsigned long> &species_list) override;
   
       void createMetacommunityNSENeutralModel();
   
       void applyNoOutput(shared_ptr<SpecSimParameters> sp) override;
   
       void approximateSAD();
   
       void readSAD();
   
       void printMetacommunityParameters();
   
   };
   
   #endif //SPECIATIONCOUNTER_METACOMMUNITY_H
