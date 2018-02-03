// This file is part of NECSim project which is released under BSD-3 license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.

/**
 * @author Samuel Thompson
 * @date 24/03/17
 * @file Tree.cpp
 *
 * @brief  Contains the Tree class implementation as the main simulation object for spatially-explicit
 * coalescence simulations.
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 */

#include <algorithm>
#include "SpatialTree.h"

void SpatialTree::importSimulationVariables(const string &configfile)
{
	sim_parameters.importParameters(configfile);
	// Now check that our folders exist
	checkFolders();
	// Now check for paused simulations
	checkSims();
}

void SpatialTree::parseArgs(vector<string> & comargs)
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
		writeWarning(os.str());
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
		writeWarning(os.str());
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
			writeWarning(os.str());
			exit(1); // exit the program right away as there is no need to continue if there is no simulation to run!
		}
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
		has_paused = true;
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
			throw FatalException("ERROR_MAIN_011: FATAL. -c or -config used to attempt importSpatialParameters from "
										 "config file, but no config file provided.");
		}
		bConfig = true;
	}
	bFullmode = false;
	if(comargs[1] == "-f" || comargs[2] == "-f")
	{
		writeInfo("Full command-line mode enabled.\n");
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
		throw FatalException(err);
		// note argc-1 which takes in to account the automatic generation of one command line argument which is the number of arguments.
	}
	argc = comargs.size();
}


void SpatialTree::checkFolders()
{
	
	stringstream os;
	os << "Checking folder existance..." << flush;
	bool bFineMap, bCoarseMap, bFineMapPristine, bCoarseMapPristine, bSampleMask, bOutputFolder;
	try
	{
		bFineMap = doesExistNull(sim_parameters.finemapfile);
	}
	catch(FatalException& fe)
	{
		cerr << fe.what() << endl;
		bFineMap = false;
	}
	try
	{
		bCoarseMap = doesExistNull(sim_parameters.coarsemapfile);
	}
	catch(FatalException& fe)
	{
		cerr << fe.what() << endl;
		bCoarseMap = false;
	}
	try
	{
		bFineMapPristine = doesExistNull(sim_parameters.pristinefinemapfile);
	}
	catch(FatalException& fe)
	{
		cerr << fe.what() << endl;
		bFineMapPristine = false;
	}
	try
	{
		bCoarseMapPristine = doesExistNull(sim_parameters.pristinecoarsemapfile);
	}
	catch(FatalException& fe)
	{
		cerr << fe.what() << endl;
		bCoarseMapPristine = false;
	}
	bOutputFolder = checkOutputDirectory();
	try
	{
		bSampleMask = doesExistNull(sim_parameters.samplemaskfile);
	}
	catch(FatalException& fe)
	{
		cerr << fe.what() << endl;
		bSampleMask = false;
	}
	if(bFineMap && bCoarseMap && bFineMapPristine && bCoarseMapPristine && bOutputFolder && bSampleMask)
	{
		os << "\rChecking folder existance...done!                                                                " << endl;
		writeInfo(os.str());
		return;
	}
	else
	{
		throw FatalException("Required files do not all exist. Check program inputs.");
	}
}


void SpatialTree::setParameters()
{
	if(!has_imported_vars)
	{
		Tree::setParameters();
		// Set the variables equal to the value from the Mapvars object.
		fine_map_input = sim_parameters.finemapfile;
		coarse_map_input = sim_parameters.coarsemapfile;
		grid_x_size = sim_parameters.vargridxsize;
		grid_y_size = sim_parameters.vargridysize;

		fine_map_x_size = sim_parameters.varfinemapxsize;
		fine_map_y_size = sim_parameters.varfinemapysize;
		fine_map_x_offset = sim_parameters.varfinemapxoffset;
		fine_map_y_offset = sim_parameters.varfinemapyoffset;

		coarse_map_x_size = sim_parameters.varcoarsemapxsize;
		coarse_map_y_size = sim_parameters.varcoarsemapysize;
		coarse_map_x_offset = sim_parameters.varcoarsemapxoffset;
		coarse_map_y_offset = sim_parameters.varcoarsemapyoffset;
		coarse_map_scale = sim_parameters.varcoarsemapscale;
		dispersal_relative_cost = sim_parameters.dispersal_relative_cost;


		// pristine map information
		pristine_fine_map_input = sim_parameters.pristinefinemapfile;
		pristine_coarse_map_input = sim_parameters.pristinecoarsemapfile;
		gen_since_pristine = sim_parameters.gen_since_pristine;
		habitat_change_rate = sim_parameters.habitat_change_rate;
		desired_specnum = sim_parameters.desired_specnum;
		sigma = sim_parameters.sigma;
		tau = sim_parameters.tau;
		if(sim_parameters.landscape_type == "none")
		{
			sim_parameters.landscape_type = "closed";
		}
		if(sim_parameters.dispersal_method == "none")
		{
			sim_parameters.dispersal_method = "normal";
		}
	}
	else
	{
		throw FatalException("ERROR_MAIN_001: Variables already imported.");
	}
}



void SpatialTree::importMaps()
{
	if(has_imported_vars)
	{
		// Set the dimensions
		habitat_map.setDims(sim_parameters);
		try
		{
			// Set the time variables
			habitat_map.checkMapExists();
			// habitat_map.setTimeVars(gen_since_pristine,habitat_change_rate);
			// Import the fine map
			habitat_map.calcFineMap();
			// Import the coarse map
			habitat_map.calcCoarseMap();
			// Calculate the offset for the extremeties of each map
			habitat_map.calcOffset();
			// Import the pristine maps;
			habitat_map.calcPristineFineMap();
			habitat_map.calcPristineCoarseMap();
			// Calculate the maximum values
			habitat_map.recalculateHabitatMax();
			importReproductionMap();
			samplegrid.importSampleMask(sim_parameters);
		}
		catch(FatalException& fe)
		{
			stringstream ss;
			ss <<"Problem setting up map files: " << fe.what() << endl;
			throw FatalException(ss.str());
		}
	}
	else
	{
		throw FatalException("ERROR_MAIN_002: Variables not imported.");
	}
}

