
.. _program_listing_file_ApplySpec.cpp:

Program Listing for File ApplySpec.cpp
========================================================================================

- Return to documentation for :ref:`file_ApplySpec.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #include "ApplySpec.h"
   
   void ApplySpec::setArgs(string database, bool is_spatial, string sample_file, string time_config, string is_fragments,
                            vector<double> speciation_rates)
   {
       sp.filename = database;
       sp.RecordSpatial = is_spatial;
       sp.samplemask = sample_file;
       sp.autocorrel_file = time_config;
       importTimeConfig();
       if(is_fragments == "F")
       {
           sp.RecordFragments = false;
       }
       else
       {
           sp.RecordFragments = true;
       }
       sp.fragment_config_file = is_fragments;
       if(speciation_rates.size() > 1)
       {
           sp.bMultiRun = true;
       }
       else
       {
           sp.bMultiRun = false;
       }
       for(unsigned long i = 0; i < speciation_rates.size(); i ++ )
       {
           sp.vSpecRates.push_back(speciation_rates[i]);
       }
       iMultiNumber = speciation_rates.size();
   }
   
   void ApplySpec::parseArgs()
   {
       bool bRunDefault = false;
       bool bInvalidArguments = false;
       bool bAskHelp = false;
   #ifndef verbose
       dup2(saved_stdout, fileno(stdout));
   // close(saved_stdout);
   #endif
       if(argc < 7)
       {
           if(argc == 1)
           {
               bInvalidArguments = true;
           }
           bInvalidArguments = true;
           if(argc == 2)
           {
               if((comargs[1]) == "-d")
               {
                   bInvalidArguments = false;
                   bRunDefault = true;
               }
               if(comargs[1] == "-h" || comargs[1] == "-help")
               {
                   bInvalidArguments = false;
                   bAskHelp = true;
               }
           }
           if(bInvalidArguments)
           {
               write_cout("Incorrect number of arguments.");
               bInvalidArguments = true;
               if(argc == 1)
               {
                   comargs.push_back("-e");
               }
               else
               {
                   comargs[1] = "-e";
               }
           }
       }
       else
       {
           sp.samplemask = comargs[3];
           sp.filename = comargs[1];
           sp.autocorrel_file = comargs[4];
       }
       if(argc > 7)
       {
           sp.bMultiRun = true;
           int i = 6;
           while(i < argc)
           {
               sp.vSpecRates.push_back(stof(comargs[i]));
               i++;
           }
       }
       else if(argc == 7 && !bInvalidArguments && !bAskHelp)
       {
           sp.bMultiRun = false;
           sp.vSpecRates.push_back(stod(comargs[6]));
       }
       if(!bInvalidArguments && !bAskHelp && !bRunDefault)
       {
           if(comargs[2] == "true" || comargs[2] == "True" || comargs[2] == "T" || comargs[2] == "TRUE" ||
              comargs[2] == "t")
           {
               sp.RecordSpatial = true;
           }
           else
           {
               sp.RecordSpatial = false;
           }
           if(comargs[5] == "false" || comargs[5] == "False" || comargs[5] == "F" || comargs[5] == "FALSE" ||
              comargs[5] == "f")
           {
               sp.RecordFragments = false;
           }
           else
           {
               if(comargs[5] == "true" || comargs[5] == "True" || comargs[5] == "T" || comargs[5] == "TRUE" ||
                  comargs[5] == "t")
               {
                   sp.fragment_config_file = "null";
               }
               else
               {
                   sp.fragment_config_file = comargs[5];
               }
               sp.RecordFragments = true;
           }
       }
       if(bInvalidArguments || bAskHelp)
       {
           stringstream os;
           os << "At least six command-line arguments are expected." << endl;
           os << "1 - Path to SQL database file." << endl;
           os << "2 - T/F of whether to record full spatial data." << endl;
           os << "3 - the sample mask to use (use null if no mask is to be used)" << endl;
           os << "4 - the file containing tempororal points of interest. If null, the present is used for all "
                 "calculations."
              << endl;
           os << "5 - T/F of whether to calculate abundances for each rectangular fragment. Alternatively, provide a "
                 "csv file with fragment data to be read."
              << endl;
           os << "6 - Speciation rate." << endl;
           os << "7 - onwards - Further speciation rates. [OPTIONAL]" << endl;
           os << "Would you like to run with the default paramenters?" << endl;
           os << "       (This requires a SQL database file at ../../Data/Coal_sim/Test_output/SQL_data/data_0_1.db)"
              << endl;
           os << "Enter Y/N: " << flush;
           write_cout(os.str());
           string sDef;
           cin >> sDef;
           if(sDef == "Y" || sDef == "y")
           {
               bRunDefault = true;
           }
           else
           {
               bRunDefault = false;
               exit(0);
           }
       }
       if(comargs[1] == "-d" || bRunDefault)
       {
           sp.filename = "../../Data/Coal_sim/Test_output/SQL_data/data_0_1.db";
           sp.vSpecRates.push_back(0.001);
           sp.samplemask = "null";
           sp.autocorrel_file = "null";
           sp.fragment_config_file = "null";
           sp.RecordFragments = false;
           sp.RecordSpatial = true;
       }
       try
       {
           importTimeConfig();
       }
       catch(Config_Exception& ce)
       {
           cerr << ce.what() << endl;
           throw Config_Exception("Could not import from " + sp.autocorrel_file);
       }
   #ifndef verbose
       openLogFile(true);
   #endif
   }
   
   void ApplySpec::writeSpeciationRates()
   {
       stringstream os;
       os << "***************************" << endl;
       os << "STARTING CALCULATIONS" << endl;
       os << "Input file is " << sp.filename << endl;
       if(!sp.bMultiRun)
       {
           os << "Speciation rate is " << sp.vSpecRates[0] << endl;
       }
       else
       {
           os << "Speciation rates are: " << flush;
           for(unsigned int i = 0; i < iMultiNumber; i++)
           {
               os << sp.vSpecRates[i] << flush;
               if(i + 1 == iMultiNumber)
               {
                   os << "." << endl;
               }
               else
               {
                   os << ", " << flush;
               }
           }
       }
       write_cout(os.str());
   }
   
   void ApplySpec::importTimeConfig()
   {
       if(sp.autocorrel_file == "null")
       {
           sp.bAuto = false;
       }
       else
       {
           sp.bAuto = true;
           vector<string> tmpimport;
           ConfigOption tmpconfig;
           tmpconfig.setConfig(sp.autocorrel_file, false);
           tmpconfig.importConfig(tmpimport);
           for(unsigned int i = 0; i < tmpimport.size(); i++)
           {
               sp.autocorrel_times.push_back(stod(tmpimport[i]));
               //                  os << "t_i: " << sp.autocorrel_times[i] << endl;
           }
       }
   }
   
   void ApplySpec::importData()
   {
       try
       {
           //      nodes.detectDimensions(sp.filename);
           // First import the parameters so that the samplemask file will be the correct size.
           nodes.importSimParameters(sp.filename);
           nodes.importSamplemask(sp.samplemask);
           nodes.importData(sp.filename);
           if(sp.RecordFragments)
           {
               nodes.calcFragments(sp.fragment_config_file);
           }
       }
       catch(exception& se)
       {
           string msg = "Could not import data: ";
           msg += se.what();
           throw Fatal_Exception(msg);
       }
   }
   
   bool ApplySpec::checkUniqueSpec(unsigned int i)
   {
       for(unsigned int j = 0; j < dUniqueSpec.size(); j++)
       {
           if(dUniqueSpec[j] == sp.vSpecRates[i])
           {
               return false;
           }
       }
       return true;
   }
   
   void ApplySpec::applyMultiTimes(int i)
   {
       dUniqueSpec.push_back(sp.vSpecRates[i]);
       stringstream os;
       for(unsigned int k = 0; k < sp.autocorrel_times.size(); k++)
       {
           os.str("");
           os << "Calculating generation " << sp.autocorrel_times[k] << "\n";
           write_cout(os.str());
           nodes.setGeneration(sp.autocorrel_times[k]);
           nodes.resetTree();
           try
           {
               if(nodes.checkRepeatSpeciation(sp.vSpecRates[i], sp.autocorrel_times[k]))
               {
                   nodes.createDatabase(sp.vSpecRates[i]);
                   if(sp.RecordSpatial)
                   {
                       nodes.recordSpatial();
                   }
               }
               if(nodes.checkRepeatSpeciation(sp.vSpecRates[i], sp.autocorrel_times[k], true))
               {
                   if(sp.RecordFragments)
                   {
                       nodes.applyFragments();
                   }
               }
           }
           catch(SpeciesException& se)
           {
               cerr << se.what() << endl;
           }
       }
   }
   
   void ApplySpec::applySingleTime(int i)
   {
       dUniqueSpec.push_back(sp.vSpecRates[i]);
       nodes.resetTree();
       try
       {
           if(nodes.checkRepeatSpeciation(sp.vSpecRates[i]))
           {
               nodes.createDatabase(sp.vSpecRates[i]);
               if(sp.RecordSpatial)
               {
                   nodes.recordSpatial();
               }
           }
           if(nodes.checkRepeatSpeciation(sp.vSpecRates[i], 0.0, false))
           {
               if(sp.RecordFragments)
               {
                   nodes.applyFragments();
               }
           }
       }
       catch(SpeciesException& se)
       {
           cerr << se.what() << endl;
       }
   }
   
   void ApplySpec::calculateTree()
   {
       nodes.resetTree();
       nodes.setGeneration(0);
       // Calculate the new tree structure.
       if(sp.bMultiRun)
       {
           for(unsigned int i = 0; i < iMultiNumber; i++)
           {
               if(checkUniqueSpec(i))
               {
                   if(sp.bAuto)
                   {
                       applyMultiTimes(i);
                   }
                   else
                   {
                       applySingleTime(i);
                   }
               }
               else
               {
                   write_cout("Repeat speciation rate... ignoring");
               }
           }
       }
       else
       {
           if(sp.bAuto)
           {
               applyMultiTimes(0);
           }
           else
           {
               applySingleTime(0);
           }
       }
       nodes.exportDatabase(sp.filename);
   }
   
   int ApplySpec::applyFromComargs(int argc_in, char** argv)
   {
       argc = argc_in;
       iMultiNumber = argc - 6;
   #ifndef verbose
       openLogFile(false);
   #endif
       importArgs(argc, argv, comargs);
       parseArgs();
       apply();
       return 0;
   }
   
   void ApplySpec::apply()
   {
       // Start the clock
       time(&tStart);
       // First print the variables
       writeSpeciationRates();
   
       // Set up the objects
       
       nodes.setList(&data);
       //  unsigned long iCount;
       // Import the data from the file into the Row<Treenode> object.
       importData();
       // Get rid of any previous speciation calculations
       calculateTree();
       //  os << "speciation rate of 0.0001: " << list.calcSpecies(0.0001);
       //  list.resetTree();
       //  os << "speciation rate of 0.001: " << list.calcSpecies(0.001);
       //  list.resetTree();
       //  os << "speciation rate of 0.01: " << list.calcSpecies(0.01);
       time(&tEnd);
       stringstream os;
       os << "Calculations complete." << endl;
       os << "Time taken was " << floor((tEnd - tStart) / 3600) << " hours "
          << (floor((tEnd - tStart) / 60) - 60 * floor((tEnd - tStart) / 3600)) << " minutes " << (tEnd - tStart) % 60
          << " seconds" << endl;
       write_cout(os.str());
   }
   
