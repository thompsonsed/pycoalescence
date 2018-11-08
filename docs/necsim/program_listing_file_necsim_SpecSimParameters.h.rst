
.. _program_listing_file_necsim_SpecSimParameters.h:

Program Listing for File SpecSimParameters.h
============================================

- Return to documentation for :ref:`file_necsim_SpecSimParameters.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
   #define SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
   
   #include <string>
   #include <utility>
   #include <vector>
   #include "ConfigParser.h"
   #include "custom_exceptions.h"
   #include "double_comparison.h"
   #include "parameters.h"
   
   using namespace std;
   
   struct SpecSimParameters
   {
       bool use_spatial;
       bool bMultiRun;
       bool use_fragments;
       string filename;
       set<double> all_speciation_rates;
       string samplemask;
       string times_file;
       set<double> all_times;
       string fragment_config_file;
       vector<ProtractedSpeciationParameters> protracted_parameters;
       MetacommunitiesArray metacommunity_parameters;
   
       SpecSimParameters() : use_spatial(false), bMultiRun(false), use_fragments(false), filename("none"),
                             all_speciation_rates(), samplemask("none"), times_file("null"), all_times(),
                             fragment_config_file("none"), protracted_parameters(), metacommunity_parameters()
       {
   
       }
   
       SpecSimParameters(const string &fragment_config_file) : fragment_config_file(fragment_config_file){}
   
       void setup(string file_in, bool use_spatial_in, string sample_file, const vector<double> &times,
                  const string &use_fragments_in, vector<double> speciation_rates)
       {
           filename = std::move(file_in);
           use_spatial = use_spatial_in;
           samplemask = std::move(sample_file);
           if(times.empty() && all_times.empty())
           {
               times_file = "null";
               all_times.insert(0.0);
           }
           else
           {
               times_file = "set";
               for(const auto item : times)
               {
                   all_times.insert(item);
               }
           }
           use_fragments = !(use_fragments_in == "F");
           fragment_config_file = use_fragments_in;
           bMultiRun = speciation_rates.size() > 1;
           for(auto speciation_rate : speciation_rates)
           {
               all_speciation_rates.insert(speciation_rate);
           }
       }
   
       void addMetacommunityParameters(const unsigned long &metacommunity_size_in,
                                       const double &metacommunity_speciation_rate_in,
                                       const string &metacommunity_option_in,
                                       const unsigned long &metacommunity_reference_in)
       {
           MetacommunityParameters tmp_meta_parameters = MetacommunityParameters(0, metacommunity_size_in,
                                                                                 metacommunity_speciation_rate_in,
                                                                                 metacommunity_option_in,
                                                                                 metacommunity_reference_in);
           if(!metacommunity_parameters.hasOption(tmp_meta_parameters))
           {
               metacommunity_parameters.addNew(tmp_meta_parameters);
           }
           else
           {
               stringstream ss;
               ss << "Parameters already added for metacommunity with size " << metacommunity_size_in << ", ";
               ss << "speciation rate " << metacommunity_speciation_rate_in << ", " << "using option ";
               ss << metacommunity_option_in << " and reference " << metacommunity_reference_in << endl;
               writeInfo(ss.str());
           }
       }
   
       void importTimeConfig()
       {
           if(times_file == "null")
           {
               all_times.insert(0.0);
           }
           else
           {
               vector<string> tmpimport;
               ConfigParser tmpconfig;
               tmpconfig.setConfig(times_file, false);
               tmpconfig.importConfig(tmpimport);
               for(const auto &i : tmpimport)
               {
                   all_times.insert(stod(i));
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
           metacommunity_parameters.clear();
       }
   
       void addTime(double time)
       {
           all_times.insert(time);
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
