//This file is part of NECSim project which is released under BSD-3 license.
//See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
/**
 * @author Samuel Thompson
 * @date 31/08/16
 * @file Community.cpp
 *
 * @brief Contains the Community object, which is used for reconstructing the coalescence tree after simulations are complete.
 *
 * For use with Coal_sim 3.1 and above.
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 */

#ifndef TREELIST
#define TREELIST

#include <cmath>
#include <sqlite3.h>
#include <cstring>
#include <cmath>
#include <stdexcept>
#include <string>
# include <boost/filesystem.hpp>
#include <boost/lexical_cast.hpp>
#include <set>

#include "TreeNode.h"
#include "Matrix.h"
#include "DataMask.h"
#include "SpecSimParameters.h"

using namespace std;
using std::string;

/**
 * @brief Checks whether speciation has occured for the provided parameters. 
 * Provided here for ease of use when bug-fixing.
 * @param random_number the random number associated with a lineage
 * @param speciation_rate the global speciation rate
 * @param number_of_generations the number of generations the lineage has existed
 * @return bool the speciation state of the lineage
 */
bool checkSpeciation(const long double &random_number, const long double &speciation_rate,
					 const unsigned long &no_generations);

/**
 * @brief Compares two doubles and returns a boolean of whether they are equal, within the epsilon deviation.
 * This is useful for floating point errors in saving and reading doubles from file.
 * @param d1 the first double.
 * @param d2 the second double.
 * @param epsilon the deviation within which the values are assumed to be equal.
 * @return true if the doubles are within epsilon of each other
 */
bool doubleCompare(double d1, double d2, double epsilon);

/**
 * @brief Compares two doubles and returns a boolean of whether they are equal, within the epsilon deviation.
 * This is useful for floating point errors in saving and reading doubles from file.
 * Overloaded version for long doubles.
 * @param d1 the first double.
 * @param d2 the second double.
 * @param epsilon the deviation within which the values are assumed to be equal.
 * @return true if the doubles are within epsilon of each other
 */
bool doubleCompare(long double d1, long double d2, long double epsilon);

/**
 * @brief Compares two doubles and returns a boolean of whether they are equal, within the epsilon deviation.
 * This is useful for floating point errors in saving and reading doubles from file.
 * Overloaded version for long doubles and double epsilon.
 * @param d1 the first double.
 * @param d2 the second double.
 * @param epsilon the deviation within which the values are assumed to be equal.
 * @return true if the doubles are within epsilon of each other
 */
bool doubleCompare(long double d1, long double d2, double epsilon);

/**
 * @brief A struct for containing pairs of previous calculations to make sure that aren't repeated.
 */
struct CommunityParameters
{
	unsigned long reference;
	long double speciation_rate;
	long double time;
	bool fragment;
	unsigned long metacommunity_reference; // will be 0 if no metacommunity used.
	bool updated; // set to true if the fragment reference needs updating in the database

	CommunityParameters()
	{
		reference = 0;
		speciation_rate = 0.0;
		time = 0.0;
		fragment = false;
		metacommunity_reference = 0;
		updated = false;
	}

	/**
	 * @brief Constructor for CommunityParameters, for storing a pairs of previous calculations, requiring a speciation rate
	 * and a time.
	 * Overloaded version with setup routines.
	 * @param reference_in the reference to set for this CommunityParameters set
	 * @param speciation_rate_in the speciation rate of the previous calculation
	 * @param time_in the time of the previous calculation
	 * @param fragment_in bool of whether fragments  were used in the previous calculation
	 * @param metacommunity_reference_in the metacommunity reference, or 0 for no metacommunity
	 */
	CommunityParameters(unsigned long reference_in, long double speciation_rate_in, long double time_in,
						bool fragment_in, unsigned long metacommunity_reference_in);

