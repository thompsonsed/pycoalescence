# Basic pycoalescence overview
*A python package for coalescence-based spatially-explicit neutral ecology simulations*



##INTRODUCTION
pycoalescence is a python package for spatially-explicit coalescence neutral simulations. pycoalescence provides a
pythonic interface for setting up, running and analysing spatially-explicit neutral simulations. Simulations themselves
are performed in c++ using [necsim](http://pycoalescence.readthedocs.io/en/release/necsim/necsim_library.html) for 
excellent performance. Usage of python allows for easier setup of simulation parameters. 

For full documentation please see [here](http://pycoalescence.readthedocs.io/en/release/).

##INSTALLATION

Simply run `setup.py` with any required compilation flags. This requires all dependencies have been installed.
By default, .o files are compiled to lib/obj and .so files are compiled to build/sharedpyX
where X is the major python version number (allowing for both python 2.x and python 3.x versions
 to be installed in the same directory). 
 
 Make sure compilation is performed under the same python version simulations will be performed in.  


##BASIC USAGE

The Simulation class contains most of the operations required for setting up a coalescence simulation.
The important set up functions are:

* `set_simulation_params()` sets a variety of key simulation variables, including the seed, output directory, dispersal
  parameters and speciation rate.
* `set_map()` is used to specify a map file to use. More complex map file set-ups can be provided using
  `set_map_files`. `set_map_parameters()` can also be used to customise parameters, instead of detecting from the
  provided tif files.
* `set_speciation_rates()` takes a list of speciation rates to apply at the end of the simulation. This is optional.
* `finalise_setup()` creates the configuration file and performs a variety of basic checks.
* `run_coalescence()` starts the simulation. This stage can take an extremely long time (up to tens of hours) depending
  on the size of the simulation and the dispersal variables. Upon completion, an SQL file will have been created
  containing the coalescence tree.

The CoalescenceTree class also contains some basic analysis abilities, such as applying additional speciation rates
post-simulation, or calculating species abundances for fragments within the main simulation.

The basic procedure for this procedure is

* `set_database()` to provide the path to the completed simulation database
* `set_speciation_params()` which takes as arguments 
	* T/F of recording full spatial data
	*  either a csv file containing fragment data, or T/F for whether fragments should be 
		calculated from squares of continuous habitat.
    * list of speciation rates to apply
	* [optional] a sample file to specify certain cells to sample from
	* [optional] a config file containing the temporal sampling points desired.
* `apply_speciation()` performs the analysis. This can be extremely RAM and time-intensive for large simulations. 
  The calculations will be stored in extra tables within the same SQL file as originally specified.


##REQUIREMENTS

### Essential
* Python version 2 >= 2.7.9 or 3 >= 3.4.1
* C++ compiler (such as GNU g++) with C++11 support.
* The SQLite library available here. Require both c++ and python installations.
* The Boost library for C++ available here.
* Numerical python (numpy) package. 
* Note that gdal `c++` files are also required for compiling the coalescence simulator with tif file support.

###Recommended
* The gdal library for both python and C++ (available here). This is **ESSENTIAL** if you wish to use .tif files for necsim. 
It allows reading parameter information from .tif files (using detect_map_dimensions()). Both the python package and 
c++ binaries are required; installation differs between systems, so view the gdal documentation for more help installing
 gdal properly.
* The fast-cpp-csv-parser by Ben Strasser, available here. This provides much faster csv read and write capabilities and
 is probably essential for larger-scale simulations, but not necessary if your simulations are small. 
 The folder fast-cpp-csv-parser/ should be in the same directory as your necsim C++ header files 
 (the lib/necsim directory).
* Scientific python (scipy) package v12.0 or later for generating landscapes.
Only necessary if usage of the `FragmentedLandscapes` class is needed.

##CONTACTS

Author: Samuel Thompson

Contact: samuelthompson14@imperial.ac.uk - thompsonsed@gmail.com

Institution: Imperial College London and National University of Singapore

Version: 1.0.1
This project is released under MIT 
See file **LICENSE.txt** or go to [here](https://opensource.org/licenses/MIT) for full license details.