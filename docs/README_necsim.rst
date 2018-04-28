**A Neutral Ecology Coalescence Simulator**

.. _`Introduction_necsim`:

Introduction
------------

**necsim** is a generic spatial coalescence simulator for neutral systems. It is intended to simulate an ecological
community under individual-based neutral dynamics. It applies the model to maps for the supplied parameters and outputs
information for each individual to a SQL database.

Functionality is also provided for applying varying speciation rates to outputs of **necsim** for analysis after
simulations are complete. This enables the main simulation to be run with the *minimum* speciation rate
required and afterwards analysis can be completed using different speciation rates. The same functionality is also
provided within **necsim** for application of speciation rates immediately after simulations are complete.

.. important::
   The recommended method of installing the program and running simulations is to use the
   :ref:`pycoalescence module <Introduction_pycoalescence>`.

A Note on the Neutral Theory of Ecology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Neutral theory in ecology refers to the idea that individuals can be modelled as ecologically identical entities,
undergoing dispersal, drift and speciation without niche effects or other competitive elements.

Whilst obviously not realistic, the patterns produced by such models can often give a surprisingly accurate portrayal of
real-world systems. For more information on the topic, please see [Hubbell2001]_.






Instructions
------------

Compiling the program
~~~~~~~~~~~~~~~~~~~~~
For compilation, there are several provided options:

* Compilation can be handled within pycoalescence by running ``python setup.py``. **This is the recommended option.**
* Alternatively, compilation can be completed with additional options using make. The steps are outlined below

    - You might need to first run ``autoconf`` from within the **necsim** directory to generate the configure executable.
    - Run ``./configure`` (located within the **necsim** directory). Provide additional compilation flags if necessary (detailed below).
    - Run ``make all`` to create the executable.
    - [Optional] Move the executable (called **necsim**) to the *build/Default* directory in **pycoalescence**.

* If you require compilation outside of the pycoalescence module, make use of the the file **Makefile** located in
  **Makefiles/SimpleCompile**. This can be modified and run using ``make`` to generate the executable.

.. note:: If you want to also compile the module for integrating with python, provide the python library (PYTHON_LIB) and
          python include directories (PYTHON_INCLUDE) as command line flags to ``./configure``. You must then run This is
          not recommended, and it is advised you use the :ref:`install proceedure outlined here <Introduction_pycoalescence>`.

.. warning:: Compilation on High-performance clusters will likely require an icc compiler and custom linking to the
             required libraries.

See the Requirements section for a full list of the necessary
prerequisites.


Requirements
''''''''''''

-  The SQLite library available `here <https://www.sqlite.org/download.html>`__.
-  The Boost library available `here <http://www.boost.org>`__.
-  C++ compiler (such as GNU g++) with C++11 support.
-  Access to the relevant folders for Default simulations (see FAQS).

Recommended, but not essential:

- gdal library available `here <http://www.gdal.org>`__: provides reading of tif files.
- The fast-cpp-csv-parser by Ben Strasser, available
  `here <https://github.com/ben-strasser/fast-cpp-csv-parser>`__: provides much faster csv read and write capabilities.
  This is only really necessary if you have extremely large csv files as your map objects. If that is the case, I would
  highly recommend moving to using tif files, as they provide much more error-checking support within **necsim**, as well as
  much more advanced tools for dealing with spatial data.

.. note:: To use the fast-cpp-csv-parser, copy the whole folder (with csv.h in) to the **necsim** directory. Then
          reconfigure and recompile your code, making sure that you see 'fast-cpp-csv-parser = enabled' in the
          configuration output.



Compiler Options
''''''''''''''''

Recognised compiler options include:

.. csv-table::
   :header: "Option", "Description"
   :widths: 20, 80

   "--with-debug", "Adds additional debugging information to a log file in /logs"
   "--with-gdal=DIR", "Define a gdal library at DIR"
   "--with-hpc", "Compile ready for HPC, using intel's icpc compilation and a variety of optimisation flags."
   "--with-boost=DIR", "Define a boost library at DIR"

Additional c++ compilation flags can be specified by ``CPPFLAGS=opts`` for additional library paths or compilation options as required.

Note that gdal and fast-cpp-csv-parser availability will be automatically detected and included in the compilation if possible.

Running simulations
~~~~~~~~~~~~~~~~~~~


As of version 3.1 and above, the routine relies on
supplying command line arguments (see below) for all the major
simulation variables. Alternatively, supplying a config .txt file and
using the command line arguments ``./necsim -c /path/to/config.txt``
can be used for parsing command line arguments from the text file.

Command Line Arguments
''''''''''''''''''''''

.. deprecated::
   This method of supplying simulation parameters is not recommended and is provided for backwards-compatibility only.
   Support will be dropped completely in a future release.

