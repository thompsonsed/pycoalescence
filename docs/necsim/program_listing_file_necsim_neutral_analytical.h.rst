
.. _program_listing_file_necsim_neutral_analytical.h:

Program Listing for File neutral_analytical.h
=============================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_neutral_analytical.h>` (``necsim/neutral_analytical.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef NECSIM_NEUTRAL_ANALYTICAL_H
   #define NECSIM_NEUTRAL_ANALYTICAL_H
   
   #include <cmath>
   #include <vector>
   #include <map>
   
   namespace neutral_analytical
   {
       long double nseMetacommunitySpeciesWithAbundance(const unsigned long &n, const unsigned long &community_size,
                                                        const long double &speciation_rate);
   
       long double getFundamentalBiodiversityNumber(const unsigned long &community_size,
                                                    const long double &speciation_rate);
   
       long double nseSpeciesRichnessDeprecated(const unsigned long &community_size, const long double &speciation_rate);
   
       long double nseSpeciesRichness(const unsigned long &community_size, const long double &speciation_rate);
   
       std::map<unsigned long, long double> nseSpeciesAbundanceCumulativeDistribution(const unsigned long &community_size,
                                                                                      const long double &speciation_rate);
   
   }
   #endif //NECSIM_NEUTRAL_ANALYTICAL_H
