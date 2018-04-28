.. _`Introduction_pycoalescence`:
pycoalescence
=============

Introduction
------------

**pycoalescence** is a python module for the spatially-explicit coalescence neutral simulator, described
:ref:`here <Introduction_necsim>`. **pycoalescence** provides a pythonic interface for setting up, running and analysing
spatially-explicit neutral simulations. It allows for a swift and clean creation management of simulations.

Features
--------

A large number of performance-enhancing features have been implemented, as well as support for a wide number of
scenarios. The features include:

- Coalescence methods for excellent performance.
- Full output of community structure, with species IDs generated for every individual.
- Full spatial modelling, using a dispersal kernel to simulate spatial dynamics.
- Multiple sampling points, both spatially and temporally.
- Simulations of a region much larger than the sample area.
- Calculation of many biodiversity metrics, including species richness, species abundances, beta-diversity and
  locations of lineages.
- Scalability - support for simulations of tens or hundreds of millions of individuals in a single simulation.

Getting started
---------------
.. contents::
   :depth: 1
   :local:

Installation
~~~~~~~~~~~~
Currently, only macOS and linux-based operating systems are supported. Windows compatibility will likely be added at a
later date.

Method
''''''

Before attempting installation, make sure the `prerequisites are installed`_. There are a few options for installation.

.. _`prerequisites are installed`: Prerequisites_

- Use in-built installation **[recommended]**

    - Simply run ``python setup.py`` from the terminal.
    - You can also run ``python setup.py [opts]`` where ``[opts]`` are
      your required compilation flags (see  `Compilation Options`_). On some systems this requires that ``autoconf`` and
      ``autotools`` are installed on your computer.
- Use :py:mod:`setup.py <pycoalescence.setup>` to customise options and install locations. The procedure is the same
  as exists in :py:func:`main() <pycoalescence.setup.main>`.


    .. code-block:: python

        from pycoalescence import setup
        # Replace with desired install options
        setup.run_configure(["--with-hpc", "--with-verbose"])
        # This compiles the c++ code in the lib folder to lib/obj for .o files the package directory
        # and build/sharedpy2 or build/sharedpy3 for .so files (depending on python version)
        setup.do_compile()

- Run ``./configure`` and ``make`` yourself.

    If you require additional compilation options, run ``./configure`` with your options from the lib/ directory. Then
    run ``make`` and check that installation is complete. The shared object file should be moved into the *build/sharedpyx*
    directory, where *x* is the major python version number (2 or 3).
- Custom compilation

    Compile the c++ files yourself with the required defines and copy the executable to the required directory.

For HPC use, running ``python hpc_setup.py`` (see :py:mod:`hpc_setup <pycoalescence.hpc_setup>`) will perform
compilation for an HPC using the intel compiler and copy the executable to "../../Code" relative to pycoalescence.

.. warning:: Additional steps may have to be taken to ensure availability of the correct packages on HPC systems. Check
             with your HPC administrator for details.

.. note:: Separate compiles of the program are usually required for each python installation and virtual environment.
          This can cause complications for certain IDEs. If you encounter problems, it is recommended that you run
          ``setup.py`` from within you IDE.

.. _`sec Compilation Options`:

Compilation Options
'''''''''''''''''''
These are the possible flags which can be provided during installation as options in ``python setup.py [opts]``. It is
not usually expected that you need to provide any of these options.

.. csv-table::
   :header: "Option", "Description"
   :widths: 20, 80

   "--with-debug", "Adds additional debugging information, including writing all messages to a log file."
   "--with-gdal=DIR", "Define a gdal library at DIR"
   "--with-hpc", "Compile ready for HPC, using intel's icpc compilation and a variety of optimisation flags."
   "--with-boost=DIR", "Define a boost library at DIR"

.. _`performing_simulations`:

Performing simulations
~~~~~~~~~~~~~~~~~~~~~~

