
.. _program_listing_file_necsim_ProtractedTree.h:

Program Listing for File ProtractedTree.h
=========================================

- Return to documentation for :ref:`file_necsim_ProtractedTree.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   //
   #include <vector>
   #include <string>
   
   #include "SpatialTree.h"
   
   #ifndef PROTRACTED_SPATIAL_TREE_H
   #define PROTRACTED_SPATIAL_TREE_H
   
   class ProtractedTree : public virtual Tree
   {
   private:
       // Variables for the protracted speciation variables
       // The number of generations a lineage must exist before speciating.
       // Speciation is therefore not allowed before this time.
       // If this value is 0, it has no effect.
       double speciation_generation_min;
       // The number of generations a lineage can exist before speciating.
       // All remaining lineages are speciated at this time.
       // If this value is 0, it has no effect.
       double speciation_generation_max;
   public:
       
       ProtractedTree() : Tree()
       {
           bIsProtracted = true;
           speciation_generation_min = 0.0;
           speciation_generation_max = 0.0;
       }
   
       bool calcSpeciation(const long double & random_number,
                           const long double & speciation_rate,
                           const unsigned long & no_generations) override;
   
       void speciateLineage(const unsigned long &data_position) override;
   
       bool getProtracted() override;
   
       void setProtractedVariables(double speciation_gen_min, double speciation_gen_max) override;
       
       string getProtractedVariables() override;
       
       double getProtractedGenerationMin() override;
       
       double getProtractedGenerationMax() override;
       
       string protractedVarsToString() override;
       
       void applySpecRate(double sr, double t);
   };
   
   #endif // PROTRACTED_SPATIAL_TREE_H