	/**
	 * @brief Sets up the CommunityParameters object
	 * @param reference_in the reference to set for this CommunityParameters set
	 * @param speciation_rate_in the speciation rate of the previous calculation
	 * @param time_in the time of the previous calculation
	 * @param fragment_in bool of whether fragments  were used in the previous calculation
	 * @param metacommunity_reference_in the metacommunity reference, or 0 for no metacommunity
	 */
	void setup(unsigned long reference_in, long double speciation_rate_in, long double time_in,
			   bool fragment_in, unsigned long metacommunity_reference_in);

	/**
	 * @brief Compare these set of parameters with the input set. If they match, return true, otherwise return false
	 * @param speciation_rate_in speciation rate to compare with stored community parameter
	 * @param time_in time to compare with stored community parameter
	 * @param fragment_in if fragments are being used on this database
	 * @param metacommunity_reference_in metacommunity reference to compare with stored community parameter
	 * @return
	 */
	bool compare(long double speciation_rate_in, long double time_in, bool fragment_in,
				 unsigned long metacommunity_reference_in);

	/**
	 * @brief Compare these set of parameters with the input set. If they match, return true, otherwise return false
	 * Overloaded version ignoring the fragments parameter
	 * @param speciation_rate_in speciation rate to compare with stored community parameter
	 * @param time_in time to compare with stored community parameter
	 * @param metacommunity_reference_in metacommunity reference to compare with stored community parameter
	 * @return
	 */
	bool compare(long double speciation_rate_in, long double time_in, unsigned long metacommunity_reference_in);

	/**
	 * @brief Checks if the supplied reference is the same in the community parameter
	 * @param reference_in
	 * @return
	 */
	bool compare(unsigned long reference_in);
};

/**
 * @brief A structure for containing an array of previous calculation information, including which fragments have been 
 * already calculated for.
 */
struct CommunitiesArray
{
	vector<CommunityParameters> calc_array;

	/**
	 * @brief Adds an extra CommunityParameters object to the calc_array vector with the supplied variables
	 * @param reference the reference for this set of community parameters
	 * @param speciation_rate the speciation rate of the past calculation
	 * @param time the time of the past calculation
	 * @param fragment bool of whether fragments were used in the past calculation
	 * @param metacommunity_reference reference for the metacommunity parameters, or 0 if no metacommunity
	 */
	void pushBack(unsigned long reference, long double speciation_rate, long double time, bool fragment,
				  unsigned long metacommunity_reference);

	/**
	 * @brief Adds the provided CommunityParameters object to the calc_array vector
	 * @param tmp_param the set of community parameters to add
	 */
	void pushBack(CommunityParameters tmp_param);

	/**
	 * @brief Adds a new communities calculation paremeters reference, with a new unique reference
	 * @param speciation_rate the speciation rate of the new calculation
	 * @param time the time used in the new calculation
	 * @param fragment true if fragments were used in the new calculation
	 * @return reference to the new CommunityParameters object added
	 */
	CommunityParameters &addNew(long double speciation_rate, long double time, bool fragment,
								unsigned long metacommunity_reference);

	/**
	 * @brief Checks whether the calculation with the supplied variables has already been performed.
	 *
	 * @note
	 * @param speciation_rate the speciation rate to check for
	 * @param time the time to check for
	 * @param fragment bool for checking if fragments were used
	 * @return true if the reference exists in past community parameters
	 */
	bool hasPair(long double speciation_rate, double time, bool fragment, unsigned long metacommunity_reference);

};

struct MetacommunityParameters
{
	unsigned long reference;
	unsigned long metacommunity_size;
	long double speciation_rate;

	/**
	 * @brief Constructor for MetacommunityParameters, storing a previously applied metacommunity
	 * @param reference_in the metacommunity reference number
	 * @param speciation_rate_in the speciation rate used for metacommunity generation
	 * @param metacommunity_size_in size of the tested metacommunity
	 */
	MetacommunityParameters(unsigned long reference_in, long double speciation_rate_in,
							unsigned long metacommunity_size_in);

