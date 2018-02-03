//This file is part of NECSim project which is released under BSD-3 license.
//See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.

/**
 * @author Samuel Thompson
 * @date 31/08/16
 * @file SpeciationCounter.cpp
 *
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 * @brief Performs calculations of the coalescence tree structure and generates the SQL database objects.
 * 
 * For use on the SQL database outputs of NECSim v3.1+. It requires command line parameters and generates a data object from them.
 * Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
 */

#include "SpeciationCommands.h"

using namespace std;
// INPUTS
// requires a SQL database file containing the the TreeNode objects from a coalescence simulations.
// the required speciation rate.

// OUTPUTS
// An updated database file that contains the species richness and species abundances of the intended lineage.





/**
 * @brief The main SpeciationCounter routine.
 * @param argc the number of command line arguments.
 * @param argv a pointer to an array of the command line arguments.
 * @return an integer, 0 representing success, anything else representing program failure.
 */
int main(int argc, char **argv)
{
	SpeciationCommands app_s;
	app_s.applyFromComargs(argc, argv);
}
