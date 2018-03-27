import logging
import unittest

from pycoalescence.dispersal_simulation import DispersalSimulation


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
		cls.m.test_mean_dispersal(number_repeats=100, output_database="output/sim_pars_test4.db",
								  map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal", sigma=2)
		cls.m.test_mean_dispersal(number_repeats=100, output_database="output/sim_pars_test4.db",
								  map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal", sigma=2)
		cls.m.test_mean_dispersal(number_repeats=100, output_database="output/sim_pars_test4.db",
								  map_file="sample/SA_sample_fine.tif", seed=3, dispersal_method="fat-tail", sigma=2, tau=1)
		cls.m.test_mean_distance_travelled(number_repeats=100, number_steps=10,
										   output_database="output/sim_pars_test4.db",
										   map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal",
										   sigma=2)
		cls.m.test_mean_distance_travelled(number_repeats=200, number_steps=10,
										   output_database="output/sim_pars_test4.db",
										   map_file="sample/SA_sample_fine.tif", seed=2, dispersal_method="normal",
										   sigma=5)
		cls.m.test_mean_distance_travelled(number_repeats=100, number_steps=20,
										   output_database="output/sim_pars_test4.db",
										   map_file="sample/SA_sample_fine.tif", seed=4, dispersal_method="normal",
										   sigma=2)

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
		with self.assertRaises(ValueError):
			m.get_mean_dispersal()

	def testRaisesValueErrorNullNotSet(self):
		"""
		Tests that a ValueError is raised when the map file is "null" but dimensions have not been manually set.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		with self.assertRaises(ValueError):
			m.test_mean_dispersal(number_repeats=10000, output_database="output/normaldispersal.db", map_file="null",
								  seed=1, dispersal_method="normal", sigma=1, tau=1, m_prob=0.0, cutoff=100)

	def testRaisesDispersalError(self):
		"""
		Tests that a dispersal.Error is raised when incorrect dispersal method is provided.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		with self.assertRaises(ValueError):
			m.test_mean_dispersal(number_repeats=10000, output_database="output/normaldispersal.db", map_file="null",
								  seed=1, dispersal_method="notreal", sigma=1, tau=1, m_prob=0.0, cutoff=100)

	def testDispersalNullOutputs(self):
		"""
		Tests that the dispersal simulations accurately generate the correct distance distribution for null landscapes.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.set_dimensions("null", 10, 10, 0, 0)
		m.test_mean_dispersal(number_repeats=10000, output_database="output/normaldispersal.db", map_file="null",
							  seed=1, dispersal_method="normal", sigma=1, tau=1, m_prob=0.0, cutoff=100)
		self.assertAlmostEqual(m.get_mean_dispersal(), (3.14 ** 0.5) / 2 ** 0.5, places=2)

	def testDispersalMapOutputs(self):
		"""
		Tests that the dispersal simulations work as intended for real maps.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.test_mean_dispersal(number_repeats=10000, output_database="output/realdispersal.db",
							  map_file="sample/SA_sample_fine.tif", seed=1, dispersal_method="normal", sigma=1, tau=1,
							  m_prob=0.0, cutoff=100, )
		self.assertEqual(1.2516809696363225, m.get_mean_dispersal())

	def testDispersalDistanceTravelled(self):
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.test_mean_distance_travelled(number_repeats=100, number_steps=10, output_database="output/sim_pars_test2.db",
									   map_file="sample/SA_sample_fine.tif", seed=1, dispersal_method="normal", sigma=1,
									   tau=1, m_prob=0.0, cutoff=100)
		self.assertEqual(4.044138945328306, m.get_mean_distance_travelled())

	def testDispersalSimulationParametersStoredCorrectly(self):
		"""
		Tests that simulation parameters are stored correctly in the database.
		"""
		m = DispersalSimulation(logging_level=logging.CRITICAL)
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
		m = DispersalSimulation(logging_level=logging.CRITICAL)
		m.test_mean_dispersal(number_repeats=10000, output_database="output/realdispersal2.db",
							  map_file="sample/SA_sample_fine.tif", seed=1, dispersal_method="normal", sigma=1, tau=1,
							  m_prob=0.0, cutoff=100)
		m2 = DispersalSimulation(dispersal_db=m.dispersal_database, logging_level=logging.CRITICAL)
		self.assertEqual(1.2516809696363225, m2.get_mean_dispersal())
		m3 = DispersalSimulation(dispersal_db=m, logging_level=logging.CRITICAL)
		self.assertEqual(1.2516809696363225, m3.get_mean_dispersal())

	def testAlternativeMapFileSetting(self):
		m = DispersalSimulation(file="sample/SA_sample_fine.tif", logging_level=logging.CRITICAL)
		if m.file_name is None:
			self.fail("File name not correctly set.")
		m.test_mean_distance_travelled(number_repeats=10, number_steps=10, output_database="output/realdispersal3.db")
		m.test_mean_dispersal(number_repeats=10)
		with self.assertRaises(ValueError):
			m.get_mean_dispersal()
		self.assertAlmostEqual(1.4932, m.get_mean_dispersal(parameter_reference=2), places=4)