	/**
	 * @brief Compare these set of parameters with the input set. If they match, return true, otherwise return false
	 * @param speciation_rate_in speciation rate to compare with stored community parameter
	 * @param metacommunity_size_in size of the tested metacommunity
	 * @return
	 */
	bool compare(long double speciation_rate_in, unsigned long metacommunity_size_in);

	/**
	 * @brief Checks if the supplied reference is the same in the metacommunity reference
	 * @param reference_in the reference to check against
	 * @return
	 */
	bool compare(unsigned long reference_in);
};

struct MetacommunitiesArray
{
	vector<MetacommunityParameters> calc_array;

	/**
	 * @brief Adds an extra CommunityParameters object to the calc_array vector with the supplied variables
	 * @param reference the reference for this set of metacommunity parameters
	 * @param speciation_rate the speciation rate used in generation of the metacommunity
	 * @param metacommunity_size the size of the metacommunity used
	 */
	void pushBack(unsigned long reference, long double speciation_rate, unsigned long metacommunity_size);

	/**
	 * @brief Adds the provided PastMetacommunityParameters object to the calc_array vector
	 * @param tmp_param the set of metacommunity parameters to add
	 */
	void pushBack(MetacommunityParameters tmp_param);

	/**
	 * @brief Adds a new metacommunities calculation paremeters reference, with a new unique reference
	 * @param speciation_rate the speciation rate of the new calculation
	 * @param metacommunity_size the size of the metacommunity in the new calculation
	 * @return the new reference number, which should be unique
	 */
	unsigned long addNew(long double speciation_rate, unsigned long metacommunity_size);

	/**
	 * @brief Checks whether the calculation with the supplied variables has already been performed.
	 * @param speciation_rate the speciation rate to check for
	 * @param metacommunity_size the size of metacommunity to check for
	 * @return true if the reference exists in past metacommunity parameters
	 */
	bool hasPair(long double speciation_rate, unsigned long metacommunity_size);

	/**
	 * @brief Checks whether the calculation with the supplied reference has already been performed.
	 * Overloaded version for checking references.
	 * @param reference the reference to check for in past metacommunity parameters
	 * @return true if the reference exists in past metacommunity parameters
	 */
	bool hasPair(unsigned long reference);

	/**
	 * @brief Gets the metacommunity reference for the provided parameters, or returns 0 if it doesn't exist
	 * @param speciation_rate the metacommunity speciation rate to obtain for
	 * @param metacommunity_size the metacommunity size to apply for
	 * @param fragment bool for checking if fragments were used
	 * @return the metacommunity reference number, or 0 if it doesn't exist
	 */
	unsigned long getReference(long double speciation_rate, unsigned long metacommunity_size);
};

// A class containing the fragment limits as x,y coordinates.
/**
 * @struct Fragment
 * @brief Contains the information needed for defining a fragment.
 * Fragments can be detected from the Samplematrix object (which only detects rectangular fragments), or (preferably) is read from an input file.
 * Currently all fragments must be rectangular, although they can be larger than the intended shape if necesssary.
 */
struct Fragment
{
	// the name for the fragment (for reference purposes)
	string name;
	// coordinates for the extremes of the site
	long x_east, x_west, y_north, y_south;
	// the number of lineages in the fragment.
	unsigned long num;
	double area;
};

// Class for creating the sample matrix object for easy referencing

/**
 * @class Samplematrix
 * @brief A child of the Matrix class as booleans.
 * Used for determining where to sample species from.
 */
class Samplematrix : public DataMask
{
private:
	bool bIsNull;
	bool bIsFragment;
	Fragment fragment;
public:
	/**
	 * @brief Inherit construction from the Matrix class, but also set the booleans.
	 */
	Samplematrix();

//	/**
//	 * @brief Returns the value at the x,y position.
//	 * This is used for testing purposes only.
//	 * @param xval the x coordinate.
//	 * @param yval the y coordinate
//	 * @param xwrap the x wrapping
//	 * @param ywrap the y wrapping
//	 * @return the value at x,y.
//	 */
	bool getTestVal(unsigned long xval, unsigned long yval, long xwrap, long ywrap);

