# PyCoalescence #



##INTRODUCTION##
PyCoalescence is a python module for spatially-explicit coalescence neutral simulations. PyCoalescence will provide a pythonic interface for setting up, running and analysing spatially-explicit neutral simulations. It allows for much swifter and cleaner creation of configuration files and setting of simulation parameters. The underlying simulations are written in c++.

##HOW-TO##
WIP

The Coalescence class contains most of the operations required for setting up a coalescence simulation. The important set up functions are:

* `setup()` links to the correct coalescence simulator executable (compiled from c++)
* `set_map_parameters()` sets size and spacial inputs. Alternatively, `set_map_config()` can be used to link to a map config file, from which map data can be read automatically.
* `set_speciation_rates()` takes a list of speciation rates to apply at the end of the simulation. This is optional.
* `finalise_setup()` generates the command to be passed to the `c++` program that runs the actual simulations.
* `run_coalescence()` starts the simulation. This stage can take an extremely long time (up to tens of hours) depending on the size of the simulation and the dispersal variables. Upon completion, an SQL file will have been created containing the coalescence tree.

The Coalescence class also contains some basic analysis abilities, such as applying additional speciation rates post-simulation, or calculating species abundances for fragments within the main simulation.

The basic procedure for this procedure is

* `set_speciation_params()` which takes as arguments 
	* the SQL database file containing a finished simulation
	* T/F of recording full spatial data
	*  either a csv file containing fragment data, or T/F for whether fragments should be 
		calculated from squares of continuous habitat.	* list of speciation rates to apply
	* [optional] a sample file to specify certain cells to sample from
	* [optional] a config file containing the temporal sampling points desired.
* `apply_speciation()` performs the analysis. This can be extremely RAM and time-intensive for large simulations. The calculations will be stored in extra tables within the same SQL file as originally specified.


##REQUIREMENTS##
For reading parameter information from .tif files and automatically setting the correct spatial data, the gdal package and binaries are required (version 2.0 or later). The installation process differs on different systems and information is available [here](http://www.gdal.org/).

Note that gdal `c++` files are also required for compiling the coalescence simulator with tif file support.

##CONTACTS##

Author: Samuel Thompson

Contact: samuelthompson14@imperial.ac.uk - thompsonsed@gmail.com

Institution: Imperial College London and National University of Singapore

Version: 1.0.1
This project is released under BSD-3 
See file **LICENSE.txt** or go to [here](https://opensource.org/licenses/BSD-3-Clause) for full license details.