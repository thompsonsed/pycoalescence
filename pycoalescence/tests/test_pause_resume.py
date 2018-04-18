import logging
import unittest

import os
import shutil

from pycoalescence import Simulation, CoalescenceTree
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

class TestSimulationPause(unittest.TestCase):
	"""
	Test a simple run on a landscape using sampling
	"""

	@classmethod
	def setUpClass(self):
		"""
		Sets up the Coalescence object test case.
		"""
		self.coal = Simulation(logging_level=30)
		self.coal2 = Simulation()
		self.tree2 = CoalescenceTree()
		self.coal.set_simulation_params(seed=10, job_type=6, output_directory="output", min_speciation_rate=0.05,
										sigma=2, tau=2, deme=1, sample_size=0.1, max_time=0,
										dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										dispersal_method="normal")
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=10, job_type=7, output_directory="output", min_speciation_rate=0.05,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0,
										 dispersal_method="normal")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null")
		self.tree2.apply_speciation()
		self.tree1 = CoalescenceTree()

	def testCanPause(self):
		"""
		Tests that simulations can pause execution and correctly store their state to the SQL database (for in-process
		analysis). Checks that the SQL database has correctly written the simulation parameters and that errors are
		thrown when one tries to connect to an incomplete simulation.
		"""
		tree2 = CoalescenceTree()
		with self.assertRaises(IOError):
			tree2.set_database(self.coal)
		actual_sim_parameters = dict(seed=10, job_type=6, output_dir='output', speciation_rate=0.05, sigma=2.0, tau=2.0,
									 deme=1, sample_size=0.1, max_time=0, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=0, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none", time_config_file="null")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none", time_config_file="null")
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
										 sample_file="null")
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


class TestSimulationPause2(unittest.TestCase):
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
										dispersal_method="normal", protracted=True,
										min_speciation_gen=0.0, max_speciation_gen=100)
		self.coal3 = Simulation(logging_level=logging.ERROR)
		self.coal3.set_simulation_params(seed=10, job_type=26, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0,
										 dispersal_method="normal", protracted=True,
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
										 min_num_species=1, habitat_change_rate=0,
										 dispersal_method="normal", protracted=True,
										 min_speciation_gen=0.0, max_speciation_gen=100)
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.set_speciation_rates([0.5])
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null")
		self.tree2.apply_speciation()
		self.tree1 = CoalescenceTree()

	def testCanResume2(self):
		"""
		Tests that simulations can resume execution by detecting the paused files
		"""
		self.tree1.set_database(self.coal3)
		actual_sim_parameters = dict(seed=10, job_type=26, output_dir='output', speciation_rate=0.5, sigma=2.0, tau=2.0,
									 deme=1, sample_size=0.1, max_time=10, dispersal_relative_cost=1.0,
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=1, min_speciation_gen=0.0,
									 max_speciation_gen=100.0, dispersal_map="none", time_config_file="null")
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
									  dispersal_method="normal", protracted=False,
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
										 sample_file="null")
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


class TestSimulationPause3(unittest.TestCase):
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
										dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								coarse_file="sample/SA_sample_coarse.tif")
		# self.coal.detect_map_dimensions()
		self.coal.finalise_setup()
		self.coal.run_coalescence()
		self.coal2.set_simulation_params(seed=10, job_type=17, output_directory="output", min_speciation_rate=0.5,
										 sigma=2, tau=2, deme=1, sample_size=0.1, max_time=10,
										 dispersal_relative_cost=1,
										 min_num_species=1, habitat_change_rate=0,
										 dispersal_method="normal")
		# self.coal.set_simulation_params(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT.tif", fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.set_speciation_rates([0.5])
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=0, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none", time_config_file="null")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none", time_config_file="null")
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
										 sample_file="null")
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


class TestSimulationPause4(unittest.TestCase):
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
										dispersal_method="normal")
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
										 min_num_species=1, habitat_change_rate=0,
										 dispersal_method="normal")
		self.coal2.set_map_files(sample_file="sample/SA_samplemaskINT spaced.tif",
								 fine_file="sample/SA_sample_fine.tif",
								 coarse_file="sample/SA_sample_coarse.tif")
		self.coal2.set_speciation_rates([0.5])
		self.coal2.finalise_setup()
		self.coal2.run_coalescence()
		self.tree2.set_database(self.coal2)
		self.tree2.set_speciation_params(record_spatial="T", record_fragments="F", speciation_rates=[0.6, 0.7],
										 sample_file="null")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT spaced.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=0, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none", time_config_file="null")
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
									 min_num_species=1, habitat_change_rate=0.0, gen_since_historical=0.0,
									 coarse_map_file='sample/SA_sample_coarse.tif',
									 coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
									 coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
									 fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
									 sample_file='sample/SA_samplemaskINT spaced.tif', grid_x=13, grid_y=13,
									 sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
									 historical_coarse_map='none', historical_fine_map='none',
									 sim_complete=1, dispersal_method='normal', m_probability=0.0, cutoff=0.0,
									 landscape_type='closed', protracted=0, min_speciation_gen=0.0,
									 max_speciation_gen=0.0, dispersal_map="none", time_config_file="null")
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
										 sample_file="null")
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