	/**
	 * @brief Returns the value at the x,y position, with the given x and y wrap.
	 * Also checks whether or not the map is set to null, or whether the value comes from within a fragment.
	 * @param x1 the x coordinate.
	 * @param y1 the y coordinate
	 * @return the value at x,y.
	 */
	bool getMaskVal(unsigned long x1, unsigned long y1, long x_wrap, long y_wrap);

	/**
	 * @brief Set the fragment for the samplemask to some calculated fragment. 
	 * This can be set multiple times.
	 * @param fragment_in the Fragment to set the samplemask to.
	 */
	void setFragment(Fragment &fragment_in);

	/**
	 * @brief Removes the fragment.
	 */
	void removeFragment();
};

/**
 * @class Community
 * @brief A class to contain the tree object lineages and reconstructing the coalescence tree.
 * Contains functions for calculating the number of species for a given speciation rate,
 * outputting spatial data and generating species abundance distributions.
 * Requires a link to the SQLite database from simulation output,
 * and produces results within the same database file.
 */
class Community
{
protected:
	bool bMem; // boolean for whether the database is in memory or not.
	bool bFileSet; // boolean for whether the database has been set already.
	sqlite3 *database; // stores the in-memory database connection.
	sqlite3 *outdatabase; // stores the file database connection
	bool bSqlConnection; // true if the data connection has been established.
	Row<TreeNode> *nodes; // in older versions this was called list. Changed to avoid confusion with the built-in class.
	Row<unsigned long> rOut;
	unsigned long iSpecies;
	bool bSample; // checks whether the samplemask has already been imported.
	bool bDataImport; // checks whether the main sim data has been imported.
	Samplematrix samplemask; // the samplemask object for defining the areas we want to sample from.
	vector<Fragment> fragments; // a vector of fragments for storing each fragment's coordinates.
	CommunityParameters *current_community_parameters;
	// the minimum speciation rate the original simulation was run with (this is read from the database SIMULATION_PARAMETERS table)
	long double min_spec_rate;
	// The dimensions of the sample grid size.
	unsigned long grid_x_size, grid_y_size;
	// The dimensions of the original sample map file
	unsigned long samplemask_x_size, samplemask_y_size, samplemask_x_offset, samplemask_y_offset;
	// Vector containing past speciation rates
	CommunitiesArray past_communities;
	MetacommunitiesArray past_metacommunities;
	// Protracted speciation parameters
	bool protracted;
	double min_speciation_gen, max_speciation_gen, applied_min_speciation_gen, applied_max_speciation_gen;
	unsigned long max_species_id, max_fragment_id, max_locations_id;
	// Does not need to be stored during simulation pause
	SpecSimParameters *spec_sim_parameters;
public:

	/**
	 * @brief Contructor for the community linking to Treenode list.
	 * @param r Row of TreeNode objects to link to.
	 */
	Community(Row<TreeNode> *r) : nodes(r)
	{
		bMem = false;
		iSpecies = 0;
		bSample = false;
		bSqlConnection = false;
		bFileSet = false;
		bDataImport = false;
		min_speciation_gen = 0.0;
		max_speciation_gen = 0.0;
		applied_max_speciation_gen = 0.0;
		protracted = false;
		current_community_parameters = nullptr;
		max_species_id = 0;
		max_locations_id = 0;

	}

	/**
	 * @brief Default constructor
	 */
	Community()
	{
		bMem = false;
		iSpecies = 0;
		bSample = false;
		bSqlConnection = false;
		bFileSet = false;
		bDataImport = false;
		min_speciation_gen = 0.0;
		max_speciation_gen = 0.0;
		applied_max_speciation_gen = 0.0;
		protracted = false;
		current_community_parameters = nullptr;
		max_species_id = 0;
		max_locations_id = 0;
	}

