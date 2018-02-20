"""
Compiles NECSim for several simulation scenarios and tests the output to make sure simulation results are as expected.
Also performs limited tests of the PyCoalescence setup routines.

.. note:: If test_install.py has not been run before, compilation may take a while, depending on your system, as it
   compiles NECSim for several different options.
"""
from __future__ import absolute_import

import os, sys, inspect
import unittest
from shutil import rmtree
import numpy as np
import gdal
# Conditional import for python 2 being stupid


if sys.version_info[0] is not 3:
	class FileExistsError(IOError):
		pass

try:
	import sqlite3
except ImportError:
	import sqlite as sqlite3

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from pycoalescence.simulation import Simulation, Map, NECSimError
from pycoalescence.coalescence_tree import CoalescenceTree, get_parameter_description, fetch_table_from_sql,\
	check_sql_table_exist, ApplySpecError
from pycoalescence.setup import *
from pycoalescence.system_operations import *
from pycoalescence.fragments import FragmentedLandscape
from pycoalescence.merger import Merger
from pycoalescence.helper import update_parameter_names


# from pycoalescence.setup import configure_and_compile as setupmain


def make_all_compile(recompile=False, build_dir="build/", opt_list=None, folder_list=None):
	"""
	Compiles the program for a set number of options arguments. The default behaviour (override by recompile=True) is to
	only compile if there is no NECSim or SpeciationCounter executable.

	Without providing an build_dir, opt_list or folder_list, it takes the following values:
	build_dir = "build/nv/"
	opt_list = [["--with-normal_dispersal", "--with-infinite_landscape"],
				[ "--with-fat_tail_dispersal"],["--with-normal_dispersal"]]

	folder_list = ["norm_inf_land/", "fat_tailed/", "norm/"]

	These are the required executables for performing the unit testing of pycoalescence.

	.. deprecated:: 1.1.0

	:param recompile: if True, deletes any existing file and recompiles.
	:param build_dir: optionally set a build directory. Defaults to the non-verbose version, saving outputs in build/nv/
	:param opt_list: optionally set a list of options to compile with. Must also specify a folder_list
	:param folder_list: optionally set a list of output folders. Must also specify an opt_list
	"""
	set_logging_method(logging_level=logging.CRITICAL, output=None)
	if (opt_list is None and folder_list is not None) or (folder_list is None and opt_list is not None):
		raise RuntimeError("Attempt to set option list without specifying a folder list.")
	if opt_list is None:
		opt_list = [["--with-normal_dispersal", "--with-infinite_landscape"],
					["--with-fat_tail_dispersal", "--with-infinite_landscape"], ["--with-normal_dispersal"],
					["--with-verbose", "--with-normal-dispersal"]]
		folder_list = ["nv/norm_inf_land/", "nv/fat_tailed/", "nv/norm/", "v/norm/"]
	autoconf()
	for i, each in enumerate(opt_list):
		try:
			output_path = os.path.join(build_dir, folder_list[i])
			if recompile or not os.path.exists(os.path.join(output_path, "NECSim")) or not \
					os.path.exists(os.path.join(output_path, "SpeciationCounter")):
				configure(each)
				clean()
				do_compile()
				move_executable(output_path)
		except RuntimeError as rte:
			logging.warning(rte.message)
		except IOError as ioe:
			logging.warning(ioe.message)
		except Exception as ue:
			raise ue


def setUpModule():
	"""
	Copies the log folder to a new folder so that the normal log folder can be removed entirely.
	"""
	set_logging_method(logging_level=logging.CRITICAL)
	np.random.seed(0)
	if os.path.exists("output"):
		rmtree("output", True)
	os.mkdir("output")
	global log_path
	log_path = None
	if os.path.exists("Logs"):
		try:
			log_path = "Logs2"
			os.rename("Logs/", "Logs2")
		except OSError:
			try:
				log_path = "Logs_tmp"
				os.rename("Logs/", "Logs_tmp")
			except OSError as oe:
				logging.warning(oe.message)
				logging.warning("Cannot rename Log directory: deleting instead.")
				log_path = None


def tearDownModule():
	"""
	Overrides the in-built behaviour for tearing down the module. Removes the output folder to clean up after testing.
	"""
	rmtree("output", True)
	if os.path.exists("output"):
		for file in os.listdir("output"):
			p = os.path.join("output", file)
			if os.path.isdir(p):
				rmtree(p, ignore_errors=True)
			else:
				os.remove(p)
		try:
			os.removedirs("output")
		except OSError:
			raise OSError("Output not deleted")
	rmtree("Logs", True)
	rmtree("log", True)
	if log_path is not None:
		os.rename(log_path, "Logs")


def perform_checks():
	"""
	Tests the install for certain parameters to ensure that output is as expected.
	"""
	# testSuite2 = unittest.TestLoader().loadTestsFromTestCase(CoalComplexRun)
	# unittest.TextTestRunner().run(testSuite2)
	unittest.makeSuite(TestMap)
	unittest.makeSuite(TestCoalNorm)
	unittest.makeSuite(TestCoalInfLand)
	unittest.makeSuite(TestCoalFatInf)
	unittest.makeSuite(TestCoalTiledInfinite)
	unittest.makeSuite(TestCoalTiledInfinite2)
	unittest.makeSuite(TestCoalAnalyse)
	unittest.makeSuite(TestCoalTif)
	unittest.makeSuite(TestCoalTifCoarse)
	unittest.makeSuite(TestCoalConfigReadWrite)
	unittest.makeSuite(TestCoalComplexRun)
	unittest.makeSuite(TestCoalComplexRun2)
	unittest.makeSuite(TestCoalSampleRun)
	unittest.makeSuite(TestCoalPause)
	unittest.makeSuite(TestCoalPause2)
	unittest.makeSuite(TestCoalPause3)
	unittest.makeSuite(TestCoalPause4)
	unittest.makeSuite(TestCoalSimple)
	unittest.makeSuite(TestCoalFuncCheck)
	unittest.makeSuite(TestNormalMatchesFatTailedExtreme)
	unittest.makeSuite(TestSimulationAnalysis)
	unittest.makeSuite(TestFattailVersionsMatch)
	unittest.makeSuite(TestFileCreation)
	unittest.makeSuite(TestFileNaming)
	unittest.makeSuite(TestExtremeSpeciation)
	unittest.makeSuite(TestParameterDescriptions)
	unittest.makeSuite(TestDispersalSimulation)
	unittest.makeSuite(TestCoalDispersalMaps)
	unittest.makeSuite(TestMapDensityReading)
	unittest.makeSuite(TestDetectRamUsage)

class TestNullSimulationErrors(unittest.TestCase):
	"""
	Tests that simulations that are not linked raise the correct error.
	"""
	def testRaisesError(self):
		"""
		Tests that a null simulation will raise an error when any operation is performed.
		"""
		t = CoalescenceTree()
		with self.assertRaises(RuntimeError):
			t.get_richness()
		with self.assertRaises(RuntimeError):
			t.calculate_fragment_richness()
		with self.assertRaises(RuntimeError):
			t.calculate_alpha_diversity()
		with self.assertRaises(RuntimeError):
			t.calculate_beta_diversity()
		with self.assertRaises(RuntimeError):
			t.calculate_fragment_abundances()
		with self.assertRaises(RuntimeError):
			t.calculate_fragment_octaves()
		with self.assertRaises(RuntimeError):
			t.calculate_octaves()
		with self.assertRaises(RuntimeError):
			t.get_fragment_list()
		with self.assertRaises(RuntimeError):
			t.get_alpha_diversity()
		with self.assertRaises(RuntimeError):
			t.get_beta_diversity()
		with self.assertRaises(RuntimeError):
			t.get_community_references()
		with self.assertRaises(RuntimeError):
			t.get_metacommunity_references()
		with self.assertRaises(RuntimeError):
			t.get_species_locations()
		with self.assertRaises(RuntimeError):
			t.get_species_abundances()
		with self.assertRaises(RuntimeError):
			t.get_species_list()
		with self.assertRaises(RuntimeError):
			s = t.get_simulation_parameters()
		with self.assertRaises(RuntimeError):
			t.get_fragment_abundances("null", 1)
		with self.assertRaises(RuntimeError):
			t.get_landscape_richness()
		with self.assertRaises(RuntimeError):
			t.get_octaves(1)

class TestParameterDescriptions(unittest.TestCase):
	"""
	Tests that program correctly reads from the parameter_descriptions.json dictionary.
	"""

	def testReadsCorrectly(self):
		"""
		Tests that the dictionary is read correctly.
		"""
		tmp_dict = {"habitat_change_rate": "the rate of change from present density maps to historic density maps",
					"sample_file": "the sample area map for spatially selective sampling. Can be null to sample all cells",
					"sample_x": "the sample map x dimension",
					"sample_y": "the sample map y dimension",
					"sample_x_offset": "the sample x map offset from the grid",
					"sample_y_offset": "the sample y map offset from the grid",
					"output_dir": "the output directory for the simulation database",
					"seed": "the random seed to start the simulation, for repeatability",
					"coarse_map_x": "the coarse density map x dimension",
					"fine_map_file": "the density map file location at the finer resolution, covering a smaller area",
					"tau": "the tau dispersal value for fat-tailed dispersal",
					"grid_y": "the simulated grid y dimension",
					"dispersal_relative_cost": "the relative rate of moving through non-habitat compared to habitat",
					"fine_map_y_offset": "the number of cells the fine map is offset from the sample map in the y dimension, at the fine resolution",
					"gen_since_pristine": "the number of generations that occur before the pristine, or historic, state is reached",
					"dispersal_method": "the dispersal method used. Can be one of 'normal', 'norm-uniform' or 'fat-tail'.",
					"pristine_fine_map": "the pristine, or historic, coarse density map file location",
					"coarse_map_scale": "the scale of the coarse density map compared to the fine density map. 1 means equal density",
					"grid_x": "the simulated grid x dimension",
					"coarse_map_file": "the density map file location at the coarser resolution, covering a larger area",
					"min_num_species": "the minimum number of species known to exist (currently has no effect)",
					"pristine_coarse_map": "the pristine, or historic, coarse density map file location",
					"m_probability": "the probability of choosing from the uniform dispersal kernel in normal-uniform dispersal",
					"sigma": "the sigma dispersal value for normal, fat-tailed and normal-uniform dispersals",
					"deme": "the number of individuals inhabiting a cell at a map density of 1",
					"time_config_file": "the time config file containing points to sample in time, given in generations",
					"coarse_map_y": "the coarse density map y dimension",
					"fine_map_x": "the fine density map x dimension",
					"coarse_map_y_offset": "the number of cells the coarse map is offset from the fine map in the y dimension, at the fine resolution",
					"cutoff": "the maximal dispersal distance possible, for normal-uniform dispersal",
					"fine_map_y": "the fine density map y dimension",
					"sample_size": "the proportion of individuals to sample from each cell (0-1)",
					"fine_map_x_offset": "the number of cells the fine map is offset from the sample map in the x dimension, at the fine resolution",
					"speciation_rate": "the minimum speciation rate the simulation was run with",
					"job_type": "the job reference number given to this simulation",
					"coarse_map_x_offset": "the number of cells the coarse map is offset from the fine map in the x dimension, at the fine resolution",
					"infinite_landscape": "if false, landscapes have hard boundaries. Otherwise, can be infinite, with 1s everywhere, or tiled_coarse or tiled_fine for repeated units of tiled maps",
					"max_time": "the maximum simulation time to run for (in seconds)",
					"sim_complete": "set to true upon simulation completion, false for incomplete simulations",
					"protracted": "if true, the simulation was run with protracted speciation.",
					"min_speciation_gen": "the minimum number of generations required before speciation can occur",
					"max_speciation_gen": "the maximum number of generations a lineage can exist before it is speciated",
					"dispersal_map": "a tif file where rows represent cumulative dispersal probability to every other cell, using the row number = x + (y * x_max)"
					}
		t = CoalescenceTree("sample/sample.db")
		sim_output = t.get_simulation_parameters()
		for key in sim_output.keys():
			self.assertIn(key, get_parameter_description().keys())
		for key in get_parameter_description().keys():
			self.assertIn(key, sim_output.keys())
		for key in tmp_dict.keys():
			self.assertEqual(tmp_dict[key], get_parameter_description(key))
		self.assertDictEqual(tmp_dict, get_parameter_description())


class TestMap(unittest.TestCase):
	"""
	Tests the functions for the Map object work properly.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Map object
		"""
		self.fine_map = Map()
		self.fine_map.file_name = "sample/SA_sample_fine.tif"
		self.coarse_map = Map()
		self.coarse_map.file_name = "sample/SA_sample_coarse.tif"

	def testDetectGeoTransform(self):
		"""
		Tests the fine and coarse map geo transforms
		"""
		# Test the fine map
		x, y, ulx, uly, xres, yres = self.fine_map.get_dimensions()
		self.assertEqual(x, 13)
		self.assertEqual(y, 13)
		self.assertAlmostEqual(ulx, -78.375, 8)
		self.assertAlmostEqual(uly, 0.8583333333333, 8)
		self.assertAlmostEqual(xres, 0.00833333333333, 8)
		self.assertAlmostEqual(yres, -0.0083333333333333, 8)
		# Now test the coarse map
		x, y, ulx, uly, xres, yres = self.coarse_map.get_dimensions()
		self.assertEqual(x, 35)
		self.assertEqual(y, 41)
		self.assertAlmostEqual(ulx, -78.466666666, 8)
		self.assertAlmostEqual(uly, 0.975, 8)
		self.assertAlmostEqual(xres, 0.00833333333333, 8)
		self.assertAlmostEqual(yres, -0.0083333333333333, 8)

	def testGetXY(self):
		"""
		Tests the get_x_y() functionality
		"""
		x, y = self.fine_map.get_x_y()
		self.assertEqual(x, 13)
		self.assertEqual(y, 13)
		x, y = self.coarse_map.get_x_y()
		self.assertEqual(x, 35)
		self.assertEqual(y, 41)

	def testSetDimensions(self):
		"""
		Tests set_dimensions method
		"""
		tmp = Map()
		tmp.set_dimensions("sample/SA_sample_fine.tif")
		x, y, ulx, uly, xres, yres = [tmp.x_size, tmp.y_size, tmp.x_offset, tmp.y_offset, tmp.x_res, tmp.y_res]
		self.assertEqual(x, 13)
		self.assertEqual(y, 13)
		self.assertAlmostEqual(ulx, -78.375, 8)
		self.assertAlmostEqual(uly, 0.8583333333333, 8)
		self.assertAlmostEqual(xres, 0.00833333333333, 8)
		self.assertAlmostEqual(yres, -0.0083333333333333, 8)

	def testFail(self):
		"""
		Tests the correct exceptions are thrown when stupid things are attempted!
		"""
		map_fail = Map()
		map_fail.file_name = "sample/not_here.tif"

		with self.assertRaises(IOError):
			map_fail.get_dimensions()
		map_fail.file_name = "sample/SA_sample_fine"
		with self.assertRaises(IOError):
			map_fail.get_dimensions()
		map_fail.file_name = None
		with self.assertRaises(RuntimeError):
			map_fail.set_dimensions()
		with self.assertRaises(RuntimeError):
			map_fail.check_map()

	def testOffset(self):
		"""
		Tests that the offsets are correctly calculated between the fine and coarse maps
		"""
		self.assertListEqual(self.coarse_map.calculate_offset(self.fine_map), [-11, -14])
		self.assertListEqual(self.coarse_map.calculate_offset(self.coarse_map), [0, 0])
		self.assertListEqual(self.fine_map.calculate_offset(self.coarse_map), [11, 14])

class MapAssignment(unittest.TestCase):
	"""
	Asserts that the Map class correctly reads and writes data properly.
	"""
	@classmethod
	def setUpClass(cls):
		shutil.copy("sample/null.tif", "output/")
		cls.map = Map(file="output/null.tif")
		cls.map.open()
		cls.map.data[0:5, 0:2] = 10
		cls.map.write()

	def testBaseMap(self):
		"""
		Just a double check to make sure that the base map file is correct (not really a test of this code at all).
		"""
		ds = gdal.Open("sample/null.tif")
		arr = ds.GetRasterBand(1).ReadAsArray()
		self.assertEqual(np.sum(arr), 169)
		ds = None

	def testMapUpdates(self):
		ds = gdal.Open("output/null.tif")
		arr = ds.GetRasterBand(1).ReadAsArray()
		self.assertEqual(np.sum(arr), 259)
		ds = None


