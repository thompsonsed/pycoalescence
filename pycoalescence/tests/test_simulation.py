"""
Contains relatively high-level tests of Simulation object, testing a variety of simulation parameter combinations
to assert simulation outputs are as expected.
"""
import logging
import os
import unittest

try:
	from cStringIO import StringIO  # Python 2 string support
except ImportError:
	from io import StringIO

from pycoalescence import Simulation
from pycoalescence.tests.setup import setUpAll, tearDownAll, skipLongTest


def setUpModule():
	"""
	Creates the output directory and moves logging files
	"""
	setUpAll()


def tearDownModule():
	"""
	Removes the output directory
	"""
	tearDownAll()


class TestFileCreation(unittest.TestCase):
	"""
	Tests the main Simulation set up routine by running some tiny simulations and checking that simulation parameters
	are passed properly.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=logging.CRITICAL)
		self.coal.set_simulation_params(0, 0, "output/test_output/test_output2/", 0.1, 4, 4, deme=1, sample_size=1.0,
										max_time=2,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_historical=2, dispersal_method="normal")
		self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.run()

	def testFileCreation(self):
		"""
		Checks that outputting is to the correct place and folder structure is created properly.
		"""
		self.assertTrue(os.path.isfile(self.coal.output_database))
		self.assertEqual(os.path.join(self.coal.output_database),
						 os.path.join(self.coal.output_directory, "data_{}_{}.db".format(self.coal.seed,
																						 self.coal.job_type)))


class TestFileNaming(unittest.TestCase):
	"""
	Tests that the file naming structure makes sense
	"""
	def testNoneNaming(self):
		"""
		Tests that the fine map file naming throws the correct error when called 'none'.
		:return:
		"""
		coal = Simulation()
		coal.set_simulation_params(0, 0, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
								   dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
								   gen_since_historical=2, dispersal_method="normal")
		with self.assertRaises(ValueError):
			coal.set_map_files(sample_file="null", fine_file="null")


class TestOffsetMismatch(unittest.TestCase):
	"""
	Tests if simulations correctly detect when offsets between fine and sample, or fine and coarse maps do not make
	sense.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the class by creating simulation object with the desired map structure.
		"""
		cls.coal1 = Simulation(logging_level=logging.CRITICAL)
		cls.coal1.set_simulation_params(seed=1, job_type=38, output_directory="output", min_speciation_rate=0.1,
										sigma=4, max_time=2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										cutoff=0.0)
		cls.coal2 = Simulation()
		cls.coal2.set_simulation_params(seed=1, job_type=38, output_directory="output", min_speciation_rate=0.1,
										sigma=4, max_time=2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										cutoff=0.0)

	def testRaisesErrorFineSampleOffset(self):
		"""
		Tests the correct error is raised when offsetting is incorrect
		"""
		with self.assertRaises(ValueError):
			self.coal1.set_map_files(sample_file="sample/SA_samplemaskINT.tif",
									 fine_file="sample/SA_sample_fine_offset.tif")

	def testRaisesErrorFineSampleOffset2(self):
		"""
		Tests the correct error is raised when offsetting is incorrect
		"""
		with self.assertRaises(ValueError):
			self.coal2.set_map_files(sample_file="null",
									 fine_file="sample/SA_sample_fine_offset.tif",
									 coarse_file="sample/SA_sample_coarse.tif")

	def testRaisesErrorAfterIncorrectSamplegridBoundaries(self):
		"""
		Checks that setting incorrect limits for the sample grid outside of the fine map causes an error to be thrown.
		"""
		sim = Simulation()
		sim.set_simulation_params(seed=1, job_type=1, output_directory="output", min_speciation_rate=0.001, sigma=2)
		sim.set_map_files(sample_file="null", fine_file="sample/SA_sample_fine_offset.tif",
						  coarse_file="none")
		sim.sample_map.x_offset = 10000
		sim.sample_map.y_offset = 10000
		sim.grid.x_size = 1000
		sim.grid.y_size = 1000
		sim.grid.file_name = "set"
		with self.assertRaises(ValueError):
			sim.finalise_setup()
			sim.run_coalescence()


class TestSimulationRaisesErrors(unittest.TestCase):
	"""
	Tests that protracted and normal simulations raise the NECSimError when NECSim throws an error
	"""

	def testNormalRaisesError(self):
		"""
		Tests a normal simulation raises an error when no files exist
		"""
		c = Simulation()
		c.set_simulation_params(5, 4, "output", 0.1, 4, 4, 1, 0.01, 2, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								dispersal_method="fat-tail")
		c.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
						coarse_file="sample/SA_sample_coarse.tif")
		# Now change map name to something that doesn't exist

		c.fine_map.file_name = "not_here.tif"
		with self.assertRaises(IOError):
			c.finalise_setup()
		with self.assertRaises(RuntimeError):
			c.run_coalescence()

	def testProtractedRaisesError(self):
		"""
		Tests a protracted simulation raises an error if there is a problem
		"""
		c = Simulation(logging_level=logging.ERROR)
		c.set_simulation_params(6, 4, "output", 0.1, 4, 4, 1, 0.01, 2, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								dispersal_method="fat-tail", protracted=True)
		c.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
						coarse_file="sample/SA_sample_coarse.tif")
		# Now change map name to something that doesn't exist

		c.fine_map.file_name = "not_here.tif"
		with self.assertRaises(IOError):
			c.finalise_setup()
		with self.assertRaises(RuntimeError):
			c.run_coalescence()


class TestSimulationConfigReadWrite(unittest.TestCase):
	"""
	Tests the reading and writing to a config text file.
	Independently tests the main config, map config and time config writing ability.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=logging.CRITICAL)
		self.coal.set_simulation_params(1, 23, "output", 0.1, 4, 4, 1, 1.0, max_time=200, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										dispersal_method="fat-tail")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.add_sample_time(0.0)
		self.coal.add_sample_time(1.0)
		self.coal.full_config_file = "output/conf1.txt"
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.create_config()

	def testConfigWrite(self):
		"""
		Tests that the main configuration file has been correctly generated.
		"""
		with open("output/conf1.txt", "r") as mapconf:
			lines = mapconf.readlines()
			lines = [x.strip() for x in lines]
			self.assertEqual(lines[0], "[main]")
			self.assertEqual(lines[1].replace(" ", ""), "seed=1")
			self.assertEqual(lines[2].replace(" ", ""), "job_type=23")

	def testMapConfigWrite(self):
		"""
		Tests the map config output to check output is correct.
		"""
		self.coal.add_historical_map(fine_map="sample/SA_sample_fine_historical1.tif",
									 coarse_map="sample/SA_sample_coarse_historical1.tif",
									 time=1, rate=0.5)
		self.coal.add_historical_map(fine_map="sample/SA_sample_fine_historical2.tif",
									 coarse_map="sample/SA_sample_coarse_historical2.tif",
									 time=4, rate=0.7)
		self.coal.create_map_config("output/mapconf2.txt")
		with open("output/mapconf2.txt", "r") as mapconf:
			lines = mapconf.readlines()
			lines = [x.strip() for x in lines]
			self.assertEqual(lines[21], "[sample_grid]")
			self.assertEqual(lines[22].replace(" ", ""), "path=null", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[28].replace(" ", ""), "[fine_map]",
							 msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[29].replace(" ", ""), "path=sample/SA_sample_fine.tif",
							 msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[30].replace(" ", ""), "x=13", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[31].replace(" ", ""), "y=13", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[32].replace(" ", ""), "x_off=0", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[33].replace(" ", ""), "y_off=0", msg="Config file doesn't produce expected output.")

	def testTimeConfigWrite(self):
		"""
		Tests the map config writing is correct.
		"""
		with open("output/conf1.txt", "r") as f:
			lines = f.readlines()
			lines = [x.strip().replace(" ", "") for x in lines]
			self.assertEqual(lines[17], "[times]", msg="Time config file doesn't produce expected output.")
			self.assertEqual(lines[18], "time0=0.0", msg="Time config file doesn't produce expected output.")
			self.assertEqual(lines[19], "time1=1.0", msg="Time config file doesn't produce expected output.")


