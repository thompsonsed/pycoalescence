
.. _program_listing_file_necsim_parameters.h:

Program Listing for File parameters.h
=====================================

- Return to documentation for :ref:`file_necsim_parameters.h`

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef NECSIM_PARAMETERS_H
   #define NECSIM_PARAMETERS_H
   
   #include <cstring>
   #include <stdexcept>
   #include <string>
   #include <memory>
   #include <vector>
   #include "double_comparison.h"
   
   using namespace std;
   
   struct ProtractedSpeciationParameters
   {
       double min_speciation_gen;
       double max_speciation_gen;
   
       ProtractedSpeciationParameters() : min_speciation_gen(0), max_speciation_gen(0){};
   
       bool operator==(const ProtractedSpeciationParameters &p1) const
       {
           return (doubleCompare(p1.min_speciation_gen, min_speciation_gen, 0.00000001) &&
                   doubleCompare(p1.max_speciation_gen, max_speciation_gen, 0.00000001));
       }
   
   };
   
   struct CommunityParameters
   {
       unsigned long reference;
       long double speciation_rate;
       long double time;
       bool fragment;
       unsigned long metacommunity_reference; // will be 0 if no metacommunity used.
       // protracted speciation current_metacommunity_parameters
       ProtractedSpeciationParameters protracted_parameters;
       bool updated; // set to true if the fragment reference needs updating in the database
   
       CommunityParameters() : reference(0), speciation_rate(0.0), time(0), fragment(false), metacommunity_reference(0),
                               protracted_parameters(), updated(false){}
   
       CommunityParameters(unsigned long reference_in, long double speciation_rate_in, long double time_in,
                           bool fragment_in, unsigned long metacommunity_reference_in,
                           const ProtractedSpeciationParameters &protracted_params);
   
       void setup(unsigned long reference_in, long double speciation_rate_in, long double time_in, bool fragment_in,
                  unsigned long metacommunity_reference_in, const ProtractedSpeciationParameters &protracted_params);
   
       bool compare(long double speciation_rate_in, long double time_in, bool fragment_in,
                    unsigned long metacommunity_reference_in,
                    const ProtractedSpeciationParameters &protracted_params);
   
       bool compare(long double speciation_rate_in, long double time_in,
                    unsigned long metacommunity_reference_in,
                    const ProtractedSpeciationParameters &protracted_params);
   
       bool compare(unsigned long reference_in);
   };
   
   struct CommunitiesArray
   {
       vector<shared_ptr<CommunityParameters>> comm_parameters;
   
       CommunitiesArray();
   
       void pushBack(unsigned long reference, long double speciation_rate, long double time, bool fragment,
                     unsigned long metacommunity_reference,
                     const ProtractedSpeciationParameters &protracted_params);
   
       void pushBack(shared_ptr<CommunityParameters> tmp_param);
   
       shared_ptr<CommunityParameters> addNew(long double speciation_rate, long double time, bool fragment,
                                              unsigned long metacommunity_reference,
                                              const ProtractedSpeciationParameters &protracted_params);
   
       bool hasPair(long double speciation_rate, double time, bool fragment,
                    unsigned long metacommunity_reference,
                    const ProtractedSpeciationParameters &protracted_params);
   
   };
   
   struct MetacommunityParameters
   {
       unsigned long reference{};
       unsigned long metacommunity_size{};
       long double speciation_rate{};
       string option;
       unsigned long external_reference{};
   
       MetacommunityParameters();
   
       MetacommunityParameters(const unsigned long &reference_in, const unsigned long &metacommunity_size_in,
                               const long double &speciation_rate_in, const string &option_in,
                               const unsigned long &external_reference_in);
   
       bool compare(unsigned long metacommunity_size_in, long double speciation_rate_in, const string &option_in,
                    const unsigned long &ext_reference_in);
   
       bool compare(const MetacommunityParameters &metacomm_in);
   
       bool compare(unsigned long reference_in);
   
       bool isMetacommunityOption() const;
   
       void clear();
   
       MetacommunityParameters &operator=(const MetacommunityParameters &parameters);
   };
   
   struct MetacommunitiesArray
   {
       vector<shared_ptr<MetacommunityParameters>> metacomm_parameters;
   
       MetacommunitiesArray();
   
       vector<shared_ptr<MetacommunityParameters>>::iterator begin();
   
       vector<shared_ptr<MetacommunityParameters>>::iterator end();
   
       vector<shared_ptr<MetacommunityParameters>>::const_iterator begin() const;
   
       vector<shared_ptr<MetacommunityParameters>>::const_iterator end() const;
   
       void pushBack(const unsigned long &reference, const unsigned long &metacommunity_size,
                     const long double &speciation_rate, const string &option,
                     const unsigned long &external_reference);
   
       void pushBack(shared_ptr<MetacommunityParameters> tmp_param);
   
       void clear();
   
       unsigned long size();
   
       bool empty();
   
       unsigned long addNew(const unsigned long &metacommunity_size, const long double &speciation_rate,
                            const string &option, const unsigned long &external_reference);
   
       unsigned long addNew(const MetacommunityParameters &metacomm_in);
   
       bool hasOption(const unsigned long &metacommunity_size, const long double &speciation_rate,
                      const string &option, const unsigned long &external_reference);
   
       bool hasOption(unsigned long reference);
   
       bool hasOption(const MetacommunityParameters &metacomm_in);
   
       unsigned long getReference(const unsigned long &metacommunity_size, const long double &speciation_rate,
                                  const string &option, const unsigned long &external_reference);
   
       unsigned long getReference(const MetacommunityParameters &metacomm_parameters);
   
       void addNull();
   };
   
   #endif //NECSIM_PARAMETERS_H