void SpatialTree::importReproductionMap()
{
	rep_map.import(sim_parameters.reproduction_file,
				   sim_parameters.varfinemapxsize, sim_parameters.varfinemapysize);
	rep_map.setOffsets(sim_parameters.varcoarsemapxoffset, sim_parameters.varfinemapyoffset,
					   sim_parameters.vargridxsize, sim_parameters.vargridysize);
	// Now verify that the reproduction map is always non-zero when the density is non-zero.
	verifyReproductionMap();
}


unsigned long SpatialTree::getInitialCount()
{
	if(sim_parameters.uses_spatial_sampling)
	{
		long x = 1;
		long y = 1;
		long xwrap = 0;
		long ywrap = 0;
		samplegrid.recalculate_coordinates(x, y, xwrap, ywrap);
	}
	unsigned long initcount = 0;
	// Get a count of the number of individuals on the grid.
	try
	{
		long max_x, max_y;
		if(samplegrid.getDefault())
		{
			max_x = sim_parameters.varfinemapxsize;
			max_y = sim_parameters.varfinemapysize;
		}
		else
		{
			if(sim_parameters.uses_spatial_sampling)
			{
				max_x = samplegrid.sample_mask_exact.GetCols();
				max_y = samplegrid.sample_mask_exact.GetRows();
			}
			else
			{
				max_x = samplegrid.sample_mask.GetCols();
				max_y = samplegrid.sample_mask.GetRows();
			}
		}
		long x, y, xwrap, ywrap;
		for(long i = 0; i < max_y; i++)
		{
			for(long j = 0; j < max_x; j++)
			{
				x = j;
				y = i;
				xwrap = 0;
				ywrap = 0;
				samplegrid.recalculate_coordinates(x, y, xwrap, ywrap);
				initcount += getIndividualsSampled(x, y, xwrap, ywrap, 0.0);
			}
		}
	}
	catch(exception& e)
	{
		throw FatalException(e.what());
	}
	// Set active and data at the correct sizes.
	if(initcount == 0)
	{
		throw runtime_error("Initial count is 0. No individuals to simulate. Exiting program.");
	}
	else
	{
		writeInfo("Initial count is " + to_string(initcount) + "\n");
	}
	if(initcount > 10000000000)
	{
		writeWarning("Initial count extremely large, RAM issues likely: " + to_string(initcount));
	}
	return initcount;
}


void SpatialTree::setupDispersalCoordinator()
{
	dispersal_coordinator.setHabitatMap(&habitat_map);
	dispersal_coordinator.setRandomNumber(&NR);
	dispersal_coordinator.setGenerationPtr(&generation);
	dispersal_coordinator.setDispersal(sim_parameters.dispersal_method, sim_parameters.dispersal_file,
										sim_parameters.varfinemapxsize, sim_parameters.varfinemapysize,
										sim_parameters.m_prob, sim_parameters.cutoff, sim_parameters.sigma,
										sim_parameters.tau, sim_parameters.restrict_self);
}

void SpatialTree::setup()
{
	printSetup();
	if(has_paused)
	{
		if(!has_imported_pause)
		{
			setResumeParameters();
		}
		simResume();
		setupDispersalCoordinator();
	}
	else
	{
		setParameters();
		setInitialValues();
		importMaps();
		setupDispersalCoordinator();
		habitat_map.setLandscape(sim_parameters.landscape_type);
#ifdef DEBUG
		habitat_map.validateMaps();
#endif
		generateObjects();
	}
}

