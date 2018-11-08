
.. _program_listing_file_necsim_SpeciesAbundancesHandler.h:

Program Listing for File SpeciesAbundancesHandler.h
===================================================

- Return to documentation for :ref:`file_necsim_SpeciesAbundancesHandler.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef SPECIES_ABUNDANCES_H
   #define SPECIES_ABUNDANCES_H
   
   #include <vector>
   #include <map>
   #include <memory>
   #include "NRrand.h"
   
   using namespace std;
   
   class SpeciesAbundancesHandler
   {
   protected:
   
       shared_ptr<NRrand> random;
       unsigned long max_species_id;
       unsigned long community_size;
       long double speciation_rate;
   public:
   
       SpeciesAbundancesHandler();
   
       virtual ~SpeciesAbundancesHandler() = default;
   
       virtual void setup(shared_ptr<NRrand> random, const unsigned long &community_size,
                          const long double &speciation_rate);
   
       virtual unsigned long getRandomSpeciesID() = 0;
   
       virtual void setAbundanceList(const shared_ptr<map<unsigned long, unsigned long>> &abundance_list_in);
   
       virtual void setAbundanceList(shared_ptr<vector<unsigned long>> abundance_list_in);
   
       virtual unsigned long getRandomAbundanceOfIndividual();
   
       virtual unsigned long getSpeciesRichnessOfAbundance(const unsigned long &abundance)
       {
           return 0;
       }
   
   };
   
   #endif //SPECIES_ABUNDANCES_H
