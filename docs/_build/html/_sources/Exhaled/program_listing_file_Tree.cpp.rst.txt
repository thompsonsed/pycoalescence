
.. _program_listing_file_Tree.cpp:

Program Listing for File Tree.cpp
========================================================================================

- Return to documentation for :ref:`file_Tree.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   //#include <gperftools/profiler.h>
   #include "Tree.h"
   
   void Tree::importSimulationVariables(vector<string> & comargs)
   {
   
       // First parse the command line arguments
       parseArgs(comargs);
       if(bResume && !bConfig)
       {
           setResumeParameters(comargs[1], comargs[1], stol(comargs[2]), stol(comargs[3]), stol(comargs[4]));
       }
       // Import the simulation variables into our SimParameters object.
       else
       {
           sim_parameters.import(comargs, bFullmode, bConfig);
       }
   
       // Now check that our folders exist
       checkFolders();
       // Now check for paused simulations
       checkSims();
   }
   
   
   void Tree::parseArgs(vector<string> & comargs)
   {
       // First parse the command line arguments
       bool bCheckUser=false;
       unsigned long argc = comargs.size();
       if(argc==1)
       {
           comargs.emplace_back("-e");
           if(comargs.size()!=2)
           {
               cerr << "ERROR_MAIN_010: Incorrect command line parsing." << endl;
           }
       }
       if(comargs[1]=="-h"||comargs[1]=="-H"||argc==1||comargs[1]=="-help" || comargs[1] == "-e")
       {
           stringstream os;
           // Sort out piping to terminal if verbose has not been defined.
           #ifndef verbose
           dup2(saved_stdout, fileno(stdout));
           //close(saved_stdout);
           #endif
           if(argc==1)
           {
               os << "No arguments supplied: expected 30. These are: " << endl;
           }
           else
           {
               os << "30 command line arguments are required. These are: " << endl;
           }
           os << "1: the seed for the simulation." << endl;
           os << "2: the simulation task (for file reference)." << endl;
           os << "3: the map config file." << endl;
           os << "4: the output directory." << endl;
           os << "5: the minimum speciation rate." << endl;
           os << "6: the dispersal tau value." << endl;
           os << "7: the dispersal sigma value." << endl;
           os << "8: the deme size." << endl;
           os << "9: the deme sample size." << endl;
           os << "10: the maximum simulation time (in seconds)." << endl;
           os << "11: the dispersal_relative_cost value for moving through non-habitat." << endl;
           os << "12: the temporal sampling file containing tab-separated generation values for sampling points in time (null for only sampling the present)." << endl;
           os << "13: the minimum number of species known to exist. (Currently has no effect)." << endl;
           os << "14 onwards: speciation rates to apply after simulation." << endl;
           os << "There is also a full-command line mode, (flag -f), which allows for more options to be specified via the command line." << endl;
           os << "Would you like to see these options? Y/N: " << flush;
           write_cerr(os.str());
           os.str("");
           string fullopts;
           cin >> fullopts;
           if(fullopts == "Y" || fullopts == "y")
           {
               os << "1: the task_iter used for setting the seed." << endl;
               os << "2: the sample grid x dimension." << endl;
               os << "3: the sample grid y dimension." << endl;
               os << "4: the fine map file relative path." << endl;
               os << "5: the fine map x dimension." << endl;
               os << "6: the fine map y dimension." << endl;
               os << "7: the fine map x offset." << endl;
               os << "8 the fine map y offset." << endl;
               os << "9: the coarse map file relative path." << endl;
               os << "10: the coarse map x dimension." << endl;
               os << "11: the coarse map y dimension." << endl;
               os << "12: the coarse map x offset." << endl;
               os << "13: the coarse map y offset." << endl;
               os << "14: the scale of the coarse map compared to the fine (10 means resolution of coarse map = 10 x resolution of fine map)." << endl;
               os << "15: the output directory." << endl;
               os << "16: the speciation rate." << endl;
               os << "17: the dispersal distance (tau)." << endl;
               os << "18: the deme size." << endl;
               os << "19: the deme sample size (as a proportion of deme size)." << endl;
               os << "20: the time to run the simulation (in seconds)." << endl;
               os << "21: dispersal_relative_cost - the relative cost of moving through non-forest." << endl;
               os << "22: the_task - for referencing the specific task later on." << endl;
               os << "23: the minimum number of species the system is known to contain." << endl;
               os << "24: the pristine fine map file to use." << endl;
               os << "25: the pristine coarse map file to use." << endl;
               os << "26: the rate of forest change from pristine." << endl;
               os << "27: the time (in generations) since the pristine forest was seen." << endl;
               os << "28: the dispersal sigma value." << endl;
               os << "29: the sample mask, with binary 1:0 values for areas that we want to sample from. If this is not provided then this will default to mapping the entire grid." << endl;
               os << "30: a file containing a tab-separated list of sample points in time (in generations). If this is null then only the present day will be sampled." << endl;
               os << "31-onwards: speciation rates to be applied at the end of the simulation" << endl;
               os << "Note that using the -f flag prohibits more than one two historic maps being used." << endl;
           }
           os << "Would you like to run with the default settings? (Y/N)" << flush;
           write_cerr(os.str());
           os.str("");
           string cDef;
           cin >> cDef;
           if(cDef == "Y"||cDef=="y")
           {
               bCheckUser = true;
           }
           else
           {
               bCheckUser = false;
               os << "Possible command line arguments: " << endl;
               os << "-h/-help: Show the help file." << endl;
               os << "-d/-D: Run with default small parameters." << endl;
               os << "-dl/-DL: Run with default large parameters." << endl;
               os << "-dx/-DX: Run with the default very large parameters." << endl;
               os << "-c/-config: Run with the supplied config file." << endl;
               write_cerr(os.str());
               exit(1); // exit the program right away as there is no need to continue if there is no simulation to run!
           }
           #ifndef verbose
           openLogFile(true);
           #endif
       }
       
       if(comargs[1] == "-r" || comargs[1] == "-R" || comargs[1] == "-resume")
       {
           comargs[1] = "resuming";
           if(argc != 6)
           {
               cerr << "Incorrect number of parameters provided for resuming simulation. Expecting:" << endl;
               cerr << "1: -r flag" << endl;
               cerr << "2: the folder containing the paused simulation (should hold a 'Pause' folder)" << endl;
               cerr << "3: the simulation seed" << endl;
               cerr << "4: the simulation task" << endl;
               cerr << "5: the time to run the simulation for" << endl;
               exit(-1);
           }
           bResume = true;
           bPaused = true;
       }
       // Import the default parameters if required.
       if(comargs[1]=="-d"||comargs[1]=="-D"||bCheckUser)
       {
           runAsDefault(comargs);
           bCheckUser=true;
       }
       if(comargs[1]=="-dl"||comargs[1]=="-DL"||comargs[1]=="-dL"||comargs[1]=="-Dl")
       {
           runLarge(comargs);
           bCheckUser = true;
       }
       if(comargs[1]=="-dx"||comargs[1]=="-dX"||comargs[1]=="-DX"||comargs[1]=="-Dx")
       {
           runXL(comargs);
           bCheckUser = true;
       }
       if(comargs[1]=="-c"||comargs[1]=="-C"||comargs[1]=="-config"|| comargs[1]=="-Config")
       {
           // Check that the config file is supplied.
           if(argc!=3 && argc)
           {
               throw Main_Exception("ERROR_MAIN_011: FATAL. -c or -config used to attempt import from config file, but no config file provided.");
           }
           bConfig = true;
       }
       bFullmode = false;
       if(comargs[1] == "-f" || comargs[2] == "-f")
       {
           write_cout("Full command-line mode enabled.\n");
           bFullmode = true;
       }
       removeComOption(argc, comargs);
       removeComOption(argc, comargs);
       if(argc > 12 && !bFullmode)
       {
           return;
       }
       if(argc<31&&!bCheckUser &&!bConfig)
       {
           string err = "ERROR_MAIN_000: FATAL.  Incorrect arguments supplied (" + to_string((long long)argc-1) + " supplied; expected 30).";
           throw Main_Exception(err);
           // note argc-1 which takes in to account the automatic generation of one command line argument which is the number of arguments.
       }
       argc = comargs.size();
   }
   
   
   void Tree::checkFolders()
   {
       
       stringstream os;
       os << "Checking folder existance..." << flush;
       bool bFineMap, bCoarseMap, bFineMapPristine, bCoarseMapPristine, bSampleMask, bOutputFolder;
       try
       {
           bFineMap = doesExistNull(sim_parameters.finemapfile);
       }
       catch(Fatal_Exception& fe)
       {
           cerr << fe.what() << endl;
           bFineMap = false;
       }
       try
       {
           bCoarseMap = doesExistNull(sim_parameters.coarsemapfile);
       }
       catch(Fatal_Exception& fe)
       {
           cerr << fe.what() << endl;
           bCoarseMap = false;
       }
       try
       {
           bFineMapPristine = doesExistNull(sim_parameters.pristinefinemapfile);
       }
       catch(Fatal_Exception& fe)
       {
           cerr << fe.what() << endl;
           bFineMapPristine = false;
       }
       try
       {
           bCoarseMapPristine = doesExistNull(sim_parameters.pristinecoarsemapfile);
       }
       catch(Fatal_Exception& fe)
       {
           cerr << fe.what() << endl;
           bCoarseMapPristine = false;
       }
       if(sim_parameters.outdirectory != "null")
       {
           try
           {
               bOutputFolder = doesExist(sim_parameters.outdirectory);
           }
           catch(runtime_error &re)
           {
               cerr << "Output folder does not exist... creating..." << flush;
               bOutputFolder = boost::filesystem::create_directory(sim_parameters.outdirectory);
               if( bOutputFolder)
               {
                   cerr << "done!" << endl;
               }
               else
               {
                   cerr << endl << re.what() << endl;
               }
           }
       }
       else
       {
           throw Fatal_Exception("ERROR_MAIN_009: FATAL. Output folder cannot be null.");
       }
       try
       {
           bSampleMask = doesExistNull(sim_parameters.samplemaskfile);
       }
       catch(Fatal_Exception& fe)
       {
           cerr << fe.what() << endl;
           bSampleMask = false;
       }
       if(bFineMap && bCoarseMap && bFineMapPristine && bCoarseMapPristine && bOutputFolder && bSampleMask)
       {
           os << "\rChecking folder existance...done!                                                                " << endl;
           write_cout(os.str());
           return;
       }
       else
       {
           throw Fatal_Exception("Required files do not all exist. Check program inputs.");
       }
   }
   
   void Tree::checkSims()
   {
       checkSims(sim_parameters.outdirectory, sim_parameters.the_seed, sim_parameters.the_task);
   }
   
   void Tree::checkSims(string output_dir, long seed_in, long task_in)
   {
       
       stringstream os;
       os << "Checking for unfinished simulations..." << flush;
       ifstream out;
       string file_to_open;
   //  char file_to_open[100];
   //  sprintf (file_to_open, "%s/Pause/Data_%i.csv",outdirect,int(the_task));
       file_to_open = output_dir + string("/Pause/Dump_active_") + to_string((unsigned long long)task_in)+"_"+to_string((unsigned long long)seed_in) + string(".csv");
       out.open(file_to_open);
       if(out.good())
       {
           os << "done!" << endl << "File found containing unfinished simulations." << endl;
           write_cout(os.str());
           if(!bPausedImport)
           {
               setResumeParameters(sim_parameters.outdirectory, sim_parameters.outdirectory, sim_parameters.the_seed,
                                   sim_parameters.the_task, sim_parameters.maxtime);
           }
           bPaused = true;
       }
       else
       {
           os << "done!" << endl << "No files found containing unfinished simulations." << endl;
           write_cout(os.str());
           bPaused = false;
       }
   }
   
   void Tree::setParameters()
   {
       sim_parameters.printVars();
       if(!varimport)
       {
           // Set the variables equal to the value from the Mapvars object.
           finemapinput = sim_parameters.finemapfile;
           coarsemapinput = sim_parameters.coarsemapfile;
           gridxsize = sim_parameters.vargridxsize;
           gridysize = sim_parameters.vargridysize;
   
           finemapxsize = sim_parameters.varfinemapxsize;
           finemapysize = sim_parameters.varfinemapysize;
           finemapxoffset = sim_parameters.varfinemapxoffset;
           finemapyoffset = sim_parameters.varfinemapyoffset;
   
           coarsemapxsize = sim_parameters.varcoarsemapxsize;
           coarsemapysize = sim_parameters.varcoarsemapysize;
           coarsemapxoffset = sim_parameters.varcoarsemapxoffset;
           coarsemapyoffset = sim_parameters.varcoarsemapyoffset;
           coarsemapscale = sim_parameters.varcoarsemapscale;
   
           outdirectory = sim_parameters.outdirectory;
   
           dispersal_relative_cost = sim_parameters.dispersal_relative_cost;
           the_task = sim_parameters.the_task;
           the_seed = sim_parameters.the_seed;
           desired_specnum = sim_parameters.desired_specnum;
   
           // pristine map information
           pristinefinemapinput = sim_parameters.pristinefinemapfile;
           pristinecoarsemapinput = sim_parameters.pristinecoarsemapfile;
           dPristine = sim_parameters.dPristine;
           dForestTransform = sim_parameters.dForestChangeRate;
   
           deme = sim_parameters.deme;
           deme_sample = sim_parameters.deme_sample;
           spec = sim_parameters.spec;
           sigma = sim_parameters.sigma;
           tau = sim_parameters.tau;
           maxtime = sim_parameters.maxtime;
           autocorrel_file = sim_parameters.autocorrel_file;
           setProtractedVariables(sim_parameters.min_speciation_gen, sim_parameters.max_speciation_gen);
           varimport = true;
       }
       else
       {
           throw Main_Exception("ERROR_MAIN_001: Variables already imported.");
       }
   }
   
   vector<double> Tree::getTemporalSampling()
   {
       if(bAutocorrel)
       {
           return (autocorrel_times);
       }
       else
       {
           vector<double> tmp;
           tmp.push_back(0.0);
           return (tmp);
       }
   }
   
   void Tree::importMaps()
   {
       if(varimport)
       {
           // Set the dimensions
           forestmap.setDims(sim_parameters);
           try
           {
               // Set the time variables
               forestmap.checkMapExists();
               // forestmap.setTimeVars(dPristine,dForestTransform);
               // Import the fine map
               forestmap.calcFineMap();
               // Import the coarse map
               forestmap.calcCoarseMap();
               // Calculate the offset for the extremeties of each map
               forestmap.calcOffset();
               // Import the pristine maps;
               forestmap.calcPristineFineMap();
               forestmap.calcPristineCoarseMap();
               // Calculate the maximum values
               forestmap.recalculateForestMax();
               rep_map.import(sim_parameters.reproduction_file,
                              sim_parameters.varfinemapxsize, sim_parameters.varfinemapysize);
               rep_map.setOffsets(sim_parameters.varcoarsemapxoffset, sim_parameters.varfinemapyoffset,
                                  sim_parameters.vargridxsize, sim_parameters.vargridysize);
               // Now verify that the reproduction map is always non-zero when the density is non-zero.
               verifyReproductionMap();
           }
           catch(Map_Exception& me)
           {
               throw Fatal_Exception("No dimensions set - can't start simulations");
           }
       }
       else
       {
           throw Fatal_Exception("ERROR_MAIN_002: Variables not imported.");
       }
   }
   
   long long Tree::getSeed()
   {
       return the_seed;
   }
   
   void Tree::setSeed(long long theseedin)
   {
       if(!seeded)
       {
           NR.setSeed(theseedin);
           the_seed = theseedin;
           seeded = true;
       }
   }
   
   bool Tree::getbPaused()
   {
       return bPaused;
   }
   
   vector<long> Tree::randomList(long maxnum, long numnum)
   {
       vector<long> isin;
       vector<long> isout;
       isin.clear();
       isout.clear();
       long endisout = maxnum + 1;
       for(long i = 0; i <= maxnum; i++)
       {
           isout.push_back(i);
       }
       while(unsigned(isin.size()) < numnum)
       {
           long chosen = NR.i0(endisout - 1);
           isin.push_back(isout[chosen]);
           isout[chosen] = isout[endisout - 1];
           endisout--;
       }
   
       return isin;
   }
   
   unsigned long Tree::setObjectSizes()
   {
       unsigned long initcount;
   
       samplegrid.importDatamask(sim_parameters);
       //  os << "Datamask import complete" << endl;
       // Get a count of the number of individuals on the grid.
       try
       {
           initcount = forestmap.getInitialCount(deme_sample, samplegrid);
       }
       catch(exception& e)
       {
           cerr << e.what() << endl;
           throw Fatal_Exception(e.what());
       }
       // Set active and data at the correct sizes.
       if(initcount == 0)
       {
           throw runtime_error("Initial count is 0. No individuals to simulate. Exiting program.");
       }
       else
       {
           write_cout("Initial count is " + to_string(initcount) + "\n");
       }
       if(initcount > 10000000000)
       {
           write_cerr("Initial count extremely large, RAM issues likely: " + to_string(initcount));
       }
       active.SetRowSize(initcount + 1);
       data.SetRowSize(2 * initcount + 1);
       // Make the grid size with 1 entry per deme.
       // Previous versions used 1 entry per individual for increased spatial movement. However, with percentage cover,
       // this was now deemed unneccessary.
       grid.SetSize(gridysize, gridxsize);
       return (initcount);
   }
   
   void Tree::setupDispersalCoordinator()
   {
       dispersal_coordinator.setForestMap(&forestmap);
       dispersal_coordinator.setRandomNumber(&NR);
       dispersal_coordinator.setGenerationPtr(&generation);
       dispersal_coordinator.setDispersal(sim_parameters.dispersal_method, sim_parameters.dispersal_file,
                                           sim_parameters.varfinemapxsize, sim_parameters.varfinemapysize,
                                           sim_parameters.m_prob, sim_parameters.cutoff, sim_parameters.sigma,
                                           sim_parameters.tau, sim_parameters.restrict_self);
   }
   
   void Tree::setup()
   {
       stringstream os;
       os << "*************************************************" << endl;
       os << "Setting up simulation..." << endl;
       write_cout(os.str());
       os.str("");
       // deme = square root of Deme size - note deme*deme*number of demes is the total size of the system.  Number of
       // demes is given by the map scenario
       // deme_sample = number of individuals to be sampled from each deme (cannot be more than deme^2)
       // spec = speciation rate required
       // dispersal = dispersal distance (double)
       // typeflag = 2 normal
       // typeflag != 2 fat
       // sigma = kernel fatness
       // map_scenario gives the index of the predefined map list vectors that will indicate which habitat map to load
       // generations_since = number of generations since disturbance at present day of sampling
       // equilibrium mask = do we ignore the generations_since tag and simply run all the way to equilibrium on the
       // fragmented landscape?
       // max time allowed for this simulation (useful for HPC runs)
       // Set the private variables for the simulation
       // Start the timer
       time(&start);
       if(bPaused)
       {
           if(!bPausedImport)
           {
               setResumeParameters();
           }
           // try to import the resume variables
           simResume();
           setupDispersalCoordinator();
       }
       else
       {
           // Otherwise, try to read parameters and set up objects.
           // Use the Mapvars object to import the necessary information
           setParameters();
           // Set the seed
           setSeed(the_seed);
           // Determine the speciation rates which will be applied after the simulation completes.
           determineSpeciationRates();
           try
           {
               if(autocorrel_file == "null")
               {
                   bAutocorrel = false;
               }
               else
               {
                   // Import the time sample points
                   bAutocorrel = true;
                   vector<string> tmpimport;
                   ConfigOption tmpconfig;
                   tmpconfig.setConfig(autocorrel_file, false);
                   tmpconfig.importConfig(tmpimport);
                   for(const auto &i : tmpimport)
                   {
                       autocorrel_times.push_back(stod(i));
                       //                  os << "t_i: " << autocorrel_times[i] << endl;
                   }
               }
           }
           catch(Config_Exception& ce)
           {
               cerr << ce.what() << endl;
           }
           // Make the mask map with 1 entry in each deme
           // Previous versions worked with 1 entry per individual.
           importMaps();  // This will import the fine and coarse maps using the routine specified in the Map class.
           // Set up the dispersal coordinator
           setupDispersalCoordinator();
   //      NR.setDispersalMethod(sim_parameters.dispersal_method, sim_parameters.m_prob, sim_parameters.cutoff);
           forestmap.setLandscape(sim_parameters.landscape_type);
       #ifdef DEBUG
           forestmap.validateMaps();  // If you're having problems with the maps generating errors, run this line to check the
       #endif
           unsigned long initial_count = setObjectSizes();
           // import the grid file
           unsigned long number_start;
           number_start = 0;
           endactive = 0;
           active[0].setup(0, 0, 0, 0, 0, 0, 0);
           //      data[0].setSpec(1.0);
           os << "\rSetting up simulation...filling grid                           " << flush;
           write_cout(os.str());
           // Add the individuals to the grid, and add wrapped individuals to their correct locations.
           // This loop adds individuals to data and active (for storing the coalescence tree and active lineage tracking)
           for(unsigned long i = 0; i < sim_parameters.varsamplexsize; i++)
           {
               for(unsigned long j = 0; j < sim_parameters.varsampleysize; j++)
               {
                   long x, y;
                   x = i;
                   y = j;
                   long x_wrap, y_wrap;
                   x_wrap = 0;
                   y_wrap = 0;
                   samplegrid.recalculate_coordinates(x, y, x_wrap, y_wrap);
                   if(x_wrap == 0 && y_wrap == 0)
                   {
                       unsigned long stored_next = grid[y][x].getNext();
                       unsigned long stored_nwrap = grid[y][x].getNwrap();
                       grid[y][x].initialise(forestmap.getVal(x, y, 0, 0, 0));
                       grid[y][x].fillList();
                       grid[y][x].setNwrap(stored_nwrap);
                       grid[y][x].setNext(stored_next);
                       if(samplegrid.getVal(x, y, 0, 0))
                       {
                           double dSample_amount = floor(deme_sample * grid[y][x].getMaxsize());
                           for(unsigned long k = 0; k < dSample_amount; k++)
                           {
                               if(k >= grid[y][x].getMaxsize())
                               {
                                   break;
                               }
                               if(number_start + 1 > initial_count)
                               {
                                   stringstream msg;
                                   msg << "Number start greater than initial count. Please report this error!" << endl;
                                   msg << "Number start: " << number_start << ". Initial count: " << initial_count
                                       << endl;
                                   throw out_of_range(msg.str());
                               }
                               else
                               {
                                   number_start++;
                                   unsigned long listpos = grid[y][x].addSpecies(number_start);
                                   // Add the species to active
                                   active[number_start].setup(x, y, 0, 0, number_start, listpos, 1);
                                   // Add a tip in the Treenode for calculation of the coalescence tree at the
                                   // end of the simulation.
                                   // This also contains the start x and y position of the species.
                                   data[number_start].setup(true, x, y, 0, 0);
                                   data[number_start].setSpec(NR.d01());
                                   endactive++;
                                   enddata++;
                               }
                           }
                       }
                   }
                   else
                   {
                       if(samplegrid.getVal(x, y, x_wrap, y_wrap))
                       {
                           double dSample_amount = floor(deme_sample * forestmap.getVal(x, y, x_wrap, y_wrap, 0.0));
                           for(unsigned long k = 0; k < dSample_amount; k++)
                           {
                               if(number_start + 1 > initial_count)
                               {
                                   stringstream msg;
                                   msg << "Number start greater than initial count. Please report this error!";
                                   msg << "Number start: " << number_start << ". Initial count: " << initial_count
                                       << endl;
                                   throw out_of_range(msg.str());
                               }
                               else
                               {
                                   number_start++;
                                   // Add the lineage to the wrapped lineages
                                   active[number_start].setup((unsigned long) x,
                                                              (unsigned long) y,
                                                              x_wrap, y_wrap, number_start, 0, 1);
                                   addWrappedLineage(number_start, x, y);
                                   // Add a tip in the Treenode for calculation of the coalescence tree at the
                                   // end of the simulation.
                                   // This also contains the start x and y position of the species.
                                   data[number_start].setup(true, x, y, x_wrap, y_wrap);
                                   data[number_start].setSpec(NR.d01());
                                   endactive++;
                                   enddata++;
                               }
                           }
                       }
                   }
               }
           }
           if(number_start == initial_count)  // Check that the two counting methods match up.
           {
           }
           else
           {
               if(initial_count > 1.1 * number_start)
               {
                   write_cerr("Data usage higher than neccessary - check allocation of individuals to the grid.");
                   stringstream ss;
                   ss << "Initial count: " << initial_count << "  Number counted: " << number_start << endl;
                   write_cerr(ss.str());
               }
           }
           // Now validate all lineages
   #ifdef DEBUG
           validateLineages();
   #endif
           // other variables
           steps = 0;
           generation = 0;
           os.str("");
           os << "\rSetting up simulation...done!                           " << endl;
           os << "Number of individuals simulated: " << endactive << endl;
           write_cout(os.str());
           maxsimsize = enddata;
           if(active.size() < endactive || endactive == 0)
           {
               cerr << "endactive: " << endactive << endl;
               cerr << "active.size: " << active.size() << endl;
               cerr << "initial_count: " << initial_count << endl;
               cerr << "number_start: " << number_start << endl;
               if(endactive == 0)
               {
                   throw runtime_error("No individuals to simulate! Check map set up. Exiting...");
               }
               else
               {
                   throw Fatal_Exception(
                       "ERROR_MAIN_007: FATAL. Sizing error - endactive is greater than the size of active.");
               }
           }
           startendactive = endactive;
       }
   }
   
   void Tree::removeOldPos(const unsigned long& chosen)
   {
       long nwrap = active[chosen].getNwrap();
       long oldx = active[chosen].getXpos();
       long oldy = active[chosen].getYpos();
       if(nwrap == 0)
       {
           if(active[chosen].getXwrap() != 0 || active[chosen].getYwrap() != 0)
           {
               cerr << "chosen: " << chosen << endl;
               cerr << "x,y wrap: " << active[chosen].getXwrap() << "," << active[chosen].getYwrap() << endl;
               throw Fatal_Exception("ERROR_MOVE_015: Nwrap not set correctly. Nwrap 0, but x and y wrap not 0. ");
           }
   // Then the lineage exists in the main list;
   // debug (can be removed later)
   #ifdef pristine_mode
           if(grid[oldy][oldx].getMaxsize() < active[chosen].getListpos())
           {
               cerr << "grid maxsize: " << grid[oldy][oldx].getMaxsize() << endl;
               throw Fatal_Exception("ERROR_MOVE_001: Listpos outside maxsize. Check move programming function.");
           }
   #endif
           // delete the species from the list
           grid[oldy][oldx].deleteSpecies(active[chosen].getListpos());
           // clear out the variables.
           active[chosen].setNext(0);
           active[chosen].setNwrap(0);
           active[chosen].setListpos(0);
       }
       else  // need to loop over the nwrap to check nexts
       {
           if(nwrap == 1)
           {
               grid[oldy][oldx].setNext(active[chosen].getNext());
               // Now reduce the nwrap of the lineages that have been effected.
               long nextpos = active[chosen].getNext();
               // loop over the rest of the list, reducing the nwrap
               while(nextpos != 0)
               {
                   active[nextpos].decreaseNwrap();
                   nextpos = active[nextpos].getNext();
               }
               // decrease the nwrap
               grid[oldy][oldx].decreaseNwrap();
               active[chosen].setNwrap(0);
               active[chosen].setNext(0);
               active[chosen].setListpos(0);
               nwrap = 0;
           }
           else
           {
               long lastpos = grid[oldy][oldx].getNext();
               while(active[lastpos].getNext() !=
                     chosen)  // loop until we reach the next, then set the next correctly.
               {
                   lastpos = active[lastpos].getNext();
               }
               if(lastpos != 0)
               {
                   active[lastpos].setNext(active[chosen].getNext());
                   // check
                   if(active[lastpos].getNwrap() != (active[chosen].getNwrap() - 1))
                   {
                       cerr << "lastpos : " << lastpos << " lastpos nwrap: " << active[lastpos].getNwrap()
                            << endl;
                       cerr << "chosen: " << chosen << " chosen nwrap: " << active[chosen].getNwrap()
                            << endl;
                       throw Fatal_Exception("ERROR_MOVE_022: nwrap setting of either chosen or the "
                                             "lineage wrapped before chosen. Check move function.");
                   }
                   lastpos = active[lastpos].getNext();
                   while(lastpos != 0)
                   {
                       active[lastpos].decreaseNwrap();
                       lastpos = active[lastpos].getNext();
                   }
   
               }
               else
               {
                   cerr << "lastpos: " << lastpos << " endactive: " << endactive << " chosen: " << chosen
                        << endl;
                   throw Fatal_Exception(
                       "ERROR_MOVE_024: Last position before chosen is 0 - this is impossible.");
               }
               grid[oldy][oldx].decreaseNwrap();
               active[chosen].setNwrap(0);
               active[chosen].setNext(0);
               active[chosen].setListpos(0);
               nwrap = 0;
   
           }
           unsigned long iCount = 1;
           long pos = grid[oldy][oldx].getNext();
           if(pos == 0)
           {
               iCount = 0;
           }
           else
           {
               int c = 0;
               while(active[pos].getNext() != 0)
               {
                   c++;
                   iCount++;
                   pos = active[pos].getNext();
                   if(c > 10000)
                   {
                       //                  os << pos << endl;
                       //                  os << active[pos].getNext() << endl;
                       break;
                   }
               }
           }
   
           if(iCount != grid[oldy][oldx].getNwrap())
           {
               cerr << "Nwrap: " << grid[oldy][oldx].getNwrap() << " Counted lineages: " << iCount << endl;
               throw Fatal_Exception("ERROR_MOVE_014: Nwrap not set correctly after move for grid cell");
           }
       }
   }
   
   void Tree::calcMove(Step &this_step)
   {
       dispersal_coordinator.disperse(this_step);
   }
   
   
   long double Tree::calcMinMax(const unsigned long& current)
   {
       // this formula calculates the speciation rate required for speciation to have occured on this branch.
       // need to allow for the case that the number of gens was 0
       long double newminmax = 1;
       long double oldminmax = active[current].getMinmax();
       if(data[active[current].getMpos()].getGenRate() == 0)
       {
           newminmax = data[active[current].getMpos()].getSpecRate();
       }
       else
       {
           // variables need to be defined separately for the decimal division to function properly.
           long double tmpdSpec = data[active[current].getMpos()].getSpecRate();
           long double tmpiGen = data[active[current].getMpos()].getGenRate();
           newminmax = 1 - (pow(1 - tmpdSpec, (1 / tmpiGen)));
       }
       long double toret = min(newminmax, oldminmax);
       return toret;
   }
   
   void Tree::coalescenceEvent(const unsigned long& chosen, unsigned long& coalchosen)
   {
       // coalescence occured, so we need to adjust the data appropriatedly
       // our chosen lineage has merged with the coalchosen lineage, so we need to sync up the data.
       enddata++;
       data[enddata].setup(0, active[chosen].getXpos(), active[chosen].getYpos(), active[chosen].getXwrap(),
                           active[chosen].getYwrap());
   
       // First perform the move
       data[active[chosen].getMpos()].setParent(enddata);
       data[active[coalchosen].getMpos()].setParent(enddata);
       active[coalchosen].setMinmax(
           max(active[coalchosen].getMinmax(),
               active[chosen].getMinmax()));  // set the new minmax to the maximum of the two minimums.
       active[chosen].setMinmax(active[coalchosen].getMinmax());
       data[enddata].setIGen(0);
       data[enddata].setSpec(NR.d01());
       active[chosen].setMpos(enddata);
       active[coalchosen].setMpos(enddata);
       //      removeOldPos(chosen);
       switchPositions(chosen);
   }
   
   void Tree::calcNewPos(bool& coal,
                         const unsigned long& chosen,
                         unsigned long& coalchosen,
                         const long& oldx,
                         const long& oldy,
                         const long& oldxwrap,
                         const long& oldywrap)
   {
       // Calculate the new position of the move, whilst also calculating the probability of coalescence.
       unsigned long nwrap = active[chosen].getNwrap();
       if(oldxwrap == 0 && oldywrap == 0)
       {
           // Debug check (to remove later)
           if(nwrap != 0)
           {
               throw Fatal_Exception(
                   "ERROR_MOVE_006: NON FATAL. Nwrap not set correctly. Check move programming function.");
           }
           // then the procedure is relatively simple.
           // check for coalescence
           // check if the grid needs to be updated.
           if(grid[oldy][oldx].getMaxsize() != forestmap.getVal(oldx, oldy, oldxwrap, oldywrap, generation))
           {
               grid[oldy][oldx].setMaxsize(forestmap.getVal(oldx, oldy, 0, 0, generation));
           }
           coalchosen = grid[oldy][oldx].getRandLineage(NR);
   #ifdef DEBUG
           if(coalchosen != 0)
           {
               if(active[coalchosen].getXpos() != (unsigned long)oldx ||
                  active[coalchosen].getYpos() != (unsigned long)oldy ||
                  active[coalchosen].getXwrap() != oldxwrap || active[coalchosen].getYwrap() != oldywrap)
               {
                   cerr << chosen << "," << coalchosen << endl;
                   cerr << "chosen - x,y: " << oldx << "," << oldy << endl
                        << "x, y wrap: " << oldxwrap << "," << oldywrap << endl;
                   cerr << "coalchosen - x,y:" << active[coalchosen].getXpos() << ","
                        << active[coalchosen].getYpos() << endl;
                   cerr << " x,y wrap: " << active[coalchosen].getXwrap() << ","
                        << active[coalchosen].getYwrap() << endl;
                   throw Fatal_Exception(
                       "ERROR_MOVE_006: NON FATAL. Nwrap not set correctly. Check move programming function.");
               }
           }
   #endif
           if(coalchosen == 0)  // then the lineage can be placed in the empty space.
           {
               long tmplistindex = grid[oldy][oldx].addSpecies(chosen);
               // check
               if(grid[oldy][oldx].getSpecies(tmplistindex) != chosen)
               {
                   throw Fatal_Exception("ERROR_MOVE_005: Grid index not set correctly for species. Check "
                                         "move programming function.");
               }
   #ifdef pristine_mode
               if(grid[oldy][oldx].getListsize() > grid[oldy][oldx].getMaxsize())
               {
                   throw Fatal_Exception(
                       "ERROR_MOVE_001: Listpos outside maxsize. Check move programming function.");
               }
   #endif
               active[chosen].setNwrap(0);
               active[chosen].setListpos(tmplistindex);
               coal = false;
           }
           else  // then coalescence has occured
           {
               active[chosen].setNwrap(0);
               active[chosen].setListpos(0);
               // DO THE COALESCENCE STUFF
               coal = true;
           }
       }
       else  // need to check all the possible places the lineage could be.
       {
           if(nwrap != 0)
           {
               throw Fatal_Exception("ERROR_MOVE_022: Nwrap not set correctly in move.");
           }
           nwrap = grid[oldy][oldx].getNwrap();
           if(nwrap != 0)  // then coalescence is possible and we need to loop over the nexts to check those that are
           // in the same position
           {
               // Count the possible matches of the position.
               unsigned long matches = 0;
               // Create an array containing the list of active references for those that match as
               // this stops us having to loop twice over the same list.
               unsigned long matchlist[nwrap];
               unsigned long next_active;
               next_active = grid[oldy][oldx].getNext();
               // Count if the first "next" matches
               if(active[next_active].getXwrap() == oldxwrap && active[next_active].getYwrap() == oldywrap)
               {
   // check
   #ifdef DEBUG
                   if(active[next_active].getNwrap() != 1)
                   {
                       throw Fatal_Exception("ERROR_MOVE_022a: Nwrap not set correctly in move.");
                   }
   #endif
                   matchlist[matches] = next_active;  // add the match to the list of matches.
                   matches++;
               }
               // Now loop over the remaining nexts counting matches
               //#ifdef DEBUG
               unsigned long ncount = 1;
               //#endif
               while(active[next_active].getNext() != 0)
               {
                   next_active = active[next_active].getNext();
                   if(active[next_active].getXwrap() == oldxwrap && active[next_active].getYwrap() == oldywrap)
                   {
                       matchlist[matches] = next_active;
                       matches++;
                   }
                   // check
                   //#ifdef DEBUG
                   ncount++;
   #ifdef DEBUG
                   if(active[next_active].getNwrap() != ncount)
                   {
                       throw Fatal_Exception("ERROR_MOVE_022d: Nwrap not set correctly in move.");
                   }
   #endif
               }
               if(nwrap != ncount)
               {
                   throw Fatal_Exception("ERROR_MOVE_022c: Nwrap not set correctly in move.");
               }
               // Matches now contains the number of lineages at the exact x,y, xwrap and ywrap position.
               // Check if there were no matches at all
               if(matches == 0)
               {
                   coalchosen = 0;
                   coal = false;
                   active[next_active].setNext(chosen);
                   grid[oldy][oldx].increaseNwrap();
                   active[chosen].setNwrap(grid[oldy][oldx].getNwrap());
                   active[chosen].setListpos(0);
               }
               else  // if there were matches, generate a random number to see if coalescence occured or not
               {
                   unsigned long randwrap =
                       floor(NR.d01() * (forestmap.getVal(oldx, oldy, oldxwrap, oldywrap, generation)) + 1);
   // Get the random reference from the match list.
   // If the movement is to an empty space, then we can update the chain to include the new
   // lineage.
   #ifdef pristine_mode
                   if(randwrap > forestmap.getVal(oldx, oldy, oldxwrap, oldywrap, generation))
                   {
                       throw Fatal_Exception(
                           "ERROR_MOVE_004: Randpos outside maxsize. Check move programming function");
                   }
                   if(matches > forestmap.getVal(oldx, oldy, oldxwrap, oldywrap, generation))
                   {
                       cerr << "matches: " << matches << endl
                            << "forestmap value: "
                            << forestmap.getVal(oldx, oldy, oldxwrap, oldywrap, generation);
                       throw Fatal_Exception(
                           "ERROR_MOVE_004: matches outside maxsize. Check move programming function");
                   }
   #endif
                   if(randwrap > matches)  // coalescence has not occured
                   {
                       // os << "This shouldn't happen" << endl;
                       coalchosen = 0;
                       coal = false;
                       active[next_active].setNext(chosen);
                       grid[oldy][oldx].increaseNwrap();
                       active[chosen].setNwrap(grid[oldy][oldx].getNwrap());
                       active[chosen].setListpos(0);
                   }
                   else  // coalescence has occured
                   {
                       coal = true;
                       coalchosen = matchlist[randwrap - 1];
                       active[chosen].setEndpoint(oldx, oldy, oldxwrap, oldywrap);
                       if(coalchosen == 0)
                       {
                           throw Fatal_Exception(
                               "ERROR_MOVE_025: Coalescence attempted with lineage of 0.");
                       }
                   }
               }
   #ifdef pristine_mode
               if(grid[oldy][oldx].getMaxsize() < active[chosen].getListpos())
               {
                   throw Fatal_Exception(
                       "ERROR_MOVE_001: Listpos outside maxsize. Check move programming function.");
               }
   #endif
           }
           else  // just add the lineage to next.
           {
               if(grid[oldy][oldx].getNext() != 0)
               {
                   throw Fatal_Exception("ERROR_MOVE_026: No nwrap recorded, but next is non-zero.");
               }
               coalchosen = 0;
               coal = false;
               //              if(chosen==3893119)
               //              {
               //                  validationCheck(31556348,12,chosen);
               //                  os << "test1..." << endl;
               //              }
               //              debug_504(chosen,12);
               grid[oldy][oldx].setNext(chosen);
               active[chosen].setNwrap(1);
               active[chosen].setNext(0);
               grid[oldy][oldx].increaseNwrap();
   // check
   #ifdef DEBUG
               if(grid[oldy][oldx].getNwrap() != 1)
               {
                   throw Fatal_Exception("ERROR_MOVE_022b: Nwrap not set correctly in move.");
               }
   #endif
               //              debug_504(chosen,11);
               //              if(chosen==3893119)
               //              {
               //                  validationCheck(31556348,13,chosen);
               //                  os << "test2..." << endl;
               //              }
           }
           //#ifdef DEBUG
           if(coalchosen != 0)
           {
               if(active[coalchosen].getXpos() != (unsigned long)oldx ||
                  active[coalchosen].getYpos() != (unsigned long)oldy ||
                  active[coalchosen].getXwrap() != oldxwrap || active[coalchosen].getYwrap() != oldywrap)
               {
                   cerr << chosen << "," << coalchosen << endl;
                   cerr << "chosen - x,y: " << oldx << "," << oldy << endl
                        << "x, y wrap: " << oldxwrap << "," << oldywrap << endl;
                   cerr << "coalchosen - x,y:" << active[coalchosen].getXpos() << ","
                        << active[coalchosen].getYpos() << endl;
                   cerr << " x,y wrap: " << active[coalchosen].getXwrap() << ","
                        << active[coalchosen].getYwrap() << endl;
                   throw Fatal_Exception("ERROR_MOVE_006b: NON FATAL. Nwrap not set correctly. Check move "
                                         "programming function.");
               }
           }
           //#endif
       }
   }
   
   void Tree::switchPositions(const unsigned long chosen)
   {
       if(chosen > endactive)
       {
           cerr << "chosen: " << chosen << " endactive: " << endactive << endl;
           throw Fatal_Exception("ERROR_MOVE_023: Chosen is greater than endactive. Check move function.");
       }
       if(chosen != endactive)
       {
           // This routine assumes that the previous chosen position has already been deleted.
           Datapoint tmpdatactive;
           tmpdatactive.setup(active[chosen]);
           // now need to remove the chosen lineage from memory, by replacing it with the lineage that lies in the last
           // place.
           if(active[endactive].getXwrap() == 0 &&
              active[endactive].getYwrap() == 0)  // if the end lineage is simple, we can just copy it across.
           {
               // check endactive
               if(active[endactive].getNwrap() != 0)
               {
                   cerr << "ERROR_MOVE_020: NON FATAL. Nwrap is not set correctly for endactive (nwrap should "
                           "be 0, but is "
                        << active[endactive].getNwrap() << " ). Identified during switch of positions."
                        << endl;
               }
               grid[active[endactive].getYpos()][active[endactive].getXpos()].setSpecies(
                   active[endactive].getListpos(), chosen);
               active[chosen].setup(active[endactive]);
               active[endactive].setup(tmpdatactive);
               active[endactive].setNwrap(0);
               active[endactive].setNext(0);
           }
           else  // else the end lineage is wrapped, and needs to be processed including the wrapping routines.
           {
               if(active[endactive].getNwrap() == 0)
               {
                   cerr << "ERROR_MOVE_021: NON FATAL. Nwrap is not set correctly for endactive (nwrap "
                           "incorrectly 0). Identified during switch of positions."
                        << endl;
               }
               //              os << "wrap"<<endl;
               long tmpactive = grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext();
               int tmpnwrap = active[endactive].getNwrap();
   
               // if the wrapping is just once, we need to set the grid next to the chosen variable.
               if(tmpnwrap == 1)
               {
                   // check
                   if(grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext() != endactive)
                   {
                       throw Fatal_Exception(string(
                           "ERROR_MOVE_019: FATAL. Nwrap for endactive not set correctly. Nwrap is 1, but "
                           "lineage at 1st position is " +
                           to_string(
                               (long long)grid[active[endactive].getYpos()][active[endactive].getXpos()]
                                   .getNext()) +
                           ". Identified during the move."));
                   }
                   grid[active[endactive].getYpos()][active[endactive].getXpos()].setNext(chosen);
               }
               else  // otherwise, we just set the next to chosen instead of endactive.
               {
                   int tmpcount = 0;
                   // loop over nexts until we reach the right lineage.
                   while(active[tmpactive].getNext() != endactive)
                   {
                       tmpactive = active[tmpactive].getNext();
                       tmpcount++;
                       // debug check
                       if(tmpcount > tmpnwrap)
                       {
                           cerr << "ERROR_MOVE_013: NON FATAL. Looping has not encountered a match, "
                                   "despite going further than required. Check nwrap counting."
                                << endl;
                           if(tmpactive == 0)
                           {
                               cerr << "gridnext: "
                                    << grid[active[endactive].getYpos()][active[endactive]
                                                                             .getXpos()]
                                           .getNext()
                                    << endl;
                               cerr << "x,y: " << active[endactive].getXpos() << ","
                                    << active[endactive].getYpos() << endl;
                               cerr << "xwrap,ywrap: " << active[endactive].getXwrap() << ","
                                    << active[endactive].getYwrap() << endl;
                               cerr << "endactive: " << endactive << endl;
                               cerr << "tmpactive: " << tmpactive << endl;
                               cerr << "tmpnwrap: " << tmpnwrap << " tmpcount: " << tmpcount
                                    << endl;
                               cerr << "FATAL!" << endl;
                               throw Fatal_Exception();
                           }
                       }
                   }
                   active[tmpactive].setNext(chosen);
               }
               active[chosen].setup(active[endactive]);
               active[endactive].setup(tmpdatactive);
   
               // check - debugging
               long testwrap = active[chosen].getNwrap();
               unsigned long testnext = grid[active[chosen].getYpos()][active[chosen].getXpos()].getNext();
               for(int i = 1; i < testwrap; i++)
               {
                   testnext = active[testnext].getNext();
               }
   
               if(testnext != chosen)
               {
                   throw Fatal_Exception("ERROR_MOVE_009: Nwrap position not set correctly after coalescence. "
                                         "Check move process.");
               }
           }
       }
       endactive--;
   }
   
   void Tree::speciation(const unsigned long& chosen)
   {
       // alter the data such that it reflects the speciation event.
       unsigned long tmpmpos = active[chosen].getMpos();
   // data[tmpmpos].increaseGen();
   #ifdef DEBUG
       // Store debug information in DEBUG mode
       this_step.location = "speciation";
       logfile << "SPECIATION" << endl;
       if(data[tmpmpos].hasSpeciated())
       {
           throw Fatal_Exception("ERROR_MOVE_028: Attempting to speciate a speciated species.");
       }
   #endif
       data[tmpmpos].speciate();
       // TEST REMOVE THIS WHEN TESTING COMPLETE!! done
       //      data[tmpmpos].setPosition(active[chosen].getXpos(),active[chosen].getYpos(),active[chosen].getXwrap(),active[chosen].getYwrap());
       // Now remove the old chosen lineage from the active directory.
       removeOldPos(chosen);
       switchPositions(chosen);
   }
   
   bool Tree::calcSpeciation(const long double& random_number,
                             const long double& speciation_rate,
                             const int& no_generations)
   {
       return checkSpeciation(random_number, speciation_rate, no_generations);
   }
   
   unsigned long Tree::estSpecnum()
   {
       // This bit has been removed as it has a very significant performance hit and is not required for most simulations.
       // As of version 3.2 it was fully compatible with the rest of the simulation, however. See estSpecnum for commented
       // code
       // (removed from here to make things tidier).
       // This bit was moved from runSimulation() to make things tidier there.
       /*
       if(steps%1000000==0)
   {
               time(&now);
               if(now - time_taken>200&&dPercentComplete>95)
               {
                               time(&time_taken);
                               unsigned long specnum = est_specnum();
                               os << "Estimated number of species: " << specnum <<
                               flush;
                               if(specnum<desired_specnum)
                               {
                                               os << " - desired
                                               number of species reached." << endl << "Halting
                                               simulations..." << endl;
                                               bContinueSim = false;
                               }
                               else
                               {
                                               os << endl;
                               }
               }
   }
   //*/
       long double dMinmax = 0;
       // first loop to find the maximum speciation rate required
       for(unsigned int i = 1; i <= endactive; i++)
       {
           long double tmpminmax = calcMinMax(i);
           active[i].setMinmax(tmpminmax);
           dMinmax = (long double)max(dMinmax, tmpminmax);
       }
       for(unsigned long i = 0; i <= enddata; i++)
       {
           if(data[i].isTip())
           {
               data[i].setExistance(true);
           }
           double maxret = 1;
           if(data[i].getGenRate() == 0)
           {
               maxret = 1;
           }
           else
           {
               maxret = data[i].getGenRate();
           }
           // This is the line that compares the individual random numbers against the speciation rate.
           if(data[i].getSpecRate() < (1 - pow((1 - dMinmax), maxret)))
           {
               data[i].speciate();
           }
       }
       bool loop = true;
       while(loop)
       {
           loop = false;
           for(unsigned int i = 0; i <= enddata; i++)
           {
               if(data[i].getExistance() && !data[data[i].getParent()].getExistance() && !data[i].hasSpeciated())
               {
                   loop = true;
                   data[data[i].getParent()].setExistance(true);
               }
           }
       }
       unsigned long iSpecies = 0;
       for(unsigned int i = 0; i <= enddata; i++)
       {
           if(data[i].getExistance() && data[i].hasSpeciated())
           {
               iSpecies++;
           }
       }
       for(unsigned int i = 0; i <= enddata; i++)
       {
           data[i].qReset();
       }
       //      os << "Estimated species number is: " << iSpecies << endl;
       return iSpecies;
   }
   
   void Tree::runChecks(const unsigned long& chosen, const unsigned long& coalchosen)
   {
   // final checks
   #ifdef pristine_mode
       if(active[chosen].getListpos() > grid[active[chosen].getYpos()][active[chosen].getXpos()].getMaxsize() &&
          active[chosen].getNwrap() == 0)
       {
           //              usleep(1);
           cerr << "listpos: " << active[chosen].getListpos()
                << " maxsize: " << grid[active[chosen].getYpos()][active[chosen].getXpos()].getMaxsize() << endl;
           throw Fatal_Exception("ERROR_MOVE_001: Listpos outside maxsize.");
       }
   
       if(active[coalchosen].getListpos() >
              grid[active[coalchosen].getYpos()][active[coalchosen].getXpos()].getMaxsize() &&
          active[coalchosen].getNwrap() == 0 && coalchosen != 0)
       {
           //              usleep(1);
           throw Fatal_Exception("ERROR_MOVE_002: Coalchosen listpos outside maxsize.");
       }
   #endif
       if(active[chosen].getNwrap() != 0)
       {
           unsigned long tmpactive = grid[active[chosen].getYpos()][active[chosen].getXpos()].getNext();
           unsigned long lastactive = 0;
           for(unsigned long i = 1; i < active[chosen].getNwrap(); i++)
           {
               lastactive = tmpactive;
               tmpactive = active[tmpactive].getNext();
           }
           if(tmpactive != chosen)
           {
               cerr << "nwrap: " << active[chosen].getNwrap() << endl;
               cerr << "gridnwrap: " << grid[active[chosen].getYpos()][active[chosen].getXpos()].getNwrap()
                    << endl;
               cerr << "chosen: " << chosen << endl;
               cerr << "active x,y" << active[chosen].getXpos() << "," << active[chosen].getYpos() << endl;
               cerr << "wrap x,y: " << active[chosen].getXwrap() << "," << active[chosen].getYwrap() << endl;
               cerr << "tmpactive: " << tmpactive << " chosen: " << chosen
                    << " chosennext: " << active[chosen].getNext() << "lastactive: " << lastactive << endl;
               throw Fatal_Exception("ERROR_MOVE_003: Nwrap not set correctly.");
           }
       }
   
       if(active[chosen].getNwrap() != 0)
       {
           if(active[chosen].getXwrap() == 0 && active[chosen].getYwrap() == 0)
           {
               throw Fatal_Exception("ERROR_MOVE_10: Nwrap set to non-zero, but x and y wrap 0.");
           }
       }
       if(active[endactive].getNwrap() != 0)
       {
           unsigned long nwrap = active[endactive].getNwrap();
           if(nwrap == 1)
           {
               if(grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext() != endactive)
               {
                   cerr << "Lineage at 1st position: "
                        << grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext() << endl;
                   cerr << "endactive: " << endactive << endl
                        << "nwrap: " << nwrap << endl
                        << "x,y: " << active[endactive].getXpos() << "," << active[endactive].getYpos()
                        << endl;
                   cerr << "chosen: " << chosen << endl;
                   throw Fatal_Exception("ERROR_MOVE_016: Nwrap for endactive not set correctly. Nwrap is 1, "
                                         "but the lineage at 1st position is not endactive.");
               }
           }
           else
           {
               unsigned long tmpcheck = grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext();
               unsigned long tmpnwrap = 1;
               while(tmpcheck != endactive)
               {
                   tmpnwrap++;
                   tmpcheck = active[tmpcheck].getNext();
                   if(tmpnwrap > nwrap + 1)
                   {
                       cerr << "ERROR_MOVE_017: NON FATAL. Nrap for endactive not set correctly; looped "
                               "beyond nwrap and not yet found enactive."
                            << endl;
                       cerr << "endactive: " << endactive << endl
                            << "nwrap: " << nwrap << endl
                            << "x,y: " << active[endactive].getXpos() << "," << active[endactive].getYpos()
                            << endl;
                       cerr << "chosen: " << chosen << endl;
                   }
               }
               if(tmpnwrap != nwrap)
               {
                   cerr << "ERROR_MOVE_018: NON FATAL. Nwrap for endactive not set correctly. Nwrap is "
                        << nwrap << " but endactive is at position " << tmpnwrap << endl;
                   cerr << "endactive: " << endactive << endl
                        << "nwrap: " << nwrap << endl
                        << "x,y: " << active[endactive].getXpos() << "," << active[endactive].getYpos()
                        << endl;
                   cerr << "chosen: " << chosen << endl;
               }
           }
       }
   }
   
   void Tree::validationCheck(const unsigned long& chosen, int o, const unsigned long& current, const bool& coal)
   {
       // if(active[chosen].getNwrap()!=0||chosen>endactive)
       //{
       //  return;
       //}
       //      os << "check..." << endl;
       stringstream os;
       if(active[chosen].getListpos() > grid[active[chosen].getYpos()][active[chosen].getXpos()].getMaxsize() &&
          active[chosen].getNwrap() == 0)
       {
           //              usleep(1);
           os << "listpos: " << active[chosen].getListpos()
              << " maxsize: " << grid[active[chosen].getYpos()][active[chosen].getXpos()].getMaxsize() << endl;
           os << "VALIDATION_001: Listpos outside maxsize." << endl;
           write_cout(os.str());
           throw Fatal_Exception("VALIDATION_001: Listpos outside maxsize.");
       }
       if(!coal && !data[active[chosen].getMpos()].hasSpeciated() && active[chosen].getNwrap() == 0 &&
          chosen != grid[active[chosen].getYpos()][active[chosen].getXpos()].getSpecies(active[chosen].getListpos()))
       {
           os << "nwrap: " << active[chosen].getNwrap() << endl;
           os << "gridnwrap: " << grid[active[chosen].getYpos()][active[chosen].getXpos()].getNwrap() << endl;
           os << "chosen: " << chosen << endl;
           os << "active x,y: " << active[chosen].getXpos() << "," << active[chosen].getYpos() << endl;
           os << "wrap x,y: " << active[chosen].getXwrap() << "," << active[chosen].getYwrap() << endl;
           os << " chosen: " << chosen << " chosennext: " << active[chosen].getNext() << endl;
           os << "listpos: " << active[chosen].getListpos() << endl;
           os << "lineage at pos " << active[chosen].getListpos() << ": "
              << grid[active[chosen].getYpos()][active[chosen].getXpos()].getSpecies(active[chosen].getListpos())
              << endl;
           os << "o: " << o << endl;
           os << "current chosen: " << current << endl;
           write_cout(os.str());
           throw Fatal_Exception("VALIDATION_003: Listpos not set correctly.");
       }
       if(active[chosen].getNwrap() != 0)
       {
           //              os << "nwrap1: " << active[chosen].getNwrap() << endl;
           unsigned long tmpactive = grid[active[chosen].getYpos()][active[chosen].getXpos()].getNext();
           unsigned long lastactive = 0;
           for(unsigned long i = 1; i < active[chosen].getNwrap(); i++)
           {
               lastactive = tmpactive;
               tmpactive = active[tmpactive].getNext();
           }
           if(tmpactive != chosen)
           {
               os << "nwrap: " << active[chosen].getNwrap() << endl;
               os << "gridnwrap: " << grid[active[chosen].getYpos()][active[chosen].getXpos()].getNwrap() << endl;
               //              os << "speccounter: " << spec_counter << endl;
               //              os << "startnwrap: " << startnwrap << endl;
               os << "chosen: " << chosen << endl;
               //              os << "start x,y: " << startx << "," << starty << endl;
               //              os << "end x,y: " << oldx << "," << oldy << endl;
               os << "active x,y: " << active[chosen].getXpos() << "," << active[chosen].getYpos() << endl;
               os << "wrap x,y: " << active[chosen].getXwrap() << "," << active[chosen].getYwrap() << endl;
               os << "tmpactive: " << tmpactive << " chosen: " << chosen
                  << " chosennext: " << active[chosen].getNext() << "lastactive: " << lastactive << endl;
               os << "VALIDATION_002: Nwrap not set correctly." << endl;
               os << "o: " << o << endl;
               os << "current chosen: " << current << endl;
               write_cout(os.str());
               throw Fatal_Exception("VALIDATION_001: Listpos outside maxsize.");
           }
       }
   }
   
   void Tree::checkSimSize(unsigned long req_data, unsigned long req_active)
   {
       //      os << "Started change size" << endl;
       // need to be triple the size of the maximum number of individuals plus enddata
       unsigned long min_data = (3 * req_data) + enddata + 2;
       unsigned long min_active = endactive + req_active + 2;
       if(data.size() <= min_data)
       {
           // change the size of data
           data.changeSize(min_data);
       }
   
       if(active.size() <= min_active)
       {
           // change the size of active.
           active.changeSize(min_active);
       }
       //      os << "finished change size" << endl;
   }
   
   void Tree::writeSimStartToConsole()
   {
       // now do the calculations required to build the tree
       stringstream os;
       os << "*************************************************" << endl;
       os << "Beginning simulations..." << flush;
       write_cout(os.str());
       os.str("");
   
       //      double current_gen =0;
       // check time
       time(&sim_start);
       time(&sim_end);
       time(&now);
   }
   
   void Tree::setSimStartVariables()
   {
       this_step.bContinueSim = true;
       this_step.iAutoComplete = 0;
       if(bAutocorrel && generation > 0.0)
       {
           for(unsigned int i = 0; i < autocorrel_times.size(); i++)
           {
               if(autocorrel_times[i] > generation)
               {
                   this_step.iAutoComplete = i + 1;
                   break;
               }
           }
       }
   }
   
   #ifdef verbose
   void Tree::writeStepToConsole()
   {
       if(steps % 10000 == 0)
       {
           time(&sim_end);
           if(sim_end - now > 0.2 && log_all)  // output every 0.2 seconds
           {
               double dPercentComplete = 20 * (1 - (double(endactive) / double(startendactive)));
               time(&now);
               if(this_step.number_printed < dPercentComplete)
               {
                   stringstream os;
                   os << "\rBeginning simulations...";
                   this_step.number_printed = 0;
                   while(this_step.number_printed < dPercentComplete)
                   {
                       os << ".";
   
                       this_step.number_printed++;
                   }
                   os << flush;
                   //                  cout << os.str() << endl;
                   write_cout(os.str());
               }
           }
       }
   #ifdef DEBUG
       logfile << "STEP " << steps << endl;
       logfile << "chosen: " << this_step.chosen << endl;
       logfile << "STARTPOS: " << this_step.oldx << ", " << this_step.oldy << endl;
   #endif
   }
   #endif
   
   #ifdef pristine_mode
   void Tree::pristineStepChecks()
   {
       if(forestmap.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap, this_step.oldywrap, generation) == 0)
       {
           cerr << "x,y: " << this_step.oldx << "," << this_step.oldy << " xwrap, ywrap: " << this_step.oldxwrap;
           cerr << "," << this_step.oldywrap << endl;
           cerr << "listsize: " << grid[this_step.oldy][this_step.oldx].getListsize()
                << "maxsize: " << grid[this_step.oldy][this_step.oldx].getMaxsize() << endl;
           throw Fatal_Exception(
               string("ERROR_MOVE_008: Dispersal attempted from non-forest. Check dispersal function. Forest "
                      "cover: " +
                      to_string((long long)forestmap.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap,
                                                            this_step.oldywrap, generation))));
       }
   }
   
   #endif
   
   void Tree::checkMapUpdate()
   {
       if(bAutocorrel && this_step.iAutoComplete < autocorrel_times.size())
       {
           // check if we need to update
           if(autocorrel_times[this_step.iAutoComplete] <= generation)
           {
               //                  os << "check2" << endl;
               if(autocorrel_times[this_step.iAutoComplete] > 0.0)
               {
                   stringstream os;
                   os << "\n" << "expanding map at generation " << generation << endl;
                   expandMap(autocorrel_times[this_step.iAutoComplete]);
                   write_cout(os.str());
               }
               this_step.iAutoComplete++;
           }
       }
   }
   
   void Tree::chooseRandomLineage()
   {
       steps++;
       // increment generation counter
       generation += 2.0 / (double(endactive));
       forestmap.updateMap(generation);
       checkMapUpdate();
       // check if the map is pristine yet
       forestmap.checkPristine(generation);
       // choose a random lineage to die and be reborn out of those currently active
       this_step.chosen = NR.i0(endactive - 1) + 1;  // cannot be 0
       // Rejection sample based on reproductive potential
       while(!rep_map.hasReproduced(NR, active[this_step.chosen].getXpos(), active[this_step.chosen].getYpos(),
                                    active[this_step.chosen].getXwrap(), active[this_step.chosen].getYwrap()))
       {
           this_step.chosen = NR.i0(endactive - 1) + 1;  // cannot be 0
       }
       this_step.coalchosen = 0;
       // record old position of lineage
       this_step.oldx = active[this_step.chosen].getXpos();
       this_step.oldy = active[this_step.chosen].getYpos();
       this_step.oldxwrap = active[this_step.chosen].getXwrap();
       this_step.oldywrap = active[this_step.chosen].getYwrap();
       this_step.coal = false;
   }
   
   #ifdef DEBUG
   void Tree::debugCoalescence()
   {
       logfile << "COALESCENCE" << endl;
       this_step.location = "coalescence: coalchosen - " + to_string(this_step.coalchosen);
       if(active[this_step.coalchosen].getXpos() != active[this_step.chosen].getXpos() ||
          active[this_step.coalchosen].getYpos() != active[this_step.chosen].getYpos() ||
          active[this_step.coalchosen].getXwrap() != active[this_step.chosen].getXwrap() ||
          active[this_step.coalchosen].getYwrap() != active[this_step.chosen].getYwrap())
       {
           cerr << this_step.chosen << "," << this_step.coalchosen << endl;
           cerr << "chosen - x,y: " << active[this_step.chosen].getXpos() << "," << active[this_step.chosen].getYpos()
                << endl
                << "x, y wrap: " << active[this_step.chosen].getXwrap();
           cerr << "," << active[this_step.chosen].getYwrap() << endl;
           cerr << "coalchosen - x,y:" << active[this_step.coalchosen].getXpos() << ","
                << active[this_step.coalchosen].getYpos() << endl;
           cerr << " x,y wrap: " << active[this_step.coalchosen].getXwrap() << ","
                << active[this_step.coalchosen].getYwrap() << endl;
           throw Fatal_Exception("ERROR_MOVE_006: NON FATAL. Nwrap not set "
                                 "correctly. Check move programming "
                                 "function.");
       }
       if(active[this_step.coalchosen].getXpos() != (unsigned long)this_step.oldx ||
          active[this_step.coalchosen].getYpos() != (unsigned long)this_step.oldy ||
          active[this_step.coalchosen].getXwrap() != this_step.oldxwrap ||
          active[this_step.coalchosen].getYwrap() != this_step.oldywrap)
       {
           cerr << this_step.chosen << "," << this_step.coalchosen << endl;
           cerr << "chosen - x,y: " << this_step.oldx << "," << this_step.oldy << endl
                << "x, y wrap: " << this_step.oldxwrap << "," << this_step.oldywrap << endl;
           cerr << "coalchosen - x,y:" << active[this_step.coalchosen].getXpos() << ","
                << active[this_step.coalchosen].getYpos() << endl;
           cerr << " x,y wrap: " << active[this_step.coalchosen].getXwrap() << ","
                << active[this_step.coalchosen].getYwrap() << endl;
           throw Fatal_Exception("ERROR_MOVE_006: NON FATAL. Nwrap not set "
                                 "correctly. Check move programming "
                                 "function.");
       }
   }
   
   void Tree::debugDispersal()
   {
       if(forestmap.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap, this_step.oldywrap, generation) == 0)
       {
           throw Fatal_Exception(
               string("ERROR_MOVE_007: Dispersal attempted to non-forest. "
                      "Check dispersal function. Forest cover: " +
                      to_string((long long)forestmap.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap,
                                                            this_step.oldywrap, generation))));
       }
   }
   
   void Tree::debugEndStep()
   {
       logfile << "ENDPOS: " << active[this_step.chosen].getXpos() << ", " << active[this_step.chosen].getYpos() << endl;
       logfile << "mpos: " << active[this_step.chosen].getMpos() << endl;
       try
       {
           validationCheck(this_step.chosen, 112, this_step.chosen, this_step.coal);  // this can probably be removed now
       }
       catch(Fatal_Exception& fe)
       {
           cerr << fe.what() << endl;
           cerr << "Location tag: " << this_step.location << endl;
           throw Fatal_Exception();
       }
       try
       {
           runChecks(this_step.chosen, this_step.coalchosen);
           // runs the debug every 10,000 time steps
           if(steps % 10000 == 0)
           {
               for(int i = 0; i <= endactive; i++)
               {
                   runChecks(i, i);
               }
           }
       }
       catch(Fatal_Exception& fe)
       {
           cerr << fe.what() << endl;
           cerr << "dumping data file..." << endl;
           sqlCreate();
   #ifdef sql_ram
           sqlOutput();
   #endif
           cerr << "done!" << endl;
       }
   }
   #endif
   
   bool Tree::runSimulation()
   {
       writeSimStartToConsole();
   
   #ifdef DEBUG
       string file_to_open = outdirectory + "/Logfile_" + to_string(the_task) + "_" + to_string(the_seed) + ".log";
       logfile.open(file_to_open.c_str());
   #endif
       // Main while loop to process while there is still time left and the simulation is not complete.
       // Ensure that the step object contains no data.
       this_step.wipeData();
       // Create the move object
       do
       {
           chooseRandomLineage();
   #ifdef verbose
           writeStepToConsole();
   #endif
   #ifdef pristine_mode
           pristineStepChecks();
   #endif
           // See estSpecnum for removed code.
           // Check that we still want to continue the simulation.
           if(this_step.bContinueSim)
           {
               // os << "check1" << endl;
               this_step.coal = false;
               // increase the counter of the number of moves (or generations) the lineage has undergone.
               data[active[this_step.chosen].getMpos()].increaseGen();
               // Check if speciation happens
               if(checkSpeciation(data[active[this_step.chosen].getMpos()].getSpecRate(), 0.99999*spec,
                                  data[active[this_step.chosen].getMpos()].getGenRate()))
               {
                   speciation(this_step.chosen);
               }
               else
               {
   #ifdef DEBUG
                   this_step.location = "standard: oldpos " + to_string(this_step.oldx) + to_string(this_step.oldy);
   #endif
                   // remove the species data from the species list to be placed somewhere new.
                   removeOldPos(this_step.chosen);
                   calcMove(this_step);
                   // Calculate the new position, perform the move if coalescence doesn't occur or
                   // return the variables for the coalescence event if coalescence does occur.
                   active[this_step.chosen].setEndpoint(this_step.oldx, this_step.oldy,
                                                        this_step.oldxwrap,
                                                        this_step.oldywrap);  // the "old" variables
                   // have been updated, so we can just input them back in to the function.
                   calcNewPos(this_step.coal, this_step.chosen, this_step.coalchosen, this_step.oldx,
                              this_step.oldy, this_step.oldxwrap, this_step.oldywrap);
                   // coalescence occured, so we need to adjust the data appropriatedly
                   if(this_step.coal)
                   {
   #ifdef DEBUG
                       // This is only required if we are running in debug mode.
                       debugCoalescence();
   #endif
                       coalescenceEvent(this_step.chosen, this_step.coalchosen);
                   }
   #ifdef DEBUG
                   else  // debugging only now as the move process has been incorportated into
                   {
                       // for debugging only
                       debugDispersal();
                   }
   #endif
               }
           }
   
   
   #ifdef DEBUG
           debugEndStep();
   #endif
           if(bAutocorrel && endactive == 1)
           {
               // Check whether we need to continue simulating at a later time.
               if(autocorrel_times[this_step.iAutoComplete] > generation)
               {
                   // Then we need to expand the map
                   // This is a hack, I know it's a hack and is wrong, and I aint gonna change it :)
                   data[active[endactive].getMpos()].setSpec(0.0);
                   // First speciate the remaining lineage
                   speciation(endactive);
                   generation = autocorrel_times[this_step.iAutoComplete] + 0.000000000001;
                   checkMapUpdate();
                   if(endactive < 2)
                   {
                       break;
                   }
               }
               // TODO fix this to account for potential speciation of the remaining lineage!
           }
       }
       while(steps < 100 || ((endactive > 1) && (difftime(sim_end, start) < maxtime) && this_step.bContinueSim));
   // If the simulations finish correctly, output the completed data.
   // Otherwise, pause the simulation and save objects to file.
   #ifdef DEBUG
       logfile.close();
   #endif
       
       return stopSimulation();
   }
   
   bool Tree::stopSimulation()
   {
       if(endactive > 1)
       {
           stringstream os;
           time(&sim_finish);
           time_taken += sim_finish - start;
           os.str("");
           os << "........out of time!" << endl;
           //          os << "Time taken: " << time_taken << endl;
           os << "Pausing simulation: add extra time or re-run to ensure simulation completion."
              << "\n";
           os << "Lineages remaining: " << endactive << "\n";
           write_cout(os.str());
           simPause();
           return false;
       }
       else
       {
           for(unsigned int i = 0; i <= endactive; i++)
           {
               data[active[i].getMpos()].speciate();
               data[active[i].getMpos()].setSpec(0);
           }
           sim_complete = true;
           time(&sim_finish);
           time_taken += sim_finish - start;
           if(!this_step.bContinueSim)
           {
               write_cout("done - desired number of species achieved!\n");
               return true;
           }
           else
           {
               write_cout("done!\n");
               return true;
           }
       }
   }
   
   void Tree::expandMap(double generationin)
   {
       // First loop over the grid to check for the number that needs to be added to active
       unsigned long added_active = 0;
       unsigned long added_data = 0;
       for(unsigned long i = 0; i < sim_parameters.varsamplexsize; i++)
       {
           for(unsigned long j = 0; j < sim_parameters.varsampleysize; j++)
           {
               long x, y;
               x = i;
               y = j;
               long xwrap, ywrap;
               xwrap = 0;
               ywrap = 0;
               samplegrid.recalculate_coordinates(x, y, xwrap, ywrap);
               if(samplegrid.getVal(x, y, xwrap, ywrap))
               {
                   unsigned long num_to_add = countCellExpansion(x, y, xwrap, ywrap, generationin, false);
                   added_data += (unsigned long)(deme_sample *
                           double(forestmap.getVal(x, y, xwrap, ywrap, generationin))) - num_to_add;
                   added_active += num_to_add;
               }
           }
       }
       added_data += added_active;
       // now resize data and active if necessary
       checkSimSize(added_data, added_active);
       // Add the new lineages and modify the existing lineages within our sample area
       for(unsigned long i = 0; i < sim_parameters.varsamplexsize; i++)
       {
           for(unsigned long j = 0; j < sim_parameters.varsampleysize; j++)
           {
               long x, y;
               x = i;
               y = j;
               long xwrap, ywrap;
               xwrap = 0;
               ywrap = 0;
               samplegrid.recalculate_coordinates(x, y, xwrap, ywrap);
               if(samplegrid.getVal(x, y, xwrap, ywrap))
               {
                   // Count the number of new cells that we need to add (after making those that already exist into tips)
                   // Note that this function won't make more tips than the proportion we are sampling
                   unsigned long num_to_add = countCellExpansion(x, y, xwrap, ywrap, generationin, true);
                   expandCell(x, y, xwrap, ywrap, generationin, num_to_add);
               }
           }
       }
       // double check sizes
       if(enddata >= data.size() || endactive >= active.size())
       {
           throw Fatal_Exception("ERROR_MAIN_012: FATAL. Enddata or endactive is greater than the size of the "
                                 "relevant object. Programming error likely.");
       }
       if(endactive > startendactive)
       {
           startendactive = endactive;
       }
   #ifdef DEBUG
       validateLineages();
   #endif
   }
   
   unsigned long Tree::sortData()
   {
       // Sort and process the species list so that the useful information can be extracted from it.
       stringstream os;
       os << "Finalising data..." << flush;
       write_cout(os.str());
       os.str("");
       // coalescence finished - process speciation
       // check the data structure
       if(enddata > data.size())
       {
           cerr << "enddata: " << enddata << endl;
           cerr << "data.size(): " << data.size() << endl;
           throw Fatal_Exception("Enddata greater than data size. Programming error likely.");
       }
       // Now make sure those left in endactive will definitely speciate.
       for(unsigned int i = 1; i <= endactive; i++)
       {
           // check
           data[active[i].getMpos()].setSpec(0.0);
       }
       // Double check speciation events have been counted.
       unsigned long spec_up_to = 0;
       for(unsigned int i = 1; i <= enddata; i++)
       {
           if(checkSpeciation(data[i].getSpecRate(), spec, data[i].getGenRate()))
           {
               spec_up_to++;
               data[i].speciate();
           }
       }
       // os << "Precount1: " << lineages.countSpecies() << endl;
       // lineages.resetTree();
       // Calculates the lineage data for the minimum speciation rate. // removed this process as output data is not
       // required to be as a calculated tree.
       // unsigned long spec_up_to = 1;
       // disabled checks...
       // here we check the data is valid - only required for debugging
       try
       {
           for(unsigned long i = 1; i <= enddata; i++)
           {
               if((!(data[i].hasSpeciated())) && (data[i].getParent() == 0 && data[i].getExistance()))
               {
                   throw Main_Exception(string("ERROR_MAIN_004: " + to_string((long long)i) +
                                               " has not speciated and parent is 0."));
               }
               if(data[i].isTip() && !samplegrid.getVal(data[i].getXpos(), data[i].getYpos(), data[i].getXwrap(),
                                                        data[i].getYwrap()))
               {
                   cerr << "ERROR_MAIN_014: Tip assignment error. Samplemask is not correctly assigning tips. "
                           "Check samplemask programming."
                        << endl;
               }
           }
   
           // here we check the data is valid - alternative validity check.
           for(unsigned long i = 1; i <= enddata; i++)
           {
               if(!(data[i].hasSpeciated()) && data[i].getExistance())
               {
                   long j = i;
                   while(!(data[j].hasSpeciated()))
                   {
                       j = data[j].getParent();
                       if(j == 0)
                       {
                           throw Main_Exception(
                               "ERROR_MAIN_005:0 found in parent while following speciation trail.");
                           // string james;
                           // cin >> james;
                       }
                   }
               }
           }
       }
       catch(Main_Exception& me)
       {
           cerr << me.what() << endl;
           cerr << "Returning max possible size (may cause RAM issues)." << endl;
           return data.size();
       }
       write_cout("done!\n");
       return spec_up_to;
   }
   
   void Tree::outputData()
   {
       unsigned long species_richness = sortData();
       outputData(species_richness);
       return;
   }
   
   void Tree::outputData(unsigned long species_richness)
   {
       // Run the data sorting functions and output the data into the correct format.
       // sort the data
       //          bool loopon;
       // Write the data to the first file
       // species richness data
       stringstream os;
       os << "Writing results to file..." << flush;
       ofstream out;
       out.precision(10);
       string filename_ab;
       // sprintf (filename_ab, "%s/Data_%i.csv",outdirectory, int(the_task)); // altered in v3.0
       filename_ab = outdirectory + string("/Data_") + to_string((long long)the_task) + "_" +
                     to_string((long long)the_seed) + string(".csv");
       out.open(filename_ab);
       // Simulation fixed variables
       out << "random_seed=," << the_seed << "\n";
       out << "fine map=," << finemapinput << "\n";
       out << "fine map x y," << finemapxsize << " - " << finemapysize << "\n";
       out << "coarse map=," << coarsemapinput << "\n";
       out << "coarse map x y," << coarsemapxsize * deme << " - " << coarsemapysize * deme << "\n";
       out << "deme=," << deme << "\n";
       out << "deme_sample=," << deme_sample << "\n";
       out << "spec=," << spec << "\n";
       out << "sigma=," << sigma << "\n";
       out << "maxtime=," << maxtime << "\n\n";
       out << "species_richness=," << species_richness << "\n\n";
       out.close();
       os << "done!              " << endl;
       write_cout(os.str());
       time(&out_finish);
   #ifdef sql_ram
       sqlOutput();
   #endif
       time(&sim_end);
       writeTimes();
   }
   
   void Tree::writeTimes()
   {
       stringstream os;
       os << "Total generations simulated (steps): " << generation << " (" << steps << ")" << endl;
   #ifdef DEBUG
       os << "Count dispersal, density fails: " << count_dispersal_fails << ", " << count_density_fails << endl;
   #endif
       os << "Setup time was " << floor((sim_start - start) / 60) << " minutes " << (sim_start - start) % 60 << " seconds"
          << endl;
       os << "Simulation time was " << floor((sim_finish - sim_start) / 3600) << " hours "
          << (floor((sim_finish - sim_start) / 60) - 60 * floor((sim_finish - sim_start) / 3600)) << " minutes "
          << (sim_finish - sim_start) % 60 << " seconds" << endl;
       os << "File output and species calculation time was " << floor((out_finish - sim_finish) / 60) << " minutes "
          << (out_finish - sim_finish) % 60 << " seconds" << endl;
       os << "SQL output time was " << floor((sim_end - out_finish) / 60) << " minutes " << (sim_end - out_finish) % 60
          << " seconds" << endl;
       time_taken += (sim_end - out_finish);
       os << "Total time taken was " << floor((time_taken) / 3600) << " hours " << flush;
       os << (floor((time_taken) / 60) - 60 * floor((time_taken) / 3600)) << flush;
       os << " minutes " << (time_taken) % 60 << " seconds" << endl;
       write_cout(os.str());
   }
   
   void Tree::setProtractedVariables(double speciation_gen_min, double speciation_gen_max)
   {
       return;
   }
   
   
   string Tree::getProtractedVariables()
   {
       stringstream ss;
       ss << "0.0\n0.0\n";
       return ss.str();
   }
   
   double Tree::getProtractedGenerationMin()
   {
       return 0.0;
   }
   
   double Tree::getProtractedGenerationMax()
   {
       return 0.0;
   }
   
   void Tree::simPause()
   {
       // Completely changed how this sections works - it won't currently allow restarting of the simulations, but will
       // dump the data file to memory. - simply calls sqlCreate and sqlOutput.
       // sqlCreate();
       // sqlOutput();
   
       // This function saves the data to 4 files. One contains the main simulation parameters, the other 3 contain the
       // simulation results thus far
       // including the grid object, data object and active object.
       stringstream os;
       os << "Pausing simulation..." << endl << "Saving data to temp file in " << outdirectory << "/Pause/ ..." << flush;
       write_cout(os.str());
       os.str("");
       ofstream out;
       out.precision(64);
       string file_to_open;
       // Create the pause directory
       string pause_folder = outdirectory + "/Pause/";
       boost::filesystem::path pause_dir(pause_folder);
       if(!boost::filesystem::exists(pause_dir))
       {
           try
           {
               boost::filesystem::create_directory(pause_dir);
           }
           catch(exception& e)
           {
               cerr << "Failure to create " << outdirectory << "/Pause/"
                    << "." << endl;
               cerr << e.what() << endl;
               cerr << "Writing directly to output directory." << endl;
               pause_folder = outdirectory;
           }
       }
       try
       {
           file_to_open = pause_folder + "Dump_main_" + to_string(the_task) + "_" + to_string(the_seed) + ".csv";
           out.open(file_to_open.c_str());
           out << setprecision(64);
           // Save that this simulation was not a protracted speciation sim
           out << bIsProtracted << "\n";
           // Saving the initial data to one file.
           out << enddata << "\n" << seeded << "\n" << the_seed << "\n" << the_task << "\n" << autocorrel_file << "\n"
               << bAutocorrel << "\n";
           out << finemapinput << "\n" << coarsemapinput << "\n" << outdirectory << "\n" << pristinefinemapinput
               << "\n" << pristinecoarsemapinput << "\n";
           out << dPristine << "\n" << dForestTransform << "\n" << gridxsize << "\n" << gridysize << "\n"
               << finemapxsize << "\n" << finemapysize << "\n";
           out << finemapxoffset << "\n" << finemapyoffset << "\n" << coarsemapxsize << "\n" << coarsemapysize << "\n"
               << coarsemapxoffset << "\n";
           out << coarsemapyoffset << "\n" << coarsemapscale << "\n" << varimport << "\n" << start << "\n" << sim_start
               << "\n" << sim_end << "\n" << now << "\n";
           out << time_taken << "\n" << sim_finish << "\n" << out_finish << "\n" << endactive << "\n" << startendactive
               << "\n" << maxsimsize << "\n" << steps << "\n";
           out << generation << "\n" << sigma << "\n" << tau << "\n" << maxtime << "\n" << deme_sample << "\n" << spec
               << "\n" << dispersal_relative_cost << "\n" << deme << "\n";
           out << desired_specnum << "\n" << sqloutname << "\n" << NR << "\n" << sim_parameters << "\n";
           // now output the protracted speciation variables (there should be two of these).
           out << getProtractedVariables();
           out << rep_map;
           out.close();
       }
       catch(exception& e)
       {
           cerr << e.what() << endl;
           cerr << "Failed to perform main dump to " << pause_folder << endl;
       }
       // This part is no longer required (for saving of disk space)
       //  try
       //  {
       //      // Saving the larger data in single files for simpler reading in.
       //      // Output the grid object
       //      ofstream out2;
       //      file_to_open = pause_folder + "Dump_grid_" + to_string(the_task) + "_" + to_string(the_seed) + ".csv";
       //      out2 << setprecision(64);
       //      out2.open(file_to_open.c_str());
       //      out2 << grid;
       //      out2.close();
       //  }
       //  catch(exception& e)
       //  {
       //      cerr << e.what() << endl;
       //      cerr << "Failed to perform grid dump to " << pause_folder << endl;
       //  }
       try
       {
           // Output the active object
           ofstream out3;
           file_to_open = pause_folder + "Dump_active_" + to_string(the_task) + "_" + to_string(the_seed) + ".csv";
           out3 << setprecision(64);
           out3.open(file_to_open.c_str());
           out3 << active;
           out3.close();
       }
       catch(exception& e)
       {
           cerr << e.what() << endl;
           cerr << "Failed to perform active dump to " << pause_folder << endl;
       }
       try
       {
           // Output the data object
           ofstream out4;
           file_to_open = pause_folder + "Dump_data_" + to_string(the_task) + "_" + to_string(the_seed) + ".csv";
           out4 << setprecision(64);
           out4.open(file_to_open.c_str());
           out4 << data;
           out4.close();
       }
       catch(exception& e)
       {
           cerr << e.what() << endl;
           cerr << "Failed to perform data dump to " << pause_folder << endl;
       }
       try
       {
           // Output the data object
           ofstream out4;
           file_to_open = pause_folder + "Dump_map_" + to_string(the_task) + "_" + to_string(the_seed) + ".csv";
           out4 << setprecision(64);
           out4.open(file_to_open.c_str());
           out4 << forestmap;
           out4.close();
       }
       catch(exception& e)
       {
           cerr << e.what() << endl;
           cerr << "Failed to perform map dump to " << pause_folder << endl;
       }
       os << "done!" << endl;
       os << "SQL dump started" << endl;
       write_cout(os.str());
       os.str("");
       time(&out_finish);
       sqlCreate();
   #ifdef sql_ram
       sqlOutput();
   #endif
       os << "Data dump complete" << endl;
       write_cout(os.str());
       time(&sim_end);
       writeTimes();
   }
   
   void Tree::setResumeParameters()
   {
       if(!bPausedImport)
       {
           pause_sim_directory = outdirectory;
           bPausedImport = true;
       }
   }
   
   void Tree::setResumeParameters(
       string pausedir, string outdir, unsigned long seed, unsigned long task, unsigned long new_max_time)
   {
       if(!bPausedImport)
       {
           pause_sim_directory = move(pausedir);
           outdirectory = move(outdir);
           the_seed = static_cast<long long int>(seed);
           the_task = static_cast<long long int>(task);
           maxtime = new_max_time;
           bPausedImport = true;
       }
   }
   
   void Tree::loadMainSave()
   {
       string file_to_open;
       try
       {
           stringstream os;
           os << "\rLoading data from temp file...main..." << flush;
           write_cout(os.str());
           os.str("");
           ifstream in1;
           file_to_open = pause_sim_directory + string("/Pause/Dump_main_") + to_string(the_task) + "_" +
                          to_string(the_seed) + string(".csv");
           //      os << file_to_open << endl;
           in1.open(file_to_open);
           // Reading the initial data
           string string1;
           // First read our boolean which just determines whether the simulation is a protracted simulation or not.
           // For these simulations, it should not be.
           bool tmp;
           in1 >> tmp;
           if(tmp != bIsProtracted)
           {
               if(bIsProtracted)
               {
                   throw Fatal_Exception("Paused simulated is not a protracted speciation simulation. "
                                     "Cannot be resumed by this program. Please report this bug");
               }
               else
               {
                   throw Fatal_Exception("Paused simulated is a protracted speciation simulation. "
                                         "Cannot be resumed by this program. Please report this bug");
               }
           }
           in1 >> enddata >> seeded >> the_seed >> the_task;
           in1.ignore(); // Ignore the endline character
           getline(in1, autocorrel_file);
           in1 >> bAutocorrel;
           in1.ignore();
           getline(in1, finemapinput);
           getline(in1, coarsemapinput);
           getline(in1, string1);
           getline(in1, pristinefinemapinput);
           getline(in1, pristinecoarsemapinput);
   //      in1 >> finemapinput >> coarsemapinput >> string1 >> pristinefinemapinput >> pristinecoarsemapinput;
           in1 >> dPristine >> dForestTransform >> gridxsize >> gridysize >> finemapxsize >> finemapysize;
           in1 >> finemapxoffset >> finemapyoffset >> coarsemapxsize >> coarsemapysize >> coarsemapxoffset;
           time_t tmp_time;
           in1 >> coarsemapyoffset >> coarsemapscale >> varimport >> tmp_time >> sim_start >> sim_end >> now;
           //          os << "sim_start: " << sim_start << endl;
           in1 >> time_taken >> sim_finish >> out_finish >> endactive >> startendactive >> maxsimsize >> steps;
           unsigned long tempmaxtime = maxtime;
           in1 >> generation >> sigma >> tau >> maxtime;
           if(maxtime == 0)
           {
               maxtime = tempmaxtime;
           }
           in1 >> deme_sample >> spec >> dispersal_relative_cost >> deme;
           in1 >> desired_specnum;
           in1.ignore();
           getline(in1, sqloutname);
           in1 >> NR;
           in1.ignore();
           in1 >> sim_parameters;
           NR.setDispersalMethod(sim_parameters.dispersal_method, sim_parameters.m_prob, sim_parameters.cutoff);
           double tmp1, tmp2;
           in1 >> tmp1 >> tmp2;
           setProtractedVariables(tmp1, tmp2);
           in1 >> rep_map;
           in1.close();
           try
           {
               if(autocorrel_file == "null")
               {
                   if(bAutocorrel)
                   {
                       throw runtime_error("bAutocorrel should not be true");
                   }
               }
               else
               {
                   if(!bAutocorrel)
                   {
                       throw runtime_error("bAutocorrel should not be false");
                   }
                   vector<string> tmpimport;
                   ConfigOption tmpconfig;
                   tmpconfig.setConfig(autocorrel_file, false);
                   tmpconfig.importConfig(tmpimport);
                   for(unsigned int i = 0; i < tmpimport.size(); i++)
                   {
                       autocorrel_times.push_back(stod(tmpimport[i]));
                       //                  os << "t_i: " << autocorrel_times[i] << endl;
                   }
               }
           }
           catch(Config_Exception& ce)
           {
               cerr << ce.what() << endl;
           }
       }
       catch(exception& e)
       {
           string msg;
           msg = string(e.what()) + "Failure to import from " + file_to_open;
           throw Fatal_Exception(msg);
       }
   }
   
   void Tree::loadDataSave()
   {
       string file_to_open;
       // Input the data object
       try
       {
           stringstream os;
           os << "\rLoading data from temp file...data..." << flush;
           write_cout(os.str());
           ifstream in4;
           //      sprintf(file_to_open,"%s/Pause/Data_%i_data.csv",outdirectory,int(the_task));
           file_to_open = pause_sim_directory + string("/Pause/Dump_data_") + to_string(the_task) + "_" +
                          to_string(the_seed) + string(".csv");
           in4.open(file_to_open);
           in4 >> data;
           //          os << data[0] << endl;
           //          os << data[1] << endl;
           in4.close();
       }
       catch(exception& e)
       {
           string msg;
           msg = string(e.what()) + "Failure to import from " + file_to_open;
           throw Fatal_Exception(msg);
       }
   }
   
   void Tree::loadActiveSave()
   {
       string file_to_open;
       try
       {
           stringstream os;
           os << "\rLoading data from temp file...active..." << flush;
           write_cout(os.str());
           // Input the active object
           ifstream in3;
           file_to_open = pause_sim_directory + string("/Pause/Dump_active_") + to_string(the_task) + "_" +
                          to_string(the_seed) + string(".csv");
           in3.open(file_to_open);
           in3 >> active;
           in3.close();
       }
       catch(exception& e)
       {
           string msg;
           msg = string(e.what()) + "Failure to import from " + file_to_open;
           throw Fatal_Exception(msg);
       }
   }
   
   void Tree::loadGridSave()
   {
       string file_to_open;
       try
       {
           stringstream os;
           os << "\rLoading data from temp file...grid..." << flush;
           // New method for re-creating grid data from active lineages
           // First initialise the empty grid object
           write_cout(os.str());
           for(unsigned long i = 0; i < gridysize; i++)
           {
               for(unsigned long j = 0; j < gridxsize; j++)
               {
                   grid[i][j].initialise(forestmap.getVal(j, i, 0, 0, generation));
                   grid[i][j].fillList();
               }
           }
           // Now fill the grid object with lineages from active. Only need to loop once.
           for(unsigned long i = 1; i <= endactive; i++)
           {
               if(active[i].getXwrap() == 0 && active[i].getYwrap() == 0)
               {
                   grid[active[i].getYpos()][active[i].getXpos()].setSpeciesEmpty(active[i].getListpos(), i);
                   grid[active[i].getYpos()][active[i].getXpos()].increaseListSize();
               }
               else
               {
                   if(active[i].getNwrap() == 0)
                   {
                       throw runtime_error(
                           "Nwrap should not be 0 if x and y wrap are not 0. Programming error likely.");
                   }
                   if(active[i].getNwrap() == 1)
                   {
                       grid[active[i].getYpos()][active[i].getXpos()].setNext(i);
                   }
                   grid[active[i].getYpos()][active[i].getXpos()].increaseNwrap();
               }
           }
       }
       catch(exception& e)
       {
           string msg;
           msg = string(e.what()) + "Failure to import from " + file_to_open;
           throw Fatal_Exception(msg);
       }
   }
   
   void Tree::loadMapSave()
   {
       string file_to_open;
       // Input the map object
       try
       {
           stringstream os;
           os << "\rLoading data from temp file...map..." << flush;
           write_cout(os.str());
           ifstream in5;
           file_to_open = pause_sim_directory + string("/Pause/Dump_map_") + to_string(the_task) + "_" +
                          to_string(the_seed) + string(".csv");
           in5.open(file_to_open);
           in5 >> forestmap;
           //      forestmap.setPristine(false);
           //      forestmap.updateMap(generation); This has been removed, because I'm not sure about it
           in5.close();
       }
       catch(exception& e)
       {
           string msg;
           msg = string(e.what()) + "Failure to import from " + file_to_open;
           throw Fatal_Exception(msg);
       }
   }
   
   void Tree::simResume()
   {
       // Start the timer
       // Only resume the simulation if there is a simulation to resume from.
       if(!bPaused)
       {
           return;
       }
       time(&start);
       // Loads the data from the files into the relevant objects.
       stringstream os;
       os << "Resuming simulation..." << endl << "Loading data from temp file..." << flush;
       write_cout(os.str());
       os.str("");
       // now load the objects
       loadMainSave();
       loadMapSave();
       setObjectSizes();
       loadActiveSave();
       loadDataSave();
       loadGridSave();
       time(&sim_start);
       write_cout("\rLoading data from temp file...done!\n");
   }
   
   void Tree::sqlCreate()
   {
       time(&out_finish);
       stringstream os;
       os << "Creating SQL database file..." << endl;
       os << "    Checking for existing folders...." << flush;
       write_cout(os.str());
       os.str("");
       // Create the folder if it doesn't exist
       sqloutname = outdirectory;
       string sqlfolder = outdirectory + "/SQL_data/";
       try
       {
           boost::filesystem::path dir(sqlfolder);
           if(!boost::filesystem::exists(dir))
           {
               os << "\r    SQL_data folder not found....creating..." << flush;
               if(boost::filesystem::create_directory(sqlfolder))
               {
                   os << "\r    SQL_data folder created successfully                             " << flush;
               }
               else
               {
                   os << "\r    SQL_data folder not created successfully                             " << endl;
                   throw Main_Exception("ERROR_SQL_012: SQL folder could not be created. Check write "
                                        "permissions and that the parent folder is accessible.");
               }
               write_cout(os.str());
           }
           else
           {
               os << "\r    Checking for existing folders....done!        " << flush;
               write_cout(os.str());
           }
           // create the empty file, deleting if it exists.
           sqloutname += string("/SQL_data/data_") + to_string(the_task) + "_" + to_string(the_seed) + ".db";
       }
       catch(Main_Exception& me)
       {
           cerr << me.what() << endl;
           sqloutname = string("data_") + to_string(the_task) + "_" + to_string(the_seed) + ".db";
       }
       remove(sqloutname.c_str());
       os.str("");
       os << "\r    Generating species list....              " << flush;
       write_cout(os.str());
       // for outputting the full data from the simulation in to a SQL file.
       sqlite3_stmt* stmt;
       char* sErrMsg;
       int rc = 0;
   // Open a SQL database in memory. This will be written to disk later.
   // A check here can be done to write to disc directly instead to massively reduce RAM consumption
   #ifdef sql_ram
       sqlite3_open(":memory:", &database);
   #endif
   #ifndef sql_ram
       rc = sqlite3_open_v2(sqloutname.c_str(), &database, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE, "unix-dotfile");
   
   #endif
       // Create the command to be executed by adding to the string.
       string all_commands;
       all_commands =
           "CREATE TABLE SPECIES_LIST (ID int PRIMARY KEY NOT NULL, unique_spec INT NOT NULL, xval INT NOT NULL,";
       all_commands += "yval INT NOT NULL, xwrap INT NOT NULL, ywrap INT NOT NULL, tip INT NOT NULL, speciated INT NOT "
                       "NULL, parent INT NOT NULL,existance INT NOT NULL,randnum DOUBLE NOT NULL, gen_alive INT NOT "
                       "NULL, gen_added DOUBLE NOT NULL);";
   
       // Create the table within the SQL database
       rc = sqlite3_exec(database, all_commands.c_str(), NULL, NULL, &sErrMsg);
       if(rc != SQLITE_OK)
       {
   #ifndef sql_ram
           sqlite3_close(database);
           //          cerr << "unix-dotfile not working - attempting default SQL VFS method..." << flush;
           // delete any old database files - this is risky, but there isn't a better way of ensuring that the file
           // actually gets created.
           remove(sqloutname.c_str());
           rc = sqlite3_open(sqloutname.c_str(), &database);
           rc = sqlite3_exec(database, all_commands.c_str(), NULL, NULL, &sErrMsg);
           if(rc == SQLITE_OK)
           {
               //              cerr << "done! Default unix VFS method functional." << endl;
           }
           else
           {
               cerr << "Database file creation failed. Check file system." << endl;
               cerr << "Error code: " << rc << endl;
               exit(-1);
           }
   #endif
           if(rc != SQLITE_OK)
           {
               cerr << "ERROR_SQL_007: Cannot generate in-memory table. Check memory database assignment and SQL "
                       "commands."
                    << endl;
               cerr << "Error code: " << rc << endl;
           }
       }
       // Now create the prepared statement into which we shall insert the values from the table
       all_commands = "INSERT INTO SPECIES_LIST "
                      "(ID,unique_spec,xval,yval,xwrap,ywrap,tip,speciated,parent,existance,randnum,gen_alive,gen_added) "
                      "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)";
       sqlite3_prepare_v2(database, all_commands.c_str(), strlen(all_commands.c_str()), &stmt, NULL);
   
       // Start the transaction
       rc = sqlite3_exec(database, "BEGIN TRANSACTION;", NULL, NULL, &sErrMsg);
       if(rc != SQLITE_OK)
       {
           cerr << "ERROR_SQL_008: Cannot start SQL transaction. Check memory database assignment and SQL commands."
                << endl;
       }
       for(unsigned int i = 0; i <= enddata; i++)
       {
           sqlite3_bind_int(stmt, 1, i);
           sqlite3_bind_int(stmt, 2, data[i].getSpeciesID());
           sqlite3_bind_int(stmt, 3, data[i].getXpos());
           sqlite3_bind_int(stmt, 4, data[i].getYpos());
           sqlite3_bind_int(stmt, 5, data[i].getXwrap());
           sqlite3_bind_int(stmt, 6, data[i].getYwrap());
           sqlite3_bind_int(stmt, 7, data[i].isTip());
           sqlite3_bind_int(stmt, 8, data[i].hasSpeciated());
           sqlite3_bind_int(stmt, 9, data[i].getParent());
           sqlite3_bind_int(stmt, 10, data[i].getExistance());
           sqlite3_bind_double(stmt, 11, data[i].getSpecRate());
           sqlite3_bind_int(stmt, 12, data[i].getGenRate());
           sqlite3_bind_double(stmt, 13, data[i].getGeneration());
           sqlite3_step(stmt);
           sqlite3_clear_bindings(stmt);
           sqlite3_reset(stmt);
       }
       os.str("");
       os << "\r    Executing SQL commands...." << flush;
       write_cout(os.str());
       // execute the command and close the connection to the database
       rc = sqlite3_exec(database, "END TRANSACTION;", NULL, NULL, &sErrMsg);
       if(rc != SQLITE_OK)
       {
           cerr << "ERROR_SQL_008: Cannot complete SQL transaction. Check memory database assignment and SQL "
                   "commands. Ensure SQL statements are properly cleared."
                << endl;
           cerr << "Error code: " << rc << endl;
           // try again
           int i = 0;
           while((rc != SQLITE_OK && rc != SQLITE_DONE) && i < 10)
           {
               sleep(1);
               i++;
               rc = sqlite3_exec(database, "END TRANSACTION;", NULL, NULL, &sErrMsg);
               cerr << "Attempt " << i << " failed..." << endl;
               cerr << "ERROR_SQL_008: Cannot complete SQL transaction. Check memory database assignment and SQL "
                       "commands. Ensure SQL statements are properly cleared."
                    << endl;
           }
       }
       // Need to finalise the statement
       rc = sqlite3_finalize(stmt);
       if(rc != SQLITE_OK)
       {
           cerr << "ERROR_SQL_008: Cannot complete SQL transaction. Check memory database assignment and SQL "
                   "commands. Ensure SQL statements are properly cleared."
                << endl;
           cerr << "Error code: " << rc << endl;
       }
       // Vacuum the file so that the file size is reduced (reduces by around 3%)
       rc = sqlite3_exec(database, "VACUUM;", NULL, NULL, &sErrMsg);
       if(rc != SQLITE_OK)
       {
           cerr << "ERROR_SQL_014: Cannot vacuum the database. Error message: " << sErrMsg << endl;
       }
   
       // Now additionally store the simulation parameters (extremely useful data)
       string to_execute = "CREATE TABLE SIMULATION_PARAMETERS (seed INT PRIMARY KEY not null, job_type INT NOT NULL,";
       to_execute += "output_dir TEXT NOT NULL, spec_rate DOUBLE NOT NULL, sigma DOUBLE NOT NULL,tau DOUBLE NOT "
                     "NULL, deme INT NOT NULL, ";
       to_execute += "sample_size DOUBLE NOT NULL, max_time INT NOT NULL, dispersal_relative_cost DOUBLE NOT NULL, "
                     "min_num_species ";
       to_execute += "INT NOT NULL, forest_change_rate DOUBLE NOT NULL, time_since_pristine DOUBLE NOT NULL, ";
       to_execute += "time_config_file TEXT NOT NULL, coarse_map_file TEXT NOT NULL, coarse_map_x INT NOT NULL, "
                     "coarse_map_y INT NOT NULL,";
       to_execute += "coarse_map_x_offset INT NOT NULL, coarse_map_y_offset INT NOT NULL, coarse_map_scale DOUBLE NOT "
                     "NULL, fine_map_file TEXT NOT NULL, fine_map_x INT NOT NULL,";
       to_execute += "fine_map_y INT NOT NULL, fine_map_x_offset INT NOT NULL, fine_map_y_offset INT NOT NULL, ";
       to_execute += "sample_file TEXT NOT NULL, grid_x INT NOT NULL, grid_y INT NOT NULL, sample_x INT NOT NULL, ";
       to_execute += "sample_y INT NOT NULL, sample_x_offset INT NOT NULL, sample_y_offset INT NOT NULL, ";
       to_execute += "pristine_coarse_map TEXT NOT NULL, pristine_fine_map TEXT NOT NULL, sim_complete INT NOT NULL, ";
       to_execute += "dispersal_method TEXT NOT NULL, m_probability DOUBLE NOT NULL, cutoff DOUBLE NOT NULL, ";
       to_execute += "restrict_self INT NOT NULL, infinite_landscape TEXT NOT NULL, protracted INT NOT NULL, ";
       to_execute += "min_speciation_gen DOUBLE NOT NULL, max_speciation_gen DOUBLE NOT NULL, dispersal_map TEXT NOT NULL);";
       rc = sqlite3_exec(database, to_execute.c_str(), NULL, NULL, &sErrMsg);
       if(rc != SQLITE_OK)
       {
           cerr << "ERROR_SQL_008: Cannot start SQL transaction. Check memory database assignment and SQL commands."
                << endl;
           cerr << "Error code: " << rc << endl;
       }
       to_execute = "INSERT INTO SIMULATION_PARAMETERS VALUES(" + to_string((long long)the_seed) + "," +
                    to_string((long long)the_task);
       to_execute += ",'" + outdirectory + "'," + boost::lexical_cast<std::string>((long double)spec) + "," +
                     to_string((long double)sigma) + ",";
       to_execute += to_string((long double)tau) + "," + to_string((long long)deme) + ",";
       to_execute += to_string((long double)deme_sample) + "," + to_string((long long)maxtime) + ",";
       to_execute += to_string((long double)dispersal_relative_cost) + "," + to_string((long long)desired_specnum) + ",";
       to_execute += to_string((long double)sim_parameters.dForestChangeRate) + ",";
       to_execute += to_string((long double)sim_parameters.dPristine) + ",'" + sim_parameters.autocorrel_file + "','";
       to_execute += coarsemapinput + "'," + to_string((long long)coarsemapxsize) + ",";
       to_execute += to_string((long long)coarsemapysize) + "," + to_string((long long)coarsemapxoffset) + ",";
       to_execute += to_string((long long)coarsemapyoffset) + "," + to_string((long long)coarsemapscale) + ",'";
       to_execute += finemapinput + "'," + to_string((long long)finemapxsize) + "," + to_string((long long)finemapysize);
       to_execute += "," + to_string((long long)finemapxoffset) + "," + to_string((long long)finemapyoffset) + ",'";
       to_execute += sim_parameters.samplemaskfile + "'," + to_string((long long)gridxsize) + "," +
                     to_string((long long) gridysize) + "," + to_string((long long) sim_parameters.varsamplexsize) + ", ";
       to_execute += to_string((long long) sim_parameters.varsampleysize) + ", ";
       to_execute += to_string((long long) sim_parameters.varsamplexoffset) + ", ";
       to_execute += to_string((long long) sim_parameters.varsampleyoffset) + ", '";
       to_execute += pristinecoarsemapinput + "','" + pristinefinemapinput + "'," + to_string(sim_complete);
       to_execute += ", '" + sim_parameters.dispersal_method + "', ";
       to_execute += boost::lexical_cast<std::string>(sim_parameters.m_prob) + ", ";
       to_execute += to_string((long double)sim_parameters.cutoff) + ", ";
       to_execute += to_string(sim_parameters.restrict_self) + ", '";
       to_execute += sim_parameters.landscape_type + "', ";
       // Now save the protracted speciation variables (not relevant in this simulation scenario)
       to_execute += protractedVarsToString();
       to_execute += ", '" + sim_parameters.dispersal_file + "'";
       to_execute += ");";
       rc = sqlite3_exec(database, to_execute.c_str(), NULL, NULL, &sErrMsg);
       if(rc != SQLITE_OK)
       {
           os << to_execute << endl;
           os << boost::lexical_cast<std::string>((double)spec) << endl;
           os << spec << endl;
           cerr << "ERROR_SQL_008: Cannot start SQL transaction. Check memory database assignment and SQL commands."
                << endl;
           cerr << "Error code: " << rc << endl;
       }
       write_cout("done!\n");
   }
   
   string Tree::protractedVarsToString()
   {
       string tmp = to_string(false) + ", " + to_string(0.0) + ", " + to_string(0.0);
       return tmp;
   }
   
   void Tree::sqlOutput()
   {
   #ifdef sql_ram
       // open connection to the database file
       remove(sqloutname.c_str());
       stringstream os;
       os << "\r    Writing to " << sqloutname << " ....     " << flush;
       write_cout(os.str());
       int rc =
           sqlite3_open_v2(sqloutname.c_str(), &outdatabase, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE, "unix-dotfile");
       if(rc != SQLITE_OK && rc != SQLITE_DONE)
       {
           int i = 0;
           while((rc != SQLITE_OK && rc != SQLITE_DONE) && i < 10)
           {
               i++;
               sleep(1);
               rc = sqlite3_open_v2(sqloutname.c_str(), &outdatabase, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE,
                                    "unix-dotfile");
               //              cerr << "Attempt " << i << " failed..." << endl;
           }
           // Attempt different opening method if the first fails.
           int j = 0;
           while((rc != SQLITE_OK && rc != SQLITE_DONE) && j < 10)
           {
               j++;
               sleep(1);
               rc = sqlite3_open(sqloutname.c_str(), &outdatabase);
               //              cerr << "Attempt " << i << " failed..." << endl;
           }
           if(rc != SQLITE_OK && rc != SQLITE_DONE)
           {
               cerr << "ERROR_SQL_010: SQLite database file could not be opened. Check the folder exists and you "
                       "have write permissions. (REF1) Error code: "
                    << rc << endl;
               cerr << "Attempted call " << max(i, j) << " times" << endl;
           }
       }
       // create the backup object to write data to the file from memory.
       sqlite3_backup* backupdb;
       backupdb = sqlite3_backup_init(outdatabase, "main", database, "main");
       if(!backupdb)
       {
           cerr << "ERROR_SQL_011: Could not write to the backup database. Check the file exists." << endl;
       }
       // Perform the backup
       rc = sqlite3_backup_step(backupdb, -1);
       if(rc != SQLITE_OK && rc != SQLITE_DONE)
       {
           //          cerr <<  "ERROR_SQL_010: SQLite database file could not be opened. Check the folder
           // exists
           // and
           // you
           // have write permissions. (REF2) Error code: " << rc << endl;
           // try again
           int i = 0;
           while((rc != SQLITE_OK && rc != SQLITE_DONE) && i < 10)
           {
               i++;
               sleep(1);
               rc = sqlite3_backup_step(backupdb, -1);
               //              cerr << "Attempt " << i << " failed..." << endl;
           }
           if(rc != SQLITE_OK && rc != SQLITE_DONE)
           {
               cerr << "ERROR_SQL_010: SQLite database file could not be opened. Check the folder exists and you "
                       "have write permissions. (REF3) Error code: "
                    << rc << endl;
               cerr << "Attempted call " << i << " times" << endl;
           }
       }
       sqlite3_backup_finish(backupdb);
       //      sqlite3_exec(database,"VACUUM;",NULL,NULL,&sErrMsg);
       os.str("");
       os << "\r    Writing to " << sqloutname << " ....  done!              " << endl;
       write_cout(os.str());
   #endif
   }
   
   void Tree::applySpecRate(double sr, double t)
   {
       if(!tl.hasImportedData())
       {
           tl.setDatabase(database);
       }
       // os << "Precount: " << tl.countSpecies() << endl;
       tl.setGeneration(t);
       tl.resetTree();
       tl.internalOption();
       tl.setProtractedParameters(getProtractedGenerationMin(), getProtractedGenerationMax());
       tl.setProtracted(false);
       tl.createDatabase(sr);
   #ifdef record_space
       tl.recordSpatial();
   #endif
   }
   
   void Tree::applySpecRate(double sr)
   {
       applySpecRate(sr, 0.0);
   }
   
   void Tree::applyMultipleRates()
   {
       stringstream os;
       unsigned long iMultiNumber = speciation_rates.size();
       if(iMultiNumber == 0)
       {
           os << "No additional speciation rates to apply." << endl;
           iMultiNumber = 1;
           speciation_rates.push_back(spec);
       }
       os << "Speciation rate" << flush;
       if(speciation_rates.size() > 1)
       {
           os << "s are: " << flush;
       }
       else
       {
           os << " is: " << flush;
       }
       for(unsigned long i = 0; i < iMultiNumber; i++)
       {
           os << speciation_rates[i] << flush;
           if(i + 1 == iMultiNumber)
           {
               os << "." << endl;
           }
           else
           {
               os << ", " << flush;
           }
       }
       write_cout(os.str());
       // Now check to make sure repeat speciation rates aren't done twice (this is done to avoid the huge number of errors
       // SQL throws if you try to add identical data
       double dUniqueSpec[iMultiNumber];
       unsigned long spec_upto = sortData();
       sqlCreate();
       for(unsigned long i = 0; i < iMultiNumber; i++)
       {
           bool bCont = true;
           for(unsigned long j = 0; j < iMultiNumber; j++)
           {
               if(dUniqueSpec[j] == speciation_rates[i])
               {
                   bCont = false;
               }
           }
           if(bCont)
           {
               dUniqueSpec[i] = speciation_rates[i];
               vector<double> temp_sampling = getTemporalSampling();
               for(unsigned long k = 0; k < temp_sampling.size(); k++)
               {
                   try
                   {
                       write_cout(string("Calculating generation " + to_string(temp_sampling[k]) + "\n"));
                       if(speciation_rates[i] > spec)
                       {
                           applySpecRate(speciation_rates[i], temp_sampling[k]);
                       }
                       else if(speciation_rates[i] == spec)
                       {
                           // Use the run spec if the rates are very close to equal
                           applySpecRate(spec, temp_sampling[k]);
                       }
                   }
                   catch(const std::exception& e)
                   {
                       os << e.what() << endl;
                       write_cerr(os.str());
                   }
               }
           }
           else
           {
               write_cerr("Repeat speciation rate... ignoring\n");
           }
       }
       outputData(spec_upto);
   }
   
   
   
   void Tree::determineSpeciationRates()
   {
       if(bConfig)
       {
           if(sim_parameters.configs.hasSection("spec_rates"))
           {
               vector<string> spec_rates = sim_parameters.configs.getSectionValues("spec_rates");
               for(const auto &spec_rate : spec_rates)
               {
                   speciation_rates.push_back(stod(spec_rate));
               }
           }
       }
       else
       {
           speciation_rates.push_back(spec);
       }
   }
   
   void Tree::verifyReproductionMap()
   {
       if(!(sim_parameters.reproduction_file == "none" || sim_parameters.reproduction_file == "null"))
       {
           for(unsigned long i = 0; i < sim_parameters.varfinemapysize; i++)
           {
               for(unsigned long j = 0; j < sim_parameters.varfinemapxsize; j ++)
               {
                   if(rep_map[i][j] == 0.0 && forestmap.getValFine(j, i, 0.0) != 0)
                   {
                       throw Fatal_Exception("Reproduction map is zero where density is non-zero."
                                             " This will cause an infinite loop.");
                   }
                   if(forestmap.getValFine(j, i, 0.0) == 0 && rep_map[i][j] != 0.0)
                   {
                       write_error("Density is zero where reproduction map is non-zero. This is likely incorrect.");
                   }
               }
           }
       }
   }
   
   void Tree::addWrappedLineage(unsigned long numstart, long x, long y)
   {
       if(grid[y][x].getNwrap() == 0)
       {
           grid[y][x].setNext(numstart);
           grid[y][x].setNwrap(1);
           active[numstart].setNwrap(1);
       }
       else
       {
           unsigned long tmp_next = grid[y][x].getNext();
           unsigned long tmp_last = tmp_next;
           unsigned long tmp_nwrap = 0;
           while(tmp_next != 0)
           {
               tmp_nwrap ++;
               tmp_last = tmp_next;
               tmp_next = active[tmp_next].getNext();
           }
           grid[y][x].increaseNwrap();
           active[tmp_last].setNext(numstart);
           active[numstart].setNwrap(tmp_nwrap + 1);
       }
   #ifdef DEBUG
       debugAddingLineage(numstart, x, y);
   #endif
   }
   
   void Tree::convertTip(unsigned long i, double generationin)
   {
       enddata++;
       if(enddata >= data.size())
       {
           throw Fatal_Exception(
                   "Cannot add tip - no space in data. Check size calculations.");
       }
       data[enddata].setup(true, active[i].getXpos(), active[i].getYpos(),
                           active[i].getXwrap(),
                           active[i].getYwrap(), generationin);
       // Now link the old tip to the new tip
       data[active[i].getMpos()].setParent(enddata);
       data[enddata].setIGen(0);
       data[enddata].setSpec(NR.d01());
       active[i].setMpos(enddata);
   }
   
   unsigned long Tree::countCellExpansion(const long &x, const long &y, const long &xwrap, const long &ywrap,
                                          const double &generation_in, const bool& make_tips)
   {
       unsigned long mapcover = (unsigned long)(floor(forestmap.getVal(x, y, xwrap,
                                                                                  ywrap, generation_in) * deme_sample));
       unsigned long num_to_add = mapcover;
       if(xwrap == 0 && ywrap == 0)
       {
           unsigned long ref = 0;
           if(mapcover >= grid[y][x].getMaxsize())
           {
               grid[y][x].changePercentCover(mapcover);
           }
           while(ref < grid[y][x].getMaxsize() && num_to_add > 0)
           {
               unsigned long tmp_active = grid[y][x].getSpecies(ref);
               if(tmp_active != 0)
               {
                   if(make_tips)
                   {
                       makeTip(tmp_active, generation_in);
                   }
                   num_to_add --;
               }
               ref ++;
           }
       }
       else
       {
           unsigned long next = grid[y][x].getNext();
           while(next != 0 && num_to_add > 0)
           {
               if(active[next].getXwrap() == xwrap && active[next].getYwrap() == ywrap)
               {
                   num_to_add--;
                   if(make_tips)
                   {
                       makeTip(next, generation_in);
                   }
               }
               next = active[next].getNext();
           }
       }
       return num_to_add;
   }
   
   void Tree::expandCell(long x, long y, long xwrap, long ywrap, double generation_in, unsigned long num_to_add)
   {
       if(num_to_add > 0)
       {
           for(unsigned long k = 0; k < num_to_add; k ++)
           {
               endactive ++;
               enddata ++;
               unsigned long listpos = 0;
               // Add the species to active
               if(xwrap == 0 && ywrap == 0)
               {
                   listpos = grid[y][x].addSpecies(endactive);
                   active[endactive].setup(x, y, xwrap, ywrap, enddata, listpos, 1);
               }
               else
               {
                   active[endactive].setup(x, y, xwrap, ywrap, enddata, listpos, 1);
                   addWrappedLineage(endactive, x, y);
               }
               if(enddata >= data.size())
               {
                   throw Fatal_Exception("Cannot add lineage - no space in data. "
                                                 "Check size calculations.");
               }
               if(endactive >= active.size())
               {
                   throw Fatal_Exception("Cannot add lineage - no space in active. "
                                                 "Check size calculations.");
               }
   
               // Add a tip in the Treenode for calculation of the coalescence tree at the
               // end of the simulation.
               // This also contains the start x and y position of the species.
               data[enddata].setup(true, x, y, xwrap, ywrap, generation_in);
               data[enddata].setSpec(NR.d01());
           }
       }
   }
   
   void Tree::makeTip(const unsigned long &tmp_active, const double &generationin)
   {
       unsigned long m_pos = active[tmp_active].getMpos();
       if(data[m_pos].isTip())
       {
           convertTip(tmp_active, generationin);
       }
       else
       {
           data[active[tmp_active].getMpos()].setGeneration(generationin);
           data[active[tmp_active].getMpos()].setTip(true);
       }
   }
   
   void Tree::validateLineages()
   {
       bool fail = false;
       write_cout("\nStarting lineage validation...");
       unsigned long printed = 0;
       for(unsigned long i = 1; i < endactive; i++)
       {
           stringstream ss;
           try
           {
               Datapoint tmp_datapoint = active[i];
               // Validate the location exists
               if(forestmap.getVal(tmp_datapoint.getXpos(), tmp_datapoint.getYpos(),
                                   tmp_datapoint.getXwrap(), tmp_datapoint.getYwrap(), 0.0) == 0)
               {
                   if(printed < 100)
                   {
                       printed ++;
                       ss << "forestmapval: " << forestmap.getVal(tmp_datapoint.getXpos(), tmp_datapoint.getYpos(),
                                                                  tmp_datapoint.getXwrap(), tmp_datapoint.getYwrap(),
                                                                  0.0) << endl;
                   }
                   fail = true;
               }
               if(tmp_datapoint.getXwrap() == 0 && tmp_datapoint.getYwrap() == 0)
               {
                   if(tmp_datapoint.getNwrap() != 0)
                   {
                       fail = true;
                   }
                   else
                   {
                       if(i !=
                          grid[tmp_datapoint.getYpos()][tmp_datapoint.getXpos()].getSpecies(tmp_datapoint.getListpos()))
                       {
                           fail = true;
                       }
                   }
               }
               else
               {
                   if(tmp_datapoint.getNwrap() == 0)
                   {
                       fail = true;
                   }
                   else
                   {
                       unsigned long tmp_next = grid[tmp_datapoint.getYpos()][tmp_datapoint.getXpos()].getNext();
                       unsigned long count = 0;
                       while(tmp_next != 0)
                       {
                           count++;
                           if(count != active[tmp_next].getNwrap())
                           {
                               ss << "problem in wrap: " << count << " != " << active[tmp_next].getNwrap() << endl;
                               fail = true;
                           }
                           tmp_next = active[tmp_next].getNext();
                       }
                       if(count == 0 && count != grid[tmp_datapoint.getYpos()][tmp_datapoint.getXpos()].getNwrap())
                       {
                           fail = true;
                       }
                       if(count != grid[tmp_datapoint.getYpos()][tmp_datapoint.getXpos()].getNwrap())
                       {
                           fail = true;
                       }
                   }
               }
               if(fail)
               {
                   ss << "\nFailure in map expansion. Please report this bug." << endl;
                   ss << "active reference: " << i << endl;
                   ss << "x, y position: " << tmp_datapoint.getXpos() << ", " << tmp_datapoint.getYpos() << endl;
                   ss << "wrapping: " << tmp_datapoint.getXwrap() << ", " << tmp_datapoint.getYwrap() << endl;
                   ss << "nwrap: " << tmp_datapoint.getNwrap() << endl;
                   ss << "Grid wrapping: " << grid[tmp_datapoint.getYpos()][tmp_datapoint.getXpos()].getNwrap() << endl;
                   throw out_of_range(ss.str());
               }
           }
           catch(out_of_range &oe)
           {
               write_cout(ss.str());
               throw oe;
           }
       }
       write_cout("done\n");
   }
   
   #ifdef DEBUG
   void Tree::debugAddingLineage(unsigned long numstart, long x, long y)
   {
       unsigned long tmp_next = grid[y][x].getNext();
       unsigned long tmp_nwrap = 0;
       while(tmp_next != 0)
       {
           tmp_nwrap ++;
           if(active[tmp_next].getNwrap() != tmp_nwrap)
           {
               stringstream ss;
               ss << "Incorrect setting of nwrap in wrapped lineage, please report this bug." << endl;
               ss << "next nwrap: " << active[tmp_next].getNwrap() << endl;
               ss << "tmp_nwrap: " << tmp_nwrap << endl;
               ss << "next = " << tmp_next << endl;
               ss << "numstart: " << numstart << endl;
               throw Fatal_Exception(ss.str());
           }
           tmp_next = active[tmp_next].getNext();
       }
       if(tmp_nwrap != grid[y][x].getNwrap())
       {
           stringstream ss;
           ss << "Grid wrapping value not set correctly" << endl;
           ss << "Grid nwrap: " << grid[y][x].getNwrap() << endl;
           ss << "Counted wrapping: " << tmp_nwrap << endl;
           ss << "active: " << numstart << endl;
           tmp_next = grid[y][x].getNext();
           tmp_nwrap = 0;
           while(tmp_next != 0 && tmp_nwrap < grid[y][x].getNwrap())
           {
               tmp_nwrap ++;
               ss << "tmp_next: " << tmp_next << endl;
               ss << "tmp_nwrap: " << tmp_nwrap << endl;
               tmp_next = active[tmp_next].getNext();
           }
           throw Fatal_Exception(ss.str());
       }
   }
   #endif
   
   int runMain(int argc, vector<string> &argv)
   {
       // Create our SimSetup object
       // This performs some basic checks to make sure that our simulation parameters make sense
       // It also outputs the information if the user requests help or runs with incorrect options.
   #ifndef verbose
       // Open our file for logging outputs
       openLogFile(false);
   #endif
       // Parse our arguments
       vector<string> comargs;
       comargs = argv;
       // Create our tree object that contains the simulation
       Tree tree;
       tree.importSimulationVariables(comargs);
       // Setup the sim
       tree.setup();
       // Detect speciation rates to apply
       bool isComplete = tree.runSimulation();
       if(isComplete)
       {
           tree.applyMultipleRates();
       }
   #ifndef verbose
       fclose(stdout);
   #endif
       write_cout("*************************************************\n");
       return 0;
   }
