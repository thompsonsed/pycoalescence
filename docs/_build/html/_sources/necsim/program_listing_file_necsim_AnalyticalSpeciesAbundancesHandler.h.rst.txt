
.. _program_listing_file_necsim_AnalyticalSpeciesAbundancesHandler.h:

Program Listing for File AnalyticalSpeciesAbundancesHandler.h
=============================================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_AnalyticalSpeciesAbundancesHandler.h>` (``necsim/AnalyticalSpeciesAbundancesHandler.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef ANALYICAL_SPECIES_ABUNDANCES_H
   #define ANALYICAL_SPECIES_ABUNDANCES_H
   
   #include "SpeciesAbundancesHandler.h"
   #include "neutral_analytical.h"
   #include "NRrand.h"
   
   namespace na = neutral_analytical;
   using namespace std;
   
   class AnalyticalSpeciesAbundancesHandler : public virtual SpeciesAbundancesHandler
   {
   protected:
       unsigned long seen_no_individuals;
       // Store all previous species ids in a map of cumulative numbers of individuals for searching for ids
       map<unsigned long, unsigned long> ind_to_species;
   public:
   
       AnalyticalSpeciesAbundancesHandler();
   
       ~AnalyticalSpeciesAbundancesHandler() override = default;
   
       void setup(shared_ptr<NRrand> random, const unsigned long &community_size,
                  const long double &speciation_rate) override;
   
       void generateSpeciesAbundances();
   
       unsigned long getRandomSpeciesID() override;
   
       unsigned long pickPreviousIndividual(const unsigned long &individual_id);
   
       void addNewSpecies();
   
       unsigned long getRandomAbundanceOfSpecies();
   
   };
   
   #endif //ANALYICAL_SPECIES_ABUNDANCES_H