class TestSimulationSetMaps(unittest.TestCase):
	"""
	Tests that the basic set_map_file() function works as intended and runs a very basic simulation.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Creates the coalescence object and runs the setup for the map file
		"""
		cls.c = Simulation()
		cls.c.set_map("null", 10, 10)
		cls.c.set_simulation_params(seed=1, job_type=12, output_directory="output", min_speciation_rate=0.01, sigma=2)
		cls.c.run()

	def testMapFilesSetCorrectly(self):
		"""
		Tests that the maps files are set correctly.
		"""
		self.assertEqual(self.c.fine_map.file_name, "null")
		self.assertEqual(self.c.fine_map.x_size, 10)
		self.assertEqual(self.c.fine_map.y_size, 10)
		self.assertEqual(self.c.coarse_map.file_name, "none")
		self.assertEqual(self.c.coarse_map.x_size, 10)
		self.assertEqual(self.c.coarse_map.x_size, 10)
		self.assertEqual(self.c.sample_map.file_name, "null")
		self.assertEqual(self.c.sample_map.x_size, 10)
		self.assertEqual(self.c.sample_map.y_size, 10)

	def testSimulationCompletes(self):
		"""
		Tests that the simulation completes successfully and outputs as intended.
		"""
		self.assertEqual(self.c.get_richness(), 6)

	def testOrdersHistoricalMaps(self):
		"""
		Tests that the historical maps are correctly re-ordered.
		"""
		historical_maps_fine = ["mapb", "mapa", "mapc", "mapd"]
		historical_maps_coarse = ["mapcb", "mapca", "mapcc", "mapcd"]
		times = [10, 0, 11, 14]
		rates = [0.0, 0.2, 0.9, 0.3]
		s = Simulation()
		s.historical_fine_list = historical_maps_fine
		s.historical_coarse_list = historical_maps_coarse
		s.times_list = times
		s.rates_list = rates
		s.sort_historical_maps()
		expected_fine = ["mapa", "mapb", "mapc", "mapd"]
		expected_coarse = ["mapca", "mapcb", "mapcc", "mapcd"]
		expected_times = [0, 10, 11, 14]
		expected_rates = [0.2, 0.0, 0.9, 0.3]
		self.assertListEqual(expected_fine, s.historical_fine_list)
		self.assertListEqual(expected_coarse, s.historical_coarse_list)
		self.assertListEqual(expected_times, s.times_list)
		self.assertListEqual(expected_rates, s.rates_list)