unsigned long SpatialTree::fillObjects(const unsigned long &initial_count)
{
	active[0].setup(0, 0, 0, 0, 0, 0, 0);
	grid.SetSize(grid_y_size, grid_x_size);
	unsigned long number_start = 0;
	stringstream os;
	os << "\rSetting up simulation...filling grid                           " << flush;
	writeInfo(os.str());
	// Add the individuals to the grid, and add wrapped individuals to their correct locations.
	// This loop adds individuals to data and active (for storing the coalescence tree and active lineage tracking)
	try
	{
		long x, y;
		long x_wrap, y_wrap;
		for(unsigned long i = 0; i < sim_parameters.varsamplexsize; i++)
		{
			for(unsigned long j = 0; j < sim_parameters.varsampleysize; j++)
			{

				x = i;
				y = j;

				x_wrap = 0;
				y_wrap = 0;
				samplegrid.recalculate_coordinates(x, y, x_wrap, y_wrap);
				if(x_wrap == 0 && y_wrap == 0)
				{
					unsigned long stored_next = grid[y][x].getNext();
					unsigned long stored_nwrap = grid[y][x].getNwrap();
					grid[y][x].initialise(habitat_map.getVal(x, y, 0, 0, 0));
					grid[y][x].fillList();
					grid[y][x].setNwrap(stored_nwrap);
					grid[y][x].setNext(stored_next);
					unsigned long sample_amount = getIndividualsSampled(x, y, 0, 0, 0.0);
					if(sample_amount >= 1)
					{
						for(unsigned long k = 0; k < sample_amount; k++)
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
								unsigned long list_position_in = grid[y][x].addSpecies(number_start);
								// Add the species to active
								active[number_start].setup(x, y, 0, 0, number_start, list_position_in, 1);
								// Add a tip in the TreeNode for calculation of the coalescence tree at the
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
					unsigned long sample_amount = getIndividualsSampled(x, y, x_wrap, y_wrap, 0.0);
					if(sample_amount >= 1)
					{
						for(unsigned long k = 0; k < sample_amount; k++)
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
								// Add a tip in the TreeNode for calculation of the coalescence tree at the
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
		if(sim_parameters.uses_spatial_sampling)
		{

			samplegrid.convertBoolean(habitat_map, deme_sample, generation);
			// if there are no additional time points to sample at, we can remove the sample mask from memory.
			if(!(has_times_file && this_step.time_reference < reference_times.size()))
			{
				samplegrid.clearSpatialMask();
			}
		}
	}
	catch(out_of_range &out_of_range1)
	{
		stringstream ss;
		ss << "Fatal exception thrown when filling grid (out_of_range): " << out_of_range1.what() << endl;
		throw FatalException(ss.str());
	}
	catch(exception &fe)
	{
		throw FatalException("Fatal exception thrown when filling grid (other) \n");
	}

	if(number_start == initial_count)  // Check that the two counting methods match up.
	{
	}
	else
	{
		if(initial_count > 1.1 * number_start)
		{
			writeWarning("Data usage higher than neccessary - check allocation of individuals to the grid.");
			stringstream ss;
			ss << "Initial count: " << initial_count << "  Number counted: " << number_start << endl;
			writeWarning(ss.str());
		}
	}
#ifdef DEBUG
	validateLineages();
#endif
	return number_start;
}

unsigned long SpatialTree::getIndividualsSampled(const long &x, const long &y, const long &x_wrap,
										  const long &y_wrap, const double &current_gen)
{
//	if(sim_parameters.uses_spatial_sampling)
//	{
		return static_cast<unsigned long>(max(floor(deme_sample * habitat_map.getVal(x, y, x_wrap, y_wrap, 0.0)
						 * samplegrid.getExactValue(x, y, x_wrap, y_wrap)), 0.0));
//	}
//	else
//	{
//		return static_cast<unsigned long>(max(floor(deme_sample * habitat_map.getVal(x, y, x_wrap, y_wrap, 0.0)), 0.0));
//	}
}

void SpatialTree::removeOldPosition(const unsigned long &chosen)
{
	long nwrap = active[chosen].getNwrap();
	long oldx = active[chosen].getXpos();
	long oldy = active[chosen].getYpos();
	if(nwrap == 0)
	{
#ifdef DEBUG

		if(active[chosen].getXwrap() != 0 || active[chosen].getYwrap() != 0)
		{
			active[chosen].logActive(50);
			throw FatalException("ERROR_MOVE_015: Nwrap not set correctly. Nwrap 0, but x and y wrap not 0. ");
		}
#endif // DEBUG
// Then the lineage exists in the main list;
// debug (can be removed later)
#ifdef pristine_mode
		if(grid[oldy][oldx].getMaxsize() < active[chosen].getListpos())
		{
			cerr << "grid maxsize: " << grid[oldy][oldx].getMaxsize() << endl;
			throw FatalException("ERROR_MOVE_001: Listpos outside maxsize. Check move programming function.");
		}
#endif
		// delete the species from the list
		grid[oldy][oldx].deleteSpecies(active[chosen].getListpos());
		// clear out the variables.
		active[chosen].setNext(0);
		active[chosen].setNwrap(0);
		active[chosen].setListPosition(0);
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
			active[chosen].setListPosition(0);
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
#ifdef DEBUG
				if(active[lastpos].getNwrap() != (active[chosen].getNwrap() - 1))
				{
					writeLog(50, "Logging last position: ");
					active[lastpos].logActive(50);
					writeLog(50, "Logging chosen position: ");
					active[chosen].logActive(50);
					throw FatalException("ERROR_MOVE_022: nwrap setting of either chosen or the "
										  "lineage wrapped before chosen. Check move function.");
				}
#endif // DEBUG
				lastpos = active[lastpos].getNext();
				while(lastpos != 0)
				{
					active[lastpos].decreaseNwrap();
					lastpos = active[lastpos].getNext();
				}

			}
			else
			{
#ifdef DEBUG
				writeLog(50, "Logging chosen");
				active[chosen].logActive(50);
#endif // DEBUG
				throw FatalException(
					"ERROR_MOVE_024: Last position before chosen is 0 - this is impossible.");
			}
			grid[oldy][oldx].decreaseNwrap();
			active[chosen].setNwrap(0);
			active[chosen].setNext(0);
			active[chosen].setListPosition(0);
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
					//					os << pos << endl;
					//					os << active[pos].getNext() << endl;
					break;
				}
			}
		}

		if(iCount != grid[oldy][oldx].getNwrap())
		{
#ifdef DEBUG
			stringstream ss;
			ss << "Nwrap: " << grid[oldy][oldx].getNwrap() << " Counted lineages: " << iCount << endl;
			writeLog(50, ss);
#endif // DEBUG
			throw FatalException("ERROR_MOVE_014: Nwrap not set correctly after move for grid cell");
		}
	}
}

void SpatialTree::calcMove()
{
	dispersal_coordinator.disperse(this_step);
}


long double SpatialTree::calcMinMax(const unsigned long& current)
{
	// this formula calculates the speciation rate required for speciation to have occured on this branch.
	// need to allow for the case that the number of gens was 0
	long double newminmax = 1;
	long double oldminmax = active[current].getMinmax();
	if(data[active[current].getReference()].getGenRate() == 0)
	{
		newminmax = data[active[current].getReference()].getSpecRate();
	}
	else
	{
		// variables need to be defined separately for the decimal division to function properly.
		long double tmpdSpec = data[active[current].getReference()].getSpecRate();
		long double tmpiGen = data[active[current].getReference()].getGenRate();
		newminmax = 1 - (pow(1 - tmpdSpec, (1 / tmpiGen)));
	}
	long double toret = min(newminmax, oldminmax);
	return toret;
}



void SpatialTree::calcNewPos(bool& coal,
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
			throw FatalException(
				"ERROR_MOVE_006: NON FATAL. Nwrap not set correctly. Check move programming function.");
		}
		// then the procedure is relatively simple.
		// check for coalescence
		// check if the grid needs to be updated.
		if(grid[oldy][oldx].getMaxsize() != habitat_map.getVal(oldx, oldy, oldxwrap, oldywrap, generation))
		{
			grid[oldy][oldx].setMaxsize(habitat_map.getVal(oldx, oldy, 0, 0, generation));
		}
		coalchosen = grid[oldy][oldx].getRandLineage(NR);
#ifdef DEBUG
		if(coalchosen != 0)
		{
			if(active[coalchosen].getXpos() != (unsigned long)oldx ||
			   active[coalchosen].getYpos() != (unsigned long)oldy ||
			   active[coalchosen].getXwrap() != oldxwrap || active[coalchosen].getYwrap() != oldywrap)
			{
				writeLog(50, "Logging chosen:");
				active[chosen].logActive(50);
				writeLog(50, "Logging coalchosen: ");
				active[coalchosen].logActive(50);
				throw FatalException("ERROR_MOVE_006: NON FATAL. Nwrap not set correctly. Please report this bug.");
			}
		}
#endif
		if(coalchosen == 0)  // then the lineage can be placed in the empty space.
		{
			long tmplistindex = grid[oldy][oldx].addSpecies(chosen);
			// check
			if(grid[oldy][oldx].getSpecies(tmplistindex) != chosen)
			{
				throw FatalException("ERROR_MOVE_005: Grid index not set correctly for species. Check "
									  "move programming function.");
			}
#ifdef pristine_mode
			if(grid[oldy][oldx].getListsize() > grid[oldy][oldx].getMaxsize())
			{
				throw FatalException(
					"ERROR_MOVE_001: Listpos outside maxsize. Check move programming function.");
			}
#endif
			active[chosen].setNwrap(0);
			active[chosen].setListPosition(tmplistindex);
			coal = false;
		}
		else  // then coalescence has occured
		{
			active[chosen].setNwrap(0);
			active[chosen].setListPosition(0);
			// DO THE COALESCENCE STUFF
			coal = true;
		}
	}
	else  // need to check all the possible places the lineage could be.
	{
		if(nwrap != 0)
		{
			throw FatalException("ERROR_MOVE_022: Nwrap not set correctly in move.");
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
#ifdef DEBUG
				if(active[next_active].getNwrap() != 1)
				{
					throw FatalException("ERROR_MOVE_022a: Nwrap not set correctly in move.");
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
					throw FatalException("ERROR_MOVE_022d: Nwrap not set correctly in move.");
				}
#endif
			}
			if(nwrap != ncount)
			{
				throw FatalException("ERROR_MOVE_022c: Nwrap not set correctly in move.");
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
				active[chosen].setListPosition(0);
			}
			else  // if there were matches, generate a random number to see if coalescence occured or not
			{
				unsigned long randwrap =
					floor(NR.d01() * (habitat_map.getVal(oldx, oldy, oldxwrap, oldywrap, generation)) + 1);
// Get the random reference from the match list.
// If the movement is to an empty space, then we can update the chain to include the new
// lineage.
#ifdef pristine_mode
				if(randwrap > habitat_map.getVal(oldx, oldy, oldxwrap, oldywrap, generation))
				{
					throw FatalException(
						"ERROR_MOVE_004: Randpos outside maxsize. Check move programming function");
				}
				if(matches > habitat_map.getVal(oldx, oldy, oldxwrap, oldywrap, generation))
				{
					cerr << "matches: " << matches << endl
						 << "habitat_map value: "
						 << habitat_map.getVal(oldx, oldy, oldxwrap, oldywrap, generation);
					throw FatalException(
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
					active[chosen].setListPosition(0);
				}
				else  // coalescence has occured
				{
					coal = true;
					coalchosen = matchlist[randwrap - 1];
					active[chosen].setEndpoint(oldx, oldy, oldxwrap, oldywrap);
					if(coalchosen == 0)
					{
						throw FatalException(
							"ERROR_MOVE_025: Coalescence attempted with lineage of 0.");
					}
				}
			}
#ifdef pristine_mode
			if(grid[oldy][oldx].getMaxsize() < active[chosen].getListpos())
			{
				throw FatalException(
					"ERROR_MOVE_001: Listpos outside maxsize. Check move programming function.");
			}
#endif
		}
		else  // just add the lineage to next.
		{
			if(grid[oldy][oldx].getNext() != 0)
			{
				throw FatalException("ERROR_MOVE_026: No nwrap recorded, but next is non-zero.");
			}
			coalchosen = 0;
			coal = false;
			grid[oldy][oldx].setNext(chosen);
			active[chosen].setNwrap(1);
			active[chosen].setNext(0);
			grid[oldy][oldx].increaseNwrap();
// check
#ifdef DEBUG
			if(grid[oldy][oldx].getNwrap() != 1)
			{
				throw FatalException("ERROR_MOVE_022b: Nwrap not set correctly in move.");
			}
#endif
		}
		if(coalchosen != 0)
		{
			if(active[coalchosen].getXpos() != (unsigned long)oldx ||
			   active[coalchosen].getYpos() != (unsigned long)oldy ||
			   active[coalchosen].getXwrap() != oldxwrap || active[coalchosen].getYwrap() != oldywrap)
			{
#ifdef DEBUG
				writeLog(50, "Logging chosen:");
				active[chosen].logActive(50);
				writeLog(50, "Logging coalchosen: ");
				active[coalchosen].logActive(50);
#endif // DEBUG
				throw FatalException("ERROR_MOVE_006b: NON FATAL. Nwrap not set correctly. Check move "
									  "programming function.");
			}
		}
		//#endif
	}
}

