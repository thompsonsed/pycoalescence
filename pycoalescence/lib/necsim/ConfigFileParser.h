// This file is part of NECSim project which is released under BSD-3 license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
//
/**
 * @author Sam Thompson
 * @date 31/08/2016
 * @file Config.h
 * @brief Config classes for importing command line parameters from a config text file, originally designed for usage
 * within coalescence simulations on a cluster.
 * Note, as of v1.0, ordering within the file matters.
 *
 * Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 *
 */
// Header guard
//
#ifndef CONFIGCLASS
#define CONFIGCLASS

/************************************************************
																																																INCLUDES
 ************************************************************/
#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include <stdexcept>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <cmath>
#include <cctype>
#include <algorithm>


using namespace std;
using std::string;

/**
 * @brief Import the command line arguments in to the vector for future processing.
 * Arguments will be placed in the vector comargs.
 * @param argc the number of arguments.
 * @param argv a point to the array of arguments in raw character form.
 * @param comargs a vector of the command-line arguments to be filled.
 */
void importArgs(const unsigned int &argc, char *argv[], vector<string> &comargs);

//

/**
 * @struct SectionOption
 * @brief A simple container for importing options from a config file.
 */
struct SectionOption
{
	string section;
	vector<string> val;
	vector<string> refs;

	/**
	 * @brief Default constructor for SectionOption
	 */
	SectionOption()
	{
		section = "nullSectionOption";
	}

	/**
	 * @brief Returns the value for the provided reference from within the key
	 * @param refval the reference to obtain the value of
	 * @return the requested value as a string. Returns string "null" if no reference is found.
	 */
	string getOption(string refval);

	/**
	 * @brief Overloading the << operator for outputting to the output stream.
	 * @param os the output stream.
	 * @param k the KeyOption object.
	 * @return os the output stream.
	 */
	friend ostream &operator<<(ostream &os, const SectionOption &k);

	/**
	 * @brief Overloading the >> operator for inputting from an input stream.
	 * @param is the input stream
	 * @param k the KeyOption object
	 * @return is the input stream
	 */
	friend istream &operator>>(istream &is, SectionOption &k);
};

/**
 * @class ConfigOption
 * @brief Config option class to store and import options from a file.
 */
class ConfigOption
{
private:
	string configfile;
	bool bConfig;
	bool bMain;  // is true if this is the main command line importSpatialParameters (and therefore we want to delete the first few
	// command line options)
	bool bFullParse;  // if this is true, each KeyOption structure will be returned after each read.
	vector<SectionOption> configs;  // all config data if full parse is true.
public:
	/**
	 * @brief default construtor for ConfigOption
	 */
	ConfigOption()
	{
		bConfig = false;
		configfile = "none";
		bMain = false;
		bFullParse = false;
	}

	/**
	 * @brief Sets the config file the specified string.
	 * A boolean is also provided, set equal to true if this is the main command line import.
	 * This causes the deletion of the first few command line options after import.
	 * @param file the target config file (in .txt format).
	 * @param main boolean of if this is the main command line import.
	 * @param full_parse sets bFullParse to provided value
	 */
	void setConfig(const string &file, bool main, bool full_parse = false);

	/**
	 * @brief Reads a config file of a specific configuration.
	 * Each line must be a set of values related to the object determined by ref='object'.
	 * Each key must have the form key=value, which will be read as a string into a KeyOption structure.
	 */
	void parseConfig();

	/**
	* @brief Returns the vector of key options imported from the file.
	* @return vector of key options
	*/
	vector<SectionOption> getSectionOptions();

	/**
	 * @brief Gets the SectionOption at the provided index
	 * @param index the index of the SectionOption to obtain, must be less than configs.size()
	 * @return the section option at the index
	 */
	SectionOption operator[](int index);

/**
	 * @brief Gets the size of the key options vector.
	 * @return the size of the configuration vector.
	 */
	unsigned int getSectionOptionsSize();

	/**
	 * @brief Gets the sections contained in the SectionOptions object.
	 * @return A vector of the section names.
	 */
	vector<string> getSections();

	/**
	 * @brief Checks whether the config option has the specified section.
	 * @param sec the section name to check for
	 * @return true if the section has been found
	 */
	bool hasSection(string sec);

	/**
	 * @brief Gets all values within a section.
	 *
	 * Throws a Config_Exception if the section is not found.
	 * @param sec the section to find values for
	 * @return a vector of the section's values.
	 */
	vector<string> getSectionValues(string sec);

	/**
	 * @brief Returns a specific value for a particular key options and reference.
	 * @param section the section to match
	 * @param ref the reference to match
	 * @return the string at the correct place in KeyOptions.val
	 */
	string getSectionOptions(string section, string ref);

	/**
	 * @brief Returns a specific value for a particular key options and reference.
	 * This overloaded version of the function returns the default value def when
	 * no match is found.
	 * @param section the section to match
	 * @param ref the reference to match
	 * @param def the default value to return if no match is found
	 * @return the string at the correct place in KeyOptions.val
	 */
	string getSectionOptions(string section, string ref, string def);

	/**
	 * @brief Imports the parameters from the config file and returns an integer of the number of arguments.
	 * @param comargs a vector of command line arguments to import to from file.
	 * @return a count of the number of arguments (should also be the size of comargs).
	 */
	int importConfig(vector<string> &comargs);

	/**
	 * @brief Overloading the << operator for outputting to the output stream.
	 * @param os the output stream.
	 * @param c the ConfigOption object.
	 * @return os the output stream.
	 */
	friend ostream &operator<<(ostream &os, const ConfigOption &c);

	/**
	 * @brief Overloading the >> operator for inputting from an input stream.
	 * Note that the config file must still exist for re-inport and parsing.
	 * @param is the input stream
	 * @param c the ConfigOption object
	 * @return is the input stream
	 */
	friend istream &operator>>(istream &is, ConfigOption &c);
};

#endif
