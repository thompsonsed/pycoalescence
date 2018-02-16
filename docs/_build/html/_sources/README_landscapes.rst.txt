.. _`Simulate_landscapes`:
Simulating and generating landscapes
====================================

Introduction
------------

**pycoalescence** provides functionality for generating fragmented landscapes for simulations, and simulating dispersal
kernels to produce a variety of landscape-level dispersal metrics. Generation of landscapes is provided through the
:class:`FragmentedLandscape class <pycoalescence.fragments.FragmentedLandscape>`. Simulations of dispersal kernels is
provided through the :class:`Map class <pycoalescence.map.Map>`.

Generating landscapes
---------------------

The parameters for generating a fragmented landscape are the total landscape size, the habitat area within the landscape
(i.e. the number of individuals) and the number of fragments to place. The habitat area cannot be more than 50% of the
landscape size, as at this point fragments become non-distinct. The process is handled by the
:class:`FragmentedLandscape class <pycoalescence.fragments.FragmentedLandscape>`. The process is:

.. code-block:: python

    from pycoalescence import FragmentedLandscape
    f = FragmentedLandscape(size=100, number_fragments=10, total=20, output_file="fragment.tif")
    f.generate()



Simulated landscapes
--------------------

To simulate a dispersal kernel on a landscape, there are two processes; simulating a single step and simulating multiple
steps. For a single step, the distance travelled is recorded into the output database. The mean, standard deviation and
other metrics can be obtained from this. For multiple steps, the total distance travelled after n steps is recorded.
Both methods follow the same structure,

.. code-block:: python

    from pycoalescence import Map
    m = Map(dispersal_db="path/output.db")
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

The :class:`Map class <pycoalescence.map.Map>` is also used for detecting offsets and dimensions of tif files for
the main program. There are therefore a number of additional features in this class. Data can be read
using :func:`get_subset() <pycoalescence.map.Map.get_subset>` and
:func:`get_cached_subset() <pycoalescence.map.Map.get_cached_subset>`. Dimensions can be determined using
:func:`get_dimensions() <pycoalescence.map.Map.get_dimensions>`. The entire tif file can also be read into a numpy array
using :func:`open() <pycoalescence.map.Map.open>` and then indexing on :attr:`data <pycoalescence.map.Map.data>`.