Setting up simulations
''''''''''''''''''''''

There are two methods for providing configuration options in pycoalescence. Both require the same initial procedure.
The recommended method is:

#. Specify simulation parameters

   - Use :func:`set_simulation_params() <pycoalescence.simulation.Simulation.set_simulation_params>`
     to set the job number, task number, output directory and other key simulation variables.
   - Set the map variables by one of the following:

     a. :func:`set_map_parameters() <pycoalescence.landscape.Landscape.set_map_parameters>` to input file paths and dimensions
     b. :func:`set_map_files() <pycoalescence.simulation.Simulation.set_map_files>` to set the map file paths. This
        calls :func:`detect_map_dimensions() <pycoalescence.simulation.Simulation.detect_map_dimensions>` to automatically
        detect file offsets and dimensions.

     .. tip:: Check `Limitations of simulation variables`_ for important information on restrictions on simulation
        inputs.

     .. note:: :func:`detect_map_dimensions() <pycoalescence.simulation.Simulation.detect_map_dimensions>` requires
        that the files are in **.tif** formats so that file dimensions can be read. If input files are csv format,
        method a) should be used.

     .. note:: One can specify either "null" or "none" map types; "null" creates a map at the specified
               size, whereas "none" creates hard boundaries without any in-memory map object created at all. However,
               the dimensions of these files must be manually supplied.

   - Optionally, also run :func:`set_speciation_rates() <pycoalescence.simulation.Simulation.set_speciation_rates>`
     to set a list of speciation rates to apply at the end of the simulation.

#. Finalise setup

   - Run :func:`finalise_setup() <pycoalescence.simulation.Simulation.finalise_setup>` to check that simulations are
     setup, generate the command to be passed to :ref:`necsim <Introduction_necsim>` and create any required config files.

#. Run simulations

   - Finally, start the simulation using :func:`run_coalescence() <pycoalescence.simulation.Simulation.run_coalescence>`

Custom Configuration Files
''''''''''''''''''''''''''
Although not recommended for most use-cases, it is possible to manually create a configuration file, instead of relying on
:func:`finalise_setup() <pycoalescence.simulation.Simulation.finalise_setup>` to do it for you. This may be useful if
you want to store the setup file in a particular place. The process is outlined below. The configuration
file is as default stored in mainconf_*job_num*_*seed*.txt.

#. Add a temporal sampling configuration file

   If you require sampling at points other than the present day, these can be specified within the configuration file.

   - Add temporal sampling points using :func:`add_sample_time() <pycoalescence.simulation.Simulation.add_sample_time>`
     Multiple sample points can be added.
   - Create the temporal sampling config file (:func:`create_temporal_sampling_config() <pycoalescence.simulation.Simulation.create_temporal_sampling_config>`)
#. Generate the main config file

   Run :func:`create_config() <pycoalescence.simulation.Simulation.create_config>` to generate the main config file.

   .. note:: If you wish to use multiple map files or multiple temporal samples and wish to use a main config file as well,
      you must call
      :func:`create_config() <pycoalescence.simulation.Simulation.create_config>` **after** both
      :func:`create_map_config() <pycoalescence.simulation.Simulation.create_map_config>` and
      :func:`create_temporal_sampling_config() <pycoalescence.simulation.Simulation.create_temporal_sampling_config>`

   .. warning:: It is possible to use temporal config files without using a main config file. However,
      if you want map or main options in config file, you **must** use all config options (main config and temporal config).
#. Add map configuration options

   If you require multiple map files at different points in time, you shall need to create a configuration (.txt or .cfg)
   file to make these options accessible to the program.

   These configuration options appear in the main configuration file under various headings.

   - First add the historical map options using :func:`add_historical_map() <pycoalescence.landscape.Landscape.add_historical_map>`
     This can be performed multiple times to add several maps.
   - Add the options to the configuration file (:func:`create_map_config() <pycoalescence.simulation.Simulation.create_map_config>`)

.. note::
    See Glossary_ for definitions of :term:`sample map`, :term:`fine map` and :term:`coarse map`.



Examples
''''''''

A simple simulation

.. code-block:: python

    from pycoalescence import Simulation
    # Set logging level to "info" (from logging module)
    c = Simulation(logging_level=20)
    # set the main simulation parameters - use default values for other keyword arguments
    c.set_simulation_params(seed=1, job_type=1, output_directory="output", min_speciation_rate=0.1,
                            sigma=4, deme=10, sample_size=0.1, max_time=1)
    # Optionally add a set of speciation rates to apply at the end of the simulation
    c.set_speciation_rates([0.1, 0.2, 0.3])
    # set the map parameters - null means the map will be generated with 100% cover everywhere (no file input).
    c.set_map_parameters(sample_file = "null", sample_x = 100, sample_y=100,
                         fine_file = "null", fine_x = 200, fine_y = 200, fine_x_offset = 50, fine_y_offset = 50,
                         coarse_file = "null", coarse_x = 1000, coarse_y = 1000,
                         coarse_x_offset = 100, coarse_y_offset = 100, coarse_scale = 10,
                         historical_fine_map = "null", historical_coarse_map = "null")
    # complete setup and run simulation
    c.finalise_setup()
    c.run_coalescence()

A more complex example using config files, multiple temporal sampling points and detection of map dimensions from the
inputted map files.

.. code-block:: python

    from pycoalescence import Simulation
    c = Simulation()
    # set the main simulation parameters
    c.set_simulation_params(seed=1, job_type=1, output_directory="output", min_speciation_rate=0.1,
                            sigma=4, tau=4, deme=1, sample_size=0.1
                            max_time=100, dispersal_method="fat-tailed", m_prob=0.0, cutoff=0,
                            dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0.2,
                            gen_since_historical=200, time_config_file="null", restrict_self=False,
                            landscape_type=False)
    # Add a set of speciation rates to be applied at the end of the simulation
    c.set_speciation_rates([0.2, 0.3, 0.4])
    # set the map files
    c.set_map_files(sample_file="null", fine_file="path/to/fine.tif", coarse_file="path/to/coarse.tif")
    # add sample times
    c.add_sample_time(0.0)
    c.add_sample_time(1.0)
    # add historical maps
    c.add_historical_map(fine_map="path/to/historicalfine1.tif", coarse_map="path/to/historicalcoarse1.tif", time=1, rate=0.5)
    # create configuration files, run the checks and finalise the simulation
    c.finalise_setup()
    # run the simulation
    c.run_coalescence()

.. note:: necsim can also be run directly using command line arguments (see
          :ref:`Introduction to necsim <Introduction_necsim>`).

Example configuration file

::

    [sample_grid]
    path = /Data/Maps/maskmap.tif
    x = 486
    y = 517
    mask = /Data/Maps/maskmap.tif

    [fine_map]
    path = /Data/Maps/finemap.tif
    x = 34000
    y = 28000
    x_off = 17155
    y_off = 11178

    [coarse_map]
    path = /Data/Maps/coarsemap.tif
    x = 24000
    y = 20000
    x_off = 10320
    y_off = 7200
    scale = 10.0

    [historical_fine0]
    path = none
    number = 0
    time = 200
    rate = 0

    [historical_coarse0]
    path = none
    number = 0
    time = 200
    rate = 0

    [historical_fine1]
    path = none
    number = 1
    time = 200
    rate = 0

    [historical_coarse1]
    path = none
    number = 1
    time = 200
    rate = 0

    [dispersal]
    method = norm-uniform
    m_probability = 1e-10
    cutoff = 0
    restrict_self = 0
    landscape_type = 0

    [main]
    seed = 1
    job_type = 2
    map_config = output/mainconf_2_1.txt
    output_directory = output/
    min_spec_rate = 1e-05
    sigma = 0.5
    tau = 2
    deme = 10
    sample_size = 0.1
    max_time = 2000
    dispersal_relative_cost = 1
    time_config = null
    min_species = 1


Dispersal Kernels
'''''''''''''''''