	/**
	 * @brief Default destructor
	 */
	~Community()
	{
		nodes = nullptr;
	}

	/**
	 * @brief Set the nodes object to the input Row of Treenode objects.
	 * @param l the Row of Treenode objects to link to.
	 */
	void setList(Row<TreeNode> *l);

	/**
	 * @brief Sets the database object for the sqlite functions.
	 * @param dbin the sqlite3 input database.
	 */
	void setDatabase(sqlite3 *dbin);

	/**
	 * @brief Get the boolean of whether the data has been imported yet.
	 * @return true if database has been imported.
	 */
	bool hasImportedData();

	/**
	 * @brief Get the minimum speciation rate the simulation was originally run with.
	 * This value is read in from the SIMULATION_PARAMETERS table in the database file.
	 * @return the minimum speciation rate.
	 */
	long double getMinimumSpeciation();

	/**
	 * @brief Imports the samplemask if it hasn't already been imported.
	 * @param sSamplemask the path to the samplemask file.
	 */
	void importSamplemask(string sSamplemask);

	/**
	 * @brief Counts the number of species that have speciated currently on the tree.
	 * 
	 * @return the number of species
	 */
	unsigned long countSpecies();

	/**
	 * @brief Calculate the number of species in the list for the parameters in the current_community_parameters object.
	 * This is the main function which reconstructs the coalescence tree. 
	 * Each Treenode object will end having its existence value set correctly after a call to this function.

	 * @return the number of species present.
	 */
	unsigned long calcSpecies();

	/**
	 * @brief Speciates TreeNode and updates the species count.
	 *
	 * For systems which are not using a metacommunity, this function will just perform basic speciation.
	 *
	 * @note species_list is not updated in unless the function is overridden for metacommunity application.
	 * @param species_count the total number of species currently in the community
	 * @param treenode pointer to the TreeNode object for this lineage
	 * @param species_list the set of all species ids.
	 */
	virtual void addSpecies(unsigned long &species_count, TreeNode *treenode, set<unsigned long> &species_list);

	/**
	 * @brief Calculates the species abundance of the dataset.
	 * The species abundances will be with rOut after a call do this function.
	 * If a samplemask has been applied, only lineages which originally existed in the samplemask will be counted.
	 */
	void calcSpeciesAbundance();

	/**
	 * @brief Resets the entire tree.
	 * Sets existance to false, speciation to false and removes any species ID.
	  */
	virtual void resetTree();

	/**
	 * @brief This function detects the maximum x and y values of the sql database.
	 * This allows for the dimensions before opening the map file.
	 * @deprecated This function is deprecated as of 08/2016 due to simulation parameters being stored in the SQL database.
	 * @bug If species do not exist across the whole range of the samplemask, samplemask size will not be set correctly 
	 * and samplemask referencing may be incorrect.
	 * @param db the path to the input database to read from.
	 */
	void detectDimensions(string db);

	/**
	 * @brief Opens the connection to the sql database file
	 * Note that this imports the database to memory, so functionality should be changed for extremely large database 
	 * files.
	 * @param inputfile the sql database output from a NECSim simulation.
	 */
	void openSqlConnection(string inputfile);

	/**
	 * @brief Internally sets the file referencing, data import and sql connection flags to true, for allowing checks
	 * to pass from internal object creation (so no external files are needed)
	 */
	void internalOption();

	/**
	 * @brief Imports the data from the desired SQL database object into the array.
	 * Note this function opens the sql connection if it has not already been opened.
	 * @param inputfile the path to the input SQLite database.
	 */
	void importData(string inputfile);

	/**
	 * @brief Imports the simulation parameters by reading the SIMULATION_PARAMETERS table in the provided file.
	 * This imports the grid_x_size, grid_y_size (which should also be the sample map dimensions) and the minimum 
	 * speciation rate.
	 * 
	 * Note this function opens the sql connection if it has not already been opened.
	 * 
	 * @param file the sqlite database simulation output which will be used for coalescence tree generation.
	 */
	void importSimParameters(string file);