class TestFileCreation(unittest.TestCase):
	"""
	Tests the main coalescence set up routine by running some tiny simulations and checking that simulation parameters
	are passed properly. This function requires there to be a NECSim executable in build/nv/norm and compiled
	with the correct defines. make_all_compile() should automatically generate these executables.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(0, 0, "output/test_output/test_output2/", 0.1, 4, 4, deme=1, sample_size=1.0,
										max_time=2,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_pristine=2, time_config_file="null", dispersal_method="normal")
		self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()

	def testFileCreation(self):
		"""
		Checks that outputting is to the correct place and folder structure is created properly.
		:return:
		"""
		self.assertTrue(os.path.isfile(self.coal.output_database))
		self.assertEqual(os.path.join(self.coal.output_database),
						 os.path.join(self.coal.output_directory, "SQL_data",
									  str("data_" + str(self.coal.seed) + "_" + str(self.coal.job_type) + ".db")))


class TestFileNaming(unittest.TestCase):
	"""
	Tests that the file naming structure makes sense
	"""

	def testNoneNamingFine(self):
		"""
		Tests that the fine map file naming throws the correct error when called 'none'.
		:return:
		"""
		coal = Simulation()
		coal.set_simulation_params(0, 0, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
								   dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
								   gen_since_pristine=2, time_config_file="null", dispersal_method="normal")
		self.coal.set_map_parameters("null", 10, 10, "none", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "none", "none")

		with warnings.catch_warning(record=True) as w:
			warnings.simplefilter("always")
			self.coal.finalise_setup()
			self.assertEqual(str(w[0].message), "Fine map file cannot be 'none', changing to 'null'.")

	def testNoneNamingFine(self):
		"""
		Tests that the fine map file naming throws the correct error when called 'none'.
		:return:
		"""
		coal = Simulation()
		coal.set_simulation_params(0, 0, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
								   dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
								   gen_since_pristine=2, time_config_file="null", dispersal_method="normal")
		self.coal.set_map_parameters("none", 10, 10, "null", 10, 10, 0, 0, "none", 20, 20, 0, 0, 1, "null", "null")
		with warnings.catch_warning(record=True) as w:
			warnings.simplefilter("always")
			self.coal.finalise_setup()
			self.assertEqual(len(w), 2)
			self.assertEqual(str(w[0].message),
							 "Pristine fine file is 'none' but pristine coarse file is not none. Check file names.")
			self.assertEqual(str(w[1].message), "Defaulting to pristine_coarse_map_file = 'none'")

	def testNoneNamingFine(self):
		"""
		Tests that the fine map file naming throws the correct error when called 'none'.
		:return:
		"""
		coal = Simulation()
		coal.set_simulation_params(0, 0, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
								   dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
								   gen_since_pristine=2, time_config_file="null", dispersal_method="normal")
		self.coal.set_map_parameters("none", 10, 10, "null", 10, 10, 0, 0, "none", 20, 20, 0, 0, 1, "none", "null")
		with warnings.catch_warning(record=True) as w:
			warnings.simplefilter("always")
			self.coal.finalise_setup()
			self.assertEqual(len(w), 2)
			self.assertEqual(str(w[0].message),
							 "Coarse file is 'none' but pristine coarse file is not none. Check file names.")
			self.assertEqual(str(w[1].message), "Defaulting to pristine_coarse_map_file = 'none'")

	def testNoneNamingFine(self):
		"""
		Tests that the fine map file naming throws the correct error when called 'none'.
		:return:
		"""
		coal = Simulation()
		coal.set_simulation_params(0, 0, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
								   dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
								   gen_since_pristine=2, time_config_file="null", dispersal_method="normal")
		with self.assertRaises(ValueError):
			coal.set_map_files(sample_file="null", fine_file="null")


class TestCoalNorm(unittest.TestCase):
	"""
	Tests the main coalescence set up routine by running some tiny simulations and checking that simulation parameters
	are passed properly. This function requires there to be a NECSim executable in build/nv/norm and compiled
	with the correct defines. make_all_compile() should automatically generate these executables.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(0, 0, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_pristine=2, time_config_file="null", dispersal_method="normal")
		self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database("output/SQL_data/data_0_0.db")
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		:return:
		"""
		pass  # rmtree("output",True)

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=0, job_type=0, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=1.0, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=2.0,
									 time_config_file='null', coarse_map_file='null',
									 coarse_map_x=20, coarse_map_y=20, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='null', fine_map_x=10,
									 fine_map_y=10, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=10, grid_y=10, sample_x=10, sample_y=10,
									 sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='null', pristine_fine_map='null',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key])
		# self.assertDictEqual(params, actual_sim_parameters)
		self.assertEqual(self.tree.get_job()[0], 0)
		self.assertEqual(self.tree.get_job()[1], 0)

	def testRichness(self):
		"""
		Tests that the richness stored in the SQL file is correct.
		Note that this is actually a test of both the c++ (NECSim) and the python front-end.
		"""
		self.assertEqual(self.tree.get_richness(1), 40)
		self.assertEqual(self.tree.get_richness(2), 55)

	def testRichnessLandscape(self):
		"""
		Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
		"""
		richness_01 = self.tree.get_landscape_richness(1)
		richness_02 = self.tree.get_landscape_richness(2)
		self.assertEqual(richness_01, 40)
		self.assertEqual(richness_02, 55)


class TestCoalInfLand(unittest.TestCase):
	"""
	Performs a simulation on an infinite landscape with a normal dispersal kernel and checks outputs.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(2, 2, "output", 0.1, 4, 4, 1, 1.0, 2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=2,
										time_config_file="null", dispersal_method="normal", m_prob=1,
										infinite_landscape=True)
		self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database("output/SQL_data/data_2_2.db")
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=2, job_type=2, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=1.0, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=2.0,
									 time_config_file='null', coarse_map_file='null',
									 coarse_map_x=20, coarse_map_y=20, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='null', fine_map_x=10,
									 fine_map_y=10, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=10, grid_y=10, sample_x=10, sample_y=10,
									 sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='null', pristine_fine_map='null',
									 sim_complete=1, dispersal_method='normal', m_probability=1.0, cutoff=0.0,
									 infinite_landscape='infinite', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
		self.assertEqual(self.tree.get_job()[0], 2)
		self.assertEqual(self.tree.get_job()[1], 2)

	def testRichness(self):
		"""
		Tests that the richness stored in the SQL file is correct.
		Note that this is actually a test of both the c++ (NECSim) and the python front-end.
		"""
		self.assertEqual(self.tree.get_richness(1), 64)
		self.assertEqual(self.tree.get_richness(2), 73)

	def testRichnessLandscape(self):
		"""
		Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
		"""
		richness_01 = self.tree.get_landscape_richness(1)
		richness_02 = self.tree.get_landscape_richness(2)
		self.assertEqual(richness_01, 64)
		self.assertEqual(richness_02, 73)


