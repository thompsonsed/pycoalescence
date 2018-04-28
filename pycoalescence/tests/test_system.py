"""
Runs a variety of high-level tests to ensure that system integration works as intended, mostly utilising the Simulation
and CoalescenceTree
"""
import logging
import sqlite3
import unittest
import numpy as np
import os
import shutil
from shutil import rmtree
from pycoalescence.coalescence_tree import ApplySpecError
from pycoalescence import Simulation, CoalescenceTree, set_logging_method
from pycoalescence.simulation import NECSimError
from pycoalescence.tests.setup import setUpAll, tearDownAll


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


class TestSimulationNorm(unittest.TestCase):
	"""
	Tests the main coalescence set up routine by running some tiny simulations and checking that simulation parameters
	are passed properly.
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
										gen_since_historical=2, dispersal_method="normal")
		self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database("output/SQL_data/data_0_0.db")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=2.0,
									 time_config_file='null', coarse_map_file='null',
									 coarse_map_x=20, coarse_map_y=20, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='null', fine_map_x=10,
									 fine_map_y=10, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=10, grid_y=10, sample_x=10, sample_y=10,
									 sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='null', historical_fine_map='null',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationInfLand(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=2,
										dispersal_method="normal", m_prob=1,
										landscape_type=True)
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=2.0,
									 time_config_file='null', coarse_map_file='null',
									 coarse_map_x=20, coarse_map_y=20, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='null', fine_map_x=10,
									 fine_map_y=10, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=10, grid_y=10, sample_x=10, sample_y=10,
									 sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='null', historical_fine_map='null',
									 sim_complete=1, dispersal_method='normal', m_probability=1.0, cutoff=0.0,
									 landscape_type='infinite', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationFatInf(unittest.TestCase):
	"""
	Performs a basic simulation on an infinite landscape with a fat-tailed dispersal to checks outputs.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""
		cls.coal = Simulation()
		cls.tree = CoalescenceTree()
		cls.coal.set_simulation_params(1, 1, "output", 0.1, 4, 4, 1, 1.0, 2, dispersal_relative_cost=1,
									   min_num_species=1, habitat_change_rate=0,
									   dispersal_method="fat-tail", landscape_type=True)
		cls.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "none", "none")
		cls.coal.set_speciation_rates([0.1, 0.2])
		cls.coal.finalise_setup()
		cls.coal.run_coalescence()
		cls.tree.set_database("output/SQL_data/data_1_1.db")
		cls.tree.calculate_octaves()
		cls.tree.calculate_richness()

	def testSimParamsStored(self):
		"""
		Tests the full simulation setup, checking species richness is correct and species abundance calculations are
		correct.
		:return:
		"""
		params = self.tree.get_simulation_parameters()
		actual_sim_parameters = dict(seed=1, job_type=1, output_dir='output', speciation_rate=0.1, sigma=4.0, tau=4.0,
									 deme=1, sample_size=1.0, max_time=2.0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 time_config_file='null', coarse_map_file='null',
									 coarse_map_x=20, coarse_map_y=20, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='null', fine_map_x=10,
									 fine_map_y=10, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=10, grid_y=10, sample_x=10, sample_y=10, sample_x_offset=0,
									 sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='fat-tail', m_probability=0.0, cutoff=0.0,
									 landscape_type='infinite', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationTif(unittest.TestCase):
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
										min_num_species=1, cutoff=0.0)
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 time_config_file='null', coarse_map_file='none',
									 coarse_map_x=13, coarse_map_y=13, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationTiledInfinite(unittest.TestCase):
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
										min_num_species=1, cutoff=0.0, landscape_type="tiled_fine")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 time_config_file='null', coarse_map_file='none',
									 coarse_map_x=13, coarse_map_y=13, coarse_map_x_offset=0, coarse_map_y_offset=0,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='tiled_fine', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationTiledInfinite2(unittest.TestCase):
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
										min_num_species=1, cutoff=0.0, landscape_type="tiled_coarse")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal2 = Simulation()
		self.coal2.set_simulation_params(seed=1, job_type=33, output_directory="output", min_speciation_rate=0.1,
										 sigma=4, tau=4, deme=1, sample_size=0.1, max_time=2, dispersal_relative_cost=1,
										 min_num_species=1, cutoff=0.0, landscape_type="closed")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='tiled_coarse', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationProbabilityActionMap(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										cutoff=0.0, landscape_type="closed")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								reproduction_map="sample/SA_sample_reproduction.tif")
		self.coal.set_speciation_rates([0.1, 0.2])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2 = Simulation()
		self.tree2 = CoalescenceTree()
		self.coal2.set_simulation_params(seed=1, job_type=35, output_directory="output", min_speciation_rate=0.1,
										 sigma=4, tau=4, deme=1, sample_size=0.1, max_time=2, dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										 cutoff=0.0, landscape_type="closed")
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
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								cutoff=0.0, landscape_type="closed")
		c.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
						reproduction_map="sample/SA_sample_reproduction_invalid.tif")
		c.finalise_setup()
		with self.assertRaises(NECSimError):
			c.run_coalescence()