Three different dispersal functions are currently supported, which take some combination of the *sigma* (:math:`\sigma`)
, *tau* (:math:`\tau` ), *m_prob* (:math:`m` ) and *cutoff* (:math:`c` ) dispersal parameters. You only need to provide
the required parameters for each dispersal method; any additional parameters provided will be ignored.

- Normal distribution (the default)
    This requires :math:`\sigma` only (the standard deviation). The outputted dispersal kernel in two dimensions
    will follow a Rayleigh distribution for dispersal distance, :math:`N(r)`

- Fat-tailed distribution
    This requires both :math:`\sigma` and :math:`\tau`. Importantly, for our fat-tailed dispersal kernel, :math:`F(r)`,
    :math:`\lim{\tau \to \inf} = N(r)`. Within this dispersal kernel, there is an increased chance of long-distance
    dispersal (but lower than the normal-uniform dispersal kernel).

- Normal-uniform distribution
    This requires :math:`\sigma`, :math:`m` and :math:`c` . Here, we pick with probability :math:`1-m` from a normal
    distribution with standard deviation :math:`\sigma`, and probability :math:`m` from a uniform distribution. This
    uniform distribution picks a random distance uniformly between 0 and :math:`c`, the maximal dispersal distance. For
    very large :math:`c`, extremely long distance dispersal is possible.