class TestLoggingOutputsCorrectly(unittest.TestCase):
	"""
	Tests that logging outputs as expected.
	"""

	def testOutputStreamerInfo(self):
		"""
		Tests that info output streaming works as intended.
		"""
		log_stream = StringIO()
		with open("reference/log_12_2.txt", "r") as content_file:
			expected_log = content_file.read().replace('\r', '').replace('\n', '')
		s = Simulation(logging_level=logging.INFO, stream=log_stream)
		s.set_simulation_params(seed=2, job_type=12, output_directory="output", min_speciation_rate=0.1)
		s.set_map("null", 10, 10)
		s.run()
		log = log_stream.getvalue().replace('\r', '').replace('\n', '')
		self.assertEqual(expected_log, log)

	def testOutputStreamerWarning(self):
		"""
		Tests that info output streaming works as intended.
		"""
		log_stream = StringIO()
		s = Simulation(logging_level=logging.WARNING, stream=log_stream)
		s.set_simulation_params(seed=3, job_type=12, output_directory="output", min_speciation_rate=0.1)
		s.set_map("null", 10, 10)
		s.finalise_setup()
		s.run_coalescence()
		self.assertEqual("", log_stream.getvalue())

	def testOutputStreamerCritical(self):
		"""
		Tests that info output streaming works as intended.
		"""
		log_stream = StringIO()
		s = Simulation(logging_level=logging.CRITICAL, stream=log_stream)
		s.set_simulation_params(seed=4, job_type=12, output_directory="output", min_speciation_rate=0.1)
		s.set_map("null", 10, 10)
		s.finalise_setup()
		s.run_coalescence()
		self.assertEqual("", log_stream.getvalue())


@skipLongTest
class TestInitialCountSuccess(unittest.TestCase):
	"""
	Tests that the initial count is correct
	"""

	def testInitialCountNoCritical(self):
		"""
		Tests that the initial count is successful by catching the output of the critical logging.
		"""
		log_stream = StringIO()
		s = Simulation(logging_level=logging.CRITICAL, stream=log_stream)
		s.set_simulation_params(seed=5, job_type=12, output_directory="output", min_speciation_rate=0.1)
		s.set_map_files(sample_file="null", fine_file="sample/large_fine.tif")
		s.sample_map.x_size = 10
		s.sample_map.y_size = 10
		s.fine_map.x_offset = 100
		s.fine_map.y_offset = 120
		s.finalise_setup()
		s.run_coalescence()
		self.assertEqual("", log_stream.getvalue())


