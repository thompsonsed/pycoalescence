
.. _program_listing_file_necsim_SpecSimParameters.h:

Program Listing for File SpecSimParameters.h
============================================

- Return to documentation for :ref:`file_necsim_SpecSimParameters.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
   #define SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
   
   
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
       double min_speciation_gen, max_speciation_gen;
       unsigned long metacommunity_size;
       double metacommunity_speciation_rate;
   
       void setup(string file_in, bool use_spatial_in, string sample_file, vector<double> times, string use_fragments_in,
                  vector<double> speciation_rates, double min_speciation_gen_in, double max_speciation_gen_in)
       {
           setup(file_in, use_spatial_in, sample_file, times, use_fragments_in, speciation_rates,
                 min_speciation_gen_in, max_speciation_gen_in, 0, 0.0);
       }
   
       void setup(string file_in, bool use_spatial_in, string sample_file, vector<double> times, string use_fragments_in,
                  vector<double> speciation_rates, double min_speciation_gen_in, double max_speciation_gen_in,
                  unsigned long metacommunity_size_in, double metacommunity_speciation_rate_in)
       {
           filename = std::move(file_in);
           use_spatial = use_spatial_in;
           samplemask = std::move(sample_file);
           if(times.size() == 0)
           {
               times_file = "null";
               all_times.push_back(0.0);
           }
           else
           {
               times_file = "set";
               all_times = times;
           }
           min_speciation_gen = std::move(min_speciation_gen_in);
           max_speciation_gen = std::move(max_speciation_gen_in);
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
               for(unsigned int i = 0; i < tmpimport.size(); i++)
               {
                   all_times.push_back(stod(tmpimport[i]));
                   //                  os << "t_i: " << sp.reference_times[i] << endl;
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
           min_speciation_gen = 0.0;
           max_speciation_gen = 0.0;
           metacommunity_size = 0;
           metacommunity_speciation_rate = 0.0;
       }
   };
   
   
   #endif //SPECIATIONCOUNTER_SPECSIMPARAMETERS_H