class TestCoalFatInf(unittest.TestCase):
	"""
	Performs a basic simulation on an infinite landscape with a fat-tailed dispersal to checks outputs.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(1, 1, "output", 0.1, 4, 4, 1, 1.0, 2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=2.0,
										time_config_file="null", dispersal_method="fat-tail", infinite_landscape=True)
		self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "none", "none")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database("output/SQL_data/data_1_1.db")
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=1, job_type=1, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=1.0, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=2.0,
									 time_config_file='null', coarse_map_file='null',
									 coarse_map_x=20, coarse_map_y=20, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='null', fine_map_x=10,
									 fine_map_y=10, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=10, grid_y=10, sample_x=10, sample_y=10, sample_x_offset=0,
									 sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='fat-tail', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='infinite', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key])
		self.assertEqual(self.tree.get_job()[0], 1)
		self.assertEqual(self.tree.get_job()[1], 1)

	def testRichness(self):
		"""
		Tests that the richness stored in the SQL file is correct.
		Note that this is actually a test of both the c++ (NECSim) and the python front-end.
		"""
		self.assertEqual(self.tree.get_richness(1), 80)
		self.assertEqual(self.tree.get_richness(2), 87)

	def testRichnessLandscape(self):
		"""
		Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
		"""
		richness_01 = self.tree.get_landscape_richness(1)
		richness_02 = self.tree.get_landscape_richness(2)
		self.assertEqual(richness_01, 80)
		self.assertEqual(richness_02, 87)


class TestCoalTif(unittest.TestCase):
	"""
	Tests the tif file reading ability and correct fine map parameter detection.
	This requires the file SA_sample_fine.tif in sample/
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(3, 3, "output", 0.1, 4, 4, 1, 0.1, 2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", cutoff=0.0)
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif")
		self.coal.detect_map_dimensions()
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=3, job_type=3, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=0.1, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='none',
									 coarse_map_x=13, coarse_map_y=13, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
		self.assertEqual(self.tree.get_job()[0], 3)
		self.assertEqual(self.tree.get_job()[1], 3)

	def testRichness(self):
		"""
		Tests that the richness stored in the SQL file is correct.
		Note that this is actually a test of both the c++ (NECSim) and the python front-end.
		"""
		self.assertEqual(self.tree.get_richness(1), 2667)
		self.assertEqual(self.tree.get_richness(2), 3145)

	def testRichnessLandscape(self):
		"""
		Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
		"""
		richness_01 = self.tree.get_landscape_richness(1)
		richness_02 = self.tree.get_landscape_richness(2)
		self.assertEqual(richness_01, 2667)
		self.assertEqual(richness_02, 3145)


class TestCoalTiledInfinite(unittest.TestCase):
	"""
	Tests that simulations run as expected on a tiled infinite fine map.
	This requires the file SA_sample_fine.tif in sample/
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(1, 29, "output", 0.1, 4, 4, 1, 0.1, 2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", cutoff=0.0, infinite_landscape="tiled_fine")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif")
		self.coal.detect_map_dimensions()
		# self.coal.set_map_parameters("null", 10, 10, "sample/PALSAR_CONGO_SAMPLE.tif", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1,"null", "null")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=1, job_type=29, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=0.1, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='none',
									 coarse_map_x=13, coarse_map_y=13, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='tiled_fine', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
		self.assertEqual(self.tree.get_job()[0], 1)
		self.assertEqual(self.tree.get_job()[1], 29)

	def testRichness(self):
		"""
		Tests that the richness stored in the SQL file is correct.
		Note that this is actually a test of both the c++ (NECSim) and the python front-end.
		"""
		self.assertEqual(self.tree.get_richness(1), 3367)
		self.assertEqual(self.tree.get_richness(2), 3479)

	def testRichnessLandscape(self):
		"""
		Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
		"""
		richness_01 = self.tree.get_landscape_richness(1)
		richness_02 = self.tree.get_landscape_richness(2)
		self.assertEqual(richness_01, 3367)
		self.assertEqual(richness_02, 3479)


class TestCoalTiledInfinite2(unittest.TestCase):
	"""
	Tests that simulations run as expected on a tiled infinite coarse map.
	This requires the files SA_sample_fine.tif and SA_sample_coarse.tif in sample/
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.tree2 = CoalescenceTree()
		self.coal.set_simulation_params(1, 30, "output", 0.1, 4, 4, 1, 0.1, 2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", cutoff=0.0, infinite_landscape="tiled_coarse")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal2 = Simulation()
		self.coal2.set_simulation_params(seed=1, job_type=33, output_directory="output", min_speciation_rate=0.1,
										 sigma=4, tau=4, deme=1, sample_size=0.1, max_time=2, dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", cutoff=0.0, infinite_landscape="closed")
		self.coal2.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal2.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.calculate_octaves()
		self.tree.calculate_richness()
		self.tree2.set_database(self.coal2)
		self.tree2.calculate_octaves()
		self.tree2.calculate_richness()

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=1, job_type=30, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=0.1, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='tiled_coarse', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
		self.assertEqual(self.tree.get_job()[0], 1)
		self.assertEqual(self.tree.get_job()[1], 30)

	def testRichnessGreater(self):
		"""
		Tests that the richness produced by the tiled map is greater than that produced by the closed map.
		"""
		self.assertGreater(self.tree.get_richness(1),
						   self.tree2.get_richness(1))

	def testRichness(self):
		"""
		Tests that the richness stored in the SQL file is correct.
		Note that this is actually a test of both the c++ (NECSim) and the python front-end.
		"""
		self.assertEqual(self.tree.get_richness(1), 3468)
		self.assertEqual(self.tree.get_richness(2), 3601)

	def testRichnessLandscape(self):
		"""
		Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
		"""
		richness_01 = self.tree.get_landscape_richness(1)
		richness_02 = self.tree.get_landscape_richness(2)
		self.assertEqual(richness_01, 3468)
		self.assertEqual(richness_02, 3601)


class TestCoalProbabilityActionMap(unittest.TestCase):
	"""
	Tests that a birth/death map can be properly applied across a map. This is incorporated when choosing a lineage
	using rejection sampling.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=logging.CRITICAL)
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(seed=1, job_type=34, output_directory="output", min_speciation_rate=0.1,
										sigma=4, tau=4, deme=1, sample_size=0.1, max_time=2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", cutoff=0.0, infinite_landscape="closed")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								reproduction_map="sample/SA_sample_reproduction.tif")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2 = Simulation()
		self.tree2 = CoalescenceTree()
		self.coal2.set_simulation_params(seed=1, job_type=35, output_directory="output", min_speciation_rate=0.1,
										 sigma=4, tau=4, deme=1, sample_size=0.1, max_time=2, dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", cutoff=0.0, infinite_landscape="closed")
		self.coal2.set_map_files("null", fine_file="sample/SA_sample_fine.tif")
		self.coal2.set_speciation_rates([0.1, 0.2])
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree2.set_database(self.coal2)

	def testRichnessDifferent(self):
		"""
		Tests that the richness produced by a probability map is not the same as the richness produced without.
		"""
		self.assertNotEqual(self.coal.get_richness(1), self.coal2.get_richness(1))
		self.assertEqual(self.coal.get_richness(1), 2605)

	def testReproductionMapNullRaisesError(self):
		"""
		Tests that an error is raised when the reproduction map has a zero value where the density map does not.
		"""
		c = Simulation(logging_level=logging.CRITICAL)
		c.set_simulation_params(seed=2, job_type=34, output_directory="output", min_speciation_rate=0.1,
								sigma=4, tau=4, deme=1, sample_size=0.1, max_time=2, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null", cutoff=0.0, infinite_landscape="closed")
		c.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
						reproduction_map="sample/SA_sample_reproduction_invalid.tif")
		c.finalise_setup()
		with self.assertRaises(NECSimError):
			c.run_coalescence()
			# pass


class TestTifBytes(unittest.TestCase):
	"""
	Tests the tif file reading ability and correct fine map parameter detection for byte-encoded tif files, without
	geospatial data.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=logging.CRITICAL)
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(3, 4, "output", 0.1, 4, 4, 1, 1, 2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", cutoff=0.0)
		self.coal.set_map_files("null", fine_file="sample/bytesample.tif")
		self.coal.detect_map_dimensions()
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()

	def testByteTifDimensions(self):
		"""
		Tests that the program correctly reads dimensions from a byte-encoded tif file without geo-spatial data.
		"""
		self.assertEqual(self.coal.fine_map.x_offset, 0)
		self.assertEqual(self.coal.fine_map.y_offset, 0)
		self.assertEqual(self.coal.fine_map.x_size, 24)
		self.assertEqual(self.coal.fine_map.y_size, 24)
		self.assertEqual(self.coal.fine_map.x_res, 1.0)
		self.assertEqual(self.coal.fine_map.y_res, 1.0)

	def testSimOuptputDimensions(self):
		"""
		Tests that the simulation correctly completes with a byte-encoded tif file and the dimensions were read correctly
		by NECSim
		"""
		self.tree.set_database(self.coal)
		sim_params = self.tree.get_simulation_parameters()
		self.assertEqual(sim_params["fine_map_x"], 24)
		self.assertEqual(sim_params["fine_map_y"], 24)
		self.assertEqual(sim_params["fine_map_x_offset"], 0)
		self.assertEqual(sim_params["fine_map_y_offset"], 0)
		self.assertEqual(sim_params["sim_complete"], 1)

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
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", cutoff=0.0)
		cls.coal2 = Simulation()
		cls.coal2.set_simulation_params(seed=1, job_type=38, output_directory="output", min_speciation_rate=0.1,
										sigma=4, max_time=2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", cutoff=0.0)


	def testRaisesErrorFineSampleOffset(self):
		"""
		Tests the correct error is raised when offsetting is incorrect
		"""
		with self.assertRaises(ValueError):
			self.coal1.set_map_files(sample_file="sample/SA_samplemaskINT.tif",
									 fine_file="sample/SA_sample_fine_offset.tif")

	def testRaisesErrorFineSampleOffset(self):
		"""
		Tests the correct error is raised when offsetting is incorrect
		"""
		with self.assertRaises(ValueError):
			self.coal2.set_map_files(sample_file="null",
									 fine_file="sample/SA_sample_fine_offset.tif",
									 coarse_file="sample/SA_sample_coarse.tif")


class TestCoalTifCoarse(unittest.TestCase):
	"""
	Tests the coarse tif reading and correct parameter detection.
	This requires the files SA_sample_fine.tif and SA_sample_coarse.tif in sample/
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(4, 4, "output", 0.1, 4, 4, 1, 0.01, 2, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", dispersal_method="fat-tail")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=4, job_type=4, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=0.01, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='fat-tail', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key],
							 msg="Error in {}: {}!={}".format(key, params[key], actual_sim_parameters[key]))
		self.assertEqual(self.tree.get_job()[0], 4, msg="Job number not stored correctly.")
		self.assertEqual(self.tree.get_job()[1], 4, msg="Job number not stored correctly.")

	def testRichness(self):
		"""
		Tests that the richness stored in the SQL file is correct.
		Note that this is actually a test of both the c++ (NECSim) and the python front-end.
		"""
		self.assertEqual(self.tree.get_richness(1), 283)
		self.assertEqual(self.tree.get_richness(2), 283)

	def testRichnessLandscape(self):
		"""
		Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
		"""
		richness_01 = self.tree.get_landscape_richness(1)
		richness_02 = self.tree.get_landscape_richness(2)
		self.assertEqual(richness_01, 283)
		self.assertEqual(richness_02, 283)


class TestSimsRaiseErrors(unittest.TestCase):
	"""
	Tests that protracted and normal simulations raise the NECSimError when NECSim throws an error
	"""

	def testNormalRaisesError(self):
		"""
		Tests a normal simulation raises an error when no files exist
		"""
		c = Simulation()
		c.set_simulation_params(5, 4, "output", 0.1, 4, 4, 1, 0.01, 2, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null", dispersal_method="fat-tail")
		c.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
						coarse_file="sample/SA_sample_coarse.tif")
		# Now change map name to something that doesn't exist

		c.fine_map.file_name = "not_here.tif"
		with self.assertRaises(IOError):
			c.finalise_setup()
		with self.assertRaises(NECSimError):
			c.run_coalescence()

	def testProtractedRaisesError(self):
		"""
		Tests a protracted simulation raises an error if there is a problem
		"""
		c = Simulation(logging_level=logging.ERROR)
		c.set_simulation_params(6, 4, "output", 0.1, 4, 4, 1, 0.01, 2, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null", dispersal_method="fat-tail", protracted=True)
		c.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
						coarse_file="sample/SA_sample_coarse.tif")
		# Now change map name to something that doesn't exist

		c.fine_map.file_name = "not_here.tif"
		with self.assertRaises(IOError):
			c.finalise_setup()
		with self.assertRaises(NECSimError):
			c.run_coalescence()


class TestCoalAnalyse(unittest.TestCase):
	"""
	Tests analysis is performed correctly
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""
		
		cls.test = CoalescenceTree("sample/sample.db")
		cls.test.clear_calculations()
		cls.test.import_comparison_data("sample/PlotBiodiversityMetrics.db")
		cls.test.calculate_comparison_octaves(True)
		cls.test.calculate_fragment_richness()
		cls.test.calculate_fragment_octaves()
		cls.test.calculate_octaves_error()
		cls.test.calculate_alpha_diversity()
		cls.test.calculate_beta_diversity()
		cls.test2 = CoalescenceTree()
		cls.test2.set_database("sample/sample_nofrag.db")

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		"""
		cls.test.clear_calculations()

	def testFragmentOctaves(self):
		num = self.test.cursor.execute(
			"SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'P09' AND octave == 0"
			" AND community_reference == 1").fetchall()[0][0]
		self.assertEqual(num, 7, msg="Fragment octaves not correctly calculated.")
		num = self.test.cursor.execute(
			"SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'P09' AND octave == 0 "
			" AND community_reference == 2").fetchall()[0][0]
		self.assertEqual(num, 7, msg="Fragment octaves not correctly calculated.")
		num = self.test.cursor.execute(
			"SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'cerrogalera' AND octave == 1 "
			" AND community_reference == 1").fetchall()[0][0]
		self.assertEqual(num, 3, msg="Fragment octaves not correctly calculated.")
		num = self.test.cursor.execute(
			"SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'whole' AND octave == 1 "
			" AND community_reference == 2").fetchall()[0][0]
		self.assertEqual(num, 221, msg="Fragment octaves not correctly calculated.")

	def testFragmentAbundances(self):
		"""
		Tests that fragment abundances are produced properly by the fragment detection functions.

		"""
		num = self.test.cursor.execute(
			"SELECT COUNT(fragment) FROM FRAGMENT_ABUNDANCES WHERE fragment == 'P09' "
			" AND community_reference == 1").fetchall()[0][0]
		self.assertEqual(num, 9, msg="Fragment abundances not correctly calculated.")
		num = self.test.cursor.execute(
			"SELECT COUNT(fragment) FROM FRAGMENT_ABUNDANCES WHERE fragment == 'P09' "
			" AND community_reference == 2").fetchall()[0][0]
		self.assertEqual(num, 9, msg="Fragment abundances not correctly calculated.")
		num = self.test.cursor.execute(
			"SELECT COUNT(fragment) FROM FRAGMENT_ABUNDANCES WHERE fragment == 'cerrogalera' "
			" AND community_reference == 1").fetchall()[0][0]
		self.assertEqual(num, 9, msg="Fragment abundances not correctly calculated.")

	def testSpeciesAbundances(self):
		"""
		Tests that the produced species abundances are correct by comparing species richness.
		"""
		num = self.test.cursor.execute(
			"SELECT COUNT(species_id) FROM SPECIES_ABUNDANCES WHERE community_reference == 2").fetchall()[0][0]
		self.assertEqual(num, 1029, msg="Species abundances not correctly calculated.")
		num = self.test.cursor.execute(
			"SELECT COUNT(species_id) FROM SPECIES_ABUNDANCES WHERE community_reference == 1").fetchall()[0][0]
		self.assertEqual(num, 884, msg="Species abundances not correctly calculated.")

	def testSpeciesLocations(self):
		"""
		Tests that species locations have been correctly assigned.
		"""
		num = self.test.cursor.execute("SELECT species_id FROM SPECIES_LOCATIONS WHERE x==1662 AND y==4359 "
									   " AND community_reference == 1").fetchall()
		self.assertEqual(len(set(num)), 2, msg="Species locations not correctly assigned")
		all_list = self.test.get_species_locations()
		select_list = self.test.get_species_locations(community_reference=1)
		self.assertListEqual([1, 1662, 4359, 1], all_list[0])
		self.assertListEqual([1, 1662, 4359], select_list[0])

	def testAlphaDiversity(self):
		"""
		Tests that alpha diversity is correctly calculated and fetched for each parameter reference
		"""
		self.assertEqual(9, self.test.get_alpha_diversity(1))
		self.assertEqual(10, self.test.get_alpha_diversity(2))

	def testBetaDiversity(self):
		"""
		Tests that beta diversity is correctly calculated and fetched for the reference
		"""
		self.assertAlmostEqual(98.111111111, self.test.get_beta_diversity(1), places=5)
		self.assertAlmostEqual(102.8, self.test.get_beta_diversity(2), places=5)

	def testRaisesErrorNoFragmentsAlpha(self):
		"""
		Tests that an error is raised when alpha diversity is calculated without any fragment abundance data
		"""
		with self.assertRaises(RuntimeError):
			self.test2.calculate_alpha_diversity()

	def testRaisesErrorNoFragmentsBeta(self):
		"""
		Tests that an error is raised when alpha diversity is calculated without any fragment abundance data
		"""
		with self.assertRaises(RuntimeError):
			self.test2.calculate_beta_diversity()

	def testRaisesErrorNoFragmentsRichness(self):
		"""
		Tests that an error is raised when fragment richness is calculated without any fragment abundance data
		"""
		with self.assertRaises(RuntimeError):
			self.test2.calculate_fragment_richness()

	def testRaisesErrorNoFragmentsOctaves(self):
		"""
		Tests that an error is raised when fragment richness is calculated without any fragment abundance data
		"""
		with self.assertRaises(RuntimeError):
			self.test2.calculate_fragment_octaves()

	def testModelFitting(self):
		"""
		Tests that the goodness-of-fit calculations are correctly performed.
		"""
		self.test.calculate_goodness_of_fit()
		self.assertAlmostEqual(self.test.get_goodness_of_fit(), 0.301, places=3)
		self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_octaves(), 0.066, places=3)
		self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_richness(), 0.924, places=3)


class TestCoalAnalyse2(unittest.TestCase):
	"""
	Tests analysis is performed correctly
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""

		cls.test = CoalescenceTree()
		cls.test.set_database("sample/sample.db")
		cls.test.import_comparison_data("sample/PlotBiodiversityMetricsNoAlpha.db")
		cls.test.calculate_comparison_octaves(True)
		cls.test.clear_calculations()
		cls.test.calculate_fragment_richness()
		cls.test.calculate_fragment_octaves()
		cls.test.calculate_octaves_error()
		cls.test.calculate_alpha_diversity()
		cls.test.calculate_beta_diversity()
		cls.test2 = CoalescenceTree()
		cls.test2.set_database("sample/sample_nofrag.db")

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		"""
		cls.test.clear_calculations()

	def testRaisesErrorMismatchParameters(self):
		"""
		Tests that an error is raised when there is a parameter mismatch
		"""
		with self.assertRaises(ValueError):
			self.test.calculate_goodness_of_fit()


class TestCoalConfigReadWrite(unittest.TestCase):
	"""
	Tests the reading and writing to a config text file.
	Independently tests the main config, map config and time config writing ability.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(1, 23, "output", 0.1, 4, 4, 1, 1.0, max_time=200, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", dispersal_method="fat-tail")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.add_sample_time(0.0)
		self.coal.add_sample_time(1.0)
		self.coal.create_temporal_sampling_config("output/tempconf1.txt")
		self.coal.create_map_config("output/mapconf1.txt")
		self.coal.create_config("output/conf1.txt")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		:return:
		"""
		os.remove("output/mapconf1.txt")

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
			self.assertEqual(lines[12].replace(" ", ""), "time_config=output/tempconf1.txt")

	def testMapConfigWrite(self):
		"""
		Tests the map config output to check output is correct.
		"""
		self.coal.add_pristine_map(fine_map="sample/SA_sample_fine_pristine1.tif",
								   coarse_map="sample/SA_sample_coarse_pristine1.tif",
								   time=1, rate=0.5)
		self.coal.add_pristine_map(fine_map="sample/SA_sample_fine_pristine2.tif",
								   coarse_map="sample/SA_sample_coarse_pristine2.tif",
								   time=4, rate=0.7)
		self.coal.create_map_config("output/mapconf2.txt")
		with open("output/mapconf2.txt", "r") as mapconf:
			lines = mapconf.readlines()
			lines = [x.strip() for x in lines]
			self.assertEqual(lines[0], "[sample_grid]")
			self.assertEqual(lines[1].replace(" ", ""), "path=null", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[7].replace(" ", ""), "[fine_map]",
							 msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[8].replace(" ", ""), "path=sample/SA_sample_fine.tif",
							 msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[9].replace(" ", ""), "x=13", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[10].replace(" ", ""), "y=13", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[11].replace(" ", ""), "x_off=0", msg="Config file doesn't produce expected output.")
			self.assertEqual(lines[12].replace(" ", ""), "y_off=0", msg="Config file doesn't produce expected output.")

	def testTimeConfigWrite(self):
		"""
		Tests the map config writing is correct.
		"""
		with open("output/tempconf1.txt", "r") as f:
			lines = f.readlines()
			lines = [x.strip().replace(" ", "") for x in lines]
			self.assertEqual(lines[0], "[main]", msg="Time config file doesn't produce expected output.")
			self.assertEqual(lines[1], "time0=0.0", msg="Time config file doesn't produce expected output.")
			self.assertEqual(lines[2], "time1=1.0", msg="Time config file doesn't produce expected output.")

class TestNonSpatialSimulation(unittest.TestCase):
	"""
	Performs all the sanity checks for non spatially-explicit simulations, including protracted sims.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Runs the simulations to be used in testing
		:return:
		"""
		cls.c = Simulation(logging_level=logging.ERROR)
		cls.c.set_simulation_params(seed=1, job_type=39, output_directory="output", min_speciation_rate=1, deme=100,
								spatial=False)
		cls.c.finalise_setup()
		cls.c.run_coalescence()
		cls.c2 = Simulation(logging_level=logging.ERROR)
		cls.c2.set_simulation_params(seed=1, job_type=40, output_directory="output", min_speciation_rate=0.5, deme=100,
								 spatial=False)
		cls.c2.finalise_setup()
		cls.c2.run_coalescence()
		cls.c3 = Simulation(logging_level=logging.ERROR)
		cls.c3.set_simulation_params(seed=1, job_type=41, output_directory="output", min_speciation_rate=0.5, deme=100,
									spatial=False, protracted=True, min_speciation_gen=0, max_speciation_gen=1)
		cls.c3.finalise_setup()
		cls.c3.run_coalescence()
		cls.c4 = Simulation(logging_level=logging.ERROR)
		cls.c4.set_simulation_params(seed=1, job_type=42, output_directory="output", min_speciation_rate=0.5, deme=100,
									 spatial=False, protracted=True, min_speciation_gen=100, max_speciation_gen=1000)
		cls.c4.finalise_setup()
		cls.c4.run_coalescence()

	def testNSESanityChecks(self):
		"""
		Runs the sanity checks for non-spatially explicit simulations
		"""
		self.assertEqual(self.c.get_richness(), 100)
		self.assertEqual(self.c2.get_richness(), 70)

	def testNSELocations(self):
		"""
		Tests that all locations for lineages is 0
		"""
		t = CoalescenceTree(self.c2)
		t.set_speciation_params(record_spatial=True, record_fragments=False, speciation_rates=[0.6, 0.7])
		t.apply_speciation()
		locations = t.get_species_locations()
		for row in locations:
			self.assertEqual(0, row[1])
			self.assertEqual(0, row[2])

	def testProtractedNSESanityChecks(self):
		"""
		Tests that protracted simulations work with NSE sims.
		"""
		self.assertGreater(self.c3.get_richness(1), self.c2.get_richness(1))
		self.assertLess(self.c4.get_richness(1), self.c3.get_richness(1))



class TestCoalSampleRun(unittest.TestCase):
	"""
	Test a simple run on a landscape using sampling.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""
		cls.coal = Simulation()
		cls.tree = CoalescenceTree()
		cls.coal.set_simulation_params(seed=6, job_type=8, output_directory="output", min_speciation_rate=0.5,
									   sigma=4, tau=4, deme=1, sample_size=0.1, max_time=2, dispersal_relative_cost=1,
									   min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
									   time_config_file="null", dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		cls.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							   coarse_file="sample/SA_sample_coarse.tif")
		cls.coal.set_speciation_rates([0.5, 0.7])
		cls.coal.finalise_setup()
		cls.coal.run_coalescence()
		cls.tree.set_database("output/SQL_data/data_8_6.db")
		cls.tree.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
									   sample_file="null", time_config_file=cls.coal.time_config_file)
		# self.tree.apply_speciation()
		cls.tree.calculate_octaves()
		cls.tree.calculate_richness()

	def testSampleRichness(self):
		"""
		Tests that the simulation using sampling returns the correct species richness.
		Also tests that both methods of obtaining species richness work.
		"""
		self.tree.calculate_richness()
		self.assertEqual(self.tree.get_landscape_richness(1), 1163)
		self.assertEqual(self.tree.get_landscape_richness(2), 1169)
		self.assertEqual(self.tree.get_landscape_richness(1), self.tree.get_richness(1))
		self.assertEqual(self.tree.get_landscape_richness(2), self.tree.get_richness(2))
		self.assertEqual(self.tree.get_landscape_richness(3), self.tree.get_richness(3))

class TestCoalSampleRun2(unittest.TestCase):
	"""
	Sample run with test cases to make sure the sample map relative sampling is taken into account.
	"""
	@classmethod
	def setUpClass(cls):
		cls.coal = Simulation(logging_level=logging.CRITICAL)
		cls.coal.set_simulation_params(seed=7, job_type=8, output_directory="output", min_speciation_rate=0.5,
									   sigma=4, deme=10, sample_size=1, max_time=2, uses_spatial_sampling=True)
		cls.coal.set_map_files(sample_file="sample/null_sample.tif", fine_file="sample/null.tif")
		cls.coal.set_speciation_rates([0.5, 0.6])
		cls.coal.finalise_setup()
		cls.coal.run_coalescence()
		cls.tree = CoalescenceTree(cls.coal)
		cls.tree.set_speciation_params(record_spatial=True, record_fragments="sample/FragmentsTest.csv",
									   speciation_rates=[0.5, 0.6])
		cls.tree.apply_speciation()
		# Copy the simulation file to a backup
		shutil.copy2(cls.coal.output_database, "output/temp.db")

	def testNumberIndividuals(self):
		"""
		Tests that the number of individuals simulated is correct.
		"""
		self.assertEqual(356, self.tree.get_number_individuals())
		self.assertEqual(53, self.tree.get_number_individuals(fragment="fragment1"))
		self.assertEqual(39, self.tree.get_number_individuals(fragment="fragment2"))

	def testIncorrectFragmentsRaisesError(self):
		"""
		Tests that having an incorrect fragments file raises an error as expected. Tests if either there are the wrong
		number of columns, or an failed conversion from string to integer/double.
		"""
		for f in [1, 2, 3]:
			fragment_file = "sample/FragmentsTestFail{}.csv".format(f)
			with self.assertRaises(ApplySpecError):
				t = CoalescenceTree("output/temp.db")
				t.wipe_data()
				t.set_speciation_params(record_spatial=False, record_fragments=fragment_file,
										speciation_rates=[0.5, 0.6])
				t.apply_speciation()

class TestNullLandscape(unittest.TestCase):
	"""
	Tests that a simple null landscape provides the expected species richness for speciation rate = 1 and the number of
	individuals simulated is correctly calculated.
	Also tests that the set_map() function works correctly.
	"""
	@classmethod
	def setUpClass(cls):
		"""
		Runs the neutral simulation and generates the coalescence tree.
		:return:
		"""
		cls.coal = Simulation()
		cls.coal.set_simulation_params(seed=8, job_type=8, output_directory="output", min_speciation_rate=0.5,
									   sigma=4, deme=10, sample_size=1, max_time=2)
		cls.coal.set_speciation_rates([0.5, 0.99])
		cls.coal.set_map(map_file="sample/null.tif")
		cls.coal.finalise_setup()
		cls.coal.run_coalescence()
		cls.tree = CoalescenceTree(cls.coal)
		cls.tree.set_speciation_params(record_spatial=False, record_fragments="sample/FragmentsTest.csv",
									   speciation_rates=[0.5, 0.95])
		cls.tree.apply_speciation()

	def testRichness(self):
		"""
		Tests that the richness produced by a landscape is sensible for the relevant speciation rates.
		"""
		self.assertEqual(self.tree.get_richness(1), 1204)
		self.assertEqual(self.tree.get_richness(2), 1684)


	def testNumberIndividuals(self):
		"""
		Tests that the number of individuals in each fragment is correct, and also the number of individuals in the
		whole landscape
		:return:
		"""
		self.assertEqual(1690, self.tree.get_number_individuals())
		self.assertEqual(120, self.tree.get_number_individuals(fragment="fragment1"))
		self.assertEqual(280, self.tree.get_number_individuals(fragment="fragment2"))


class TestCoalPause(unittest.TestCase):
	"""
	Test a simple run on a landscape using sampling
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.coal2 = Simulation()
		self.tree2 = CoalescenceTree()
		self.coal.set_simulation_params(seed=10, job_type=6, output_directory="output", min_speciation_rate=0.05,
										sigma=2, tau=2, deme=1, sample_size=0.1, max_time=0,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_pristine=200,
										time_config_file="null", dispersal_method="normal")
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=10, job_type=7, output_directory="output", min_speciation_rate=0.05,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal2.time_config_file)
		self.tree2.apply_speciation()
		self.tree1 = CoalescenceTree()

	def testCanPause(self):
		"""
		Tests that simulations can pause executation and correctly store their state to the SQL database (for in-process
		analysis). Checks that the SQL database has correctly written the simulation parameters and that errors are
		thrown when one tries to connect to an incomplete simulation.
		"""
		tree2 = CoalescenceTree()
		with self.assertRaises(IOError):
			tree2.set_database(self.coal)
		actual_sim_parameters = dict(seed=10, job_type=6, output_dir='output', speciation_rate=0.05, sigma=2.0, tau=2.0,
									 deme=1, sample_size=0.1, max_time=0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=0, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		params = tree2.get_simulation_parameters()
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))

	def testCanResume(self):
		"""
		Tests that simulations can resume execution.
		"""
		self.coal.resume_coalescence("output", 10, 6, 10)
		self.tree1.set_database(self.coal)
		actual_sim_parameters = dict(seed=10, job_type=6, output_dir='output', speciation_rate=0.05, sigma=2.0, tau=2.0,
									 deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		params = self.tree1.get_simulation_parameters()
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key])

	def testPauseSimMatchesSingleRunSim(self):
		"""
		Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
		identical results. Checks using comparison of the SPECIES_LIST tables
		"""
		self.tree1.set_database(self.coal)
		self.tree1.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal.time_config_file)
		self.tree1.apply_speciation()
		dict1 = self.tree1.get_simulation_parameters()
		dict2 = self.tree2.get_simulation_parameters()
		for key in dict1.keys():
			if key != "job_type" and key != "max_time":
				self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
		self.assertEqual(self.coal.get_richness(), self.coal2.get_richness())
		single_run_species_list = list(self.tree1.get_species_list())
		pause_sim_species_list = list(self.tree2.get_species_list())
		self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
		self.assertListEqual([x for x in pause_sim_species_list],
							 [x for x in single_run_species_list])


class TestCoalPause2(unittest.TestCase):
	"""
	Test a simple run on a landscape using sampling with pause/resume functionality with protractedness
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=logging.ERROR)
		self.coal2 = Simulation(logging_level=logging.ERROR)
		self.tree2 = CoalescenceTree(logging_level=logging.ERROR)
		self.coal.set_simulation_params(seed=10, job_type=26, output_directory="output", min_speciation_rate=0.5,
										sigma=2, tau=2, deme=1, sample_size=0.1, max_time=0,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_pristine=200,
										time_config_file="null", dispersal_method="normal", protracted=True,
										min_speciation_gen=0.0, max_speciation_gen=100)
		self.coal3 = Simulation(logging_level=logging.ERROR)
		self.coal3.set_simulation_params(seed=10, job_type=26, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										 gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal", protracted=True,
										 min_speciation_gen=0.0, max_speciation_gen=100)
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal3.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		# self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		try:
			self.coal3.finalise_setup()
		except FileExistsError:
			pass
		self.coal3.run_coalescence()
		self.coal2.set_simulation_params(seed=10, job_type=27, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal", protracted=True,
										 min_speciation_gen=0.0, max_speciation_gen=100)
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.set_speciation_rates([0.5])
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal2.time_config_file)
		self.tree2.apply_speciation()
		self.tree1 = CoalescenceTree()

	def testCanResume2(self):
		"""
		Tests that simulations can resume execution by detecting the paused files
		"""
		self.tree1.set_database(self.coal3)
		actual_sim_parameters = dict(seed=10, job_type=26, output_dir='output', speciation_rate=0.5, sigma=2.0, tau=2.0,
									 deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=1, min_speciation_gen=0.0,
									 max_speciation_gen=100.0, dispersal_map="none")
		params = self.tree1.get_simulation_parameters()
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key])

	def testRaisesErrorOnProtractedResume(self):
		"""
		Tests that an error is raise if the protracted simulation is attempted to be run from a non-protracted paused
		file, or visa versa.
		"""
		coaltmp = Simulation()
		coaltmp.set_simulation_params(seed=10, job_type=26, output_directory="output", min_speciation_rate=0.5,
									  sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
									  dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
									  gen_since_pristine=200,
									  time_config_file="null", dispersal_method="normal", protracted=False,
									  min_speciation_gen=0.0, max_speciation_gen=100)
		with self.assertRaises(NECSimError):
			coaltmp.resume_coalescence(job_type=26, seed=10, pause_directory="output", max_time=10,
									   out_directory="output")

	def testPauseSimMatchesSingleRunSim2(self):
		"""
		Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
		identical results. Checks using comparison of the SPECIES_LIST tables
		"""
		self.tree1.set_database(self.coal3)
		self.tree1.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal3.time_config_file)
		self.tree1.apply_speciation()
		self.assertEqual(self.coal3.get_richness(), self.coal2.get_richness())
		single_run_species_list = list(self.tree1.get_species_list())
		pause_sim_species_list = list(self.tree2.get_species_list())
		dict1 = self.tree1.get_simulation_parameters()
		dict2 = self.tree2.get_simulation_parameters()
		for key in dict1.keys():
			if key != "job_type":
				self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
		# print(pause_sim_species_list)
		# print(single_run_species_list)
		self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
		self.assertListEqual([x for x in pause_sim_species_list],
							 [x for x in single_run_species_list])


