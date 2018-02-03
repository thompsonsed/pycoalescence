.. _program_listing_file_README.md:

Program Listing for File README.md
========================================================================================

- Return to documentation for :ref:`file_README.md`

.. code-block:: cpp

   # NECSim #
   
   Version: 3.6
   This project is released under BSD-3 
   See file **LICENSE.txt** or go to [here](https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   ## CONTENTS ##
   * **INTRODUCTION**
   * **INSTRUCTIONS**
   * **REQUIREMENTS**
   * **DEGUGGING**
   * **CLASS DESCRIPTIONS**
   * **KNOWN BUGS**
   * **FAQS**
   * **CONTACTS**
   
   ## INTRODUCTION ##
   
   NECSim is a generic spatial coalescence simulator for neutral systems. It applies the model to map objects, which can change over time, for a specific set of supplied parameters, and outputs information for each individual to a SQL database. 
   
   SpeciationCounter is a program for applying varying speciation rates to outputs of NECSim for analysis after simulations are complete. This enables the main simulation to be run with the *minimum* speciation rate required and afterwards analysis can be completed using different speciation rates. As of version 3.4, different speciation rates can be applied directly within NECSim at run time.
   
   You are free to modify and distribute the code as per the license specified in **LICENCE.txt** to suit any additional neutral simulation requirements (or any other purpose).
   
   ## INSTRUCTIONS ##
   ###Compiling the program###
   See the Requirements section for a full list of the necessary prerequisites. Once these are installed, compiling the program should be relatively easy. NECSim requires a linker to the boost libraries, as well as the sqlite3 library. It is recommended to run with the maximum optimisation possible. Under `g++` it will look something like
   
   ```
   g++ main_ST.cpp -std=c++11 -o3 -Wall -o ./Coal_sim -g  -lsqlite3 -lboost_filesystem -lboost_system
   ```
   
   This will create an executable called Coal_sim under the same directory as the source files. Additionally, if support is required for tif files (an alternative to importing csv files), the [gdal library](http://www.gdal.org/) is required. See the online documentation for help compiling gdal for your operating system. When compiling using gdal, use the ```-D with_gdal``` compilation flag.
   
   For compilation on High Performance Computing (HPC) systems, they will likely use intel compilers. The header files for the sqlite and boost packages may need to be copied in to the working directory to avoid problems with linking to libraries. Check the service providers' documentation for whether these libraries are already installed on the HPC. 
   
   Depending on the set up of the HPC, the compilation itself will be something like 
   ```
   icc -O3 -xSSE4.2 -axAVX,CORE-AVX-I,CORE-AVX2 -lsqlite3 -lpthread -lboost_filesystem -lboost_system -std=c++11 -o ./Coal_sim main_ST.cpp 
   ```
   or 
   ```
   icc -O3 -lsqlite3 -lpthread -lboost_filesystem -lboost_system -std=c++11 -o ./Coal_v1 main_ST.cpp
   ```
   
   for the simulation program and 
   ```
   icc -O3 -xSSE4.2 -axAVX,CORE-AVX-I,CORE-AVX2 -lsqlite3 -lpthread -std=c++11 -o ./SpeciationCounter Speciation_Counter.cpp
   ```
   or
   ```
   icc -O3 -lpthread -std=c++11 -lsqlite3 -lboost_filesystem -lboost_system -lsqlite3 -o ./SpeciationCounter Speciation_Counter.cpp
   ```
   for the application of different speciation rates.
   
   ###Running simulations###
   As of version 3.1 of the main simulation code, the routine relies on supplying command line arguments (see below) for all the major simulation variables. Alternatively, supplying a config .txt file and using the command line arguments `./Coal_sim -c /path/to/config.txt` can be used for parsing command line arguments from the text file. 
   
   ####Command Line Arguments ####
   The following command line arguments are required. This list can be accessed by running `“./Coal_sim -h”` or `./Coal_sim -help`
   
   As of version 3.6, the command line options to be specified are:
   
   1. the seed for the simulation.
   2. the simulation task (for file reference).
   3. the map config file.
   4. the output directory.
   5. the minimum speciation rate.
   6. the dispersal z_fat value.
   7. the dispersal L value.
   8. the deme size.
   9. the deme sample size.
   10. the maximum simulation time (in seconds).
   11. the lambda value for moving through non-habitat.
   12. the temporal sampling file containing tab-separated generation values for sampling points in time (null for only sampling the present)
   13. the minimum number of species known to exist. (Currently has no effect).
   14. (and onwards) speciation rates to apply after simulation.
   
   In this set up, the map config file contains a file on each line, with tab separation between the different variables. The "ref" flag contains the object type, followed by all other parameters. An example is given below.
   
   ref=sample_grid path=/path/to/file  x=100   y=200   mask=/path/to/mask
   ref=fine_map    path=/path/to/file  x=100   y=200   x_off=10    y_off=20
   ref=pristine_fine   path=/path/to/file  number=n    rate=r  time=g
   
   Alternatively, by specifying the -f flag, (full mode) as the first argument, the program can read in pre-3.6 command line arguments, which are as followed.
   
   1. the task_iter used for setting the seed.
   2. the sample grid x dimension
   3. the sample grid y dimension
   4. the fine map file relative path.
   5. the fine map x dimension
   6. the fine map y dimension
   7. the fine map x offset
   8. the fine map y offset
   9. the coarse map file relative path.
   10. the coarse map x dimension
   11. the coarse map y dimension
   12. the coarse map x offset
   13. the coarse map y offset
   14. the scale of the coarse map compared to the fine (10 means resolution of coarse map = 10 x resolution of fine map)
   15. the output directory
   16. the speciation rate.
   17. the dispersal distance (zfat).
   18. the deme size
   19. the deme sample size (as a proportion of deme size)
   20. the time to run the simulation (in seconds).
   21. lambda - the relative cost of moving through non-forest
   22. the_task - for referencing the specific task later on.
   23. the minimum number of species the system is known to contain.
   24. the pristine fine map file to use
   25. the pristine coarse map file to use
   26. the rate of forest change from pristine
   27. the time (in generations) since the pristine forest was seen.
   28. the dispersal L value (the width of the kernel.
   29. the sample mask, with binary 1:0 values for areas that we want to sample from. If this is not provided then this will default to mapping the whole area.
   30.  the link to the file containing every generation that the list should be expanded. This should be in the format of a list.
   31. (and onwards) - speciation rates to apply after the simulation is complete.
   
   ####Config Files ####
   The program also accepts a config file, specified by running `./Coal_sim -c /path/to/config.txt`. The format of the config file is
   ```
   rand_seed = i
   sample_x_dim = i
   sample_y_dim = i
   fine_source = /path/to/fine.csv
   fine_x_dim = i
   fine_y_dim = i
   fine_x_offset = i
   fine_y_offset = i
   coarse_source = /path/to/coarse.csv
   coarse_x_dim = i
   coarse_y_dim = i
   coarse_x_offset = i
   coarse_y_offset = i
   coarse_scale = i
   output_dir = /path/to/outdir
   spec_rate = d
   zfat = f
   deme_size = i
   deme_sample = d
   wall_time = i
   lambda = 1
   job_num = i
   est_spec = i
   pristine_fine_source = /path/to/pristine/fine.csv
   pristine_coarse_source = /path/to/pristine/coarse.csv
   forest_change = d
   time_since = f
   dispersal = f
   sampledatamask = /path/to/sample/mask.csv
   time_config_file = /path/to/time/file.txt
   speciationrate1 = d
   speciationrate2 = d
   ...
   ```
   where `i` represents a positive integer, `d` is a decimal value between 0 and 1, and `f` is any positive number (float). Whilst this does help with readability of the code, the order of the arguments is essential at this stage (i.e. don't switch the order of the lines). Future versions may alter the system of reading such that the parameters are set according to their key. Any number of speciation rates (or 0) can be at the end of the file.
   
   ####Default parameters####
   To run the program with the default parameters for testing purposes, run with the command line arguments -d or -dl (for the larger default run). Note that this will require access to the following folders relative to the path of the program for storing the outputs to the default runs:
   
   **../../Data/Coal_sim/Test_output/**
   
   **../../Data/Coal_sim/Test_output/SQL_data/**
   
   ####Outputs####
   Upon successful completion of a simulation, the Coal\_v1 program will produce an SQLite database file in the output directory in an SQL\_data folder. This database contains several tables, which can be accessed using a program like [DB Browser for SQLite](http://sqlitebrowser.org/) or Microsoft Access. Alternatively, most programming languages have an SQLite interface ([RSQlite](https://cran.r-project.org/web/packages/RSQLite/index.html), [python sqlite3](https://docs.python.org/2/library/sqlite3.html))
   
   * The main table within the database is the SPECIES\_LIST table, which is the location and inheritence of every lineage recorded. Several other important data structures (such as whether it is a "tip" of the phylogenetic tree of not) which are used by Speciation_Counter when re-constructing the species identity.
   * A secondary output from Coal\_v1 is a SIMULATION\_PARAMETERS table for identifying the exact parameters with which the model is run.
   * SpeciationCounter also produces a SPECIES_ABUNDANCES table containing species abundances across the whole sample map, plus (optionally) a table of SPECIES\_LOCATIONS (containing the x,y location of every individual) and FRAGMENT\_ABUNDANCES (species abundances for each habitat fragment separately).
   
   ## REQUIREMENTS ##
   * The SQLite library available [here](https://www.sqlite.org/download.html).
   * The Boost library available [here](http://www.boost.org).
   * The fast-cpp-csv-parser by Ben Strasser, available [here](https://github.com/ben-strasser/fast-cpp-csv-parser).
   * C++ compiler (such as GNU g++) with C++11 support.
   * Access to the relevant folders for Default simulations (see FAQS).
   
   
   ## DEBUGGING ##
   Most errors will return an error code in the form “ERROR\_NAME\_XXX: Description” a list of which can be found in ERROR_REF.txt.
   
   ## CLASS DESCRIPTIONS ##
   
   
   A brief description of the important classes is given below. Some classes also contain customised exceptions for better tracing of error handling.
   
   * The `Tree` class.
       - The most important class!
       - Contains the main setup, run and data output routines. 
       - Setup imports the data files from csv (if necessary) and creates the in-memory objects for the storing of the coalescence tree and the spatial grid of active lineages. Setup time mostly depends on the size of the csv file being imported.
       - Run continually loops over sucessive coalesence, move or speciation events until all individuals have speciated or coalesced. This is where the majority of the simulation time will be, and is mostly dependent on the number of individuals, speciation rate and size of the spatial grid.
       - At the end of the simulation, the sqlCreate() routine will generate the in-memory SQLite database for storing the coalescent tree. It can run multiple times if multiple speciation rates are required. outputData() will then be called to create a small csv file containing important information, and output the SQLite database to file if required.
   * The `Treenode` class
       - Contains a single record of a node on the phylogenetic tree, to be used in reassembling the tree structure at the end of the simulation.
       - Operations are mostly basic getters and setters, with functionality called from higher-level functions.
       - An array of treenodes makes up the `data` object in `tree`.
   * The `Datapoint` class
       - Contains a single record of the location of a lineage.
       - An array of datapoints makes up the `active` object in `tree`.
       - `endactive` refers to the number of lineages currently being simulated. After each coalescence or speciation event this will decrease.
   * The `NRrand` class
       - Contains the random number generator, as written by James Rosindell (j.rosindell@imperial.ac.uk).
   * The `Map` class
       - Contains the routines for importing and calling values from the map objects.
       - The `GetVal()` and `runDispersal()` functions can be modified to produce altered dispersal behaviour, or alterations to the structure of the map.
   * The `Matrix` and `Row` classes
       - Based on code written by James Rosindell (j.rosindell@imperial.ac.uk).
       - Handles indexing of the 2D object plus importing values from a csv file.
   * The `SpeciesList` class
       - Contains the list of individuals, for application in a matrix, to essentially create a 3D array. 
       - Handles the positioning of individuals in space within a grid cell.
   * The `ConfigOption` class
       - Contains basic functions for importing command line arguments from a config file, providing an alternative way of setting up simulations.
   * The `Treelist` class
        - Contained in SpeciationCounter.h.
        - Provides the routines for applying different speciation rates to a phylogenetic tree, to be used either immediately after simulation within NECSim, or at a later time using SpeciationCounter.cpp
        
   ## KNOWN BUGS ##
   * Simulation pause and resume functions do not work properly at this time (should be fixed in a later update).
   * Simulations run until completion, rather than aiming for a desired number of species. This is an intentional change. Functions related to this functionality remain but are deprecated.
   * In SpeciationCounter, only continuous rectangular fragments are properly calculated. Other shapes must be calculated by post-processing.
   * In SpeciationCounter, 3 fragments instead of 2 will be calculated for certain adjacent rectangular patches.
   
   ## FAQS (WIP) ##
   * **Why doesn’t the default simulation output anything?**
       - Check that the program has access to the folders relative to the program at:
       ../../Data/Coal_sim/Test_output/
       ../../Data/Coal_sim/Test_output/SQL_data/
   
   
   * **Why can’t I compile the program?**
       - This could be due to a number of reasons, most likely that you haven’t compiled with access to the lsqlite3 or boost packages. Installation and compilation differs across different systems; for most UNIX systems, compiling with the linker arguments -lsqlite3 -lboost_filesystem and -lboost_system will solve problems with the compiler not finding the sqlite or boost header file.
       - Another option could be the potential lack of access to the fast-cpp-csv-parser by Ben Strasser, available [here](https://github.com/ben-strasser/fast-cpp-csv-parser). If use\_csv has been defined at the head of the file, try without use_csv or download the csv parser and locate the folder within your working directory at compilation.
       
       
   * **Every time the program runs I get error code XXX.**
       - Check the ERROR_REF.txt file for descriptions of the files. Try running in debug mode (uncomment ```#define debug_mode```) to gain more information on the problem. It is most likely a problem with the set up of the map data (error checking is not yet properly implemented here).
     
   ## CONTACTS##
   Author: **Samuel Thompson**
   
   Contact: samuelthompson14@imperial.ac.uk - thompsonsed@gmail.com
   
   Institution: Imperial College London and National University of Singapore
   
   Based heavily on code by **James Rosindell**
   
   Contact: j.rosindell@imperial.ac.uk
   
   Institution: Imperial College London