class TestSimulationDimensionsAndOffsets(unittest.TestCase):
	"""
	Test the dimension detection and offsets of Simulation
	"""

	@classmethod
	def setUpClass(cls):
		cls.coal = Simulation()
		cls.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							   coarse_file="sample/SA_sample_coarse.tif")
		cls.coal2 = Simulation()
		cls.coal2.set_map_files(sample_file="null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")

	def testFineMapDimensions(self):
		"""
		Checks that the dimensions and offsets are properly calculated.
		"""
		self.assertEqual(self.coal.fine_map.x_offset, 0)
		self.assertEqual(self.coal.fine_map.y_offset, 0)
		self.assertAlmostEqual(self.coal.fine_map.x_res, 0.00833308, 5)
		self.assertAlmostEqual(self.coal.fine_map.y_res, -0.00833308, 5)
		self.assertEqual(self.coal.fine_map.x_size, 13)
		self.assertEqual(self.coal.fine_map.y_size, 13)

	def testFineMapDimensionsNull(self):
		"""
		Checks that the dimensions and offsets are properly calculated when there is a null map provided as the
		samplemask.
		"""
		self.assertEqual(self.coal2.fine_map.x_offset, 0)
		self.assertEqual(self.coal2.fine_map.y_offset, 0)
		self.assertAlmostEqual(self.coal2.fine_map.x_res, 0.00833308, 5)
		self.assertAlmostEqual(self.coal2.fine_map.y_res, -0.00833308, 5)
		self.assertEqual(self.coal2.fine_map.x_size, 13)
		self.assertEqual(self.coal2.fine_map.y_size, 13)

	def testCoarseMapDimensions(self):
		"""
		Checks that the dimensions and offsets are properly calculated.
		"""
		self.assertEqual(self.coal.coarse_map.x_offset, 11)
		self.assertEqual(self.coal.coarse_map.y_offset, 14)
		self.assertAlmostEqual(self.coal.coarse_map.x_res, 0.00833308, 5)
		self.assertAlmostEqual(self.coal.coarse_map.y_res, -0.00833308, 5)
		self.assertEqual(self.coal.coarse_map.x_size, 35)
		self.assertEqual(self.coal.coarse_map.y_size, 41)

	def testCoarseMapDimensionsNull(self):
		"""
		Checks that the dimensions and offsets are properly calculated when there is a null map provided as the
		samplemask.
		"""
		self.assertEqual(self.coal2.coarse_map.x_offset, 11)
		self.assertEqual(self.coal2.coarse_map.y_offset, 14)
		self.assertAlmostEqual(self.coal2.coarse_map.x_res, 0.00833308, 5)
		self.assertAlmostEqual(self.coal2.coarse_map.y_res, -0.00833308, 5)
		self.assertEqual(self.coal2.coarse_map.x_size, 35)
		self.assertEqual(self.coal2.coarse_map.y_size, 41)

	def testSimStart(self):
		"""
		Checks that the correct exceptions are raised when simulation is started without being properly setup
		"""
		with self.assertRaises(RuntimeError):
			self.coal.run_coalescence()


class TestSimulationExtremeSpeciation(unittest.TestCase):
	"""
	Tests extreme speciation values to ensure that either 1 or maximal numbers of species are produced.
	"""

	def testZeroSpeciation(self):
		"""
		Tests that running a simulation with a zero speciation rate produces a single species.
		"""
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=17, output_directory="output", min_speciation_rate=0.0,
								sigma=2.0, tau=1, deme=1, sample_size=1, max_time=4,
								dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								dispersal_method="normal",
								landscape_type=False)
		c.set_map("null", 10, 10)
		c.run()
		self.assertEqual(c.get_richness(), 1)

	def testMaxSpeciation(self):
		"""
		Tests that running a simulation with a zero speciation rate produces a single species.
		"""
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=18, output_directory="output", min_speciation_rate=1.0,
								sigma=2.0, tau=1, deme=1, sample_size=1, max_time=4,
								dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								dispersal_method="normal",
								landscape_type=False)
		c.set_map("null", 10, 10)
		c.run()
		self.assertEqual(c.get_richness(), 100)