class TestCoalPause3(unittest.TestCase):
	"""
	Test a simple run on a landscape using sampling, moving the paused files between simulations.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.coal2 = Simulation()
		self.tree2 = CoalescenceTree()
		self.coal.set_simulation_params(seed=10, job_type=16, output_directory="output", min_speciation_rate=0.5,
										sigma=2, tau=2, deme=1, sample_size=0.1, max_time=0,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_pristine=200,
										time_config_file="null", dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		# self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=10, job_type=17, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.set_speciation_rates([0.5])
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal2.time_config_file)
		self.tree2.apply_speciation()
		self.tree1 = CoalescenceTree()

	@classmethod
	def tearDownClass(self):
		shutil.rmtree("output2", ignore_errors=True)
		shutil.rmtree("output3", ignore_errors=True)

	def testCanPause(self):
		"""
		Tests that simulations can pause executation and correctly store their state to the SQL database (for in-process
		analysis). Checks that the SQL database has correctly written the simulation parameters and that errors are
		thrown when one tries to connect to an incomplete simulation.
		"""
		tree2 = CoalescenceTree()
		with self.assertRaises(IOError):
			tree2.set_database(self.coal)
		actual_sim_parameters = dict(seed=10, job_type=16, output_dir='output', speciation_rate=0.5, sigma=2.0, tau=2.0,
									 deme=1, sample_size=0.1, max_time=0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=0, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		params = tree2.get_simulation_parameters()
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))

	def testCanResume(self):
		"""
		Tests that simulations can resume execution.
		"""
		paused_file_list = ["Dump_map_", "Dump_main_", "Dump_active_", "Dump_data_"]
		os.mkdir("output2")
		os.mkdir("output2/Pause")
		for file in paused_file_list:
			os.rename(os.path.join("output", "Pause", file + "16_10.csv"),
					  os.path.join("output2", "Pause", file + "16_10.csv"))
		if not os.path.exists("output3"):
			os.mkdir("output3")
		self.coal.resume_coalescence("output2", 10, 16, 10, out_directory="output3")
		self.tree1.set_database(self.coal)
		actual_sim_parameters = dict(seed=10, job_type=16, output_dir='output3', speciation_rate=0.5, sigma=2.0,
									 tau=2.0,
									 deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		params = self.tree1.get_simulation_parameters()
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key])

	def testPauseSimMatchesSingleRunSim(self):
		"""
		Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
		identical results. Checks using comparison of the SPECIES_LIST tables
		"""
		self.tree1.set_database(self.coal)
		self.tree1.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal.time_config_file)
		self.tree1.apply_speciation()
		self.assertEqual(self.coal.get_richness(), self.coal2.get_richness())
		dict1 = self.tree1.get_simulation_parameters()
		dict2 = self.tree2.get_simulation_parameters()
		for key in dict1.keys():
			if key != "job_type" and key != "max_time" and key != "output_dir":
				self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
		single_run_species_list = list(self.tree1.get_species_list())
		pause_sim_species_list = list(self.tree2.get_species_list())
		self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
		self.assertListEqual([x for x in pause_sim_species_list],
							 [x for x in single_run_species_list])


class TestCoalPause4(unittest.TestCase):
	"""
	Test a simple run on a landscape using sampling, moving the paused files between simulations.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=logging.CRITICAL)
		self.coal2 = Simulation(logging_level=logging.CRITICAL)
		self.tree2 = CoalescenceTree()
		self.coal.set_simulation_params(seed=11, job_type=16, output_directory="output spaced",
										min_speciation_rate=0.5,
										sigma=2, tau=2, deme=1, sample_size=0.1, max_time=0,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_pristine=200,
										time_config_file="null", dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT spaced.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		# self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=11, job_type=17, output_directory="output spaced",
										 min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT spaced.tif",
								 fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.set_speciation_rates([0.5])
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal2.time_config_file)
		self.tree2.apply_speciation()

		# self.tree2.calculate_octaves()
		# self.tree2.calculate_richness()
		self.tree3 = CoalescenceTree()
		self.coal3 = Simulation(logging_level=logging.CRITICAL)

	@classmethod
	def tearDownClass(self):
		shutil.rmtree("output2 spaced", ignore_errors=True)
		shutil.rmtree("output spaced", ignore_errors=True)

	def testCanPause(self):
		"""
		Tests that simulations can pause executation and correctly store their state to the SQL database (for in-process
		analysis). Checks that the SQL database has correctly written the simulation parameters and that errors are
		thrown when one tries to connect to an incomplete simulation.
		"""
		tree1 = CoalescenceTree()
		with self.assertRaises(IOError):
			tree1.set_database(self.coal)
		actual_sim_parameters = dict(seed=11, job_type=16, output_dir='output spaced', speciation_rate=0.5, sigma=2.0,
									 tau=2.0,
									 deme=1, sample_size=0.1, max_time=0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT spaced.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=0, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		params = tree1.get_simulation_parameters()
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))

	def testCanResume(self):
		"""
		Tests that simulations can resume execution.
		"""
		if not os.path.exists("output2 spaced"):
			os.mkdir("output2 spaced")
		self.coal3.resume_coalescence(pause_directory="output spaced", seed=11, job_type=16, max_time=10,
									  out_directory="output2 spaced")
		self.tree3.set_database(self.coal3)
		actual_sim_parameters = dict(seed=11, job_type=16, output_dir='output2 spaced', speciation_rate=0.5, sigma=2.0,
									 tau=2.0,
									 deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT spaced.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		params = self.tree3.get_simulation_parameters()
		for key in params.keys():
			self.assertEqual(params[key], actual_sim_parameters[key])

	def testPauseSimMatchesSingleRunSim(self):
		"""
		Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
		identical results. Checks using comparison of the SPECIES_LIST tables
		"""
		self.tree3.set_database(self.coal3)
		self.tree3.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal.time_config_file)
		self.tree3.apply_speciation()
		self.assertEqual(self.tree3.get_richness(), self.tree2.get_richness())
		dict1 = self.tree3.get_simulation_parameters()
		dict2 = self.tree2.get_simulation_parameters()
		for key in dict1.keys():
			if key != "job_type" and key != "max_time" and key != "output_dir":
				self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
		single_run_species_list = list(self.tree3.get_species_list())
		pause_sim_species_list = list(self.tree2.get_species_list())
		# print(pause_sim_species_list)
		# print(single_run_species_list)
		self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
		self.assertListEqual([x for x in pause_sim_species_list],
							 [x for x in single_run_species_list])