The following command line arguments are required. This list can be
accessed by running ``“./necsim -h”`` or ``./necsim -help``

As of version 3.6 and above, the command line options to be specified are:

1.  the seed for the simulation.
2.  the simulation task (for file reference).
3.  the map config file.
4.  the output directory.
5.  the minimum speciation rate.
6.  the dispersal z\_fat value.
7.  the dispersal L value.
8.  the deme size.
9.  the deme sample size.
10. the maximum simulation time (in seconds).
11. the lambda value for moving through non-habitat.
12. the temporal sampling file containing generation
    values for sampling points in time (null for only sampling the
    present)
13. the minimum number of species known to exist. (Currently has no
    effect).
14. (and onwards) speciation rates to apply after simulation.

In this format, the map config file and temporal sampling file are as described in `Config Files`_.

Alternatively, by specifying the -f flag, (full mode) as the first
argument, the program can read in pre-3.6 command line arguments, which
are as followed.

1.  the task\_iter used for setting the seed.
2.  the sample grid x dimension
3.  the sample grid y dimension
4.  the fine map file relative path.
5.  the fine map x dimension
6.  the fine map y dimension
7.  the fine map x offset
8.  the fine map y offset
9.  the coarse map file relative path.
10. the coarse map x dimension
11. the coarse map y dimension
12. the coarse map x offset
13. the coarse map y offset
14. the scale of the coarse map compared to the fine (10 means
    resolution of coarse map = 10 x resolution of fine map)
15. the output directory
16. the speciation rate.
17. the dispersal sigma value.
18. the deme size
19. the deme sample size (as a proportion of deme size)
20. the time to run the simulation (in seconds).
21. lambda - the relative cost of moving through non-forest
22. the\_task - for referencing the specific task later on.
23. the minimum number of species the system is known to contain.
24. the historical fine map file to use
25. the historical coarse map file to use
26. the rate of forest change from historical
27. the time (in generations) since the historical forest was seen.
28. the dispersal tau value (the width of the fat-tailed kernel).
29. the sample mask, with binary 1:0 values for areas that we want to
    sample from. If this is not provided then this will default to
    mapping the whole area.
30. the link to the file containing every generation that the list
    should be expanded. This should be in the format of a list.
31. (and onwards) - speciation rates to apply after the simulation is
    complete.

.. warning:: This method of running simulations is provided for legacy purposes only, and is no longer recommended. For
   increase functionality, use the condensed command-line format, or switch to using config files.


Config Files
''''''''''''

There are two separate config files which are used when setting up simulations.

- `main simulation config file`_
    Contains the main simulation parameters, including dispersal parameters, speciation rates, sampling information and
    file referencing information. It also includes the paths to the other config files, which must be specified if the
    main simulation config is used.
    Contains the map parameters, including paths to the relevant map files, map dimensions, offsets and scaling. This
    option cannot be null (map dimensions at least must be specified).
- `time config file`_
    Contains the temporal sampling points, in generations. If this is 'null', sampling will automatically occur only
    at the present (generation time=0)

When running the simulation using config files, the path to the `main simulation config file`_ should be specified, e.g
``./necsim -c /path/to/main/config.txt``.


.. _`main simulation config file`:


Main Config File
````````````````
The configuration containing the majority of the simulation set up, outside of map dimensions. An example file is shown
below. This file can be automatically generated by :func:`create_config() <pycoalescence.coalescence.Coalescence.create_config>`
in pycoalescence. An example of this configuration is given below:

::

    [main]
    seed = 6
    job_type = 6
    map_config = output/mapconf.txt
    output_directory = output
    min_spec_rate = 0.5
    sigma = 4
    tau = 4
    deme = 1
    sample_size = 0.1
    max_time = 1
    lambda = 1
    time_config = output/tempconf.txt
    min_species = 1

    [spec_rates]
    spec_rate1  = 0.6
    spec_rate2  = 0.8


.. _`map config file`:

Map Config Options
``````````````````
The map options contain the information for setting up all maps required by the simulation. This involves maps at all
times and at all scales. An example is given below.

::

    [sample_grid]
    path = null
    x = 13
    y = 13
    mask = null

    [fine_map]
    path = sample/SA_sample_fine.tif
    x = 13
    y = 13
    x_off = 0
    y_off = 0

    [coarse_map]
    path = sample/SA_sample_coarse.tif
    x = 35
    y = 41
    x_off = 11
    y_off = 14
    scale = 1.0

    [historical_fine0]
    path = sample/SA_sample_fine_historical1.tif
    number = 0
    time = 1
    rate = 0.5

    [historical_coarse0]
    path = sample/SA_sample_coarse_historical1.tif
    number = 0
    time = 1
    rate = 0.5

    [historical_fine1]
    path = sample/SA_sample_fine_historical2.tif
    number = 1
    time = 4
    rate = 0.7

    [historical_coarse1]
    path = sample/SA_sample_coarse_historical2.tif
    number = 1
    time = 4
    rate = 0.7