class TestSimulationMapDensityReading(unittest.TestCase):
	"""
	Tests that the density estimation is relatively accurate and the reading actual density from a map is accurate.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the coalescence object for referencing the map objects
		"""
		cls.c = Simulation()
		cls.c.set_simulation_params(seed=1, job_type=36, output_directory="output", min_speciation_rate=0.5,
									sigma=2, tau=2, deme=64000, sample_size=0.00005, max_time=10,
									dispersal_relative_cost=1,
									min_num_species=1, habitat_change_rate=0, gen_since_historical=200)
		cls.c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")

	def testActualDensity(self):
		"""
		Tests the actual density
		"""
		self.assertEqual(self.c.grid_density_actual(0, 0, self.c.sample_map.x_size, self.c.sample_map.y_size), 531)

	def testEstimateDensity(self):
		"""
		Tests the estimate density for the sample grid
		"""
		self.assertEqual(self.c.grid_density_estimate(0, 0, self.c.sample_map.x_size, self.c.sample_map.y_size), 375)

	def testFineAverageMap(self):
		"""
		Tests the average density of the fine map is correct.
		"""
		self.assertAlmostEqual(self.c.get_average_density(), 38339.499790687034, 3)

	def testCountIndividuals(self):
		"""
		Tests that the count of numbers of individuals is roughly accurate
		"""
		self.assertTrue(self.c.count_individuals() - 12381 < 2200)


class TestHistoricalMapsAlterResult(unittest.TestCase):
	"""
	Makes sure that historical maps correctly alter the result of the simulation.
	"""

	@classmethod
	def setUpClass(cls):
		cls.base_sim = Simulation()
		cls.hist_sim = Simulation()
		cls.base_sim.set_simulation_params(seed=4, job_type=17, output_directory="output",
										   min_speciation_rate=0.1, sigma=2, sample_size=0.1)
		cls.base_sim.set_map("sample/SA_sample_fine.tif")
		cls.base_sim.run()
		cls.hist_sim.set_simulation_params(seed=4, job_type=18, output_directory="output",
										   min_speciation_rate=0.1, sigma=2, sample_size=0.1)
		cls.hist_sim.set_map("sample/SA_sample_fine.tif")
		cls.hist_sim.add_historical_map(fine_map="sample/example_historical_fine.tif", coarse_map="none",
										time=10, rate=0.2)
		cls.hist_sim.run()
		cls.hist_sim2 = Simulation()
		cls.hist_sim2.set_simulation_params(seed=4, job_type=19, output_directory="output",
											min_speciation_rate=0.1, sigma=2, sample_size=0.1)
		cls.hist_sim2.set_map("sample/SA_sample_fine.tif")
		cls.hist_sim2.add_historical_map(fine_map="sample/example_historical_fine.tif", coarse_map="none",
										 time=10, rate=0.2)
		cls.hist_sim2.add_historical_map(fine_map="sample/SA_sample_fine.tif", coarse_map="none",
										 time=20, rate=0.2)
		cls.hist_sim2.run()

	def testSpeciesRichnessDiffer(self):
		"""
		Tests that the species richness differs between the two simulations
		"""
		self.assertNotEqual(self.base_sim.get_richness(), self.hist_sim.get_richness())
		self.assertNotEqual(self.hist_sim.get_richness(), self.hist_sim2.get_richness())
		self.assertEqual(2627, self.base_sim.get_richness())
		self.assertEqual(2520, self.hist_sim2.get_richness())
		self.assertEqual(2434, self.hist_sim.get_richness())

@skipLongTest
class TestExpansionOverTime(unittest.TestCase):
	"""Tests that large expansions over time are dealt with properly when sampling multiple time points."""

	@classmethod
	def setUpClass(cls):
		"""Run the simulation for expansion over time."""
		cls.sim = Simulation(logging_level=50)
		cls.sim.set_simulation_params(seed=5, job_type=17, output_directory="output", min_speciation_rate=0.0001,
									  sigma=1, deme=100, sample_size=1.0, landscape_type="infinite")
		cls.sim.set_map_files("null", "sample/null.tif", "sample/null_large.tif")
		cls.sim.add_historical_map("sample/null.tif", "sample/null_large.tif", time=500, rate=0.5)
		cls.sim.add_sample_time([0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
		cls.sim.run()

	def testSpeciesRichnessAtTimes(self):
		"""Checks the species richness is correct for each time point."""
		self.assertEqual(100, self.sim.get_richness(1))
		self.assertEqual(100, self.sim.get_richness(2))
		self.assertEqual(100, self.sim.get_richness(3))
		self.assertEqual(100, self.sim.get_richness(4))
		self.assertEqual(100, self.sim.get_richness(5))
		self.assertEqual(100, self.sim.get_richness(6))