void SpatialTree::switchPositions(const unsigned long &chosen)
{
#ifdef DEBUG
	if(chosen > endactive)
	{
		stringstream ss;
		ss << "chosen: " << chosen << " endactive: " << endactive << endl;
		writeLog(50, ss);
		throw FatalException("ERROR_MOVE_023: Chosen is greater than endactive. Check move function.");
	}
#endif // DEBUG
	if(chosen != endactive)
	{
		// This routine assumes that the previous chosen position has already been deleted.
		DataPoint tmpdatactive;
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
			//				os << "wrap"<<endl;
			long tmpactive = grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext();
			unsigned long tmpnwrap = active[endactive].getNwrap();

			// if the wrapping is just once, we need to set the grid next to the chosen variable.
			if(tmpnwrap == 1)
			{
				// check
				if(grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext() != endactive)
				{
					throw FatalException(string(
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
				unsigned long tmpcount = 0;
				// loop over nexts until we reach the right lineage.
				while(active[tmpactive].getNext() != endactive)
				{
					tmpactive = active[tmpactive].getNext();
					tmpcount++;
#ifdef DEBUG
					if(tmpcount > tmpnwrap)
					{
						writeLog(30, "ERROR_MOVE_013: NON FATAL. Looping has not encountered a match, "
								"despite going further than required. Check nwrap counting.");
						if(tmpactive == 0)
						{
							stringstream ss;
							ss << "gridnext: "
								 << grid[active[endactive].getYpos()][active[endactive]
																		  .getXpos()]
										.getNext()
								 << endl;
							ss << "endactive: " << endactive << endl;
							ss << "tmpactive: " << tmpactive << endl;
							ss << "tmpnwrap: " << tmpnwrap << " tmpcount: " << tmpcount
								 << endl;
							writeLog(50, ss);
							writeLog(50, "Logging chosen:");
							active[chosen].logActive(50);
							throw FatalException("No match found, please report this bug.");
						}
					}
#endif // DEBUG
				}
				active[tmpactive].setNext(chosen);
			}
			active[chosen].setup(active[endactive]);
			active[endactive].setup(tmpdatactive);

			// check - debugging
			unsigned long testwrap = active[chosen].getNwrap();
			unsigned long testnext = grid[active[chosen].getYpos()][active[chosen].getXpos()].getNext();
			for(unsigned long i = 1; i < testwrap; i++)
			{
				testnext = active[testnext].getNext();
			}

			if(testnext != chosen)
			{
				throw FatalException("ERROR_MOVE_009: Nwrap position not set correctly after coalescence. "
									  "Check move process.");
			}
		}
	}
	endactive--;
}

void SpatialTree::calcNextStep()
{
	calcMove();
	// Calculate the new position, perform the move if coalescence doesn't occur or
	// return the variables for the coalescence event if coalescence does occur.
	active[this_step.chosen].setEndpoint(this_step.oldx, this_step.oldy,
										 this_step.oldxwrap,
										 this_step.oldywrap);
	calcNewPos(this_step.coal, this_step.chosen, this_step.coalchosen, this_step.oldx,
			   this_step.oldy, this_step.oldxwrap, this_step.oldywrap);
}

unsigned long SpatialTree::estSpecnum()
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
			data[i].setExistence(true);
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
		if(data[i].getSpecRate() < (1 - pow(double(1 - dMinmax), maxret)))
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
			if(data[i].getExistence() && !data[data[i].getParent()].getExistence() && !data[i].hasSpeciated())
			{
				loop = true;
				data[data[i].getParent()].setExistence(true);
			}
		}
	}
	unsigned long iSpecies = 0;
	for(unsigned int i = 0; i <= enddata; i++)
	{
		if(data[i].getExistence() && data[i].hasSpeciated())
		{
			iSpecies++;
		}
	}
	for(unsigned int i = 0; i <= enddata; i++)
	{
		data[i].qReset();
	}
	//		os << "Estimated species number is: " << iSpecies << endl;
	return iSpecies;
}

