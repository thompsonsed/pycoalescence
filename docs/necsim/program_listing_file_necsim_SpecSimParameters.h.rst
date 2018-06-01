
.. _program_listing_file_necsim_SpecSimParameters.h:

Program Listing for File SpecSimParameters.h
============================================

- Return to documentation for :ref:`file_necsim_SpecSimParameters.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #include <string>
   #include <vector>
   #include "ConfigFileParser.h"
   #include "CustomExceptions.h"
   #include "DoubleComparison.h"
   
   #ifndef SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
   #define SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
   using namespace std;
   
   struct ProtractedSpeciationParameters
   {
       double min_speciation_gen;
       double max_speciation_gen;
       ProtractedSpeciationParameters() : min_speciation_gen(0), max_speciation_gen(0){};
   
       bool operator== (const ProtractedSpeciationParameters &p1) const {
           return (doubleCompare(p1.min_speciation_gen, min_speciation_gen, 0.00000001) &&
                   doubleCompare(p1.max_speciation_gen, max_speciation_gen, 0.00000001));
       }
   
   };
   
   struct SpecSimParameters
   {
       bool use_spatial;
       bool bMultiRun;
       bool use_fragments;
       string filename;
       vector<double> all_speciation_rates;
       string samplemask;
       string times_file;
       vector<double> all_times;
       string fragment_config_file;
       vector<ProtractedSpeciationParameters> protracted_parameters;
       unsigned long metacommunity_size;
       double metacommunity_speciation_rate;
   
       void setup(string file_in, bool use_spatial_in, string sample_file, vector<double> times, string use_fragments_in,
                  vector<double> speciation_rates, vector<double> min_speciation_gen_in,
                  vector<double> max_speciation_gen_in)
       {
           setup(file_in, use_spatial_in, sample_file, times, use_fragments_in, speciation_rates,
                 min_speciation_gen_in, max_speciation_gen_in, 0, 0.0);
       }
   
       void setup(string file_in, bool use_spatial_in, string sample_file, const vector<double> &times,
                  string use_fragments_in, vector<double> speciation_rates, vector<double> min_speciation_gen_in,
                  vector<double> max_speciation_gen_in,
                  unsigned long metacommunity_size_in, double metacommunity_speciation_rate_in)
       {
           filename = std::move(file_in);
           use_spatial = use_spatial_in;
           samplemask = std::move(sample_file);
           if(times.empty() && all_times.empty())
           {
                   times_file = "null";
                   all_times.push_back(0.0);
           }
           else
           {
               times_file = "set";
               for(const auto item : times)
               {
                   all_times.emplace_back(item);
               }
           }
           if(min_speciation_gen_in.size() != max_speciation_gen_in.size())
           {
               throw FatalException("Protracted parameter mismatch between minimum and maximum generations (must be equal length).");
           }
           for(unsigned long i = 0; i < min_speciation_gen_in.size(); i++)
           {
               ProtractedSpeciationParameters tmp{};
               tmp.min_speciation_gen = min_speciation_gen_in[i];
               tmp.max_speciation_gen = max_speciation_gen_in[i];
               protracted_parameters.emplace_back(tmp);
           }
           use_fragments = !(use_fragments_in == "F");
           fragment_config_file = use_fragments_in;
           bMultiRun = speciation_rates.size() > 1;
           for(auto speciation_rate : speciation_rates)
           {
               all_speciation_rates.push_back(speciation_rate);
           }
           metacommunity_size = metacommunity_size_in;
           metacommunity_speciation_rate = metacommunity_speciation_rate_in;
       }
   
       void importTimeConfig()
       {
           if(times_file == "null")
           {
               all_times.push_back(0.0);
           }
           else
           {
               vector<string> tmpimport;
               ConfigOption tmpconfig;
               tmpconfig.setConfig(times_file, false);
               tmpconfig.importConfig(tmpimport);
               for(const auto &i : tmpimport)
               {
                   all_times.push_back(stod(i));
               }
           }
       }
   
       void wipe()
       {
           use_spatial = false;
           bMultiRun = false;
           use_fragments = false;
           filename = "";
           all_speciation_rates.clear();
           samplemask = "";
           times_file = "";
           all_times.clear();
           fragment_config_file = "";
           protracted_parameters.clear();
           metacommunity_size = 0;
           metacommunity_speciation_rate = 0.0;
       }
   
       void addTime(double time)
       {
           all_times.emplace_back(time);
       }
   
       void addProtractedParameters(double proc_spec_min, double proc_spec_max)
       {
           ProtractedSpeciationParameters tmp;
           tmp.min_speciation_gen = proc_spec_min;
           tmp.max_speciation_gen = proc_spec_max;
           protracted_parameters.emplace_back(tmp);
       }
   };
   
   
   #endif //SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