# pass


class TestSimulationTifBytes(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										cutoff=0.0)
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


class TestSimulationTifCoarse(unittest.TestCase):
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
										min_num_species=1, dispersal_method="fat-tail")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='fat-tail', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationNonSpatial(unittest.TestCase):
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


class TestSimulationSampling(unittest.TestCase):
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
									   min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
									   dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		cls.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							   coarse_file="sample/SA_sample_coarse.tif")
		cls.coal.set_speciation_rates([0.5, 0.7])
		cls.coal.finalise_setup()
		cls.coal.run_coalescence()
		cls.tree.set_database("output/SQL_data/data_8_6.db")
		cls.tree.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
									   sample_file="null", times=cls.coal.time_config_file)
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


class TestCoalSampling2(unittest.TestCase):
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

class TestCoalSampling3(unittest.TestCase):
	"""
	Sample run with test cases to make sure the sample map relative sampling is taken into account, and the offsets
	from the grid are correctly applied.
	"""

	@classmethod
	def setUpClass(cls):
		cls.coal = Simulation(logging_level=logging.CRITICAL)
		cls.coal.set_simulation_params(seed=9, job_type=8, output_directory="output", min_speciation_rate=0.5,
									   sigma=4, deme=1, sample_size=0.1, max_time=2, uses_spatial_sampling=True)
		cls.coal.set_map_files(sample_file="sample/null_sample.tif", fine_file="sample/SA_sample_coarse.tif")
		cls.coal.grid.x_size = 2
		cls.coal.grid.y_size = 2
		cls.coal.sample_map.x_offset = 4
		cls.coal.sample_map.y_offset = 4
		cls.coal.grid.file_name = "set"
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
		self.assertEqual(701, self.tree.get_number_individuals())
		self.assertEqual(169, self.tree.get_number_individuals(fragment="fragment1"))
		self.assertEqual(69, self.tree.get_number_individuals(fragment="fragment2"))


class TestCoalSampling4(unittest.TestCase):
	"""
	Sample run with test cases to make sure the sample map relative sampling is taken into account, and the offsets
	from the grid are correctly applied.
	"""

	@classmethod
	def setUpClass(cls):
		cls.coal = Simulation(logging_level=logging.CRITICAL)
		cls.coal.set_simulation_params(seed=10, job_type=8, output_directory="output", min_speciation_rate=0.5,
									   sigma=4, deme=1, sample_size=1, max_time=2, uses_spatial_sampling=False)
		cls.coal.set_map_files(sample_file="sample/null_sample.tif", fine_file="sample/SA_fine_expanded.tif",
							   coarse_file="sample/SA_coarse_expanded.tif")
		cls.coal.grid.x_size = 2
		cls.coal.grid.y_size = 2
		cls.coal.sample_map.x_offset = 4
		cls.coal.sample_map.y_offset = 4
		cls.coal.grid.file_name = "set"
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
		self.assertEqual(55, self.tree.get_number_individuals())
		self.assertEqual(6, self.tree.get_number_individuals(fragment="fragment1"))
		self.assertEqual(7, self.tree.get_number_individuals(fragment="fragment2"))


class TestSimulationNullLandscape(unittest.TestCase):
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


class TestSimulationComplexRun(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0.0,
										dispersal_method="normal", landscape_type=False)
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
										sample_file="null", times=[0.0, 0.5])
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 time_config_file='set',
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0, sample_file='null',
									 grid_x=13, grid_y=13, sample_x=13, sample_y=13, sample_x_offset=0,
									 sample_y_offset=0, historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
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


class TestSimulationComplexRun2(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										dispersal_method="normal")
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
										sample_file="null", times=[0.0, 1.0])
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


class TestSimulationComplexRun3(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										dispersal_method="normal")
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
										sample_file="null", times=[0.0, 1.0])
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


