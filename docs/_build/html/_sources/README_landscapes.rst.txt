.. _`simulate_and_generate_landscapes`:
Simulating and generating landscapes
====================================

Introduction
------------

**pycoalescence** provides functionality for generating fragmented landscapes for simulations, and simulating dispersal
kernels to produce a variety of landscape-level dispersal metrics. Generation of landscapes is provided through the
:class:`FragmentedLandscape class <pycoalescence.fragments.FragmentedLandscape>`. Simulations of dispersal kernels is
provided through the :class:`DispersalSimulation class <pycoalescence.dispersal_simulation.DispersalSimulation>`.

.. _`generate_landscapes`:
Generating landscapes
---------------------

Fragmented Landscapes
'''''''''''''''''''''

For our purposes, we define fragmented landscapes as continuous, fully spatial landscapes of a particular size, with n
individuals split across i equally (or as close to) sized fragments, which are evenly spaced across the landscape.
**pycoalescence** provides the routines for generating these landscapes within
:class:`FragmentedLandscape class <pycoalescence.fragments.FragmentedLandscape>`.

The parameters for generating a fragmented landscape are the total landscape size, the habitat area within the landscape
(i.e. the number of individuals) and the number of fragments to place. The habitat area cannot be more than 50% of the
landscape size, as at this point fragments become non-distinct. The process is:

.. code-block:: python

    from pycoalescence import FragmentedLandscape
    f = FragmentedLandscape(size=100, number_fragments=10, total=20, output_file="fragment.tif")
    f.generate()


Patched Landscapes
''''''''''''''''''

We define patched landscapes as a number of interconnected patches, each containing a certain number of well-mixed
individuals (the patch's density) and every patch is has some probability of dispersal to every other patch (which can
be 0). Another imagination of this concept is of a series of connected islands, where each island is modelled
non-spatially, and every island has a probability of dispersing to all other islands.
**pycoalescence** provides the routines for generating these landscapes within
:class:`PatchedLandscape class <pycoalescence.patched_landscape.PatchedLandscape>`.

Creation of a patched landscape requires first defining all the patches that exist in the landscape, and then setting
the dispersal probability between each island. If any dispersal probability is not set, it is assumed to be 0. The
dispersal probability from one patch to itself must be provided (but can be 0). The probability values provided are then
re-scaled to sum to 1, and re-generated as cumulative probabilities.



.. _`simulate_landscapes`:
Simulated landscapes
--------------------

To simulate a dispersal kernel on a landscape, there are two processes; simulating a single step and simulating multiple
steps. For a single step, the distance travelled is recorded into the output database. The mean, standard deviation and
other metrics can be obtained from this. For multiple steps, the total distance travelled after n steps is recorded.
Both methods follow the same structure,

.. code-block:: python

    from pycoalescence import DispersalSimulation
    m = DispersalSimulation(dispersal_db="path/output.db")
    m.test_mean_dispersal(number_repeats=100000, output_database=out_db, map_file="path/map.tif", seed=seed,
                          dispersal_method="normal", sigma=sigma, landscape_type="tiled")
    m.test_mean_distance_travelled(number_repeats=1000, number_steps=10,
                                   map_file="path/map.tif", seed=seed, dispersal_method="normal",
                                   sigma=sigma, landscape_type="tiled")
    # The reference parameters correspond to the order they were simulated with
    parameters_list = m.getdatabase_parameters()
    # Each of these contain parameters for the first and second simulation
    parameters_1 = parameters_list[1]
    parameters_2 = parameters_list[2]
    # We can therefore just use the reference numbers (1 or 2) to obtain metrics
    m.get_mean_dispersal(parameter_reference=1)
    m.get_mean_distance_travelled(parameter_reference=2)
    m.get_stdev_dispersal(parameters_reference=1)


.. _`map_reading`:
Reading and writing tif files
-----------------------------

The :class:`Map class <pycoalescence.map.Map>` is used for detecting offsets and dimensions of tif files for
the main program. There are therefore a number of additional features in this class.


- Data can be read using :func:`get_subset() <pycoalescence.map.Map.get_subset>` and
  :func:`get_cached_subset() <pycoalescence.map.Map.get_cached_subset>`.
- Dimensions can be determined using :func:`get_dimensions() <pycoalescence.map.Map.get_dimensions>`. The entire tif
  file can also be read into a numpy array using :func:`open() <pycoalescence.map.Map.open>` and then indexing on
  :attr:`data <pycoalescence.map.Map.data>`.
- A shapefile can be rasterised to a new tif file using :func:`rasterise() <pycoalescence.map.Map.rasterise>`.
- Tif files can be re-projected to either a new or the same file using
  :func:`open() <pycoalescence.map.Map.reproject_raster>`.

.. note:: All processing is done using the gdal module.