#ifdef pristine_mode
void SpatialTree::pristineStepChecks()
{
	if(habitat_map.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap, this_step.oldywrap, generation) == 0)
	{
		cerr << "x,y: " << this_step.oldx << "," << this_step.oldy << " xwrap, ywrap: " << this_step.oldxwrap;
		cerr << "," << this_step.oldywrap << endl;
		cerr << "listsize: " << grid[this_step.oldy][this_step.oldx].getListsize()
			 << "maxsize: " << grid[this_step.oldy][this_step.oldx].getMaxsize() << endl;
		throw FatalException(
			string("ERROR_MOVE_008: Dispersal attempted from non-forest. Check dispersal function. Forest "
				   "cover: " +
				   to_string((long long)habitat_map.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap,
														 this_step.oldywrap, generation))));
	}
}
#endif


void SpatialTree::incrementGeneration()
{
	Tree::incrementGeneration();
	habitat_map.updateMap(generation);
	checkTimeUpdate();
	// check if the map is pristine yet
	habitat_map.checkPristine(generation);

}
#ifdef DEBUG
void SpatialTree::debugDispersal()
{
	if(habitat_map.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap, this_step.oldywrap, generation) == 0)
	{
		throw FatalException(
			string("ERROR_MOVE_007: Dispersal attempted to non-forest. "
				   "Check dispersal function. Forest cover: " +
				   to_string((long long)habitat_map.getVal(this_step.oldx, this_step.oldy, this_step.oldxwrap,
														 this_step.oldywrap, generation))));
	}
}