class TestCoalComplexRun(unittest.TestCase):
	"""
	Tests a complex run over multiple historic landscapes with multiple sampling points and using the full config file
	options. Uses a normal distribution and 10% sampling for quicker calculations.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree(logging_level=logging.CRITICAL)
		self.coal.set_simulation_params(seed=6, job_type=6, output_directory="output", min_speciation_rate=0.5,
										sigma=4, tau=4, deme=1, sample_size=0.1, max_time=10,
										dispersal_relative_cost=1.0,
										min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
										time_config_file="null", dispersal_method="normal", infinite_landscape=False)
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.add_sample_time(0.0)
		self.coal.add_sample_time(0.5)
		self.coal.set_speciation_rates([0.5])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										sample_file="null", time_config_file=self.coal.time_config_file)
		self.tree.apply_speciation()
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	def testRaisesErrorFragmentList(self):
		"""
		Tests that a RuntimeError is raised when trying to get the fragments list (as none exists).
		"""
		with self.assertRaises(RuntimeError):
			self.tree.get_fragment_list()

	def testComplexRichness(self):
		"""
		Tests that the complex simulation setup returns the correct species richness.
		"""
		self.assertEqual(self.tree.get_landscape_richness(1), 3644)
		self.assertEqual(self.tree.get_landscape_richness(3), 3674)
		self.assertEqual(self.tree.get_landscape_richness(5), 3697)
		self.assertEqual(self.tree.get_landscape_richness(10), 0)

	def testComplexRichness2(self):
		"""
		Tests that the later generation of species richness is correct
		"""
		self.assertEqual(self.tree.get_landscape_richness(2), 3643)
		self.assertEqual(self.tree.get_landscape_richness(4), 3675)
		self.assertEqual(self.tree.get_landscape_richness(6), 3695)
		self.assertEqual(self.tree.get_landscape_richness(11), 0)

	def testNumberIndividualsAddsUp(self):
		"""
		Tests that the number of individuals in each generation is the same
		"""
		number = sum([x[1] for x in self.tree.get_species_abundances(reference=3)])
		number2 = sum([x[1] for x in self.tree.get_species_abundances(reference=3)])
		self.assertEqual(number, 3734)
		self.assertEqual(number2, 3734)

	def testRichnessMethodsMatch(self):
		"""
		Tests that the richness produced by the two methods matches.
		"""
		self.assertEqual(self.tree.get_landscape_richness(reference=1), self.tree.get_richness(reference=1),
						 msg="Landscape richness is not as expected.")
		self.assertEqual(self.tree.get_landscape_richness(reference=3), self.tree.get_richness(reference=3),
						 msg="Landscape richness is not as expected.")
		self.assertEqual(self.tree.get_landscape_richness(reference=100), self.tree.get_richness(reference=100),
						 msg="Landscape richness is not as expected.")
		self.assertEqual(self.tree.get_landscape_richness(reference=101), self.tree.get_richness(reference=101),
						 msg="Landscape richness is not as expected.")

	def testComplexAbundances(self):
		"""
		Tests that species abundances are correct for a complex case.
		"""
		expected_abundances = [[0, 0],
							   [1, 1],
							   [2, 1],
							   [3, 1],
							   [4, 1],
							   [5, 1],
							   [6, 1],
							   [7, 1],
							   [8, 1],
							   [9, 1]]
		actual_abundances = self.tree.get_species_abundances(reference=1)
		for i, each in enumerate(expected_abundances):
			if i == 10:
				break
			self.assertEqual(actual_abundances[i], each)

	def testSimulationParametersStored(self):
		"""
		Tests that the simulation parameters have been stored correctly, and that the functions for getting specific
		parameters work properly.
		"""
		simulation_parameters = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=6, job_type=6, output_dir='output', speciation_rate=0.5, sigma=4.0, tau=4.0,
									 deme=1, sample_size=0.1, max_time=10.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
									 time_config_file='output/timeconf_6_6.txt',
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13, sample_x=13, sample_y=13, sample_x_offset=0,
									 sample_y_offset=0, pristine_coarse_map='none', pristine_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 infinite_landscape='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none")
		for key in simulation_parameters.keys():
			self.assertEqual(simulation_parameters[key], actual_sim_parameters[key])
		self.assertDictEqual(simulation_parameters, actual_sim_parameters)
		# self.assertListEqual(simulation_parameters, actual_sim_parameters)
		self.assertEqual(self.tree.get_job()[0], 6)
		self.assertEqual(self.tree.get_job()[1], 6)

	def testCommunityParameters(self):
		"""
		Tests that the past calculations are correctly stored.
		"""
		references = self.tree.get_community_references()
		self.assertListEqual([1, 2, 3, 4, 5, 6], references)
		reference1_dict = {"speciation_rate": 0.5, "time": 0.0, "fragments": 0, "metacommunity_reference": 0}
		reference5_dict = {"speciation_rate": 0.7, "time": 0.5, "fragments": 0, "metacommunity_reference": 0}
		self.assertDictEqual(reference1_dict, self.tree.get_community_parameters(reference=1))
		self.assertDictEqual(reference5_dict, self.tree.get_community_parameters(reference=6))

	def testMetaCommunityParameters(self):
		"""
		Tests that no metacommunity has been stored - should return an empty list.
		"""
		with self.assertRaises(sqlite3.OperationalError):
			references = self.tree.get_metacommunity_parameters(reference=1)
		self.assertListEqual(self.tree.get_metacommunity_references(), [])


class TestCoalComplexRun2(unittest.TestCase):
	"""
	Tests a complex run over multiple historic landscapes with multiple sampling points and using partial config file
	options (config for temporal and map options, not for full simulation options).
	Uses a normal distribution and 10% sampling for quicker calculations.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(seed=6, job_type=7, output_directory="output", min_speciation_rate=0.5,
										sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", dispersal_method="normal")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.add_sample_time(0.0)
		self.coal.add_sample_time(1.0)
		self.coal.set_speciation_rates([0.5])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database("output/SQL_data/data_7_6.db")
		self.tree.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										sample_file="null", time_config_file=self.coal.time_config_file)
		self.tree.apply_speciation()
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		:return:
		"""
		pass  # rmtree("output", True)

	def testComplexRichness(self):
		"""
		Tests that the complex simulation setup returns the correct species richness.
		"""
		self.assertEqual(self.tree.get_landscape_richness(1), 3593)
		self.assertEqual(self.tree.get_landscape_richness(3), 3632)
		self.assertEqual(self.tree.get_landscape_richness(5), 3665)

	def testComplexRichness2(self):
		"""
		Tests that the compelx simulation setup returns the correct species richness at other time samples
		"""
		self.assertEqual(self.tree.get_landscape_richness(2), 3601)
		self.assertEqual(self.tree.get_landscape_richness(4), 3640)
		self.assertEqual(self.tree.get_landscape_richness(6), 3666)

	def testZeroRichness(self):
		"""
		Tests that zero richness is produced where expected
		:return:
		"""
		self.assertEqual(self.tree.get_landscape_richness(100), 0)
		self.assertEqual(self.tree.get_landscape_richness(1), self.tree.get_richness(1))
		self.assertEqual(self.tree.get_landscape_richness(3), self.tree.get_richness(3))
		self.assertEqual(self.tree.get_landscape_richness(6), self.tree.get_richness(6))
		self.assertEqual(self.tree.get_landscape_richness(100), self.tree.get_richness(100))


class TestCoalComplexRun3(unittest.TestCase):
	"""
	Tests a complex run over multiple historic landscapes with multiple sampling points and using partial config file
	options (config for temporal and map options, not for full simulation options).
	Uses a normal distribution and 10% sampling for quicker calculations.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(seed=6, job_type=13, output_directory="output", min_speciation_rate=0.5,
										sigma=4, tau=4, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.add_sample_time(0.0)
		self.coal.add_sample_time(1.0)
		self.coal.set_speciation_rates([0.5])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.set_speciation_params(record_spatial=True, record_fragments=False, speciation_rates=[0.6, 0.7],
										sample_file="null", time_config_file=self.coal.time_config_file)
		self.tree.apply_speciation()
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		:return:
		"""
		pass  # rmtree("output", True)

	def testComplexRichness(self):
		"""
		Tests that the complex simulation setup returns the correct species richness.
		Also tests that both methods of obtaining species richness work.
		"""
		self.tree.calculate_richness()
		self.assertEqual(self.tree.get_landscape_richness(1), 3637)
		self.assertEqual(self.tree.get_landscape_richness(3), 3671)
		self.assertEqual(self.tree.get_landscape_richness(5), 3701)
		self.assertEqual(self.tree.get_landscape_richness(8), 0)
		self.assertEqual(self.tree.get_landscape_richness(1), self.tree.get_richness(1))
		self.assertEqual(self.tree.get_landscape_richness(3), self.tree.get_richness(3))
		self.assertEqual(self.tree.get_landscape_richness(4), self.tree.get_richness(4))
		self.assertEqual(self.tree.get_landscape_richness(7), self.tree.get_richness(7))


class TestCoalComplexRun4(unittest.TestCase):
	"""
	Tests a complex run over multiple historic landscapes with a normal-uniform dispersal kernel.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(seed=7, job_type=13, output_directory="output", min_speciation_rate=0.5,
										sigma=4, tau=4, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", dispersal_method="norm-uniform", m_prob=10 ** -8,
										cutoff=160)
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.add_sample_time(0.0)
		self.coal.set_speciation_rates([0.5])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.set_speciation_params(record_spatial=True, record_fragments=False, speciation_rates=[0.6, 0.7],
										sample_file="null", time_config_file=self.coal.time_config_file)
		self.tree.apply_speciation()
		self.tree.calculate_octaves()
		self.tree.calculate_richness()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		:return:
		"""
		pass  # rmtree("output", True)

	def testComplexRichness(self):
		"""
		Tests that the complex simulation setup returns the correct species richness.
		Also tests that both methods of obtaining species richness work.
		"""
		self.tree.calculate_richness()
		self.assertEqual(3638, self.tree.get_landscape_richness(1))
		self.assertEqual(3665, self.tree.get_landscape_richness(2))
		self.assertEqual(3691, self.tree.get_landscape_richness(3))
		self.assertEqual(0, self.tree.get_landscape_richness(7))
		self.assertEqual(self.tree.get_landscape_richness(1), self.tree.get_richness(1))
		self.assertEqual(self.tree.get_landscape_richness(3), self.tree.get_richness(3))
		self.assertEqual(self.tree.get_landscape_richness(5), self.tree.get_richness(5))
		self.assertEqual(self.tree.get_landscape_richness(7), self.tree.get_richness(7))

	def testSimParametersCorrectlyStored(self):
		"""
		Tests that the simulation parameters for the normal uniform distribution are correctly stored.
		"""
		sim_pars = self.tree.get_simulation_parameters()
		self.assertEqual(10 ** -8, sim_pars["m_probability"])
		self.assertEqual(160, sim_pars["cutoff"])


class TestCoalSimple(unittest.TestCase):
	"""
	Tests the run_simple() which simply runs on a landscape with very low dispersal parameters at a tiny size.
	Checks that the pycoalescence can set up a simple simulation run correctly.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""
		cls.coal = Simulation()
		cls.tree = CoalescenceTree()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the files from output."
		:return:
		"""
		pass

	def testSimCompletes(self):
		"""
		Tests that the complex simulation setup returns the correct species richness.
		Also tests that both methods of obtaining species richness work.
		"""
		self.assertEqual(self.coal.run_simple(1, 11, "output", 0.1, 2, 10), 29)

class TestCoalSetMaps(unittest.TestCase):
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
		cls.c.finalise_setup()
		cls.c.run_coalescence()

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

class TestCoalFuncCheck(unittest.TestCase):
	"""
	Test the basic capabilities of coalescence
	"""

	@classmethod
	def setUpClass(cls):
		cls.coal = Simulation()
		cls.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							   coarse_file="sample/SA_sample_coarse.tif")
		cls.coal.detect_map_dimensions()
		cls.coal2 = Simulation()
		cls.coal2.set_map_files(sample_file="null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		cls.coal2.detect_map_dimensions()

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
		with self.assertRaises(RuntimeError):
			self.coal.generate_command()


class TestApplySpeciation(unittest.TestCase):
	"""
	Tests applying speciation rates works as expected for simple cases, including checking that the errors raised by
	applying the speciation rates make sense.
	"""

	@classmethod
	def setUpClass(cls):
		cls.coal = Simulation()
		cls.coal.set_simulation_params(seed=1, job_type=31, output_directory="output", min_speciation_rate=0.5,
									   sigma=2 * (2 ** 0.5), tau=2, deme=1, sample_size=0.1, max_time=2,
									   dispersal_relative_cost=1,
									   min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
									   time_config_file="null")
		cls.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							   coarse_file="sample/SA_sample_coarse.tif")
		cls.coal.finalise_setup()
		cls.coal.run_coalescence()

	def testRaisesErrorWhenNullSamplemaskAndFragments(self):
		"""
		Tests that a ValueError is raised when record_fragments is set to true, but the sample file is null.
		:return:
		"""
		t = CoalescenceTree(self.coal)
		with self.assertRaises(ValueError):
			t.set_speciation_params(record_spatial="T", record_fragments="T", speciation_rates=[0.5, 0.7],
									sample_file="null", time_config_file="null")

	def testRaisesErrorWhenNoSampleMask(self):
		"""
		Tests that an error is raised when the samplemask is null and record_fragments is True
		"""
		t = CoalescenceTree(self.coal)
		with self.assertRaises(ValueError):
			t.set_speciation_params(record_spatial="T", record_fragments="T", speciation_rates=[0.5, 0.7],
									sample_file="null", time_config_file="null")

	def testRaisesErrorWhenSpecNotDouble(self):
		t = CoalescenceTree(self.coal)
		t.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=["notdouble"],
								sample_file="null", time_config_file="null")
		with self.assertRaises(TypeError):
			t.apply_speciation()

	def testRaisesErrorWhenSpecNotList(self):
		t = CoalescenceTree(self.coal)
		t.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates="string",
								sample_file="null", time_config_file="null")
		with self.assertRaises(TypeError):
			t.apply_speciation()


class TestSimulationAnalysis(unittest.TestCase):
	"""
	Tests that the simulation can perform all required analyses, and that the correct errors are thrown if the object
	does not exist.
	"""

	@classmethod
	def setUpClass(cls):
		cls.coal = Simulation()
		cls.tree = CoalescenceTree()
		cls.coal.set_simulation_params(seed=9, job_type=1, output_directory="output", min_speciation_rate=0.5,
									   sigma=2 * (2 ** 0.5), tau=2, deme=1, sample_size=0.1, max_time=2,
									   dispersal_relative_cost=1,
									   min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
									   time_config_file="null")
		cls.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							   coarse_file="sample/SA_sample_coarse.tif")
		cls.coal.finalise_setup()
		cls.coal.run_coalescence()
		cls.tree.set_database("output/SQL_data/data_1_9.db")
		cls.tree.wipe_data()
		cls.tree.set_speciation_params(record_spatial="T",
									   record_fragments="sample/FragmentsTest.csv", speciation_rates=[0.5, 0.7],
									   sample_file="sample/SA_samplemaskINT.tif", time_config_file="null")
		cls.tree.apply_speciation()
		cls.tree.calculate_fragment_richness()
		cls.tree.calculate_fragment_octaves()

	def testReadsFragmentsRichness(self):
		"""
		Tests that the fragment richness can be read correctly
		"""
		sim_params = self.tree.get_simulation_parameters()
		expected_params = dict(seed=9, job_type=1, output_dir='output', speciation_rate=0.5, sigma=2.828427, tau=2.0,
							   deme=1, sample_size=0.1, max_time=2.0, dispersal_relative_cost=1.0,
							   min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=200.0,
							   time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
							   coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
							   coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
							   fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
							   sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
							   sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
							   pristine_coarse_map='none', pristine_fine_map='none', sim_complete=1,
							   dispersal_method='normal', m_probability=0.0, cutoff=0.0, infinite_landscape='closed',
							   protracted=0, min_speciation_gen=0.0, max_speciation_gen=0.0, dispersal_map="none")
		for key in sim_params.keys():
			self.assertEqual(sim_params[key], expected_params[key],
							 msg="Error in {}: {} != {}".format(key, sim_params[key], expected_params[key]))
		fragment2_richness = ["fragment2", 1, 129]
		self.assertEqual(self.tree.get_fragment_richness(fragment="fragment2", reference=1),
						 129)
		self.assertEqual(self.tree.get_fragment_richness(fragment="fragment1", reference=2), 175)
		octaves = self.tree.get_fragment_richness()
		self.assertListEqual(fragment2_richness, [list(x) for x in octaves if x[0] == "fragment2" and x[1] == 1][0])

	def testGetsFragmentList(self):
		"""
		Tests that fetching the list of fragments from FRAGMENT_ABUNDANCES is as expected
		"""
		fragment_list = self.tree.get_fragment_list()
		expected_list = ["fragment1", "fragment2"]
		self.assertListEqual(expected_list, fragment_list)

	def testReadsFragmentAbundances(self):
		"""
		Tests that the fragment abundances are correctly read
		"""
		expected_abundances = [[610, 1],
							   [611, 1],
							   [612, 1],
							   [613, 1],
							   [614, 1],
							   [615, 1],
							   [616, 1],
							   [617, 1],
							   [618, 1],
							   [619, 1]]
		actual_abundances = self.tree.get_species_abundances(fragment="fragment2", reference=1)
		for i, each in enumerate(expected_abundances):
			self.assertListEqual(actual_abundances[i], each)
		with self.assertRaises(RuntimeError):
			self.tree.get_species_abundances(fragment="fragment2")

	def testFragmentRichnessRaiseError(self):
		"""
		Tests that the correct errors are raised when no fragment exists with that name, or with the specified
		speciation rate, or time. Also checks SyntaxErrors and sqlite3.OperationalErrors when no FRAGMENT_RICHNESS table
		exists.
		"""
		failtree = CoalescenceTree()
		try:
			failtree.set_database("sample/failsample.db")
		except sqlite3.OperationalError:
			pass
		with self.assertRaises(RuntimeError):
			failtree.get_fragment_richness()
		with self.assertRaises(RuntimeError):
			self.tree.get_fragment_richness(fragment="fragment4", reference=1)
		with self.assertRaises(SyntaxError):
			self.tree.get_fragment_richness(fragment="fragment4")
		with self.assertRaises(SyntaxError):
			self.tree.get_fragment_richness(reference=1)

	def testReadsFragmentOctaves(self):
		"""
		Tests that the fragment octaves can be read correctly.
		"""

		octaves = self.tree.get_fragment_octaves(fragment="fragment2", reference=1)
		octaves2 = self.tree.get_fragment_octaves(fragment="fragment1", reference=1)
		all_octaves = self.tree.get_fragment_octaves()
		desired = ['fragment1', 1, 0, 173]
		self.assertListEqual([0, 128], octaves[0])
		self.assertListEqual([0, 173], octaves2[0])
		self.assertListEqual(desired, [x for x in all_octaves if x[0] == "fragment1" and x[1] == 1 and x[2] == 0][0])

	def testFragmentOctavesRaiseError(self):
		"""
		Tests that the correct errors are raised for different situations for reading fragment octaves
		"""
		failtree = CoalescenceTree()
		try:
			failtree.set_database("sample/failsample.db")
		except sqlite3.OperationalError:
			pass
		with self.assertRaises(sqlite3.OperationalError):
			failtree.get_fragment_octaves(fragment="fragment4", reference=100)
		with self.assertRaises(RuntimeError):
			self.tree.get_fragment_octaves(fragment="fragment4", reference=100)
		with self.assertRaises(SyntaxError):
			self.tree.get_fragment_octaves(fragment="fragment4")
		with self.assertRaises(SyntaxError):
			self.tree.get_fragment_octaves(reference=100)

	def testFragmentSampling(self):
		"""
		Tests that sampling from fragments is accurate.
		"""
		self.assertEqual(10, self.tree.sample_fragment_richness(fragment="fragment1",
																number_of_individuals=10, n=1, community_reference=2))
		self.assertEqual(10, self.tree.sample_fragment_richness(fragment="fragment2",
																number_of_individuals=10, n=10, community_reference=2))

	def testLandscapeSampling(self):
		"""
		Tests that the sampling from the landscape works as intended
		"""
		number_dict = {"fragment1" : 3, "fragment2" : 10}
		self.assertEqual(13, self.tree.sample_landscape_richness(number_of_individuals=number_dict, n=1,
																 community_reference=2))
		self.assertAlmostEqual(99.9, self.tree.sample_landscape_richness(number_of_individuals=100, n=10,
																		 community_reference=1),
							   places=1)

	def testRaisesSamplingErrors(self):
		number_dict = {"fragment1": 3000000, "fragment2": 10}
		with self.assertRaises(KeyError):
			self.assertEqual(13, self.tree.sample_landscape_richness(number_of_individuals=number_dict, n=1,
																	 community_reference=2))
		number_dict2 = {"fragment": 10, "fragment2": 10}
		with self.assertRaises(KeyError):
			self.assertEqual(13, self.tree.sample_landscape_richness(number_of_individuals=number_dict2, n=1,
																	 community_reference=2))


class TestFattailVersionsMatch(unittest.TestCase):
	"""
	Tests that the old fat-tailed dispersal kernel matches the new fat-tailed dispersal kernel. Uses an infinite
	landscape
	"""

	@classmethod
	def setUpClass(self):
		self.coal = Simulation()
		self.coal2 = Simulation()
		self.tree1 = CoalescenceTree()
		self.tree2 = CoalescenceTree()
		self.coal.set_simulation_params(seed=1, job_type=13, output_directory="output", min_speciation_rate=0.1,
										sigma=2.0, tau=1.0, deme=1, sample_size=0.1, max_time=2,
										dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", dispersal_method="fat-tail", infinite_landscape=True)
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=1, job_type=14, output_directory="output", min_speciation_rate=0.1,
										 sigma=2.0, tau=-3.0, deme=1, sample_size=0.1, max_time=2,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="fat-tail-old",
										 infinite_landscape=True)
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.detect_map_dimensions()
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree1.set_database(self.coal)
		self.tree1.calculate_richness()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.1],
										 sample_file="null", time_config_file="null")
		# self.tree2.apply_speciation()
		self.tree2.calculate_richness()

	def testOldKernelMatchesNewKernelRichness(self):
		"""
		Tests that the old dispersal kernel matches the new dispersal kernel in richness
		"""
		self.assertEqual(self.tree1.get_richness(1),
						 self.tree2.get_richness(1))
		self.assertEqual(self.tree1.get_landscape_richness(1),
						 self.tree2.get_landscape_richness(1))

	def testOldKernelMatchesNewKernelSpeciesList(self):
		"""
		Tests that the old dispersal kernel matches the new dispersal kernel for the species list object.
		This represents identical coalescence trees being produced.
		"""
		species_list1 = self.tree1.get_species_list()
		species_list2 = self.tree2.get_species_list()
		for i, each in enumerate(species_list1):
			self.assertListEqual(list(each), list(species_list2[i]))


class TestNormalMatchesFatTailedExtreme(unittest.TestCase):
	"""
	Tests that the fat-tailed dispersal kernel matches the normal distribution for very large tau. Uses an infinite
	landscape.
	"""

	@classmethod
	def setUpClass(self):
		self.coal = Simulation()
		self.coal2 = Simulation()
		self.tree1 = CoalescenceTree()
		self.tree2 = CoalescenceTree()
		self.coal.set_simulation_params(seed=1, job_type=15, output_directory="output", min_speciation_rate=0.01,
										sigma=2.0, tau=100000000000000000000000, deme=1, sample_size=0.1, max_time=4,
										dispersal_relative_cost=1,
										min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										time_config_file="null", dispersal_method="normal", infinite_landscape=True)
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=1, job_type=16, output_directory="output", min_speciation_rate=0.01,
										 sigma=2, tau=-4, deme=1, sample_size=0.1, max_time=3,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal", infinite_landscape=True)
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.detect_map_dimensions()
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		# self.coal.set_speciation_rates([0.5, 0.7])
		self.tree1.set_database(self.coal)
		self.tree1.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.01],
										 sample_file="null", time_config_file="null")
		# self.tree1.apply_speciation()
		self.tree1.calculate_richness()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.01],
										 sample_file="null", time_config_file="null")
		# self.tree2.apply_speciation()
		self.tree2.calculate_richness()

	def testOldKernelMatchesNewKernelRichness(self):
		"""
		Tests that the fat-tailed dispersal kernel matches the normal distribution for extreme tau in richness
		"""
		self.assertEqual(self.tree1.get_richness(1),
						 self.tree2.get_richness(1))
		self.assertEqual(self.tree1.get_landscape_richness(1),
						 self.tree2.get_landscape_richness(1))

	def testOldKernelMatchesNewKernelSpeciesList(self):
		"""
		Tests that the fat-tailed dispersal kernel matches the normal distribution for extreme tau in the species list.
		This represents identical coalescence trees being produced.
		"""
		species_list1 = self.tree1.get_species_list()
		species_list2 = self.tree2.get_species_list()
		for i, each in enumerate(species_list1):
			self.assertListEqual(list(each), list(species_list2[i]))


class TestExtremeSpeciation(unittest.TestCase):
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
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null", dispersal_method="normal", infinite_landscape=False)
		c.set_map("null", 10, 10)
		c.finalise_setup()
		c.run_coalescence()
		self.assertEqual(c.get_richness(), 1)

	def testMaxSpeciation(self):
		"""
		Tests that running a simulation with a zero speciation rate produces a single species.
		"""
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=18, output_directory="output", min_speciation_rate=1.0,
								sigma=2.0, tau=1, deme=1, sample_size=1, max_time=4,
								dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null", dispersal_method="normal", infinite_landscape=False)
		c.set_map("null", 10, 10)
		c.finalise_setup()
		c.run_coalescence()
		self.assertEqual(c.get_richness(), 100)


class TestDispersalSimulation(unittest.TestCase):
	"""
	Tests the dispersal simulation methods contained in Map
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the class by running the dispersal simulations for later reference.
		"""
		cls.m = Map(logging_level=logging.CRITICAL)
		cls.m.test_mean_dispersal(number_repeats=100, output_database="output/sim_pars_test4.db",
							  map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal", sigma=2)
		cls.m.test_mean_dispersal(number_repeats=100, output_database="output/sim_pars_test4.db",
							  map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal", sigma=2)
		cls.m.test_mean_dispersal(number_repeats=100, output_database="output/sim_pars_test4.db",
							  map_file="sample/SA_sample_fine.tif", seed=3, dispersal_method="fat-tail", sigma=2, tau=1)
		cls.m.test_mean_distance_travelled(number_repeats=100, number_steps=10,
									   output_database="output/sim_pars_test4.db",
									   map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal", sigma=2)
		cls.m.test_mean_distance_travelled(number_repeats=200, number_steps=10,
									   output_database="output/sim_pars_test4.db",
									   map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal", sigma=5)
		cls.m.test_mean_distance_travelled(number_repeats=100, number_steps=20,
									   output_database="output/sim_pars_test4.db",
									   map_file="sample/SA_sample_fine.tif", seed=4, dispersal_method="normal", sigma=2)

	def testRaisesIOError(self):
		"""
		Tests that an IOerror is raised when the output database doesn't exist
		"""
		m = Map(logging_level=logging.CRITICAL)
		m.dispersal_database = "doesnotexist.db"
		with self.assertRaises(IOError):
			m.get_mean_dispersal()

	def testRaisesValueErrorExistance(self):
		"""
		Tests that a value error is raised when dispersal_database does not exist
		"""
		m = Map(logging_level=logging.CRITICAL)
		with self.assertRaises(ValueError):
			m.get_mean_dispersal()

	def testRaisesValueErrorNullNotSet(self):
		"""
		Tests that a ValueError is raised when the map file is "null" but dimensions have not been manually set.
		"""
		m = Map(logging_level=logging.CRITICAL)
		with self.assertRaises(ValueError):
			m.test_mean_dispersal(number_repeats=10000, output_database="output/normaldispersal.db", map_file="null",
								  seed=1, dispersal_method="normal", sigma=1, tau=1, m_prob=0.0, cutoff=100)

	def testRaisesDispersalError(self):
		"""
		Tests that a dispersal.Error is raised when incorrect dispersal method is provided.
		"""
		m = Map(logging_level=logging.CRITICAL)
		with self.assertRaises(ValueError):
			m.test_mean_dispersal(number_repeats=10000, output_database="output/normaldispersal.db", map_file="null",
								  seed=1, dispersal_method="notreal", sigma=1, tau=1, m_prob=0.0, cutoff=100)

	def testDispersalNullOutputs(self):
		"""
		Tests that the dispersal simulations accurately generate the correct distance distribution for null landscapes.
		"""
		m = Map(logging_level=logging.CRITICAL)
		m.set_dimensions("null", 10, 10, 0, 0)
		m.test_mean_dispersal(number_repeats=10000, output_database="output/normaldispersal.db", map_file="null",
							  seed=1, dispersal_method="normal", sigma=1, tau=1, m_prob=0.0, cutoff=100)
		self.assertAlmostEqual(m.get_mean_dispersal(), (3.14 ** 0.5) / 2 ** 0.5, places=2)

	def testDispersalMapOutputs(self):
		"""
		Tests that the dispersal simulations work as intended for real maps.
		"""
		m = Map(logging_level=logging.CRITICAL)
		m.test_mean_dispersal(number_repeats=10000, output_database="output/realdispersal.db",
							  map_file="sample/SA_sample_fine.tif", seed=1, dispersal_method="normal", sigma=1, tau=1,
							  m_prob=0.0, cutoff=100, )
		self.assertEqual(1.2516809696363225, m.get_mean_dispersal())

	def testDispersalDistanceTravelled(self):
		m = Map(logging_level=logging.CRITICAL)
		m.test_mean_distance_travelled(number_repeats=100, number_steps=10, output_database="output/sim_pars_test2.db",
									   map_file="sample/SA_sample_fine.tif", seed=1, dispersal_method="normal", sigma=1,
									   tau=1, m_prob=0.0, cutoff=100)
		self.assertEqual(4.044138945328306, m.get_mean_distance_travelled())

	def testDispersalSimulationParametersStoredCorrectly(self):
		"""
		Tests that simulation parameters are stored correctly in the database.
		"""
		m = Map(logging_level=logging.CRITICAL)
		m.test_mean_dispersal(number_repeats=100, output_database="output/sim_pars_test1.db",
							  map_file="sample/SA_sample_fine.tif", seed=1, dispersal_method="normal", sigma=1)
		m.test_mean_distance_travelled(number_repeats=100, number_steps=10,
									   output_database="output/sim_pars_test1.db",
									   map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal", sigma=2)
		main_dict = m.get_database_parameters()
		comparison_dict = {
			1 : {
				"simulation_type": "DISPERSAL_DISTANCES", "sigma": 1, "tau": 1, "cutoff": 100, "m_prob": 0.0,
				"dispersal_method": "normal", "map_file": "sample/SA_sample_fine.tif", "seed": 1, "number_steps": 0,
				"number_repeats": 100

			},
			2 : {
				"simulation_type": "DISTANCES_TRAVELLED", "sigma": 2, "tau": 1, "cutoff": 100, "m_prob": 0.0,
				"dispersal_method": "normal", "map_file": "sample/SA_sample_fine.tif", "seed": 2, "number_steps": 10,
				"number_repeats": 100
			}
		}
		for key in main_dict.keys():
			for inner_key in main_dict[key].keys():
				self.assertEqual(main_dict[key][inner_key], comparison_dict[key][inner_key])

	def testMultipleSimulationsAverages(self):
		"""
		Tests that with multiple simulations, the averages are outputted correctly.
		"""

		self.assertAlmostEqual(2.538571186951144, self.m.get_mean_dispersal(parameter_reference=2))
		self.assertAlmostEqual(23.560759104038837, self.m.get_mean_dispersal(parameter_reference=3))
		self.assertAlmostEqual(7.343591615993395, self.m.get_mean_distance_travelled(parameter_reference=4))
		self.assertAlmostEqual(19.34581665661196, self.m.get_mean_distance_travelled(parameter_reference=5))

	def testStandardDeviationDistances(self):
		"""
		Tests that the standard deviation is correctly returned from the simulated database
		"""
		self.assertAlmostEqual(1.5211935372029735, self.m.get_stdev_dispersal(parameter_reference=1))
		self.assertAlmostEqual(1.5211935372029735, self.m.get_stdev_dispersal(parameter_reference=2))
		self.assertAlmostEqual(4.6574308559023772, self.m.get_stdev_distance_travelled(parameter_reference=4))
		self.assertAlmostEqual(10.408139982184849, self.m.get_stdev_distance_travelled(parameter_reference=5))


	def testDispersalMapReading(self):
		"""
		Tests that dispersal simulations are correctly read from a completed simulation
		"""
		m = Map(logging_level=logging.CRITICAL)
		m.test_mean_dispersal(number_repeats=10000, output_database="output/realdispersal2.db",
							  map_file="sample/SA_sample_fine.tif", seed=1, dispersal_method="normal", sigma=1, tau=1,
							  m_prob=0.0, cutoff=100)
		m2 = Map(dispersal_db=m.dispersal_database, logging_level=logging.CRITICAL)
		self.assertEqual(1.2516809696363225, m2.get_mean_dispersal())
		m3 = Map(dispersal_db=m, logging_level=logging.CRITICAL)
		self.assertEqual(1.2516809696363225, m3.get_mean_dispersal())


class TestCoalPaleoTime(unittest.TestCase):
	"""
	Tests that simulations across paleo time do not cause any problems, i.e. sample times being extremely far apart does
	not create any issues.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation()
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(1, 28, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_pristine=2, dispersal_method="normal")
		self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.add_sample_time(100000000.0)
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)

	def testGetsPresentRichness(self):
		"""
		Tests that the simulation obtains the present-day richnesses accurately
		"""
		self.assertEqual(self.coal.get_richness(1), 40)
		self.assertEqual(self.coal.get_richness(3), 55)

	def testGetsHistoricalRichness(self):
		"""
		Tests that the simulation obtains the historical richnesses accurately
		"""
		self.assertEqual(self.coal.get_richness(2), 43)
		self.assertEqual(self.coal.get_richness(4), 59)