.. note::
   The rates and times between the pairs of historical fine maps and historical coarse maps must match up. Without matching
   values here, there could be undetermined errors, or coarse map values being ignored.

.. note::
   Pristine maps assume the same dimensions as their respective present-day equivalents.

.. note::
   In older versions of this program these options were contained in a separate file. However, as of 1.2.4 map and main
   simulation options are contained in the same file.

.. _`time config file`:


Time Config File
````````````````
The temporal sampling config file (referred to as "time config file") specifies times, in generations, when a full
sample according to the sample map should be taken again. An example of this file is given below.

::

   [main]
   time0 = 0.0
   time1 = 1.0


.. note::
   For each speciation rate, all biodiversity measures (such as species' abundances and species' richness) will be
   calculated for each time supplied separately.

Default parameters
''''''''''''''''''

To run the program with the default parameters for testing purposes, run
with the command line arguments -d or -dl (for the larger default run).
Note that this will require access to the following folders relative to
the path of the program for storing the outputs to the default runs:

**./Default**

**./Default/SQL\_data/**

Outputs
-------

Upon successful completion of a simulation, the two files are created.

- A csv file is created called *Data\_{the\_task}\_{the\_seed}.csv* where the\_seed and the\_task are the values provided
  in simulation set-up. This contains basic simulation information for quick reference.
- an SQLite database file in the output directory in a folder called *SQL\_data*.
  This database contains all important simulation data over several tables, which can be accessed
  using a program like `DB Browser for SQLite <http://sqlitebrowser.org/>`__ or Microsoft Access.
  Alternatively, most programming languages have an SQLite interface
  (`RSQlite <https://cran.r-project.org/web/packages/RSQLite/index.html>`__,
  `python sqlite3 <https://docs.python.org/2/library/sqlite3.html>`__)

The tables in the SQLite database are
- SIMULATION\_PARAMETERS

      contains the parameters the simulation was performed with for referencing later.

- SPECIES\_LIST

      contains the locations of every coalescence event. This is used by SpeciationCounter to reconstruct the coalescence
      tree for application of speciation rates after simulations are complete.

- SPECIES\_ABUNDANCES

      contains the species abundance distributions for each speciation rate and time point that has been specified.
- SPECIES\_LOCATIONS [optional]

      contains the x, y coordinates of every individual at each time point and for every specified speciation rate,
      along with species ID numbers.
- FRAGMENT\_ABUNDANCES [optional]

      contains the species abundance distributions for each habitat fragment, either specified by the fragment csv file,
      or detected from squares across the map.

Additional information can be found in SpeciationCounter_ regarding the optional database tables.

.. _`Introduction_SpeciationCounter`:

SpeciationCounter
-----------------
SpeciationCounter provides a method for applying additional speciation rates to outputs from **necsim**, without having to
re-run the entire simulation. SpeciationCounter works by reconstructing the coalescence tree, checking at each point if
an additional speciation rate has occured. As such, SpeciationCounter can only apply speciation rates higher than the
initial speciation rate the program was run with.

Applying Speciation Rates
~~~~~~~~~~~~~~~~~~~~~~~~~

Run ``./SpeciationCounter`` with the following command-line options:

1.  path to the SQLite database file (this is the output of a **necsim** simulation).
2.  T/F for recording spatial data. If true, the SPECIES\_LOCATIONS table will be created (see Outputs_.)
3.  a sample mask to use for the data. Species' identities for the individuals will only be calculated from locations
    specified by a 1 in the sample mask (0 otherwise). Use "null" to record all locations.
4.  a `time config file`_ specifying temporal sampling locations.
5.  T/F for calculating fragment species abundances individually. If true, the FRAGMENT\_ABUNDANCES table will be created
    containing the species abundances for each fragment calculated as a square of continuous habitat. Alternatively, can
    specify a csv file that contains the fragment information in the following format. All x, y coordinates are given on
    the sample grid size specified at simulation run-time.

    ::

      fragment_name1, x_min, y_min, x_max, y_max, number_of_individuals
      fragment_name2, x_min, y_min, x_max, y_max, number_of_individuals
      ...
6.  A speciation rate to apply. Can list multiple speciation rates by supplying arguments 7 onwards.

Debugging
---------

Most errors will return an error code in the form “ERROR\_NAME\_XXX:
Description” a list of which can be found in ERROR\_REF.txt.

Brief Class Descriptions
------------------------

A brief description of the important classes is given below. Some
classes also contain customised exceptions for better tracing of error
handling.

-  The :cpp:class:`Tree` class

   -  The most important class!
   -  Contains the main setup, run and data output routines.
   -  :cpp:func:`setup()<Tree::setup()>` imports the data files from csv (if necessary) and creates
      the in-memory objects for the storing of the coalescence tree and
      the spatial grid of active lineages. Setup time mostly depends on
      the size of the csv file being imported.
   -  Run continually loops over sucessive coalesence, move or
      speciation events until all individuals have speciated or
      coalesced. This is where the majority of the simulation time will
      be, and is mostly dependent on the number of individuals,
      speciation rate and size of the spatial grid.
   -  At the end of the simulation, the sqlCreate() routine will
      generate the in-memory SQLite database for storing the coalescent
      tree. It can run multiple times if multiple speciation rates are
      required. :cpp:func:`outputData()<Tree::outputData()>` will then be called to create a small csv
      file containing important information, and output the SQLite
      database to file if required.

-  The :cpp:class:`TreeNode` class

   -  Contains a single record of a node on the phylogenetic tree, to be
      used in reassembling the tree structure at the end of the
      simulation.

-  The :cpp:class:`DataPoint` class

   -  Contains a single record of the location of a lineage.

-  The :cpp:class:`NRrand` class

   -  Contains the random number generator, as written by James
      Rosindell (j.rosindell@imperial.ac.uk).

-  The :cpp:class:`Landscape` class

   -  Contains the routines for importing and calling values from the
      map objects.
   -  The :cpp:func:`getVal() <Landscape::getVal()>` and :cpp:func:`runDispersal() <Landscape::runDispersal()>`
      functions can be modified to produce altered dispersal behaviour, or alterations to the
      structure of the :cpp:class:`Row`

-  The :cpp:class:`Matrix` and :cpp:class:`Row` classes

   -  Based on code written by James Rosindell
      (j.rosindell@imperial.ac.uk).
   -  Handles indexing of the 2D object plus importing values from a csv
      file.

-  The :cpp:class:`SpeciesList` class

   -  Contains the list of individuals, for application in a matrix, to
      essentially create a 3D array.
   -  Handles the positioning of individuals in space within a grid
      cell.

-  The :cpp:class:`ConfigOption` class

   -  Contains basic functions for importing command line arguments from
      a config file, providing an alternative way of setting up
      simulations.

-  The :cpp:class:`Community` class

   -  Provides the routines for applying different speciation rates to a
      phylogenetic tree, to be used either immediately after simulation
      within **necsim**, or at a later time using SpeciationCounter_
   -  Use to generate a community of individuals for a particular set of parameters, providing options for generating
      species identities, species abundance distributions and species locations.

Known Bugs
----------

-  Simulations run until completion, rather than aiming for a desired
   number of species. This is an intentional change. Functions related
   to this functionality remain but are deprecated.
-  In SpeciationCounter, only continuous rectangular fragments are
   properly calculated. Other shapes must be calculated by
   post-processing.
-  In SpeciationCounter, 3 fragments instead of 2 will be calculated for
   certain adjacent rectangular patches.

FAQS (WIP)
----------

-  **Why doesn’t the default simulation output anything?**

   -  Check that the program has access to the folders relative to the
      program at `Default/`

-  **Why can’t I compile the program?**

   -  This could be due to a number of reasons, most likely that you
      haven’t compiled with access to the lsqlite3 or boost packages.
      Installation and compilation differs across different systems; for
      most UNIX systems, compiling with the linker arguments -lsqlite3
      -lboost\_filesystem and -lboost\_system will solve problems with
      the compiler not finding the sqlite or boost header file.
   -  Another option could be the potential lack of access to the
      fast-cpp-csv-parser by Ben Strasser, available
      `here <https://github.com/ben-strasser/fast-cpp-csv-parser>`__. If
      use\_csv has been defined at the head of the file, try without
      use\_csv or download the csv parser and locate the folder within
      your working directory at compilation.

-  **Every time the program runs I get error code XXX.**

   -  Check the ERROR\_REF.txt file for descriptions of the files. Try compiling with the `DEBUG` precursor to gain
      more information on the problem. It is most likely a problem with
      the set up of the map data (error checking is not yet properly
      implemented here).

.. include:: Glossary.rst

Version
-------

Version |release|

Contacts
--------

Author: **Samuel Thompson**

Contact: samuelthompson14@imperial.ac.uk - thompsonsed@gmail.com

Institution: Imperial College London and National University of
Singapore

Based heavily on code by **James Rosindell**

Contact: j.rosindell@imperial.ac.uk

Institution: Imperial College London

Licence
-------
This project is released under MIT See file
**LICENSE.txt** or go to
`here <https://opensource.org/licenses/BSD-3-Clause>`__ for full license
details.

You are free to modify and distribute the code for any non-commercial purpose.