It is also possible to provide a dispersal probability map, which sets the probability of dispersing from one cell to
another. The dispersal map should be dimensions *xy* by *xy* where *x* and *y* are the dimensions of the fine map. A
dispersal map can be set by using
:func:`set_map_files(dispersal_map="/path/to/dispersal.tif") <pycoalescence.simulation.Simulation.set_map_files>`.

**pycoalescence** has the ability to simulate a dispersal kernel on a landscape. For more information about that
process, see :ref:`here <simulate_landscapes>`

.. important:: In this scenario, it is not possible to use a coarse map, which should be "none".

Differing reproductive rates
''''''''''''''''''''''''''''

Simulations can use varying reproductive rates across the landscape, but using
:func:`set_map_files(reproduction_map="/path/to/rep.tif") <pycoalescence.simulation.Simulation.set_map_files>`. In this
scenario, all species have different per-capita reproduction rates across the landscape.

.. note:: Density is already taken into account during simulations for reproduction rates, so the reproduction map
          should be solely for the *per-capita* differences in reproductive rate.

.. important:: A reproduction map can only be used with a fine map, and coarse map should be set to "none".


Limitations of simulation variables
'''''''''''''''''''''''''''''''''''

.. important:: This section contains key information about the simulation inputs. Please read carefully to minimise any
               unnecessary bugs.

Certain simulation variables have limitations, depending on the method of setting up the simulation.

- Map variables set up using :func:`set_map_parameters() <pycoalescence.landscape.Landscape.set_map_parameters>`

    - Sample map dimensions must be smaller than fine map dimensions.
    - Fine map dimensions must be smaller than coarse map dimensions (supplied at the resolution of the fine map files).
    - Dimensions of historical fine and coarse maps must match their respective current map dimensions.
    - All offsets must maintain the smaller map within the larger map
    - If any files are supplied as 'null', map sizes must still be provided. This is important for sample map size, but
      should be corrected in a future update for coarse map files.


- Map files (and variables) set using :func:`set_map_files() <pycoalescence.simulation.Simulation.set_map_files>`

    - In addition to the above conditions being true, the files must all be georeferenced, so that coarse and fine map
      dimensions will be read correctly.

    .. hint:: Use a GIS program (such as ArcGIS or QGIS) for manipulation of map files to
              ensure georeferencing is preserved.

    - If the samplemask map is "null", the program will read the dimensions from the fine map and choose that as the
      area to sample entirely over. Supplying "null" will therefore sample the entirety of the fine map.

    .. hint:: Scalings and offsets between maps should also work correctly, but if problems are encountered, try manually
              specifying offsets and dimensions to identify any problems.

    - Both the reproduction map and dispersal map (if provided) must match the dimensions of the fine map. No coarse map
      should be provided in either scenario.

An example of how the map files are related is shown below. Black arrows indicate the offsets for the fine map (in the x
and y dimensions) and purple arrows indicate the offsets for the coarse map.

.. image:: src/grid_sample.png
    :alt: Example sample map, fine map and coarse map

Infinite Landscapes
'''''''''''''''''''

Simulations can also be run on infinite landscapes. Set ``landscape_types=opt`` in
:func:`set_simulation_params() <pycoalescence.simulation.Simulation.set_simulation_params>` where *opt* is one of the
following:

- "closed" (default)
    Run without infinite landscapes, with closed boundaries to the coarse map.

- "infinite"
    Run with a historical infinite landscape outside of the coares map boundaries.

- "tiled_coarse"
    Tile the coarse map infinitely in all dimensions. A coarse map must be provided.

- "tiled_fine"
    Tile the fine map infinitely in all dimensions. No coarse map should be provided.

