"""

"""
import os
import shutil
import sqlite3
import unittest
import sys
import numpy as np
import random

from pycoalescence.coalescence_tree import CoalescenceTree, get_parameter_description
from setupTests import setUpAll, tearDownAll


def setUpModule():
	"""
	Creates the output directory and moves logging files
	"""
	setUpAll()
	t = CoalescenceTree("sample/sample.db")
	t.clear_calculations()

def tearDownModule():
	"""
	Removes the output directory
	"""
	tearDownAll()

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
					"gen_since_historical": "the number of generations that occur before the historical, or historic, state is reached",
					"dispersal_method": "the dispersal method used. Can be one of 'normal', 'norm-uniform' or 'fat-tail'.",
					"historical_fine_map": "the historical, or historic, coarse density map file location",
					"coarse_map_scale": "the scale of the coarse density map compared to the fine density map. 1 means equal density",
					"grid_x": "the simulated grid x dimension",
					"coarse_map_file": "the density map file location at the coarser resolution, covering a larger area",
					"min_num_species": "the minimum number of species known to exist (currently has no effect)",
					"historical_coarse_map": "the historical, or historic, coarse density map file location",
					"m_probability": "the probability of choosing from the uniform dispersal kernel in normal-uniform dispersal",
					"sigma": "the sigma dispersal value for normal, fat-tailed and normal-uniform dispersals",
					"deme": "the number of individuals inhabiting a cell at a map density of 1",
					"time_config_file": "will be 'set' if temporal sampling is used, 'null' otherwise",
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
					"landscape_type": "if false, landscapes have hard boundaries. Otherwise, can be infinite, with 1s everywhere, or tiled_coarse or tiled_fine for repeated units of tiled maps",
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


class TestCoalescenceTreeAnalyse(unittest.TestCase):
	"""
	Tests analysis is performed correctly
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""
		dst = "output/sampledb.db"
		if os.path.exists(dst):
			os.remove(dst)
		shutil.copyfile("sample/sample.db", dst)
		random.seed(2)
		cls.test = CoalescenceTree(dst)
		cls.test.clear_calculations()
		cls.test.import_comparison_data("sample/PlotBiodiversityMetrics.db")
		# cls.test.calculate_comparison_octaves(False)
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
		# pass

	def testComparisonDataNoExistError(self):
		c = CoalescenceTree("sample/sample.db")
		with self.assertRaises(IOError):
			c.import_comparison_data("sample/doesnotexist.db")

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

	@unittest.skipIf(sys.version[0] != '3', "Skipping python 3.x tests")
	def testModelFitting2(self):
		"""
		Tests that the goodness-of-fit calculations are correctly performed.
		"""
		random.seed(2)
		self.test.calculate_goodness_of_fit()
		self.assertAlmostEqual(self.test.get_goodness_of_fit(), 0.30140801329929373, places=6)
		self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_octaves(), 0.0680205429120108, places=6)
		self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_richness(), 0.9244977999898334, places=6)

	@unittest.skipIf(sys.version[0] == '3', "Skipping python 2.x tests")
	def testModelFitting3(self):
		"""
		Tests that the goodness-of-fit calculations are correctly performed.
		"""
		random.seed(2)
		self.test.calculate_goodness_of_fit()
		self.assertAlmostEqual(self.test.get_goodness_of_fit(), 0.30140801329929373, places=6)
		self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_octaves(), 0.0680205429120108, places=6)
		self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_richness(), 0.9244977999898334, places=6)

class TestCoalescenceTreeSpeciesDistances(unittest.TestCase):
	"""
	Tests analysis is performed correctly
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""
		dst = "output/sampledb.db"
		if os.path.exists(dst):
			os.remove(dst)
		shutil.copyfile("sample/sample.db", dst)
		cls.test = CoalescenceTree(dst)
		cls.test.clear_calculations()
		cls.test.import_comparison_data("sample/PlotBiodiversityMetrics.db")
		cls.test.calculate_species_distance_similarity()

	def testSpeciesDistanceSimilarity(self):
		"""
		Tests that the species distance similarity function works as intended.
		"""
		mean = self.test.cursor.execute(
			"SELECT value FROM BIODIVERSITY_METRICS WHERE community_reference == 1 AND "
			"metric == 'mean_distance_between_individuals'").fetchone()[0]
		self.assertAlmostEqual(mean, 5.423769507803121, places=5)
		species_distances = self.test.get_species_distance_similarity(community_reference=1)
		# for distance, similar in species_distances:
		# 	self.assertLessEqual(similar, dissimilar)
		self.assertListEqual(species_distances[0], [0, 11])
		self.assertListEqual(species_distances[1], [1, 274])
		self.assertListEqual(species_distances[2], [2, 289])

