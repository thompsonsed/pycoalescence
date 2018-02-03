
.. _program_listing_file_ProtractedTree.h:

Program Listing for File ProtractedTree.h
========================================================================================

- Return to documentation for :ref:`file_ProtractedTree.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   //
   #include <vector>
   #include <string>
   
   #include "Tree.h"
   
   #ifndef ProctractedTree
   #define ProctractedTree
   
   class ProtractedTree : public Tree
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
       
       ProtractedTree()
       {
           Tree();
           bIsProtracted = true;
       }
       
       ~ProtractedTree()
       {
           
       }
       
       bool calcSpeciation(const long double & random_number, const long double & speciation_rate, const int & no_generations);
       
       void setProtractedVariables(double speciation_gen_min, double speciation_gen_max);
       
       string getProtractedVariables();
       
       virtual double getProtractedGenerationMin();
       
       virtual double getProtractedGenerationMax();
       
       string protractedVarsToString();
       
       void applySpecRate(double sr, double t);
   };
   
   int runMainProtracted(int argc, vector<string> argv);
   
   #endif // ProctractedTree
