//This file is part of NECSim project which is released under BSD-3 license.
//See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.

/**
 * @author Samuel Thompson
 * @date 19/07/2017
 * @file ApplySpeciation.h
 *
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 * @brief Contains the ApplySpec class for performing calculations of the coalescence tree structure and generating
 *  the SQL database objects.
 * 
 * For use on the SQL database outputs of NECSim v3.1+. It requires command line parameters and generates a data object from them.
 * Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
 */


#include <cstdio>

#include "Community.h"
#include "TreeNode.h"
#include "SpecSimParameters.h"

class SpeciationCommands
{
private:
	// Contains all speciation parameters
	SpecSimParameters sp;
	// Set up for the output coalescence tree
	Row<TreeNode> data;
	// Command-line arguments for parsing
	vector<string> comargs;
	// number of command-line arguments
	int argc;


public:
	
	/**
	 * @brief Default constructor for ApplySpec class.
	 */
	SpeciationCommands()
	{
		
	}
	
	/**
	 * @brief Run the command line arguments check.
	 * Writes arguments to the SpecSimParameters object
	 * @param argc the number of arguments.
	 * @param comargs a vector filled with the command line arguments
	 */
	void parseArgs();

	/**
	 * @brief Runs the main program including parsing command line arguments and running the main analyses.
	 * @param argc the number of command line arguments
	 * @param argv the array of command line arguments
	 * @return 
	 */
	int applyFromComargs(int argc_in, char ** argv);

};