	/**
	 * @brief Gets the maximum species abundance ID from the database and stores it in the max_species_id variable.
	 * @note Does not check for SPECIES_ABUNDANCES existence and will throw an error if it cannot access it
	 */
	void getMaxSpeciesAbundancesID();

	/**
	 * @brief Changes the rOut object so that values represent cummulative species abundances.
	 *
	 * Allows binary sort on rOut (much faster) and the previous rOut value can be obtained by
	 * value = rOut[i] - rOut[i-1]
	 * @return pointer to sorted Row of species abundances
	 */
	Row<unsigned long> * getCumulativeAbundances();

	/**
	 * @brief Gets the maximum fragment abundance ID from the database and stores it in the max_fragment_id variable.
	 * @note Does not check for FRAGMENT_ABUNDANCES existence and will throw an error if it cannot access it
	 */
	void getMaxFragmentAbundancesID();

	/**
	 * @brief Gets the maximum species locations ID from the database and stores it in the max_locations_id variable.
	 * @note Does not check for SPECIES_LOCATIONS existence and will throw an error if it cannot access it

	 */
	void getMaxSpeciesLocationsID();

	/**
	 * @brief Sets the protracted parameters for application of protracted speciation
	 * @param max_speciation_gen the maximum number of generations a lineage can exist for before speciating
	 */
	void setProtractedParameters(double max_speciation_gen_in);

	/**
	 * @brief Sets the protracted parameters for application of protracted speciation
	 * 
	 * This overloaded version is for setting protracted parameters before a full simulation has been outputted (i.e. 
	 * immediately after completion of the simulation).
	 *
	 * @param max_speciation_gen_in the maximum number of generations a lineage can exist for before speciating
 	 * @param min_speciation_gen_in the minimum number of generations a lineage must exist before speciating.
	 */
	void setProtractedParameters(const double &max_speciation_gen_in, const double &mix_speciation_gen_in);

	void overrideProtractedParameters(const double &min_speciation_gen_in, const double &max_speciation_gen_in);

	/**
	 * @brief Sets the protracted boolean to the input.
	 * 
	 * @param protracted_in the protracted boolean to set
	 */
	void setProtracted(bool protracted_in);

	/**
	 * @brief Creates a new table in the database file and outputs the database object to the same file as the input 
	 * file. Calculates the community structure for the set of community parameters in current_community_parameters.
	 *
	 * The new SPECIES_ABUNDANCES table contains the species abundance distribution for the whole samplemask.
	 * A similar tabe FRAGMENT_ABUNDANCES is generated by createFragmentDatabase() if specified via the command line 
	 * parameters.
	 */
	void createDatabase();

	/**
	 * @brief Calls calcSpecies and calcSpeciesAbundances to generate the coalescence tree and calculate species
	 * abundances.
	 */
	void generateCoalescenceTree();

	/**
	 * @brief Outputs the species abundances into the database
	 */
	void outputSpeciesAbundances();

	/**
	 * @brief Checks if calculations with the given set of parameters has already been performed.
	 * @param speciation_rate the speciation rate to check for
	 * @param time the time to check for
	 * @param fragments if true, checks fragments have been used
	 * @param metacommunity_size the metacommunity size to check for
	 * @param metacommunity_speciation_rate the metacommunity speciation rate to check for
	 * @return
	 */
	bool checkCalculationsPerformed(long double speciation_rate, double time, bool fragments,
									unsigned long metacommunity_size, long double metacommunity_speciation_rate);

	/**
	 * @brief Adds a performed calculation to the lists of calculations. Also sets the current_community_parameters
	 * pointer to the set of parameters to be applied.
	 *
	 * @param speciation_rate the speciation rate of the performed calculation
	 * @param time the time of the performed calculation
	 * @param fragments if true, fragments were used
	 * @param metacommunity_size the metacommunity size of the performed calculation
	 * @param metacommunity_speciation_rate the metacommunity speciation rate of the performed calculation
	 */
	void addCalculationPerformed(long double speciation_rate, double time, bool fragments,
								 unsigned long metacommunity_size, long double metacommunity_speciation_rate);

