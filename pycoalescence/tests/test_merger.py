"""
Tests the Merger module for combining the outputs of multiple simulations
"""

import unittest

import os

from pycoalescence.sqlite_connection import fetch_table_from_sql
from pycoalescence import Merger
from setupTests import setUpAll, tearDownAll

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

class TestSimulationReadingViaMerger(unittest.TestCase):
	"""
	Tests that simulation can successfully read tables from a database.
	"""

	dbname = "output/mergers/combined1.db"

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
							   "set", "sample/SA_sample_coarse.tif", 35, 41, 11, 14, 1.0,
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
		cls.dbname = "output/mergers/combined2.db"
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
					  [91808, 4122, 1, 1, 2]]
		species_richness = fetch_table_from_sql(self.dbname, "SPECIES_ABUNDANCES")
		check_richness = [x for x in species_richness if x[0] == 238394531 or x[0] == 91808]
		for i, each in enumerate(abundances):
			self.assertListEqual(each, check_richness[i])

	def testSimulationParameters(self):
		"""
		Tests that the simulation parameters are correctly calculated in the merged database.
		"""
		sim_pars = [[6, 6, "output", 0.5, 4.0, 4.0, 1, 0.1, 10, 1.0, 1, 0.0, 200.0,
					 "set", "sample/SA_sample_coarse.tif", 35, 41, 11, 14, 1.0,
					 "sample/SA_sample_fine.tif", 13, 13, 0, 0, "null", 13, 13, 13, 13, 0, 0, "none", "none", 1,
					 "normal", 0.0, 0.0, 0, "closed", 0, 0.0, 0.0,
					 "none", 1, "sample/mergers/data_0_0.db"],
					[6, 6, "output", 0.5, 4.0, 4.0, 2, 0.1, 10, 1.0, 1, 0.0, 200.0, "set",
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
						'fine_map_x_offset': 0, 'fine_map_y': 13, 'fine_map_y_offset': 0, 'gen_since_historical': 200.0,
						'grid_x': 13, 'grid_y': 13, 'habitat_change_rate': 0.0, 'landscape_type': 'closed',
						'job_type': 6, 'm_probability': 0.0, 'max_speciation_gen': 0.0, 'max_time': 10,
						'min_num_species': 1, 'min_speciation_gen': 0.0, 'output_dir': 'output',
						'historical_coarse_map': 'none', 'historical_fine_map': 'none', 'protracted': 0,
						'sample_file': 'null', 'sample_size': 0.1, 'sample_x': 13, 'sample_x_offset': 0, 'sample_y': 13,
						'sample_y_offset': 0, 'seed': 6, 'sigma': 4.0, 'sim_complete': 1, 'speciation_rate': 0.5,
						'tau': 4.0, 'time_config_file': 'set'}
		output_pars2 = {'coarse_map_file': 'sample/SA_sample_coarse.tif', 'coarse_map_scale': 1.0, 'coarse_map_x': 35,
						'coarse_map_x_offset': 11, 'coarse_map_y': 41, 'coarse_map_y_offset': 14, 'cutoff': 0.0,
						'deme': 2, 'dispersal_map': 'none', 'dispersal_method': 'normal',
						'dispersal_relative_cost': 1.0, 'fine_map_file': 'sample/SA_sample_fine.tif', 'fine_map_x': 13,
						'fine_map_x_offset': 0, 'fine_map_y': 13, 'fine_map_y_offset': 0, 'gen_since_historical': 200.0,
						'grid_x': 13, 'grid_y': 13, 'habitat_change_rate': 0.0, 'landscape_type': 'closed',
						'job_type': 6, 'm_probability': 0.0, 'max_speciation_gen': 0.0, 'max_time': 10,
						'min_num_species': 1, 'min_speciation_gen': 0.0, 'output_dir': 'output',
						'historical_coarse_map': 'none', 'historical_fine_map': 'none', 'protracted': 0,
						'sample_file': 'null', 'sample_size': 0.1, 'sample_x': 13, 'sample_x_offset': 0, 'sample_y': 13,
						'sample_y_offset': 0, 'seed': 6, 'sigma': 4.0, 'sim_complete': 1, 'speciation_rate': 0.5,
						'tau': 4.0, 'time_config_file': 'set'}
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

class TestMergerInheritance(unittest.TestCase):
	"""
	Tests that the merger class correctly inherits from the CoalescenceTree class
	"""

	@classmethod
	def setUpClass(cls):
		cls.dbname = "output/mergers/combined3.db"
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

	def testMergerGetSpeciesRichness(self):
		"""
		Tests that species richness functions work properly.
		:return:
		"""
		self.assertEqual(self.merger.get_richness(1), 7288)
		self.assertEqual(self.merger.get_landscape_richness(1), 7288)
		self.assertEqual(self.merger.get_richness(2), 7286)
		self.assertEqual(self.merger.get_landscape_richness(2), 7286)


class TestMergerAnalysis(unittest.TestCase):
	"""
	Tests that the Merger can perform analysis in the same way as CoalescenceTree.
	"""

	@classmethod
	def setUpClass(cls):
		cls.dbname = "output/mergers/combined4.db"
		if os.path.exists(cls.dbname):
			os.remove(cls.dbname)
		cls.merger = Merger(database=cls.dbname)
		cls.merger.add_simulation("sample/mergers/data_0_0.db")
		cls.merger.add_simulation("sample/mergers/data_1_1.db")
		cls.merger.write()
		cls.merger.wipe_data()
		cls.merger.set_speciation_parameters(speciation_rates=[0.5, 0.6], record_spatial=False,
											 record_fragments="sample/FragmentsTest.csv")
		cls.merger.apply()
		cls.merger.calculate_fragment_richness()

	@classmethod
	def tearDownClass(cls):
		"""
		Removes the output database
		"""
		cls.merger.database.close()
		cls.merger.database = None
		if os.path.exists(cls.dbname):
			os.remove(cls.dbname)

	def testMergerAnalysisRichness(self):
		"""
		Tests that speciation rates can be applied.
		"""
		self.assertEqual(self.merger.get_richness(1), 7288)
		self.assertEqual(self.merger.get_richness(2), 7348)
		self.assertEqual(self.merger.get_landscape_richness(1), 7288)
		self.assertEqual(self.merger.get_landscape_richness(2), 7348)

	def testMergerAnalysisFragmentRichness(self):
		"""
		Tests that the analysis can be performed.
		"""
		self.assertEqual(self.merger.get_fragment_richness("fragment1", 1), 672)
		self.assertEqual(self.merger.get_fragment_richness("fragment2", 1), 1272)