class TestSimulationComplexRun4(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										dispersal_method="norm-uniform", m_prob=10 ** -8,
										cutoff=160)
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.set_speciation_rates([0.5])
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.tree.set_database(self.coal)
		self.tree.set_speciation_params(record_spatial=True, record_fragments=False, speciation_rates=[0.6, 0.7],
										sample_file="null")
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


class TestSimulationSimple(unittest.TestCase):
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


class TestSimulationApplySpeciation(unittest.TestCase):
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
									   min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
									   )
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
									sample_file="null", times="null")

	def testRaisesErrorWhenNoSampleMask(self):
		"""
		Tests that an error is raised when the samplemask is null and record_fragments is True
		"""
		t = CoalescenceTree(self.coal)
		with self.assertRaises(ValueError):
			t.set_speciation_params(record_spatial="T", record_fragments="T", speciation_rates=[0.5, 0.7],
									sample_file="null", times="null")

	def testRaisesErrorWhenSpecNotDouble(self):
		t = CoalescenceTree(self.coal)
		t.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=["notdouble"],
								sample_file="null", times="null")
		with self.assertRaises(TypeError):
			t.apply_speciation()

	def testRaisesErrorWhenSpecNotList(self):
		t = CoalescenceTree(self.coal)
		t.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates="string",
								sample_file="null", times="null")
		with self.assertRaises(TypeError):
			t.apply_speciation()


class TestSimulationFattailVersionsMatch(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										dispersal_method="fat-tail", landscape_type=True)
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=1, job_type=14, output_directory="output", min_speciation_rate=0.1,
										 sigma=2.0, tau=-3.0, deme=1, sample_size=0.1, max_time=2,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										 dispersal_method="fat-tail-old",
										 landscape_type=True)
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.detect_map_dimensions()
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree1.set_database(self.coal)
		self.tree1.calculate_richness()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.1],
										 sample_file="null", times="null")
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


class TestSimulationNormalMatchesFatTailedExtreme(unittest.TestCase):
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
										min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										dispersal_method="normal", landscape_type=True)
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=1, job_type=16, output_directory="output", min_speciation_rate=0.01,
										 sigma=2, tau=-4, deme=1, sample_size=0.1, max_time=3,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										 dispersal_method="normal", landscape_type=True)
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.detect_map_dimensions()
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		# self.coal.set_speciation_rates([0.5, 0.7])
		self.tree1.set_database(self.coal)
		self.tree1.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.01],
										 sample_file="null", times="null")
		# self.tree1.apply_speciation()
		self.tree1.calculate_richness()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.01],
										 sample_file="null", times="null")
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