class TestCoalProtractedSanityChecks(unittest.TestCase):
	"""
	Tests a set of protracted runs over to make sure that the results make sense.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal1 = Simulation(logging_level=logging.ERROR)
		self.coal2 = Simulation(logging_level=logging.ERROR)
		self.coal3 = Simulation(logging_level=logging.ERROR)
		self.coal4 = Simulation(logging_level=logging.ERROR)
		self.tree1 = CoalescenceTree()
		self.tree2 = CoalescenceTree()
		self.tree3 = CoalescenceTree()
		self.tree4 = CoalescenceTree()
		self.coal1.set_simulation_params(seed=1, job_type=19, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal", protracted=True,
										 min_speciation_gen=0, max_speciation_gen=2)
		self.coal2.set_simulation_params(seed=1, job_type=20, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal", protracted=True,
										 min_speciation_gen=10, max_speciation_gen=50)
		self.coal3.set_simulation_params(seed=1, job_type=21, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal", protracted=True,
										 min_speciation_gen=10, max_speciation_gen=20)
		self.coal4.set_simulation_params(seed=1, job_type=22, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
										 time_config_file="null", dispersal_method="normal", protracted=False)
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal1.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal3.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal4.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		# self.coal1.set_speciation_rates([0.5])
		# self.coal2.set_speciation_rates([0.5])
		# self.coal3.set_speciation_rates([0.5])
		# self.coal4.set_speciation_rates([0.5])
		self.coal1.finalise_setup()
		self.coal2.finalise_setup()
		self.coal3.finalise_setup()
		self.coal4.finalise_setup()
		self.coal1.run_coalescence()
		self.coal2.run_coalescence()
		self.coal3.run_coalescence()
		self.coal4.run_coalescence()
		self.tree1.set_database(self.coal1)
		self.tree2.set_database(self.coal2)
		self.tree3.set_database(self.coal3)
		self.tree4.set_database(self.coal4)
		self.tree1.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal1.time_config_file)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal2.time_config_file)
		self.tree3.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal3.time_config_file)
		self.tree4.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null", time_config_file=self.coal4.time_config_file)
		self.tree1.apply_speciation()
		self.tree2.apply_speciation()
		self.tree3.apply_speciation()
		self.tree4.apply_speciation()
		self.tree1.calculate_octaves()
		self.tree2.calculate_octaves()
		self.tree3.calculate_octaves()
		self.tree4.calculate_octaves()
		self.tree1.calculate_richness()
		self.tree2.calculate_richness()
		self.tree3.calculate_richness()
		self.tree4.calculate_richness()

	def testProtractedIsApplied(self):
		"""
		Simply checks that simulations are properly marked as protracted when using protracted speciation.
		"""
		self.assertEqual(self.tree1.get_simulation_parameters()["protracted"], 1)
		self.assertEqual(self.tree1.is_protracted(), True)
		self.assertEqual(self.tree4.get_simulation_parameters()["protracted"], 0)
		self.assertEqual(self.tree4.is_protracted(), False)

	def testComplexRichness(self):
		"""
		Tests that the complex simulation setup returns the correct species richness.
		Also tests that both methods of obtaining species richness work.
		"""
		self.assertGreaterEqual(self.tree1.get_richness(), self.tree2.get_richness())
		self.assertGreaterEqual(self.tree3.get_richness(), self.tree2.get_richness())
		self.assertGreaterEqual(self.tree1.get_richness(), self.tree4.get_richness())


class TestCoalDispersalMaps(unittest.TestCase):
	"""
	Tests the dispersal maps to ensure that values are read properly, and using dispersal maps for simulations works as
	intended.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the objects for running coalescence simulations on dispersal maps.
		"""
		self.c = Simulation(logging_level=logging.CRITICAL)
		self.c.set_simulation_params(seed=1, job_type=32, output_directory="output", min_speciation_rate=0.5,
									 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
									 min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
									 time_config_file="null")
		self.c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_coarse.tif",
							 dispersal_map="sample/dispersal_fine.tif")
		self.c.finalise_setup()
		self.c.run_coalescence()

	def testDispersalSimulation(self):
		"""
		Tests that running a simulation with a dispersal map produces the expected output.
		"""
		self.assertEqual(self.c.get_richness(1), 869)

	def testDispersalParamStorage(self):
		"""
		Tests that the dispersal parameters are stored correctly
		"""
		t = CoalescenceTree(self.c)
		self.assertEqual(t.get_simulation_parameters()['dispersal_map'], "sample/dispersal_fine.tif")

	def testDispersalDimensionsErrorCoarse(self):
		"""
		Tests that an error is raised if a coarse map is provided, but a dispersal map is also chosen.
		"""
		c = Simulation(logging_level=logging.CRITICAL)
		c.set_simulation_params(seed=2, job_type=32, output_directory="output", min_speciation_rate=0.5,
								sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null")
		with self.assertRaises(TypeError):
			c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_coarse.tif",
							coarse_file="sample/SA_sample_coarse.tif", dispersal_map="sample/dispersal_fine.tif")

	def testDispersalDimensionsErrorMismatch(self):
		"""
		Tests that an error is raised if the dispersal map does not match the dimensions of the fine map, calculated
		as a map of maps.
		"""
		c = Simulation(logging_level=logging.CRITICAL)
		c.set_simulation_params(seed=3, job_type=32, output_directory="output", min_speciation_rate=0.5,
								sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null")
		with self.assertRaises(ValueError):
			c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							dispersal_map="sample/dispersal_fine.tif")


class TestFragmentedLandscape(unittest.TestCase):
	"""
	Tests that the fragmented landscape generation creates successfully for a range of fragment numbers and sizes.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the class object by creating the required maps
		:return:
		"""
		cls.l1 = FragmentedLandscape(size=10, number_fragments=2, total=4, output_file="landscapes/l1.tif")
		cls.l2 = FragmentedLandscape(size=100, number_fragments=57, total=150, output_file="landscapes/l2.tif")
		cls.l3 = FragmentedLandscape(size=24, number_fragments=5, total=5, output_file="landscapes/l3.tif")
		cls.l1.generate()
		cls.l2.generate()
		cls.l3.generate()
		cls.l4 = FragmentedLandscape(size=10, number_fragments=1, total=2, output_file="landscapes/l4.tif")
		cls.l4.generate()
		cls.l5 = FragmentedLandscape(size=100, number_fragments=100, total=2000, output_file="landscapes/l5.tif")
		cls.l5.generate()

	@classmethod
	def tearDownClass(cls):
		# pass
		if os.path.exists("landscapes"):
			rmtree("landscapes")

	def testCreateFragmentedLandscapes(self):
		self.assertEqual(self.l1.output_file, "landscapes/l1.tif")
		self.assertTrue(os.path.exists(self.l1.output_file))
		self.assertEqual(self.l2.output_file, "landscapes/l2.tif")
		self.assertTrue(os.path.exists(self.l2.output_file))
		self.assertEqual(self.l3.output_file, "landscapes/l3.tif")
		self.assertTrue(os.path.exists(self.l3.output_file))
		self.assertEqual(self.l4.output_file, "landscapes/l4.tif")
		self.assertTrue(os.path.exists(self.l4.output_file))

	def testDimensionsCorrect1(self):
		"""
		Checks that the saved dimensions are correct.
		"""
		m1 = Map(logging_level=logging.CRITICAL)
		m1.file_name = self.l1.output_file
		m1.set_dimensions()
		self.assertEqual(m1.x_size, 10)
		self.assertEqual(m1.y_size, 10)

	def testDimensionsCorrect2(self):
		"""
		Checks that the saved dimensions are correct.
		"""
		m2 = Map()
		m2.file_name = self.l2.output_file
		m2.set_dimensions()
		self.assertEqual(m2.x_size, 100)
		self.assertEqual(m2.y_size, 100)

	def testDimensionsCorrect3(self):
		"""
		Checks that the saved dimensions are correct.
		"""
		m3 = Map()
		m3.file_name = self.l3.output_file
		m3.set_dimensions()
		self.assertEqual(m3.x_size, 24)
		self.assertEqual(m3.y_size, 24)

	def testDimensionsCorrect5(self):
		"""
		Checks that the saved dimensions are correct.
		"""
		m5 = Map()
		m5.file_name = self.l5.output_file
		m5.set_dimensions()
		self.assertEqual(m5.x_size, 100)
		self.assertEqual(m5.y_size, 100)


class TestMapDensityReading(unittest.TestCase):
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
									min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
									time_config_file="null")
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
		self.assertAlmostEqual(self.c.get_average_density(), 38339.500427246094, 3)

	def testCountIndividuals(self):
		"""
		Tests that the count of numbers of individuals is roughly accurate
		"""
		self.assertTrue(self.c.count_individuals() - 12381 < 2200)


class TestDetectRamUsage(unittest.TestCase):
	"""
	Class for testing the RAM detection and utilisation of pycoalescence
	"""

	@classmethod
	def setUpClass(cls):
		cls.c = Simulation(logging_level=logging.CRITICAL)
		cls.c.set_simulation_params(seed=1, job_type=36, output_directory="output", min_speciation_rate=0.5,
									sigma=2, tau=2, deme=1000, sample_size=0.01, max_time=100,
									dispersal_relative_cost=1,
									min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
									time_config_file="null", infinite_landscape=False)
		cls.c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
		cls.c.add_sample_time(1.0)
		try:
			cls.c.optimise_ram(ram_limit=0.03)
			cls.c.finalise_setup()
			cls.c.run_coalescence()
		except MemoryError as me:
			cls.fail("Cannot run a larger scale simulation. This should require around 500MB of RAM. If your computer"
					 " does not have these requirements, ignore this failure: {}".format(me))

	def testExcessiveRamUsage(self):
		"""
		Tests that an exception is raised if there is not enough RAM to complete the simulation.
		"""
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=36, output_directory="output", min_speciation_rate=0.5,
								sigma=2, tau=2, deme=100000000000, sample_size=0.1, max_time=10,
								dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null")
		c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
		with self.assertRaises(MemoryError):
			c.optimise_ram(ram_limit=16)

	def testGridOffsetApplyingSpeciation(self):
		"""
		Tests that additional speciation rates are correctly applied when using an offsetted grid
		"""
		t = CoalescenceTree(self.c)
		t.set_speciation_params(record_spatial="T", record_fragments="sample/FragmentsTest2.csv",
								speciation_rates=[0.6, 0.7], sample_file="null", time_config_file="null")
		t.apply_speciation()
		t.calculate_fragment_richness()
		self.assertEqual(t.get_fragment_richness(fragment="fragment2", reference=3), 30)
		self.assertEqual(t.get_fragment_richness(fragment="fragment1", reference=3), 30)

	def testOffsetsStoredCorrectly(self):
		self.assertEqual(self.c.sample_map.x_offset, 1250)
		self.assertEqual(self.c.sample_map.y_offset, 1250)
		self.assertEqual(self.c.grid.x_size, 55)
		self.assertEqual(self.c.grid.y_size, 55)
		self.assertEqual(self.c.grid.file_name, "set")

	def testExcessiveRamReallocation(self):
		"""
		Tests that in a system with excessive RAM usage, the map file structure is rearranged for lower performance,
		but optimal RAM usage.
		"""
		self.assertEqual(self.c.get_richness(1), 1770)
		self.assertEqual(self.c.get_richness(2), 1770)

	def testSingleLargeRun(self):
		"""
		Tests a single run with a huge number of individuals in two cells
		"""
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=37, output_directory="output", min_speciation_rate=0.95,
								sigma=1, tau=2, deme=70000, sample_size=1, max_time=100, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null", infinite_landscape=False)
		c.set_map_parameters(sample_file="null", sample_x=2, sample_y=1, fine_file="null",
							 fine_x=2, fine_y=1, fine_x_offset=0, fine_y_offset=0,
							 coarse_file="none", coarse_x=2, coarse_y=1, coarse_x_offset=0, coarse_y_offset=0,
							 coarse_scale=1.0, pristine_fine_map="none", pristine_coarse_map="none")
		c.finalise_setup()
		c.run_coalescence()
		self.assertEqual(c.get_richness(1), 136400)

	def testReadWriteSaveState(self):
		saved_state = self.c.get_optimised_solution()
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=36, output_directory="output", min_speciation_rate=0.5,
								sigma=2, tau=2, deme=100000000000, sample_size=0.1, max_time=10,
								dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_pristine=200,
								time_config_file="null")
		c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
		c.set_optimised_solution(saved_state)
		self.assertEqual(c.sample_map.x_offset, 1250)
		self.assertEqual(c.sample_map.y_offset, 1250)
		self.assertEqual(c.grid.x_size, 55)
		self.assertEqual(c.grid.y_size, 55)
		self.assertEqual(c.grid.file_name, "set")


class TestSubsettingMaps(unittest.TestCase):
	"""
	Tests the reading of tif files works correctly, including subsetting and cached-subsetting to obtain selections from
	the maps.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the map object for reading from.
		"""
		cls.m = Map("sample/SA_sample_fine.tif")

	def testSubsetting(self):
		arr = self.m.get_subset(x_offset=0, y_offset=0, x_size=13, y_size=13)
		self.assertEqual(arr[0, 0], 231)
		self.assertEqual(arr[1, 0], 296)
		self.assertEqual(arr[0, 1], 303)
		arr2 = self.m.get_subset(x_offset=5, y_offset=5, x_size=2, y_size=2)
		self.assertEqual(arr2[0, 0], 288)
		self.assertEqual(arr2[1, 0], 263)
		self.assertEqual(arr2[0, 1], 286)

	def testCachedSubsetting(self):
		arr = self.m.get_cached_subset(x_offset=0, y_offset=0, x_size=13, y_size=13)
		self.assertEqual(arr[0, 0], 231)
		self.assertEqual(arr[1, 0], 296)
		self.assertEqual(arr[0, 1], 303)
		arr2 = self.m.get_cached_subset(x_offset=5, y_offset=5, x_size=2, y_size=2)
		self.assertEqual(arr2[0, 0], 288)
		self.assertEqual(arr2[1, 0], 263)
		self.assertEqual(arr2[0, 1], 286)


class TestSqlFetchAndCheck(unittest.TestCase):
	"""
	Tests that fetches and checks on the SQL databases work as intended.
	"""

	def testReadsCommunityParameters(self):
		"""
		Test that community parameters are correctly read from the database.
		"""
		community_parameters = fetch_table_from_sql(database="sample/mergers/data_0_0.db",
													table_name="COMMUNITY_PARAMETERS")
		expected_community_parameters = [[1, 0.5, 0.0, 0, 0],
										 [2, 0.5, 0.5, 0, 0],
										 [3, 0.6, 0.0, 0, 0],
										 [4, 0.6, 0.5, 0, 0],
										 [5, 0.7, 0.0, 0, 0],
										 [6, 0.7, 0.5, 0, 0]]
		for i, row in enumerate(expected_community_parameters):
			self.assertListEqual(row, community_parameters[i])

	def testDetectsTablesCorrectly(self):
		"""
		Checks that check_sql_table_exist correctly detects the existence of tables
		"""
		self.assertFalse(check_sql_table_exist(database="sample/mergers/data_0_0.db",
											   table_name="notarealtable"))
		self.assertTrue(check_sql_table_exist(database="sample/mergers/data_0_0.db",
											  table_name="COMMUNITY_PARAMETERS"))


class TestSimulationReadingViaMerger(unittest.TestCase):
	"""
	Tests that simulation can successfully read tables from a database.
	"""

	dbname = "sample/mergers/combined.db"

	@classmethod
	def tearDownClass(cls):
		if os.path.exists(cls.dbname):
			os.remove(cls.dbname)


	def testReadsSimulationParameters(self):
		"""
		Tests that simulation parameters are correctly read from the database.
		"""
		simulation_parameters = Merger()._read_simulation_parameters(input_simulation="sample/mergers/data_0_0.db")
		expected_parameters = [6, 6, "output", 0.5, 4.0, 4.0, 1, 0.1, 10, 1.0, 1, 0.0, 200.0,
							   "output/timeconf_6_6.txt", "sample/SA_sample_coarse.tif", 35, 41, 11, 14, 1.0,
							   "sample/SA_sample_fine.tif", 13, 13, 0, 0, "null", 13, 13, 13, 13, 0, 0, "none",
							   "none", 1, "normal", 0.0, 0.0, 0, "closed", 0, 0.0, 0.0, "none"]
		self.assertListEqual(simulation_parameters, expected_parameters)

	def testReadsSpeciesList(self):
		"""
		Tests that the species list object is correctly read from the database.
		"""
		species_list = Merger()._read_species_list(input_simulation="sample/mergers/data_0_0.db")[0:5]
		expected_list = [[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0.0, 0, 0.0, ],
						 [1, 0, 0, 0, 0, 0, 1, 0, 3761, 0, 0.712285394568117, 0, 0.0],
						 [2, 0, 0, 0, 0, 0, 1, 0, 3762, 0, 0.113159547847957, 0, 0.0],
						 [3, 0, 0, 0, 0, 0, 1, 0, 3763, 0, 0.95236636044045, 0, 0.0],
						 [4, 0, 0, 0, 0, 0, 1, 0, 3764, 0, 0.679672305831754, 0, 0.0]]
		for i, row in enumerate(expected_list):
			for j, each in enumerate(row):
				if j == 10 or j == 12:
					self.assertAlmostEqual(each, species_list[i][j])
				else:
					self.assertEqual(each, species_list[i][j])

	def testReadsSpeciesRichness(self):
		"""
		Tests that the species richness object is correctly read from the database
		"""
		species_richness = Merger()._read_species_richness(input_simulation="sample/mergers/data_0_0.db")
		expected_richness = [[0, 1, 3644],
							 [1, 2, 3643],
							 [2, 3, 3674], [3, 4, 3675],
							 [4, 5, 3697],
							 [5, 6, 3695]]
		for i, row in enumerate(expected_richness):
			self.assertListEqual(row, species_richness[i])

	def testReadsSpeciesAbundances(self):
		"""
		Tests that the species abundances object is correctly read from the database
		"""
		species_abundances = Merger()._read_species_abundances(input_simulation="sample/mergers/data_0_0.db")[-6:]
		expected_abundances = [[22029, 3690, 2, 6],
							   [22030, 3691, 1, 6],
							   [22031, 3692, 1, 6],
							   [22032, 3693, 1, 6],
							   [22033, 3694, 1, 6],
							   [22034, 3695, 3, 6]]
		for i, row in enumerate(expected_abundances):
			self.assertListEqual(row, species_abundances[i])

	def testReadsFragmentOctaves(self):
		"""
		Tests that the fragment octaves object is correctly read from the database.
		"""
		fragment_octaves = Merger()._read_fragment_octaves(input_simulation="sample/mergers/data_0_0.db")
		expected_octaves = [[0, "whole", 0, 3560],
							[1, "whole", 0, 3559],
							[2, "whole", 0, 3617],
							[3, "whole", 0, 3619],
							[4, "whole", 0, 3662],
							[5, "whole", 0, 3658]]
		for i, row in enumerate(expected_octaves):
			self.assertListEqual(row, fragment_octaves[i])


class TestSimulationMerging(unittest.TestCase):
	"""
	Tests that simulations can be successfully merged with a variety of tables and parameters.
	"""

	@classmethod
	def setUpClass(cls):
		cls.dbname = "sample/mergers/combined1.db"
		if os.path.exists(cls.dbname):
			os.remove(cls.dbname)
		cls.merger = Merger(database=cls.dbname)
		cls.merger.add_simulation("sample/mergers/data_0_0.db")
		cls.merger.add_simulation("sample/mergers/data_1_1.db")
		cls.merger.write()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the output database
		"""
		cls.merger.database.close()
		cls.merger.database = None
		if os.path.exists(cls.dbname):
			os.remove(cls.dbname)

	def testSpeciesList(self):
		"""
		Tests that the species list object is correctly calculates for the database
		"""
		species_richness = fetch_table_from_sql(self.dbname, "SPECIES_LIST")
		check_richness = [x for x in species_richness if x[0] == 28633529 or x[0] == 8]
		check_richness.sort(key=lambda x: x[0])
		expected_richness = [[8, 0, 0, 0, 0, 0, 1, 0, 11328, 0, 0.712285394568117, 0, 0.0, 2],
							 [28633529, 0, 7, 3, 0, 0, 0, 1, 0, 0, 0.603760047033245, 2, 0.0, 1]]
		for i, row in enumerate(expected_richness):
			for j, each in enumerate(row):
				if j == 10 or j == 12:
					self.assertAlmostEqual(each, check_richness[i][j])
				else:
					self.assertEqual(each, check_richness[i][j])

	def testSpeciesRichnessGuilds(self):
		"""
		Tests that the species richness with guilds is correctly calculated from the databases.
		"""
		richness = [[2, 1, 3644, 1],
					[4, 2, 3643, 1],
					[7, 3, 3674, 1],
					[11, 4, 3675, 1],
					[16, 5, 3697, 1],
					[22, 6, 3695, 1],
					[5, 1, 3644, 2],
					[8, 2, 3643, 2],
					[12, 3, 3674, 2],
					[17, 4, 3675, 2],
					[23, 5, 3697, 2],
					[30, 6, 3695, 2]]
		self.assertListEqual(fetch_table_from_sql(self.dbname, "SPECIES_RICHNESS_GUILDS"), richness)

	def testSpeciesRichness(self):
		"""
		Tests that the landscape species richness is correctly calculated from the databases.
		"""
		richness = [[0, 1, 7288],
					[1, 2, 7286],
					[2, 3, 7348],
					[3, 4, 7350],
					[4, 5, 7394],
					[5, 6, 7390]]
		self.assertListEqual(fetch_table_from_sql(self.dbname, "SPECIES_RICHNESS"), richness)

	def testSpeciesAbundances(self):
		"""
		Tests that the species abundances are correctly calculated in the merged database
		"""
		abundances = [[238394531, 3495, 1, 6, 1],
					  [91808, 425, 1, 1, 2]]
		species_richness = fetch_table_from_sql(self.dbname, "SPECIES_ABUNDANCES")
		check_richness = [x for x in species_richness if x[0] == 238394531 or x[0] == 91808]
		for i, each in enumerate(abundances):
			self.assertListEqual(each, check_richness[i])

	def testSimulationParameters(self):
		"""
		Tests that the simulation parameters are correctly calculated in the merged database.
		"""
		sim_pars = [[6, 6, "output", 0.5, 4.0, 4.0, 1, 0.1, 10, 1.0, 1, 0.0, 200.0,
					 "output/timeconf_6_6.txt", "sample/SA_sample_coarse.tif", 35, 41, 11, 14, 1.0,
					 "sample/SA_sample_fine.tif", 13, 13, 0, 0, "null", 13, 13, 13, 13, 0, 0, "none", "none", 1,
					 "normal", 0.0, 0.0, 0, "closed", 0, 0.0, 0.0,
					 "none", 1, "sample/mergers/data_0_0.db"],
					[6, 6, "output", 0.5, 4.0, 4.0, 2, 0.1, 10, 1.0, 1, 0.0, 200.0, "output/timeconf_6_6.txt",
					 "sample/SA_sample_coarse.tif", 35, 41, 11, 14, 1.0, "sample/SA_sample_fine.tif", 13, 13, 0, 0,
					 "null", 13, 13, 13, 13, 0, 0, "none", "none", 1, "normal", 0.0, 0.0, 0, "closed", 0, 0.0, 0.0,
					 "none", 2, "sample/mergers/data_1_1.db"]]
		actual = fetch_table_from_sql(self.dbname, "SIMULATION_PARAMETERS")
		for i, each in enumerate(sim_pars):
			self.assertListEqual(actual[i], each)

	def testSimulationParametersFetching(self):
		output_pars1 = {'coarse_map_file': 'sample/SA_sample_coarse.tif', 'coarse_map_scale': 1.0, 'coarse_map_x': 35,
						'coarse_map_x_offset': 11, 'coarse_map_y': 41, 'coarse_map_y_offset': 14, 'cutoff': 0.0,
						'deme': 1, 'dispersal_map': 'none', 'dispersal_method': 'normal',
						'dispersal_relative_cost': 1.0, 'fine_map_file': 'sample/SA_sample_fine.tif', 'fine_map_x': 13,
						'fine_map_x_offset': 0, 'fine_map_y': 13, 'fine_map_y_offset': 0, 'gen_since_pristine': 200.0,
						'grid_x': 13, 'grid_y': 13, 'habitat_change_rate': 0.0, 'infinite_landscape': 'closed',
						'job_type': 6, 'm_probability': 0.0, 'max_speciation_gen': 0.0, 'max_time': 10,
						'min_num_species': 1, 'min_speciation_gen': 0.0, 'output_dir': 'output',
						'pristine_coarse_map': 'none', 'pristine_fine_map': 'none', 'protracted': 0,
						'sample_file': 'null', 'sample_size': 0.1, 'sample_x': 13, 'sample_x_offset': 0, 'sample_y': 13,
						'sample_y_offset': 0, 'seed': 6, 'sigma': 4.0, 'sim_complete': 1, 'speciation_rate': 0.5,
						'tau': 4.0, 'time_config_file': 'output/timeconf_6_6.txt'}
		output_pars2 = {'coarse_map_file': 'sample/SA_sample_coarse.tif', 'coarse_map_scale': 1.0, 'coarse_map_x': 35,
						'coarse_map_x_offset': 11, 'coarse_map_y': 41, 'coarse_map_y_offset': 14, 'cutoff': 0.0,
						'deme': 2, 'dispersal_map': 'none', 'dispersal_method': 'normal',
						'dispersal_relative_cost': 1.0, 'fine_map_file': 'sample/SA_sample_fine.tif', 'fine_map_x': 13,
						'fine_map_x_offset': 0, 'fine_map_y': 13, 'fine_map_y_offset': 0, 'gen_since_pristine': 200.0,
						'grid_x': 13, 'grid_y': 13, 'habitat_change_rate': 0.0, 'infinite_landscape': 'closed',
						'job_type': 6, 'm_probability': 0.0, 'max_speciation_gen': 0.0, 'max_time': 10,
						'min_num_species': 1, 'min_speciation_gen': 0.0, 'output_dir': 'output',
						'pristine_coarse_map': 'none', 'pristine_fine_map': 'none', 'protracted': 0,
						'sample_file': 'null', 'sample_size': 0.1, 'sample_x': 13, 'sample_x_offset': 0, 'sample_y': 13,
						'sample_y_offset': 0, 'seed': 6, 'sigma': 4.0, 'sim_complete': 1, 'speciation_rate': 0.5,
						'tau': 4.0, 'time_config_file': 'output/timeconf_6_6.txt'}
		sim_pars1 = self.merger.get_simulation_parameters(guild=1)
		sim_pars2 = self.merger.get_simulation_parameters(guild=2)
		self.assertEqual(output_pars1, sim_pars1)
		self.assertEqual(output_pars2, sim_pars2)

	def testFragmentOctavesGuilds(self):
		"""
		Tests that the fragment octaves with guilds are correctly calculated in the merged database
		"""
		fragment_octaves = [[2, "whole", 0, 3560, 1],
							[4, "whole", 0, 3559, 1],
							[7, "whole", 0, 3617, 1],
							[11, "whole", 0, 3619, 1],
							[16, "whole", 0, 3662, 1],
							[22, "whole", 0, 3658, 1],
							[5, "whole", 0, 3560, 2],
							[8, "whole", 0, 3559, 2],
							[12, "whole", 0, 3617, 2],
							[17, "whole", 0, 3619, 2],
							[23, "whole", 0, 3662, 2],
							[30, "whole", 0, 3658, 2]]
		actual = fetch_table_from_sql(self.dbname, "FRAGMENT_OCTAVES_GUILDS")
		for i, each in enumerate(fragment_octaves):
			self.assertListEqual(each, actual[i])

	def testCommunityParameters(self):
		"""
		Tests that the community parameters are correclty calculated in the merged database.
		"""
		community_params = [[1, 0.5, 0.0, 0, 0],
							[2, 0.5, 0.5, 0, 0],
							[3, 0.6, 0.0, 0, 0],
							[4, 0.6, 0.5, 0, 0],
							[5, 0.7, 0.0, 0, 0],
							[6, 0.7, 0.5, 0, 0]]
		actual = fetch_table_from_sql(self.dbname, "COMMUNITY_PARAMETERS")
		for i, each in enumerate(community_params):
			self.assertListEqual(each, actual[i])