	/**
	 * @brief Creates a new table in the database file and outputs the database object to the same file as the input file.
	 * Essentially creates a species abundance distribution (as in createDatabase()), but for the specified fragment 
	 * within the samplemask.
	 * @param f the Fragment to sample from.
	 */
	void createFragmentDatabase(const Fragment &f);

	/**
	 * @brief Output the database from memory to the database file.
	 * Most of the time, it is desirable for the outputfile to be the same path
	 * as the input file and will write to the same object.
	 * @param outputfile the path to the output file.
	 */
	void exportDatabase();

	/**
	 * @brief Checks for the current CommunityParameters reference in the SPECIES_LOCATIONS table.
	 * @return true if the reference exists in the SPECIES_LOCATIONS table
	 */
	bool checkSpeciesLocationsReference();

	/**
	 * @brief Checks for the current CommunityParameters reference in the SPECIES_ABUNDANCES table.
	 * @return return true if the reference exists in the SPECIES_LOCATIONS table
	 */
	bool checkSpeciesAbundancesReference();

	/**
	 * @brief Record the full spatial data.
	 * Creates a new table, SPECIES_LOCATIONS containing every species and their parameters. 
	 * This allows for more in-depth analysis to be performed if necessary.
	 */
	void recordSpatial();

	/**
	 * @brief Calculates the limits of each fragment in the sample map and adds it to the vector of fragments.
	 * If the fragment_file is null, then the program will attempt to calculate fragments from the map.
	 * @bug Only rectangular fragments will be detected. Problems will also be encountered for adjacent fragments.
	 * @param fragment_file the fragment file to read from.
	 */
	void calcFragments(string fragment_file);

	/**
	 * @brief Calculate species abundances for each fragment, and call createFragmentDatabase() for each Fragment.
	 */
	void applyFragments();

	/**
	 * @brief Gets the previous calculations that have already been performed.
	 */
	void getPreviousCalcs();

	/**
	 * @brief Gets the unique community references from the SQL database
	 * @return a vector containing the unique references
	 */
	vector<unsigned long> getUniqueCommunityRefs();

	/**
	 * @brief Gets the unique metacommunity reference from the SQL database
	 * @return a vector containing the unique references
	 */
	vector<unsigned long> getUniqueMetacommunityRefs();

	/**
	 * @brief Write all performed calculations to the output database.
	 */
	void writeNewCommunityParameters();

	/**
	 * @brief Write all performed calculations to the output database
	 */
	void writeNewMetacommuntyParameters();


	/**
	 * @brief Updates the fragments tag on those simulations which now have had fragments added.
	 */
	void updateCommunityParameters();

	/**
	 * @brief Prints speciation rates to terminal
	 */
	void writeSpeciationRates();

	/**
	 * @brief Calculates the coalescence tree for each set of parameters in speciation_parameters;
	 */
	void calculateTree();

	/**
	 * @brief Outputs the data to the SQL database.
	 * @param file_name the path to the sql database to output to
	 */
	void output();

	/**
	 * @brief Prints the application times.
	 * @param tStart the start time
	 * @param tEnd the end time
	 */
	void printEndTimes(time_t tStart, time_t tEnd);

	/**
	 * @brief Apply the given speciation parameters to the coalescence tree.
	 * Overridden for metacommunity application.
	 * @param sp speciation parameters to apply, including speciation rate, times and spatial sampling procedure
	 */
	virtual void apply(SpecSimParameters *sp);

	/**
	 * @brief Performs creation of the coalescence tree for the given speciation parameters.
	 * @param sp speciation parameters to apply, including speciation rate, times and spatial sampling procedure
	 */
	void doApplication(SpecSimParameters *sp);

};

#endif