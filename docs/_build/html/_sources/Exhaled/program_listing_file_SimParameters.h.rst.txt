
.. _program_listing_file_SimParameters.h:

Program Listing for File SimParameters.h
========================================================================================

- Return to documentation for :ref:`file_SimParameters.h`

.. code-block:: cpp

   //
   // Created by Sam Thompson on 10/09/2017.
   //
   
   #ifndef SPECIATIONCOUNTER_SIMPARAMETERS_H
   #define SPECIATIONCOUNTER_SIMPARAMETERS_H
   #include <string>
   #include <vector>
   #include "ConfigFileParser.h"
   
   
   /************************************************************
                       MAPVARS STRUCTURE
    ************************************************************/
   struct SimParameters
   {
       string finemapfile, coarsemapfile,outdirectory,pristinefinemapfile,pristinecoarsemapfile, samplemaskfile;
        // for file naming purposes.
       long the_task, the_seed;
       // the variables for the grid containing the initial individuals.
       unsigned long vargridxsize, vargridysize;
       // The variables for the sample grid, which may or may not be the same as the main simulation grid
       unsigned long varsamplexsize, varsampleysize;
       unsigned long varsamplexoffset, varsampleyoffset;
       // The fine map variables at the same resolution as the grid.
       unsigned long varfinemapxsize, varfinemapysize, varfinemapxoffset, varfinemapyoffset;
       // the coarse map variables at a scaled resolution of the fine map.
       unsigned long varcoarsemapxsize, varcoarsemapysize, varcoarsemapxoffset, varcoarsemapyoffset;
       unsigned long varcoarsemapscale;
       unsigned long desired_specnum;
       // the relative cost of moving through non-forest
       double dispersal_relative_cost;
       // the size of each square of habitat in numbers of individuals
       long deme;
       // the sample proportion,
        double deme_sample;
       // the speciation rate.
       long double  spec;
       // the variance of the dispersal kernel.
       double sigma;
       // max time to run for
       unsigned long maxtime;
       // the number of generations since a pristine landscape was encountered.
       double dPristine;
       // the transform rate of the forest from pristine to modern forest.
       double dForestChangeRate;
       // the fatness of the dispersal kernel
       double tau;
       // dispersal method - should be one of [normal, fat-tail, norm-uniform]
       string dispersal_method;
       // the probability of selecting from a uniform dispersal kernel (for uniformally-modified dispersals)
       double m_prob;
       // the cutoff for the normal dispersal in cells.
       double cutoff;
       // if true, restricts dispersal from the same cell.
       bool restrict_self;
       // file containing the points to record data from
       string autocorrel_file;
       // Stores the full list of configs imported from file
       ConfigOption configs;
       // Set to true if the completely pristine state has been reached.
       bool bPristine;
       // This can be closed, infinite and tiled (which is also infinite)
       string landscape_type;
       // The protracted speciation parameters - these DON'T need to be stored upon pausing simulations
       bool bProtracted;
       double min_speciation_gen, max_speciation_gen;
   
       // a map of dispersal values, where each row corresponds to the probability of moving from one cell
       // to any other.
       string dispersal_file;
   
       // a map of relative reproduction probabilities.
       string reproduction_file;
   
       void import(const vector<string> &comargs, bool fullmode, bool configmode)
       {
           finemapfile = "null";
           coarsemapfile = "null";
           pristinefinemapfile = "null";
           pristinecoarsemapfile = "null";
           dispersal_method = "normal";
           autocorrel_file = "null";
           m_prob = 0;
           cutoff = 0;
           tau =0;
           restrict_self = false;
           landscape_type = "closed";
           bProtracted = false;
           min_speciation_gen = 0.0;
           max_speciation_gen = 0.0;
           dispersal_file = "none";
           reproduction_file = "none";
           if(fullmode)
           {
               the_seed = stol(comargs[1]);
               vargridxsize = stoul(comargs[2]);
               vargridysize = stoul(comargs[3]);
               finemapfile = comargs[4];
               varfinemapxsize = stoul(comargs[5]);
               varfinemapysize = stoul(comargs[6]);
               varfinemapxoffset = stoul(comargs[7]);
               varfinemapyoffset = stoul(comargs[8]);
               coarsemapfile = comargs[9];
               varcoarsemapxsize = stoul(comargs[10]);
               varcoarsemapysize = stoul(comargs[11]);
               varcoarsemapxoffset = stoul(comargs[12]);
               varcoarsemapyoffset = stoul(comargs[13]);
               varcoarsemapscale = stoul(comargs[14]);
               outdirectory = comargs[15];
               dispersal_relative_cost = stod(comargs[21]);
               the_task = stol(comargs[22]);
               desired_specnum = stoul(comargs[23]);
               pristinefinemapfile = comargs[24];
               pristinecoarsemapfile = comargs[25];
               dForestChangeRate = stod(comargs[26]);
               dPristine = stod(comargs[27]);
               deme = stol(comargs[18]);
               deme_sample = stod(comargs[19]);
               spec = stold(comargs[16]);
               tau = stod(comargs[17]);
               maxtime = stoul(comargs[20]);
               sigma = stod(comargs[28]);
               samplemaskfile = comargs[29];
               autocorrel_file = comargs[30];
           }
           else
           {
               // do the import of the values from combination of command-line arguments and file.
               string conf_in;
               if(configmode)
               {
                   conf_in = comargs[1];
               }
               else
               {
                   conf_in = comargs[3];
               }
               configs.setConfig(conf_in, false, true);
               configs.parseConfig();
               varsamplexsize = stoul(configs.getSectionOptions("sample_grid", "x"));
               varsampleysize = stoul(configs.getSectionOptions("sample_grid", "y"));
               varsamplexoffset = stoul(configs.getSectionOptions("sample_grid", "x_off", "0"));
               varsampleyoffset = stoul(configs.getSectionOptions("sample_grid", "y_off", "0"));
               if(configs.hasSection("grid_map"))
               {
                   vargridxsize = stoul(configs.getSectionOptions("grid_map", "x"));
                   vargridysize = stoul(configs.getSectionOptions("grid_map", "y"));
               }
               else
               {
                   vargridxsize = varsamplexsize;
                   vargridysize = varsampleysize;
               }
               samplemaskfile = configs.getSectionOptions("sample_grid","mask", "null");
               finemapfile = configs.getSectionOptions("fine_map", "path");
               varfinemapxsize = stoul(configs.getSectionOptions("fine_map", "x"));
               varfinemapysize = stoul(configs.getSectionOptions("fine_map", "y"));
               varfinemapxoffset = stoul(configs.getSectionOptions("fine_map", "x_off"));
               varfinemapyoffset = stoul(configs.getSectionOptions("fine_map", "y_off"));
               coarsemapfile = configs.getSectionOptions("coarse_map", "path");
               varcoarsemapxsize = stoul(configs.getSectionOptions("coarse_map", "x"));
               varcoarsemapysize = stoul(configs.getSectionOptions("coarse_map", "y"));
               varcoarsemapxoffset = stoul(configs.getSectionOptions("coarse_map", "x_off"));
               varcoarsemapyoffset = stoul(configs.getSectionOptions("coarse_map", "y_off"));
               varcoarsemapscale = stoul(configs.getSectionOptions("coarse_map", "scale"));
               pristinefinemapfile = configs.getSectionOptions("pristine_fine0", "path");
               pristinecoarsemapfile = configs.getSectionOptions("pristine_coarse0", "path");
               dispersal_method = configs.getSectionOptions("dispersal", "method", "normal");
               m_prob = stod(configs.getSectionOptions("dispersal", "m_probability", "0"));
               cutoff = stod(configs.getSectionOptions("dispersal", "cutoff", "0.0"));
               // quick and dirty conversion for string to bool
               restrict_self = static_cast<bool>(stoi(configs.getSectionOptions("dispersal", "restrict_self", "0")));
               landscape_type = configs.getSectionOptions("dispersal", "infinite_landscape", "closed");
               dispersal_file = configs.getSectionOptions("dispersal", "dispersal_file", "none");
               reproduction_file = configs.getSectionOptions("reproduction", "map", "none");
               if(configmode)
               {
                   outdirectory = configs.getSectionOptions("main", "output_directory", "Default");
                   the_seed = stol(configs.getSectionOptions("main", "seed", "0"));
                   the_task = stol(configs.getSectionOptions("main", "job_type", "0"));
                   tau = stod(configs.getSectionOptions("main", "tau"));
                   sigma = stod(configs.getSectionOptions("main", "sigma"));
                   deme = stol(configs.getSectionOptions("main", "deme"));
                   deme_sample = stod(configs.getSectionOptions("main", "sample_size"));
                   maxtime = stoul(configs.getSectionOptions("main", "max_time"));
                   dispersal_relative_cost = stod(configs.getSectionOptions("main", "dispersal_relative_cost"));
                   autocorrel_file = configs.getSectionOptions("main", "time_config");
                   spec = stod(configs.getSectionOptions("main", "min_spec_rate"));
                   desired_specnum = stoul(configs.getSectionOptions("main", "min_species"));
                   if(configs.hasSection("protracted"))
                   {
                       bProtracted = static_cast<bool>(stoi(configs.getSectionOptions("protracted", "has_protracted", "0")));
                       min_speciation_gen = stod(configs.getSectionOptions("protracted", "min_speciation_gen", "0.0"));
                       max_speciation_gen = stod(configs.getSectionOptions("protracted", "max_speciation_gen"));
                   }
               }
               else
               {
                   outdirectory = comargs[4];
                   the_seed = stol(comargs[1]);
                   the_task = stol(comargs[2]);
                   tau = stod(comargs[6]);
                   sigma = stod(comargs[7]);
                   deme = stol(comargs[8]);
                   deme_sample = stod(comargs[9]);
                   maxtime = stoul(comargs[10]);
                   dispersal_relative_cost = stod(comargs[11]);
                   autocorrel_file = comargs[12];
                   spec = stod(comargs[5]);
                   desired_specnum = stoul(comargs[13]);
               }
               setPristine(0);
           }
       }
   
       bool setPristine(unsigned int n)
       {
           bPristine = true;
           bool finemapcheck = false;
           bool coarsemapcheck = false;
           // Loop over each element in the config file (each line) and check if it is pristine fine or pristine coarse.
           for(unsigned int i = 0; i < configs.getSectionOptionsSize(); i ++ )
           {
   
               if(configs[i].section.find("pristine_fine") == 0)
               {
                   // Then loop over each element to find the number, and check if it is equal to our input number.
                   bPristine = false;
                   if(stol(configs[i].getOption("number")) == n)
                   {
                       string tmpmapfile;
                       tmpmapfile = configs[i].getOption("path");
                       if(pristinefinemapfile != tmpmapfile)
                       {
                           finemapcheck = true;
                           pristinefinemapfile = tmpmapfile;
                       }
                       dForestChangeRate = stod(configs[i].getOption("rate"));
                       dPristine = stod(configs[i].getOption("time"));
                   }
               }
               else if(configs[i].section.find("pristine_coarse") == 0)
               {
                   if(stol(configs[i].getOption("number")) == n)
                   {
                       string tmpmapfile;
                       tmpmapfile = configs[i].getOption("path");
                       bPristine = false;
                       if(tmpmapfile != pristinecoarsemapfile)
                       {
                           coarsemapcheck=true;
                           pristinecoarsemapfile = tmpmapfile;
                           // check matches
                           if(dForestChangeRate != stod(configs[i].getOption("rate")) || dPristine != stod(configs[i].getOption("time")))
                           {
                               cerr << "Forest transform values do not match between fine and coarse maps. Using fine values." << endl;
                           }
                       }
                   }
               }
           }
           // if one of the maps has changed, we need to update, so return true.
           if(finemapcheck != coarsemapcheck)
           {
               return true;
           }
           else
           {
               // finemapcheck should therefore be the same as coarsemapcheck
               return finemapcheck;
           }
       }
       void printVars()
       {
           stringstream os;
           os << "Seed: " << the_seed << endl;
           os << "Speciation rate: " << spec << endl;
           os << "Dispersal (tau, sigma): " << tau << ", " << sigma << endl;
           os << "Dispersal method: " << dispersal_method << endl;
           if(dispersal_method == "norm-uniform")
           {
               os << "Dispersal (m, cutoff): " << m_prob << ", " << cutoff << endl;
           }
           os << "Job Type: " << the_task << endl;
           os << "Fine input file: " << finemapfile  << endl;
           os << "-dimensions: (" << varfinemapxsize << ", " << varfinemapysize <<")"<< endl;
           os << "-offset: (" << varfinemapxoffset << ", " << varfinemapyoffset << ")" << endl;
           os << "Coarse input file: " << coarsemapfile  << endl;
           os << "-dimensions: (" << varcoarsemapxsize << ", " << varcoarsemapysize <<")"<< endl;
           os << "-offset: (" << varcoarsemapxoffset << ", " << varcoarsemapyoffset << ")" << endl;
           os << "-scale: " << varcoarsemapscale << endl;
           os << "Sample grid" << endl;
           os << "-dimensions: (" << varsamplexsize << ", " << varsampleysize << ")" << endl;
           os << "-optimised area: (" << vargridxsize << ", " << vargridysize << ")" << endl;
           os << "-optimised offsets: (" << varsamplexoffset << ", " << varsampleyoffset << ")" << endl;
           os << "-deme: " << deme << endl;
           os << "-deme sample: " << deme_sample << endl;
   
           os << "Output directory: " << outdirectory << endl;
           os << "Disp Rel Cost: " << dispersal_relative_cost << endl;
           write_cout(os.str());
   
       }
   
       friend ostream& operator<<(ostream& os,const SimParameters& m)
       {
           os << m.finemapfile << "\n" << m.coarsemapfile << "\n" << m.pristinefinemapfile << "\n";
           os << m.pristinecoarsemapfile << "\n" << m.samplemaskfile << "\n";
           os << m.the_task << "\n" <<  m.vargridxsize << "\n" << m.vargridysize << "\n";
           os << m.varsamplexsize << "\n" << m.varsampleysize << "\n" << m.varsamplexoffset << "\n" << m.varsampleyoffset << "\n";
           os << m.varfinemapxsize << "\n" << m.varfinemapysize << "\n";
           os << m.varfinemapxoffset << "\n" << m.varfinemapyoffset << "\n" << m.varcoarsemapxsize << "\n" << m.varcoarsemapysize << "\n" << m.varcoarsemapxoffset << "\n";
           os << m.varcoarsemapyoffset << "\n" << m.varcoarsemapscale << "\n" << m.desired_specnum << "\n";
           os << m.dispersal_relative_cost << "\n" << m.deme << "\n" << m.deme_sample<< "\n";
           os << m.spec << "\n" << m.sigma << "\n" << m.maxtime << "\n" << m.dPristine << "\n" << m. dForestChangeRate << "\n" << m.tau;
           os << "\n" << m.dispersal_method << "\n";
           os << m.m_prob << "\n" << m.cutoff << "\n" << m.restrict_self <<"\n" << m.landscape_type << "\n" << m.autocorrel_file << "\n";
           os << m.dispersal_file << "\n";
           os << m.configs;
           return os;
       }
   
       friend istream& operator>>(istream& is, SimParameters& m)
       {
           getline(is, m.finemapfile);
           getline(is, m.coarsemapfile);
           getline(is, m.pristinefinemapfile);
           getline(is, m.pristinecoarsemapfile);
           getline(is, m.samplemaskfile);
           is >> m.the_task >>  m.vargridxsize >> m.vargridysize;
           is >> m.varsamplexsize >> m.varsampleysize >> m.varsamplexoffset >> m.varsampleyoffset;
           is >> m.varfinemapxsize >> m.varfinemapysize;
           is >> m.varfinemapxoffset >> m.varfinemapyoffset >> m.varcoarsemapxsize >> m.varcoarsemapysize >> m.varcoarsemapxoffset ;
           is >> m.varcoarsemapyoffset >> m.varcoarsemapscale >> m.desired_specnum >> m.dispersal_relative_cost >> m.deme >> m.deme_sample;
           is >> m.spec >> m.sigma >> m.maxtime >> m.dPristine >> m.dForestChangeRate >> m.tau;
           is.ignore();
           getline(is, m.dispersal_method);
           is >> m.m_prob >> m.cutoff >> m.restrict_self >> m.landscape_type;
           is.ignore();
           getline(is, m.autocorrel_file);
           getline(is, m.dispersal_file);
           is >> m.configs;
           return is;
       }
   };
   
   
   #endif //SPECIATIONCOUNTER_SIMPARAMETERS_H
