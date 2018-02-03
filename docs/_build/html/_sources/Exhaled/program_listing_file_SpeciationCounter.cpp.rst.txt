
.. _program_listing_file_SpeciationCounter.cpp:

Program Listing for File SpeciationCounter.cpp
========================================================================================

- Return to documentation for :ref:`file_SpeciationCounter.cpp`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #include "ApplySpec.h"
   
   using namespace std;
   // INPUTS
   // requires a SQL database file containing the the Treenode objects from a coalescence simulations.
   // the required speciation rate.
   
   // OUTPUTS
   // An updated database file that contains the species richness and species abundances of the intended lineage.
   
   
   
   
   
   int main(int argc, char **argv)
   {
       ApplySpec app_s;
       app_s.applyFromComargs(argc, argv);
   }