#endif

void SpatialTree::updateStepCoalescenceVariables()
{
	Tree::updateStepCoalescenceVariables();
	while(!rep_map.hasReproduced(NR, active[this_step.chosen].getXpos(), active[this_step.chosen].getYpos(),
								 active[this_step.chosen].getXwrap(), active[this_step.chosen].getYwrap()))
	{
		this_step.chosen = NR.i0(endactive - 1) + 1;  // cannot be 0
	}
	// record old position of lineage
	this_step.oldx = active[this_step.chosen].getXpos();
	this_step.oldy = active[this_step.chosen].getYpos();
	this_step.oldxwrap = active[this_step.chosen].getXwrap();
	this_step.oldywrap = active[this_step.chosen].getYwrap();
#ifdef pristine_mode
	pristineStepChecks();
#endif
}

void SpatialTree::addLineages(double generation_in)
{
	// First loop over the grid to check for the number that needs to be added to active
	unsigned long added_active = 0;
	unsigned long added_data = 0;
	// Update the sample grid boolean mask, if required.
	if(sim_parameters.uses_spatial_sampling)
	{
		samplegrid.convertBoolean(habitat_map, deme_sample, generation_in);
	}
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
				unsigned long num_to_add = countCellExpansion(x, y, xwrap, ywrap, generation_in, false);
				added_data += getIndividualsSampled(x, y, xwrap, ywrap, generation_in) - num_to_add;
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
				unsigned long num_to_add = countCellExpansion(x, y, xwrap, ywrap, generation_in, true);
				expandCell(x, y, xwrap, ywrap, generation_in, num_to_add);
			}
		}
	}
	// double check sizes
	if(enddata >= data.size() || endactive >= active.size())
	{
		throw FatalException("ERROR_MAIN_012: FATAL. Enddata or endactive is greater than the size of the "
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

string SpatialTree::simulationParametersSqlInsertion()
{
	string to_execute;
	to_execute = "INSERT INTO SIMULATION_PARAMETERS VALUES(" + to_string((long long)the_seed) + "," +
				 to_string((long long)the_task);
	to_execute += ",'" + out_directory + "'," + boost::lexical_cast<std::string>((long double)spec) + "," +
				  to_string((long double)sigma) + ",";
	to_execute += to_string((long double)tau) + "," + to_string((long long)deme) + ",";
	to_execute += to_string((long double)deme_sample) + "," + to_string((long long)maxtime) + ",";
	to_execute += to_string((long double)dispersal_relative_cost) + "," + to_string((long long)desired_specnum) + ",";
	to_execute += to_string((long double)sim_parameters.habitat_change_rate) + ",";
	to_execute += to_string((long double)sim_parameters.gen_since_pristine) + ",'" + sim_parameters.times_file + "','";
	to_execute += coarse_map_input + "'," + to_string((long long)coarse_map_x_size) + ",";
	to_execute += to_string((long long)coarse_map_y_size) + "," + to_string((long long)coarse_map_x_offset) + ",";
	to_execute += to_string((long long)coarse_map_y_offset) + "," + to_string((long long)coarse_map_scale) + ",'";
	to_execute += fine_map_input + "'," + to_string((long long)fine_map_x_size) + "," + to_string((long long)fine_map_y_size);
	to_execute += "," + to_string((long long)fine_map_x_offset) + "," + to_string((long long)fine_map_y_offset) + ",'";
	to_execute += sim_parameters.samplemaskfile + "'," + to_string((long long)grid_x_size) + "," +
				  to_string((long long) grid_y_size) + "," + to_string((long long) sim_parameters.varsamplexsize) + ", ";
	to_execute += to_string((long long) sim_parameters.varsampleysize) + ", ";
	to_execute += to_string((long long) sim_parameters.varsamplexoffset) + ", ";
	to_execute += to_string((long long) sim_parameters.varsampleyoffset) + ", '";
	to_execute += pristine_coarse_map_input + "','" + pristine_fine_map_input + "'," + to_string(sim_complete);
	to_execute += ", '" + sim_parameters.dispersal_method + "', ";
	to_execute += boost::lexical_cast<std::string>(sim_parameters.m_prob) + ", ";
	to_execute += to_string((long double)sim_parameters.cutoff) + ", ";
	to_execute += to_string(sim_parameters.restrict_self) + ", '";
	to_execute += sim_parameters.landscape_type + "', ";
	// Now save the protracted speciation variables (not relevant in this simulation scenario)
	to_execute += protractedVarsToString();
	to_execute += ", '" + sim_parameters.dispersal_file + "'";
	to_execute += ");";
	return to_execute;
}

void SpatialTree::simPause()
{
	// Completely changed how this sections works - it won't currently allow restarting of the simulations, but will
	// dump the data file to memory. - simply calls sqlCreate and sqlOutput.
	// sqlCreate();
	// sqlOutput();

	// This function saves the data to 4 files. One contains the main simulation parameters, the other 3 contain the
	// simulation results thus far
	// including the grid object, data object and active object.
	string pause_folder = initiatePause();
	dumpMain(pause_folder);
	dumpActive(pause_folder);
	dumpData(pause_folder);
	dumpMap(pause_folder);
	completePause();
}

void SpatialTree::dumpMap(string pause_folder)
{
	try
	{
		// Output the data object
		ofstream out4;
		string file_to_open = pause_folder + "Dump_map_" + to_string(the_task) + "_" + to_string(the_seed) + ".csv";
		out4 << setprecision(64);
		out4.open(file_to_open.c_str());
		out4 << habitat_map;
		out4.close();
	}
	catch(exception& e)
	{
		cerr << e.what() << endl;
		cerr << "Failed to perform map dump to " << pause_folder << endl;
	}
}

void SpatialTree::simResume()
{
	initiateResume();
	// now load the objects
	loadMainSave();
	loadMapSave();
	setObjectSizes();
	loadActiveSave();
	loadDataSave();
	loadGridSave();
	time(&sim_start);
	writeInfo("\rLoading data from temp file...done!\n");
	sim_parameters.printVars();
}



void SpatialTree::loadGridSave()
{
	grid.SetSize(grid_x_size, grid_y_size);
	string file_to_open;
	try
	{
		stringstream os;
		os << "\rLoading data from temp file...grid..." << flush;
		// New method for re-creating grid data from active lineages
		// First initialise the empty grid object
		writeInfo(os.str());
		for(unsigned long i = 0; i < grid_y_size; i++)
		{
			for(unsigned long j = 0; j < grid_x_size; j++)
			{
				grid[i][j].initialise(habitat_map.getVal(j, i, 0, 0, generation));
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
		msg = string(e.what()) + "Failure to import grid from " + file_to_open;
		throw FatalException(msg);
	}
}

void SpatialTree::loadMapSave()
{
	string file_to_open;
	// Input the map object
	try
	{
		stringstream os;
		os << "\rLoading data from temp file...map..." << flush;
		writeInfo(os.str());
		ifstream in5;
		file_to_open = pause_sim_directory + string("/Pause/Dump_map_") + to_string(the_task) + "_" +
					   to_string(the_seed) + string(".csv");
		in5.open(file_to_open);
		in5 >> habitat_map;
		in5.close();
		importReproductionMap();
	}
	catch(exception& e)
	{
		string msg;
		msg = string(e.what()) + "Failure to import map from " + file_to_open;
		throw FatalException(msg);
	}
}

void SpatialTree::verifyReproductionMap()
{
	if(!(sim_parameters.reproduction_file == "none" || sim_parameters.reproduction_file == "null"))
	{
		for(unsigned long i = 0; i < sim_parameters.varfinemapysize; i++)
		{
			for(unsigned long j = 0; j < sim_parameters.varfinemapxsize; j ++)
			{
				if(rep_map[i][j] == 0.0 && habitat_map.getValFine(j, i, 0.0) != 0)
				{
					throw FatalException("Reproduction map is zero where density is non-zero. "
												 "This will cause an infinite loop.");
				}
				if(habitat_map.getValFine(j, i, 0.0) == 0 && rep_map[i][j] != 0.0)
				{
					writeCritical("Density is zero where reproduction map is non-zero. This is likely incorrect.");
				}
			}
		}
	}
}

void SpatialTree::addWrappedLineage(unsigned long numstart, long x, long y)
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


unsigned long SpatialTree::countCellExpansion(const long &x, const long &y, const long &xwrap, const long &ywrap,
									   const double &generation_in, const bool& make_tips)
{
	unsigned long map_cover = habitat_map.getVal(x, y, xwrap, ywrap, generation_in); // think I fixed a bug here...
	unsigned long num_to_add = static_cast<unsigned long>(max(floor(map_cover * deme_sample *
																			samplegrid.getExactValue(x, y,
																									 xwrap, ywrap)),
															  0.0));
	if(xwrap == 0 && ywrap == 0)
	{
		unsigned long ref = 0;
		if(map_cover >= grid[y][x].getMaxsize())
		{
			grid[y][x].changePercentCover(map_cover);
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

void SpatialTree::expandCell(long x, long y, long x_wrap, long y_wrap, double generation_in, unsigned long num_to_add)
{
	if(num_to_add > 0)
	{
		for(unsigned long k = 0; k < num_to_add; k ++)
		{
			endactive ++;
			enddata ++;
			unsigned long listpos = 0;
			// Add the species to active
			if(x_wrap == 0 && y_wrap == 0)
			{
				listpos = grid[y][x].addSpecies(endactive);
				active[endactive].setup(x, y, x_wrap, y_wrap, enddata, listpos, 1);
			}
			else
			{
				active[endactive].setup(x, y, x_wrap, y_wrap, enddata, listpos, 1);
				addWrappedLineage(endactive, x, y);
			}
			if(enddata >= data.size())
			{
				throw FatalException("Cannot add lineage - no space in data. "
											  "Check size calculations.");
			}
			if(endactive >= active.size())
			{
				throw FatalException("Cannot add lineage - no space in active. "
											  "Check size calculations.");
			}

			// Add a tip in the TreeNode for calculation of the coalescence tree at the
			// end of the simulation.
			// This also contains the start x and y position of the species.
			data[enddata].setup(true, x, y, x_wrap, y_wrap, generation_in);
			data[enddata].setSpec(NR.d01());
		}
	}
}

#ifdef DEBUG
void SpatialTree::validateLineages()
{
	bool fail = false;
	writeInfo("\nStarting lineage validation...");
	unsigned long printed = 0;
	for(unsigned long i = 1; i < endactive; i++)
	{
		stringstream ss;
		DataPoint tmp_datapoint = active[i];
		// Validate the location exists
		if(habitat_map.getVal(tmp_datapoint.getXpos(), tmp_datapoint.getYpos(),
							tmp_datapoint.getXwrap(), tmp_datapoint.getYwrap(), 0.0) == 0)
		{
			if(printed < 100)
			{
				printed ++;
				ss << "Map value: " << habitat_map.getVal(tmp_datapoint.getXpos(), tmp_datapoint.getYpos(),
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
			stringstream ss;
			ss << "active reference: " << i << endl;
			ss << "Grid wrapping: " << grid[tmp_datapoint.getYpos()][tmp_datapoint.getXpos()].getNwrap() << endl;
			writeLog(50, ss);
			tmp_datapoint.logActive(50);
			throw FatalException("Failure in lineage validation. Please report this bug.");
		}
	}
	writeInfo("done\n");
}

void SpatialTree::debugAddingLineage(unsigned long numstart, long x, long y)
{
	unsigned long tmp_next = grid[y][x].getNext();
	unsigned long tmp_nwrap = 0;
	while(tmp_next != 0)
	{
		tmp_nwrap ++;
		if(active[tmp_next].getNwrap() != tmp_nwrap)
		{
			stringstream ss;
			ss << "tmp_nwrap: " << tmp_nwrap << endl;
			ss << "next = " << tmp_next << endl;
			ss << "numstart: " << numstart << endl;
			writeLog(50, ss);
			active[tmp_nwrap].logActive(50);
			throw FatalException("Incorrect setting of nwrap in wrapped lineage, please report this bug.");
		}
		tmp_next = active[tmp_next].getNext();
	}
	if(tmp_nwrap != grid[y][x].getNwrap())
	{
		stringstream ss;
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
		writeLog(50, ss);
		throw FatalException("Grid wrapping value not set correctly");
	}
}

void SpatialTree::runChecks(const unsigned long& chosen, const unsigned long& coalchosen)
{
// final checks
#ifdef pristine_mode
	if(active[chosen].getListpos() > grid[active[chosen].getYpos()][active[chosen].getXpos()].getMaxsize() &&
	   active[chosen].getNwrap() == 0)
	{
		//				usleep(1);
		cerr << "list_position: " << active[chosen].getListpos()
			 << " maxsize: " << grid[active[chosen].getYpos()][active[chosen].getXpos()].getMaxsize() << endl;
		throw FatalException("ERROR_MOVE_001: Listpos outside maxsize.");
	}

	if(active[coalchosen].getListpos() >
		   grid[active[coalchosen].getYpos()][active[coalchosen].getXpos()].getMaxsize() &&
	   active[coalchosen].getNwrap() == 0 && coalchosen != 0)
	{
		//				usleep(1);
		throw FatalException("ERROR_MOVE_002: Coalchosen list_position outside maxsize.");
	}
#endif
	Tree::runChecks(chosen, coalchosen);
	if(active[chosen].getNwrap() != 0)
	{
		unsigned long tmpactive = grid[active[chosen].getYpos()][active[chosen].getXpos()].getNext();
		for(unsigned long i = 1; i < active[chosen].getNwrap(); i++)
		{
			tmpactive = active[tmpactive].getNext();
		}

		if(tmpactive != chosen)
		{
			active[chosen].logActive(50);
			throw FatalException("ERROR_MOVE_003: Nwrap not set correctly.");
		}
	}

	if(active[chosen].getNwrap() != 0)
	{
		if(active[chosen].getXwrap() == 0 && active[chosen].getYwrap() == 0)
		{
			throw FatalException("ERROR_MOVE_10: Nwrap set to non-zero, but x and y wrap 0.");
		}
	}
	if(active[endactive].getNwrap() != 0)
	{
		unsigned long nwrap = active[endactive].getNwrap();
		if(nwrap == 1)
		{
			if(grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext() != endactive)
			{
				stringstream ss;
				ss << "Lineage at 1st position: "
				   << grid[active[endactive].getYpos()][active[endactive].getXpos()].getNext() << endl;
				ss << "endactive: " << endactive << endl
				   << "nwrap: " << nwrap << endl;
				ss << "chosen: " << chosen << endl;
				writeLog(10, ss);
				throw FatalException("ERROR_MOVE_016: Nwrap for endactive not set correctly. Nwrap is 1, "
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
					stringstream ss;
					ss << "ERROR_MOVE_017: NON FATAL. Nrap for endactive not set correctly; looped "
							"beyond nwrap and not yet found enactive."
					   << endl;
					ss << "endactive: " << endactive << endl
					   << "nwrap: " << nwrap << endl
					   << "x,y: " << active[endactive].getXpos() << "," << active[endactive].getYpos()
					   << endl;
					ss << "chosen: " << chosen << endl;
					writeLog(10, ss);
				}
			}
			if(tmpnwrap != nwrap)
			{
				stringstream ss;
				ss << "ERROR_MOVE_018: NON FATAL. Nwrap for endactive not set correctly. Nwrap is "
				   << nwrap << " but endactive is at position " << tmpnwrap << endl;
				ss << "endactive: " << endactive << endl
				   << "nwrap: " << nwrap << endl
				   << "x,y: " << active[endactive].getXpos() << "," << active[endactive].getYpos()
				   << endl;
				ss << "chosen: " << chosen << endl;
				writeLog(10, ss);
			}
		}
	}
}

#endif