class TestCoalescenceTreeAnalyseIncorrectComparison(unittest.TestCase):
	"""
	Tests errors are raised correctly for incorrect comparison data.
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the Coalescence object test case.
		"""
		random.seed(10)
		dst = "output/sampledb.db"
		if os.path.exists(dst):
			os.remove(dst)
		shutil.copyfile("sample/sample.db", dst)
		cls.test = CoalescenceTree()
		cls.test.set_database(dst)
		cls.test.import_comparison_data("sample/PlotBiodiversityMetricsNoAlpha.db")
		cls.test.calculate_comparison_octaves(False)
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



class TestSimulationAnalysis(unittest.TestCase):
	"""
	Tests that the simulation can perform all required analyses, and that the correct errors are thrown if the object
	does not exist.
	"""

	@classmethod
	def setUpClass(cls):
		cls.tree = CoalescenceTree()
		cls.tree.set_database("sample/sample2.db")
		cls.tree.wipe_data()
		cls.tree.set_speciation_params(speciation_rates=[0.5, 0.7], record_spatial="T",
									   record_fragments="sample/FragmentsTest.csv",
									   sample_file="sample/SA_samplemaskINT.tif")
		cls.tree.apply()
		cls.tree.calculate_fragment_richness()
		cls.tree.calculate_fragment_octaves()
		np.random.seed(100)

	def testReadsFragmentsRichness(self):
		"""
		Tests that the fragment richness can be read correctly
		"""
		sim_params = self.tree.get_simulation_parameters()
		expected_params = dict(seed=9, job_type=1, output_dir='output', speciation_rate=0.5, sigma=2.828427, tau=2.0,
							   deme=1, sample_size=0.1, max_time=2.0, dispersal_relative_cost=1.0,
							   min_num_species=1, habitat_change_rate=0.0, gen_since_historical=200.0,
							   time_config_file='null', coarse_map_file='sample/SA_sample_coarse.tif',
							   coarse_map_x=35, coarse_map_y=41, coarse_map_x_offset=11, coarse_map_y_offset=14,
							   coarse_map_scale=1.0, fine_map_file='sample/SA_sample_fine.tif', fine_map_x=13,
							   fine_map_y=13, fine_map_x_offset=0, fine_map_y_offset=0,
							   sample_file='sample/SA_samplemaskINT.tif', grid_x=13, grid_y=13,
							   sample_x=13, sample_y=13, sample_x_offset=0, sample_y_offset=0,
							   historical_coarse_map='none', historical_fine_map='none', sim_complete=1,
							   dispersal_method='normal', m_probability=0.0, cutoff=0.0, landscape_type='closed',
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
		np.random.seed(100)
		self.assertEqual(13, self.tree.sample_landscape_richness(number_of_individuals=number_dict, n=1,
																 community_reference=2))
		self.assertAlmostEqual(99.9, self.tree.sample_landscape_richness(number_of_individuals=100, n=10,
																		 community_reference=1), places=3)

	def testRaisesSamplingErrors(self):
		number_dict = {"fragment1": 3000000, "fragment2": 10}
		with self.assertRaises(KeyError):
			self.assertEqual(13, self.tree.sample_landscape_richness(number_of_individuals=number_dict, n=1,
																	 community_reference=2))
		number_dict2 = {"fragment": 10, "fragment2": 10}
		with self.assertRaises(KeyError):
			self.assertEqual(13, self.tree.sample_landscape_richness(number_of_individuals=number_dict2, n=1,
																	 community_reference=2))