class TestCantorPairing(unittest.TestCase):
	"""
	Tests that cantor pairing successfully creates unique numbers for a very large set of guilds and species
	"""
	def testCantorCreatesUniqueIds(self):
		"""
		Tests that the cantor pairing function creates unique ids for any given pair of numbers.
		Tests up to 1000 individuals in 1000 guilds
		"""
		unique_ids = set()
		for species in range(1000):
			for guild in range(1000):
				ref = cantor_pairing(species, guild)
				self.assertNotIn(ref, unique_ids)
				unique_ids.add(ref)

class TestMetacommunity(unittest.TestCase):
	"""
	Tests that metacommunities are correctly applied for edge cases.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Runs the default simulation and a the metacommunities to compare against.
		"""
		cls.c = Simulation()
		cls.c.set_simulation_params(seed=1, job_type=43, output_directory="output", min_speciation_rate=0.5,
								sigma=1, tau=2, deme=1, sample_size=1, max_time=100, infinite_landscape=False)
		cls.c.set_map("null", 10, 10)
		cls.c.finalise_setup()
		cls.c.run_coalescence()
		cls.t1 = CoalescenceTree(cls.c)
		cls.t1.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.5])
		cls.t1.apply_speciation()
		cls.c2 = Simulation()
		cls.c2.set_simulation_params(seed=1, job_type=44, output_directory="output", min_speciation_rate=0.5,
									sigma=1, tau=2, deme=1, sample_size=1, max_time=100, infinite_landscape=False)
		cls.c2.set_map("null", 10, 10)
		cls.c2.finalise_setup()
		cls.c2.run_coalescence()
		cls.t2 = CoalescenceTree(cls.c)
		cls.t2.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.5],
									 metacommunity_size = 1, metacommunity_speciation_rate=0.5)
		cls.t2.apply_speciation()
		cls.t3 = CoalescenceTree(cls.c)
		cls.t3.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.5],
									 metacommunity_size=1, metacommunity_speciation_rate=1.0)
		cls.t3.apply_speciation()
		cls.t4 = CoalescenceTree(cls.c)
		cls.t4.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.5],
									 metacommunity_size=1000000, metacommunity_speciation_rate=0.95)
		cls.t4.apply_speciation()

	def testSanityChecksMetacommunityApplication(self):
		"""
		Tests that the metacommunity application makes sense.
		"""
		self.assertEqual(self.t1.get_richness(), self.t4.get_richness(4))
		self.assertEqual(72, self.t4.get_richness(4))
		self.assertEqual(1, self.t2.get_richness(2))
		self.assertEqual(self.t2.get_richness(2), self.t3.get_richness(3))

	def testMetacommunityReferencesStorage(self):
		"""
		Tests that metacommunity references are correctly stored in the COMMUNITY_PARAMETERS table.
		"""
		community_dict1 = self.t2.get_community_parameters(1)
		community_dict2 = self.t2.get_community_parameters(2)
		community_dict3 = self.t2.get_community_parameters(3)
		community_dict4 = self.t2.get_community_parameters(4)
		comparison_dict1 = {"speciation_rate" : 0.5, "time" : 0.0, "fragments" : 0, "metacommunity_reference" : 0}
		comparison_dict2 = {"speciation_rate": 0.5, "time": 0.0, "fragments": 0, "metacommunity_reference": 1}
		comparison_dict3 = {"speciation_rate": 0.5, "time": 0.0, "fragments": 0, "metacommunity_reference": 2}
		comparison_dict4 = {"speciation_rate": 0.5, "time": 0.0, "fragments": 0, "metacommunity_reference": 3}
		self.assertDictEqual(comparison_dict1, community_dict1)
		self.assertDictEqual(comparison_dict2, community_dict2)
		self.assertDictEqual(comparison_dict3, community_dict3)
		self.assertDictEqual(comparison_dict4, community_dict4)

	def testMetacommunityParametersStorage(self):
		"""
		Tests that metacommunity parameters are stored correctly in the output simulation
		"""
		metacommunity_dict2 = self.t2.get_metacommunity_parameters(1)
		metacommunity_dict3 = self.t3.get_metacommunity_parameters(2)
		metacommunity_dict4 = self.t4.get_metacommunity_parameters(3)
		comparison_dict2 = {"speciation_rate" : 0.5, "metacommunity_size" : 1.0}
		comparison_dict3 = {"speciation_rate": 1.0, "metacommunity_size": 1.0}
		comparison_dict4 = {"speciation_rate": 0.95, "metacommunity_size": 1000000.0}
		self.assertDictEqual(comparison_dict2, metacommunity_dict2)
		self.assertDictEqual(comparison_dict3, metacommunity_dict3)
		self.assertDictEqual(comparison_dict4, metacommunity_dict4)