Optimising Simulations
''''''''''''''''''''''

:func:`optimise_ram() <pycoalescence.simulation.Simulation.optimise_ram>` exists for reducing the RAM requirements of
a simulation. Running the function with a specific RAM limit, in GB, should choose a sample map size and offsets to
minimise the in-memory object sizes. This may have a minor impact on simulation speed, but this is likely negligible.
After the function is run, the :class:`Simulation class <pycoalescence.simulation.Simulation>` should have re-defined
the grid x and y dimensions to be the largest size possible to simulate for the required memory. The sample map offsets
from the grid are then also stored, such that the grid encompasses the area with the highest number of individuals.

:func:`optimise_ram() <pycoalescence.simulation.Simulation.optimise_ram>` may take some time to run. However, for a
single set of simulations with the same RAM limit, this function should only need to be completed once. Getting and
setting the optimised solution is therefore possible with
:func:`get_optimised_solution() <pycoalescence.simulation.Simulation.get_optimised_solution>` and
:func:`set_optimised_solution() <pycoalescence.simulation.Simulation.set_optimised_solution>`. The whole procedure is
outlined below.

.. code-block:: python

    # Detect the RAM-optimised solution
    >> sim1.optimise_ram()
    # Get the optimised solution for Simulation object sim1
    >> sim1.get_optimised_solution()
    {'grid_file_name': 'set',
    'grid_x_size': 5134,
    'grid_y_size': 5134,
    'sample_x_offset': 8208,
    'sample_y_offset': 14877}
    # Now set the optimised solution for Simulation object sim2
    >> sim2.set_optimised_solution({'grid_file_name': 'set',
                                  'grid_x_size': 5134,
                                  'grid_y_size': 5134,
                                  'sample_x_offset': 8208,
                                  'sample_y_offset': 14877})


.. _`Postsim_analysis`:
Post-simulation analysis
~~~~~~~~~~~~~~~~~~~~~~~~

Once simulations are complete, necsim's :ref:`applying speciation rates functionality <Introduction_SpeciationCounter>`
can be used to apply additional speciation rates to the coalescence tree. A simple way of applying additional simulation
rates is provided within the :class:`CoalescenceTree class<pycoalescence.coalescence_tree.CoalescenceTree>`.


The two functions for this routine are

-  :func:`set_speciation_params() <pycoalescence.coalescence_tree.CoalescenceTree.set_speciation_params>` which takes as
   arguments

   -  the SQL database file containing a finished simulation
   -  T/F of recording full spatial data
   -  either a csv file containing fragment data, or T/F for whether
      fragments should be calculated from squares of continuous habitat.
      \* list of speciation rates to apply
   -  [optional] a sample file to specify certain cells to sample from
   -  [optional] a config file containing the temporal sampling points
      desired.


-  :func:`apply_speciation() <pycoalescence.coalescence_tree.CoalescenceTree.apply_speciation>` performs the analysis.
   This can be extremely RAM and time-intensive for simulations of a large number of individuals. The calculations will
   be stored in extra tables within the same SQL file as originally
   specified.

The procedure for applying additional speciation rates to an existing database is

.. code-block:: python

    from pycoalescence import CoalescenceTree
    t = CoalescenceTree()
    speciation_rates = [0.1, 0.2 ,0.3]
    t.set_database("output/SQL_data/data_1_1.db")
    t.set_speciation_params("T", "null", speciation_rates)
    t.apply_speciation()

The :class:`CoalescenceTree class<pycoalescence.coalescence_tree.CoalescenceTree>` object can also be set up from a
:class:`Simulation class<pycoalescence.simulation.Simulation>` object as:

.. code-block:: python

    from pycoalescence import Simulation, CoalescenceTree
    sim = Simulation()
    # ... set up simulation here, then run
    # Now import our completed simulation without needing to run t.set_database("filepath")
    t = CoalescenceTree(sim)

A few biodiversity metrics can then be obtained directly from the database using built-in functions, relieving the user
of having to generate these manually. These include

- species richness, using :func:`get_richness() <pycoalescence.coalescence_tree.CoalescenceTree.get_richness>`

- species abundances, using :func:`get_species_abundances() <pycoalescence.coalescence_tree.CoalescenceTree.get_species_abundances>`

- species octave (2^n) classes for generating species abundance distributions,
  using :func:`get_octaves() <pycoalescence.coalescence_tree.CoalescenceTree.get_octaves>`

.. note:: The above functions require supplying a speciation rate and time, otherwise will output data for all
          speciation rates and times.

.. tip:: Equivalent functions also exist for obtaining individual fragment biodiversity metrics.

.. tip:: The entire list of species can be outputted using
         :func:`get_species_list <pycoalescence.coalescence_tree.CoalescenceTree.get_species_list>`. This may be useful for scenarios
         where it is desirable to calculate custom biodiversity metrics.

Extended analysis
~~~~~~~~~~~~~~~~~

The :py:mod:`coalescence_tree <pycoalescence.coalescence_tree>` module can be used for more extensive simulation analysis, such
as comparing simulated landscapes to real data and calculating goodness of fits.

The general procedure for using this module involves a few functions, all contained in the
:class:`CoalescenceTree class <pycoalescence.coalescence_tree.CoalescenceTree>`.

- :func:`set_database() <pycoalescence.coalescence_tree.CoalescenceTree.set_database>` generates the link to the SQL
  database, which should be an output from a **necsim** simulation (run using the
  :class:`Simulation class <pycoalescence.simulation.Simulation>`).
- :func:`import_comparison_data() <pycoalescence.coalescence_tree.CoalescenceTree.import_comparison_data>` reads an
  SQL database which contains real data to compare to the simulation output. The comparison data should contain the
  following tables:

  - BIODIVERSITY\_ METRICS, containing *only* "metric", "fragment", "value" and "number_of_individuals" columns.
    The metric can be "fragment_richness" or any other metric created by your own functions which exists also in
    the simulated data.
  - SPECIES\_ABUNDANCES containing *at least* "SpeciesID", "Abund".

Additionally, one can provide the following if comparisons between fragments are required:

  - FRAGMENT\_ABUNDANCES containing *at least* "Plot", "Mnemonic" and "Abund".
  - FRAGMENT\_OCTAVES containing *at least* "fragment", "octave", "num_species". This can also be calculated from
    FRAGMENT\_ABUNDANCES using :func:`calculate_comparison_octaves() <pycoalescence.coalescence_tree.CoalescenceTree.calculate_comparison_octaves>`


Extended Features
~~~~~~~~~~~~~~~~~

- Read tif files and perform a number of operations taking into account georeferencing of the data.
  Functionality is contained within the :class:`Map class <pycoalescence.map.Map>` (see :ref:`here <map_reading>`).
- Generate fragmented landscapes (see :ref:`here <generate_landscapes>`). This may be useful for generating example
  landscapes of a particular size with desired characteristics.
- Simulate a dispersal kernel on a landscape to obtain characteristics of the effective dispersal kernel. Currently only
  a single map is supported with "closed", "infinite" or "tiled" landscape types (see :ref:`here <simulate_landscapes>`).
- Simulations can be merged into a single output, with each simulation occupying a separate guild (see
  :ref:`here <merging_simulations>`). Analyses can then be performed on the combined data.




Testing install
~~~~~~~~~~~~~~~

The system install can be tested by running :py:mod:`test_install.py <pycoalescence.test_install>` from the command line
(``python test_install.py``) which requires that ``python setup.py`` has been successfully run previously.

Prerequisites
-------------

Essential
~~~~~~~~~

-  Python version 2 >= 2.7.9 or 3 >= 3.4.1
-  C++ compiler (such as GNU g++) with C++11 support.
-  The SQLite library available `here <https://www.sqlite.org/download.html>`__. Require both ``c++`` and ``python`` installations.
-  The Boost library for C++ available `here <http://www.boost.org>`__.

-  Numerical python (``numpy``) package.

.. tip:: Most packages, including their c++ libraries, can be installed using `pip install package_name` on most UNIX
         systems.

Recommended
~~~~~~~~~~~

- The gdal library for both python and C++ (`available here <http://www.gdal.org/>`__). This is **ESSENTIAL** if you wish
  to use .tif files for :ref:`necsim <Introduction_necsim>`.  It allows reading parameter information from .tif files
  (using :func:`detect_map_dimensions() <pycoalescence.simulation.Simulation.detect_map_dimensions>`). Both the python
  package and ``c++`` binaries are required; installation differs between systems, so view the gdal documentation for more
  help installing gdal properly.
- The fast-cpp-csv-parser by Ben Strasser, available
  `here <https://github.com/ben-strasser/fast-cpp-csv-parser>`__. This provides much faster csv read and write capabilities
  and is probably essential for larger-scale simulations, but not necessary if your simulations are small. The folder
  *fast-cpp-csv-parser/* should be in the same directory as your **necsim** C++ header files (the lib/necsim directory).

.. note:: Running ``configure`` (or ``python setup.py``) will detect system components, including ``sqlite3``, ``boost``,
   ``gdal`` and ``fast-cpp-csv-parser`` and set the correct compilation flags.

.. include:: Glossary.rst

Version
-------

Version |release|

Contacts
--------

Author: Samuel Thompson

Contact: samuelthompson14@imperial.ac.uk - thompsonsed@gmail.com

Institution: Imperial College London and National University of
Singapore

This project is released under BSD-3 See file
**LICENSE.txt** or go to
`here <https://opensource.org/licenses/BSD-3-Clause>`__ for full license
details.