class TestSimulationPaleoTime(unittest.TestCase):
	"""
	Tests that simulations across paleo time do not cause any problems, i.e. sample times being extremely far apart does
	not create any issues.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=30)
		self.tree = CoalescenceTree()
		self.coal.set_simulation_params(1, 28, "output", 0.1, 4, 4, deme=1, sample_size=1.0, max_time=2,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										gen_since_historical=2, dispersal_method="normal")
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


class TestSimulationProtractedSanityChecks(unittest.TestCase):
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
										 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										 dispersal_method="normal", protracted=True,
										 min_speciation_gen=0, max_speciation_gen=2)
		self.coal2.set_simulation_params(seed=1, job_type=20, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										 dispersal_method="normal", protracted=True,
										 min_speciation_gen=10, max_speciation_gen=50)
		self.coal3.set_simulation_params(seed=1, job_type=21, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										 dispersal_method="normal", protracted=True,
										 min_speciation_gen=10, max_speciation_gen=20)
		self.coal4.set_simulation_params(seed=1, job_type=22, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
										 dispersal_method="normal", protracted=False)
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
										 sample_file="null")
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null")
		self.tree3.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null")
		self.tree4.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null")
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


class TestSimulationDispersalMaps(unittest.TestCase):
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
									 min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
									 )
		self.c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_coarse.tif",
							 dispersal_map="sample/dispersal_fine.tif")
		self.c.finalise_setup()
		self.c.run_coalescence()

	def testDispersalSimulation(self):
		"""
		Tests that running a simulation with a dispersal map produces the expected output.
		"""
		self.assertEqual(self.c.get_richness(1), 737)

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
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								)
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
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								)
		with self.assertRaises(ValueError):
			c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
							dispersal_map="sample/dispersal_fine.tif")

class TestSimulationDispersalMapsSumming(unittest.TestCase):
	"""
	Tests the dispersal maps to ensure that values are read properly, and using dispersal maps for simulations works as
	intended, including modifying the dispersal map to cumulative probabilities.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the objects for running coalescence simulations on dispersal maps.
		"""
		cls.c = Simulation(logging_level=logging.CRITICAL)
		cls.c.set_simulation_params(seed=2, job_type=32, output_directory="output", min_speciation_rate=0.5,
									sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
									min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
									)
		cls.c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_coarse.tif",
							dispersal_map="sample/dispersal_fine_cumulative.tif")
		cls.c.finalise_setup()
		cls.c.run_coalescence()

	def testDispersalSimulation(self):
		"""
		Tests that running a simulation with a dispersal map produces the expected output.
		"""
		self.assertEqual(self.c.get_richness(1), 1167)

	def testDispersalParamStorage(self):
		"""
		Tests that the dispersal parameters are stored correctly
		"""
		t = CoalescenceTree(self.c)
		self.assertEqual(t.get_simulation_parameters()['dispersal_map'], "sample/dispersal_fine_cumulative.tif")

	def testRaisesErrorValueMismatch(self):
		"""
		Tests that an error is raised when dispersal is possible to a cell with 0 density.
		"""
		c = Simulation(logging_level=logging.CRITICAL)
		c.set_simulation_params(seed=4, job_type=32, output_directory="output", min_speciation_rate=0.5,
								sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200)
		c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_coarse_zeros.tif",
						dispersal_map="sample/dispersal_fine_cumulative.tif")
		c.finalise_setup()
		with self.assertRaises(NECSimError):
			c.run_coalescence()

class TestSimulationDispersalMapsNoData(unittest.TestCase):
	"""
	Tests the dispersal maps to ensure that values are read properly, and using dispersal maps for simulations works as
	intended, including modifying the dispersal map to cumulative probabilities.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the objects for running coalescence simulations on dispersal maps.
		"""
		cls.c = Simulation(logging_level=logging.CRITICAL)
		cls.c.set_simulation_params(seed=3, job_type=32, output_directory="output", min_speciation_rate=0.5,
									sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1,
									min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
									)
		cls.c.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_coarse.tif",
							dispersal_map="sample/dispersal_fine_nodata.tif")
		cls.c.finalise_setup()
		cls.c.run_coalescence()

	def testDispersalSimulation(self):
		"""
		Tests that running a simulation with a dispersal map produces the expected output.
		"""
		self.assertEqual(self.c.get_richness(1), 730)

	def testDispersalParamStorage(self):
		"""
		Tests that the dispersal parameters are stored correctly
		"""
		t = CoalescenceTree(self.c)
		self.assertEqual(t.get_simulation_parameters()['dispersal_map'], "sample/dispersal_fine_nodata.tif")


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
									min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
									landscape_type=False)
		cls.c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
		cls.c.add_sample_time(1.0)
		try:
			cls.c.optimise_ram(ram_limit=0.03)
			cls.c.finalise_setup()
			cls.c.run_coalescence()
		except MemoryError as me:
			cls.fail(msg="Cannot run a larger scale simulation. This should require around 500MB of RAM. If your computer"
						  "does not have these requirements, ignore this failure: {}".format(me))

	def testExcessiveRamUsage(self):
		"""
		Tests that an exception is raised if there is not enough RAM to complete the simulation.
		"""
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=36, output_directory="output", min_speciation_rate=0.5,
								sigma=2, tau=2, deme=100000000000, sample_size=0.1, max_time=10,
								dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								)
		c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
		with self.assertRaises(MemoryError):
			c.optimise_ram(ram_limit=16)

	def testGridOffsetApplyingSpeciation(self):
		"""
		Tests that additional speciation rates are correctly applied when using an offsetted grid
		"""
		t = CoalescenceTree(self.c)
		t.set_speciation_params(record_spatial="T", record_fragments="sample/FragmentsTest2.csv",
								speciation_rates=[0.6, 0.7], sample_file="null")
		t.apply_speciation()
		t.calculate_fragment_richness()
		self.assertEqual(t.get_fragment_richness(fragment="fragment2", reference=3), 30)
		self.assertEqual(t.get_fragment_richness(fragment="fragment1", reference=3), 30)

	def testOffsetsStoredCorrectly(self):
		self.assertEqual(self.c.sample_map.x_offset, 630)
		self.assertEqual(self.c.sample_map.y_offset, 630)
		self.assertEqual(self.c.grid.x_size, 39)
		self.assertEqual(self.c.grid.y_size, 39)
		self.assertEqual(self.c.grid.file_name, "set")

	def testOffsetsOutOfBoundsDetection(self):
		"""
		Tests that offsets are not set if they are out of bounds of the main simulation.
		"""
		sim = Simulation()
		sim.set_simulation_params(seed=11, job_type=36, output_directory="output", min_speciation_rate=0.5,
								  sigma=2, tau=2, deme=1, sample_size=0.01, max_time=100,
								  dispersal_relative_cost=1,
								  min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								  landscape_type=False)
		sim.set_map_files(sample_file="null", fine_file="sample/SA_sample.tif")
		sim.optimise_ram(ram_limit=10000)
		self.assertEqual(sim.fine_map.x_size, sim.sample_map.x_size)
		self.assertEqual(sim.fine_map.y_size, sim.sample_map.y_size)
		self.assertEqual(0, sim.sample_map.x_offset)
		self.assertEqual(0, sim.sample_map.y_offset)
		self.assertEqual(sim.fine_map.x_size, sim.grid.x_size)
		self.assertEqual(sim.fine_map.y_size, sim.grid.y_size)
		self.assertEqual("null", sim.grid.file_name)
		sim.finalise_setup()
		sim.run_coalescence()

	def testExcessiveRamReallocation(self):
		"""
		Tests that in a system with excessive RAM usage, the map file structure is rearranged for lower performance,
		but optimal RAM usage.
		"""
		self.assertEqual(self.c.get_richness(1), 1769)
		self.assertEqual(self.c.get_richness(2), 1769)

	def testSingleLargeRun(self):
		"""
		Tests a single run with a huge number of individuals in two cells
		"""
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=37, output_directory="output", min_speciation_rate=0.95,
								sigma=1, tau=2, deme=70000, sample_size=1, max_time=100, dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200,
								landscape_type=False)
		c.set_map_parameters(sample_file="null", sample_x=2, sample_y=1, fine_file="null",
							 fine_x=2, fine_y=1, fine_x_offset=0, fine_y_offset=0,
							 coarse_file="none", coarse_x=2, coarse_y=1, coarse_x_offset=0, coarse_y_offset=0,
							 coarse_scale=1.0, historical_fine_map="none", historical_coarse_map="none")
		c.finalise_setup()
		c.run_coalescence()
		self.assertEqual(c.get_richness(1), 136400)

	def testReadWriteSaveState(self):
		saved_state = self.c.get_optimised_solution()
		c = Simulation()
		c.set_simulation_params(seed=1, job_type=36, output_directory="output", min_speciation_rate=0.5,
								sigma=2, tau=2, deme=100000000000, sample_size=0.1, max_time=10,
								dispersal_relative_cost=1,
								min_num_species=1, habitat_change_rate=0, gen_since_historical=200)
		c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
		c.set_optimised_solution(saved_state)
		self.assertEqual(c.sample_map.x_offset, 630)
		self.assertEqual(c.sample_map.y_offset, 630)
		self.assertEqual(c.grid.x_size, 39)
		self.assertEqual(c.grid.y_size, 39)
		self.assertEqual(c.grid.file_name, "set")


class TestSimulationMetacommunity(unittest.TestCase):
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
									sigma=1, tau=2, deme=1, sample_size=1, max_time=100, landscape_type=False)
		cls.c.set_map("null", 10, 10)
		cls.c.finalise_setup()
		cls.c.run_coalescence()
		cls.t1 = CoalescenceTree(cls.c)
		cls.t1.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.5])
		cls.t1.apply_speciation()
		cls.c2 = Simulation()
		cls.c2.set_simulation_params(seed=1, job_type=44, output_directory="output", min_speciation_rate=0.5,
									 sigma=1, tau=2, deme=1, sample_size=1, max_time=100, landscape_type=False)
		cls.c2.set_map("null", 10, 10)
		cls.c2.finalise_setup()
		cls.c2.run_coalescence()
		cls.t2 = CoalescenceTree(cls.c)
		cls.t2.set_speciation_params(record_spatial=False, record_fragments=False, speciation_rates=[0.5],
									 metacommunity_size=1, metacommunity_speciation_rate=0.5)
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
		comparison_dict1 = {"speciation_rate": 0.5, "time": 0.0, "fragments": 0, "metacommunity_reference": 0}
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
		comparison_dict2 = {"speciation_rate": 0.5, "metacommunity_size": 1.0}
		comparison_dict3 = {"speciation_rate": 1.0, "metacommunity_size": 1.0}
		comparison_dict4 = {"speciation_rate": 0.95, "metacommunity_size": 1000000.0}
		self.assertDictEqual(comparison_dict2, metacommunity_dict2)
		self.assertDictEqual(comparison_dict3, metacommunity_dict3)
		self.assertDictEqual(comparison_dict4, metacommunity_dict4)