class TestSystemOperations(unittest.TestCase):
	"""
	Tests the functions associated with the system operations.
	"""
	def testFileExistence(self):
		"""
		Tests that the file existence checks work
		"""
		check_file_exists("null")
		check_file_exists("sample/null.tif")
		check_file_exists("system_operations.py")

	def testFileExistenceErrors(self):
		"""
		Tests that the correct errors are thrown when files don't exist.
		"""
		with self.assertRaises(IOError):
			check_file_exists("not_a_file.tif")
		with self.assertRaises(IOError):
			check_file_exists("sample/not_a_file.tif")
		with self.assertRaises(IOError):
			check_file_exists("sample/also_notta_tile")

	def testCheckDirectory(self):
		"""
		Verifies that the parent directory checks work correctly.
		"""
		with self.assertRaises(ValueError):
			check_parent("")
		with self.assertRaises(ValueError):
			check_parent(None)
		check_parent("sample/not_here.tif")
		check_parent("output/create_me/")
		check_parent("output/create_me_too/file_here.tif")
		self.assertTrue(os.path.exists("output/create_me/"))
		self.assertTrue(os.path.exists("output/create_me_too/"))

	def testFileLogger(self):
		"""
		Tests that the creation of a logger to file works correctly.
		"""
		logger = logging.Logger("temp")
		file_name = "output/log.txt"
		create_logger(logger, file=file_name)
		logger.warning("test output")
		with open(file_name, 'r') as f:
			s = f.readline()
			self.assertTrue("test output" in s)
		handlers = logger.handlers.copy()
		for handler in handlers:
			handler.close()
			logger.removeHandler(handler)

	def testCantorPairing(self):
		"""
		Tests that the cantor pairing produces the expected result
		"""
		self.assertEqual(cantor_pairing(10, 100), 6205)
		self.assertEqual(cantor_pairing(0, 1), 2)
		self.assertEqual(cantor_pairing(1, 0), 1)
		self.assertEqual(cantor_pairing(100000, 1000000), 605001550000)

	def testElegantPairing(self):
		"""
		Tests the elegant pairing produces the expected output
		"""
		self.assertEqual(elegant_pairing(10, 100), 10010)
		self.assertEqual(elegant_pairing(0, 1), 1)
		self.assertEqual(elegant_pairing(1, 0), 2)
		self.assertEqual(elegant_pairing(100000, 1000000), 1000000100000)

class TestHelper(unittest.TestCase):
	"""
	Tests the helper module, with functions for changing simulations between versions
	"""
	def testSimulationUpdating(self):
		"""
		Tests that simulation parameters are correctly updated between versions.
		"""
		old1 = "output/data_old1.db"
		old2 = "output/data_old2.db"
		shutil.copy("sample/data_old1.db", old1)
		shutil.copy("sample/data_old2.db", old2)
		with self.assertRaises(sqlite3.OperationalError):
			t = CoalescenceTree(old1, logging_level=logging.CRITICAL)
			t.get_simulation_parameters()["gen_since_pristine"]
		with self.assertRaises(sqlite3.OperationalError):
			t = CoalescenceTree(old2, logging_level=logging.CRITICAL)
			t.get_simulation_parameters()["habitat_change_rate"]
		update_parameter_names(old1)
		update_parameter_names(old2)
		t1 = CoalescenceTree(old1)
		t2 = CoalescenceTree(old2)
		self.assertEqual(t1.get_simulation_parameters()["gen_since_pristine"], 2.2)
		self.assertEqual(t2.get_simulation_parameters()["gen_since_pristine"], 2.2)
		self.assertEqual(t1.get_simulation_parameters()["habitat_change_rate"], 0.2)
		self.assertEqual(t2.get_simulation_parameters()["habitat_change_rate"], 0.2)

def main():
	"""
	Set the logging method, run the program compilation (if required) and test the install.

	.. note:: The working directory is changed to the package install location for the duration of this execution.
	:return:
	"""
	set_logging_method(logging_level=logging.CRITICAL, output=None)
	# make_all_compile()
	perform_checks()
	setUpModule()
	unittest.main()
	tearDownModule()


if __name__ == "__main__":
	main()
