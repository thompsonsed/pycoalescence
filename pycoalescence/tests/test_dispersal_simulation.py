import logging
import unittest
import math

# try:
# 	import necsim
# 	NECSimError = necsim.libnecsim.NECSimError
# except ImportError:
from pycoalescence.necsim.libnecsim import NECSimError as nse
from pycoalescence.dispersal_simulation import DispersalSimulation
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


class TestDispersalSimulation(unittest.TestCase):
	"""
	Tests the dispersal simulation methods contained in Map
	"""

	@classmethod
	def setUpClass(cls):
		"""
		Sets up the class by running the dispersal simulations for later reference.
		"""
		cls.m = DispersalSimulation(logging_level=logging.CRITICAL)
		cls.m.set_map_files("sample/SA_sample_fine.tif", )
		cls.m.set_simulation_parameters(number_repeats=100, output_database="output/sim_pars_test4.db", seed=2,
										sigma=2, landscape_type="tiled_fine")
		cls.m.run_mean_dispersal()
		cls.m.set_simulation_parameters(number_repeats=100, seed=2, sigma=2, landscape_type="tiled_fine")
		cls.m.run_mean_dispersal()
		cls.m.set_simulation_parameters(number_repeats=100, seed=4, sigma=3, tau=1, landscape_type="tiled_fine",
										dispersal_method="fat-tail")
		cls.m.run_mean_dispersal()
		cls.m.set_simulation_parameters(number_repeats=100, number_steps=10, seed=2, sigma=2,
										landscape_type="tiled_fine")
		cls.m.run_mean_distance_travelled()
		cls.m.set_simulation_parameters(number_repeats=200, number_steps=10, seed=2, sigma=5,
										landscape_type="tiled_fine")
		cls.m.run_mean_distance_travelled()
		cls.m.set_simulation_parameters(number_repeats=100, number_steps=20, seed=5, sigma=2,
										landscape_type="tiled_fine")
		cls.m.run_mean_distance_travelled()

	def testRaisesIOError(self):
		"""
		Tests that an IOerror is raised when the output database doesn't exist
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.dispersal_database = "doesnotexist.db"
		with self.assertRaises(IOError):
			m.get_mean_dispersal()

	def testRaisesValueErrorExistance(self):
		"""
		Tests that a value error is raised when dispersal_database does not exist
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		with self.assertRaises(IOError):
			m.get_mean_dispersal()

	def testRaisesValueErrorNullNotSet(self):
		"""
		Tests that a ValueError is raised when the map file is "null" but dimensions have not been manually set.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		with self.assertRaises(ValueError):
			m.set_simulation_parameters(number_repeats=10000, output_database="output/normaldispersal.db", seed=1)
			m.set_map_files("null")

	def testRaisesNECSimError(self):
		"""
		Tests that a dispersal.Error is raised when incorrect dispersal method is provided.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		with self.assertRaises(nse):
			m.set_simulation_parameters(number_repeats=10000, output_database="output/emptydb.db", seed=1,
										dispersal_method="notamethod")
			m.set_map_files("sample/SA_sample_fine.tif", )
			try:
				m.run_mean_dispersal()
			except Exception as e:
				raise e

	def testDispersalNullOutputs(self):
		"""
		Tests that the dispersal simulations accurately generate the correct distance distribution for null landscapes.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map("null", 10, 10)
		m.set_simulation_parameters(number_repeats=10000, output_database="output/normaldispersal1.db", seed=2,
									sigma=10, landscape_type="infinite", restrict_self=False)
		m.run_mean_dispersal()
		self.assertAlmostEqual(m.get_mean_dispersal(), 10 * (3.14 ** 0.5) / 2 ** 0.5, places=2)

	def testLandscapeTypesMatch(self):
		"""
		Tests that a null landscape with tiled_fine matches a null landscape with infinite
		"""
		m1 = DispersalSimulation(logging_level=logging.CRITICAL)
		m1.set_map("null", 10, 10)
		m1.set_simulation_parameters(number_repeats=100000, output_database="output/normaldispersal2.db", seed=2,
									 sigma=2, landscape_type="infinite", restrict_self=False)
		m1.run_mean_dispersal()
		m2 = DispersalSimulation(logging_level=logging.CRITICAL)
		m2.set_map("null", 10, 10)
		m2.set_simulation_parameters(number_repeats=100000, output_database="output/normaldispersal3.db", seed=2,
									 sigma=2, landscape_type="tiled_fine", restrict_self=False)
		m2.run_mean_dispersal()
		self.assertEqual(m2.get_mean_dispersal(), m1.get_mean_dispersal())

	def testDispersalMapOutputs(self):
		"""
		Tests that the dispersal simulations work as intended for real maps.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map("sample/SA_sample_fine.tif")
		m.set_simulation_parameters(number_repeats=10000, output_database="output/realdispersal.db", seed=1,
									sigma=1, landscape_type="tiled_fine")
		m.run_mean_dispersal()
		self.assertAlmostEqual(1.2689283170972379, m.get_mean_dispersal(), places=4)

	def testDispersalDistanceTravelled(self):
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map("sample/SA_sample_fine.tif")
		m.set_simulation_parameters(number_repeats=100, number_steps=10, output_database="output/sim_pars_test2.db",
									seed=2, sigma=1, landscape_type="tiled_fine")
		m.run_mean_distance_travelled()
		self.assertAlmostEqual(4.076, m.get_mean_distance_travelled(), places=3)

	def testDispersalSimulationParametersStoredCorrectly(self):
		"""
		Tests that simulation parameters are stored correctly in the database.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map("sample/SA_sample_fine.tif")
		m.set_simulation_parameters(number_repeats=100, output_database="output/sim_pars_test1.db", seed=1,
									sigma=1, landscape_type="tiled_fine")
		m.run_mean_dispersal()
		m.update_parameters(sigma=2, number_steps=10, seed=2)
		m.run_mean_distance_travelled()
		main_dict = m.get_database_parameters()
		comparison_dict = {
			1: {
				"simulation_type": "DISPERSAL_DISTANCES", "sigma": 1, "tau": 1, "cutoff": 100, "m_prob": 1.0,
				"dispersal_method": "normal", "map_file": "sample/SA_sample_fine.tif", "seed": 1, "number_steps": 1,
				"number_repeats": 100

			},
			2: {
				"simulation_type": "DISTANCES_TRAVELLED", "sigma": 2, "tau": 1, "cutoff": 100.0, "m_prob": 1.0,
				"dispersal_method": "normal", "map_file": "sample/SA_sample_fine.tif", "seed": 2, "number_steps": 10,
				"number_repeats": 100
			}
		}
		for key in main_dict.keys():
			for inner_key in main_dict[key].keys():
				self.assertEqual(main_dict[key][inner_key], comparison_dict[key][inner_key],
								 msg="Error in {}, {} != {}".format(inner_key, main_dict[key][inner_key],
																	comparison_dict[key][inner_key]))

	def testMultipleSimulationsAverages(self):
		"""
		Tests that with multiple simulations, the averages are outputted correctly.
		"""

		self.assertAlmostEqual(2.4728978017662637, self.m.get_mean_dispersal(parameter_reference=2))
		self.assertAlmostEqual(27.867571579115666, self.m.get_mean_dispersal(parameter_reference=3))
		self.assertAlmostEqual(7.943272579513353, self.m.get_mean_distance_travelled(parameter_reference=4))
		self.assertAlmostEqual(19.515339089433237, self.m.get_mean_distance_travelled(parameter_reference=5))

	def testStandardDeviationDistances(self):
		"""
		Tests that the standard deviation is correctly returned from the simulated database
		"""
		self.assertAlmostEqual(1.5410309737379024, self.m.get_stdev_dispersal(parameter_reference=1))
		self.assertAlmostEqual(1.5410309737379024, self.m.get_stdev_dispersal(parameter_reference=2))
		self.assertAlmostEqual(4.1790454325780342, self.m.get_stdev_distance_travelled(parameter_reference=4))
		self.assertAlmostEqual(10.155370019080506, self.m.get_stdev_distance_travelled(parameter_reference=5))

	def testDatabaseReferences(self):
		"""
		Tests that the database parameters are stored and returned correctly.
		"""
		self.assertEqual([x for x in range(1, 7)], self.m.get_database_references())
		self.assertEqual( {"simulation_type": "DISPERSAL_DISTANCES", "sigma": 2,
						   "tau": 1, "m_prob": 1.0, "cutoff": 100.0,
						   "dispersal_method": "normal",
						   "map_file": "sample/SA_sample_fine.tif",
						   "seed": 2, "number_steps": 1,
						   "number_repeats": 100}, self.m.get_database_parameters()[1],)

	def testDispersalMapReading(self):
		"""
		Tests that dispersal simulations are correctly read from a completed simulation
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map("sample/SA_sample_fine.tif")
		m.set_simulation_parameters(number_repeats=10000, output_database="output/realdispersal2.db", seed=1,
									sigma=1, landscape_type="tiled_fine")
		m.run_mean_dispersal()
		m2 = DispersalSimulation(dispersal_db=m.dispersal_database, logging_level=logging.CRITICAL)
		self.assertAlmostEqual(1.2689283170972379, m2.get_mean_dispersal(), places=4)
		m3 = DispersalSimulation(dispersal_db=m, logging_level=logging.CRITICAL)
		self.assertAlmostEqual(1.2689283170972379, m3.get_mean_dispersal(), places=4)

	def testAlternativeMapFileSetting(self):
		m = DispersalSimulation(file="sample/SA_sample_fine.tif", logging_level=logging.CRITICAL)
		if m.fine_map.file_name is None:
			self.fail("File name not correctly set.")
		m.set_simulation_parameters(number_steps=10, number_repeats=10, output_database="output/realdispersal3.db",
									sigma=1, landscape_type="tiled_fine", seed=1)
		m.run_mean_distance_travelled()
		m.run_mean_dispersal()
		with self.assertRaises(ValueError):
			m.get_mean_dispersal()
		self.assertAlmostEqual(1.4892922, m.get_mean_dispersal(parameter_reference=2), places=4)

	def testParameterUpdating(self):
		"""
		Tests that a simulation can be run properly with updating parameters in between.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map("sample/SA_sample_fine.tif")
		m.set_simulation_parameters(number_repeats=100, output_database="output/realdispersal4.db", seed=1,
									sigma=1, landscape_type="tiled_fine")
		m.run_mean_dispersal()
		m.update_parameters(number_repeats=6, sigma=10)
		m.run_mean_dispersal()
		m.update_parameters(dispersal_method="fat-tail", number_steps=10)
		m.run_mean_distance_travelled()
		expected_params = {1: {"simulation_type": "DISPERSAL_DISTANCES", "sigma": 1.0,
							   "tau": 1.0, "m_prob": 1.0, "cutoff": 100.0, "dispersal_method": "normal",
							   "map_file": "sample/SA_sample_fine.tif", "seed": 1,
							   "number_steps": 1, "number_repeats": 100},
						   2: {"simulation_type": "DISPERSAL_DISTANCES", "sigma": 10.0,
							   "tau": 1.0, "m_prob": 1.0, "cutoff": 100.0, "dispersal_method": "normal",
							   "map_file": "sample/SA_sample_fine.tif", "seed": 1,
							   "number_steps": 1, "number_repeats": 6},
						   3: {"simulation_type": "DISTANCES_TRAVELLED", "sigma": 10.0,
							   "tau": 1.0, "m_prob": 1.0, "cutoff": 100.0, "dispersal_method": "fat-tail",
							   "map_file": "sample/SA_sample_fine.tif", "seed": 1,
							   "number_steps": 10, "number_repeats": 6}
						   }
		actual_params = m.get_database_parameters()
		for key in expected_params.keys():
			self.assertEqual(expected_params[key], actual_params[key])
		self.assertAlmostEqual(1.287133430, m.get_mean_dispersal(parameter_reference=1), places=4)
		self.assertAlmostEqual(15.233920, m.get_mean_dispersal(parameter_reference=2), places=4)
		self.assertAlmostEqual(467.58323, m.get_mean_distance_travelled(parameter_reference=3), places=4)


	def testDispersalWithCoarse(self):
		"""Tests a dispersal simulation using a coarse and fine map."""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map_files(fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif")
		m.set_simulation_parameters(number_repeats=100, output_database="output/realdispersal5.db", seed=1,
									sigma=1, landscape_type="tiled_fine")
		m.run_mean_dispersal()
		self.assertAlmostEqual(1.28034, m.get_mean_dispersal(parameter_reference=1), places=4)

	def testDispersalWithSample(self):
		"""Tests a dispersal simulation using a sample and fine map."""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map_files(fine_file="sample/SA_fine_expanded.tif", sample_file="sample/SA_sample_fine.tif")
		m.set_simulation_parameters(number_repeats=100, output_database="output/realdispersal6.db", seed=1,
									sigma=1, landscape_type="closed")
		m.run_mean_dispersal()
		self.assertAlmostEqual(0.9636800, m.get_mean_dispersal(parameter_reference=1), places=4)

	def testApplyingMultipleNumberSteps(self):
		"""Tests running a single simulation with multiple number of steps at once."""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map_files(fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif")
		m.set_simulation_parameters(number_repeats=100, output_database="output/realdispersal7.db", seed=1,
									sigma=1, landscape_type="tiled_fine", number_steps=[10, 20, 30])
		m.run_mean_distance_travelled()
		m.update_parameters(number_steps=[40, 50, 60])
		m.run_mean_distance_travelled()
		for k, v in [(1, 10), (2, 20), (3, 30), (4, 40), (5, 50), (6, 60)]:
			self.assertEqual(v, m.get_database_parameters()[k]["number_steps"])
		self.assertAlmostEqual(3.83501655, m.get_mean_distance_travelled(parameter_reference=1), places=6)
		self.assertAlmostEqual(5.250587979, m.get_mean_distance_travelled(parameter_reference=2), places=6)
		self.assertAlmostEqual(6.83168503847, m.get_mean_distance_travelled(parameter_reference=3), places=6)
		self.assertAlmostEqual(7.866507740, m.get_mean_distance_travelled(parameter_reference=4), places=6)
		self.assertAlmostEqual(8.74608830638, m.get_mean_distance_travelled(parameter_reference=5), places=6)
		self.assertAlmostEqual(9.37058123610, m.get_mean_distance_travelled(parameter_reference=6), places=6)

	def testNullDispersalWithCoarse(self):
		"""Sanity checks that the distances are calculated properly on a coarse map."""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_map_files(fine_file="sample/null.tif", coarse_file="sample/null_large.tif")
		m.set_simulation_parameters(number_repeats=1000, output_database="output/realdispersal8.db", seed=2,
									sigma=2, landscape_type="closed", number_steps=100)
		m.run_mean_distance_travelled()
		m.update_parameters(sigma=4)
		m.run_mean_distance_travelled()
		m.update_parameters(sigma=8)
		m.run_mean_distance_travelled()
		self.assertAlmostEqual(2*(math.pi*100/2)**0.5, m.get_mean_distance_travelled(parameter_reference=1), places=0)
		self.assertAlmostEqual(4*(math.pi*100/2)**0.5, m.get_mean_distance_travelled(parameter_reference=2), places=0)
		self.assertAlmostEqual(8*(math.pi*100/2)**0.5, m.get_mean_distance_travelled(parameter_reference=3), places=0)

