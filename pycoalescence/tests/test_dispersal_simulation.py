import logging
import math
import os
import unittest

from setup_tests import setUpAll, tearDownAll, skipLongTest

from pycoalescence import Map
from pycoalescence.dispersal_simulation import DispersalSimulation


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
        cls.m.set_map_files(os.path.join("sample", "SA_sample_fine.tif"))
        cls.m.set_simulation_parameters(
            number_repeats=100,
            output_database=os.path.join("output", "sim_pars_test4.db"),
            seed=2,
            sigma=2,
            landscape_type="tiled_fine",
        )
        cls.m.run_mean_dispersal()
        cls.m.set_simulation_parameters(number_repeats=100, seed=2, sigma=2, landscape_type="tiled_fine")
        cls.m.run_mean_dispersal()
        cls.m.set_simulation_parameters(
            number_repeats=100, seed=4, sigma=3, tau=1, landscape_type="tiled_fine", dispersal_method="fat-tail"
        )
        cls.m.run_mean_dispersal()
        cls.m.set_simulation_parameters(
            number_repeats=100, number_steps=10, seed=2, sigma=2, landscape_type="tiled_fine"
        )
        cls.m.run_mean_distance_travelled()
        cls.m.set_simulation_parameters(
            number_repeats=200, number_steps=10, seed=2, sigma=5, landscape_type="tiled_fine"
        )
        cls.m.run_mean_distance_travelled()
        cls.m.set_simulation_parameters(
            number_repeats=100, number_steps=20, seed=5, sigma=2, landscape_type="tiled_fine"
        )
        cls.m.run_mean_distance_travelled()

    def testGetFromDatabaseErrors(self):
        """Tests that the correct errors are raised when obtaining from a database."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.dispersal_database = "doesnotexist.db"
        with self.assertRaises(IOError):
            m.get_mean_dispersal()
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(IOError):
            m.get_mean_dispersal(database=os.path.join("sample", "sample.db"))
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(IOError):
            m.get_mean_distance_travelled(database=os.path.join("sample", "sample.db"))
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(IOError):
            m.get_stdev_dispersal(database=os.path.join("sample", "sample.db"))
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(IOError):
            m.get_stdev_distance_travelled(database=os.path.join("sample", "sample.db"))
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(IOError):
            m.get_all_distances(database=os.path.join("sample", "sample.db"))
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(IOError):
            m.get_all_dispersal(database=os.path.join("sample", "sample.db"))

    def testRaisesValueErrorNullNotSet(self):
        """
        Tests that a ValueError is raised when the map file is "null" but dimensions have not been manually set.
        """
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(ValueError):
            m.set_simulation_parameters(number_repeats=10000, output_database="output/normaldispersal.db", seed=1)
            m.set_map_files("null")

    def testRaisesError(self):
        """
        Tests that a dispersal.Error is raised when incorrect dispersal method is provided.
        """
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        with self.assertRaises(RuntimeError):
            m.set_simulation_parameters(
                number_repeats=10000, output_database="output/emptydb.db", seed=1, dispersal_method="notamethod"
            )
            m.set_map_files("sample/SA_sample_fine.tif")
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
        m.set_simulation_parameters(
            number_repeats=100000,
            output_database="output/normaldispersal1.db",
            seed=2,
            sigma=10,
            landscape_type="infinite",
            restrict_self=False,
        )
        m.run_mean_dispersal()
        self.assertAlmostEqual(m.get_mean_dispersal(), 10 * (3.14 ** 0.5) / 2 ** 0.5, places=2)
        expected_dispersal = [
            3.1622776601683795,
            27.202941017470888,
            16.1245154965971,
            15.132745950421556,
            13.038404810405298,
            13.601470508735444,
            11.180339887498949,
            13.038404810405298,
            8.48528137423857,
            12.083045973594572,
        ]

        actual_dispersal = m.get_all_dispersal()[:10]
        for expected, actual in zip(expected_dispersal, actual_dispersal):
            self.assertAlmostEqual(expected, actual, places=3)

    @skipLongTest
    def testLandscapeTypesMatch(self):
        """
        Tests that a null landscape with tiled_fine matches a null landscape with infinite
        """
        m1 = DispersalSimulation(logging_level=logging.CRITICAL)
        m1.set_map("null", 10, 10)
        m1.set_simulation_parameters(
            number_repeats=100000,
            output_database="output/normaldispersal2.db",
            seed=2,
            sigma=2,
            landscape_type="infinite",
            restrict_self=False,
        )
        m1.run_mean_dispersal()
        m2 = DispersalSimulation(logging_level=logging.CRITICAL)
        m2.set_map("null", 10, 10)
        m2.set_simulation_parameters(
            number_repeats=100000,
            output_database="output/normaldispersal3.db",
            seed=2,
            sigma=2,
            landscape_type="tiled_fine",
            restrict_self=False,
        )
        m2.run_mean_dispersal()
        self.assertEqual(m2.get_mean_dispersal(), m1.get_mean_dispersal())

    def testDispersalMapOutputs(self):
        """
        Tests that the dispersal simulations work as intended for real maps.
        """
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map("sample/SA_sample_fine.tif")
        m.set_simulation_parameters(
            number_repeats=10000,
            output_database="output/realdispersal.db",
            seed=1,
            sigma=1,
            landscape_type="tiled_fine",
        )
        m.run_mean_dispersal()
        self.assertAlmostEqual(1.2641113312060646, m.get_mean_dispersal(), places=4)

    def testDispersalDistanceTravelled(self):
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map("sample/SA_sample_fine.tif")
        m.set_simulation_parameters(
            number_repeats=100,
            number_steps=10,
            output_database="output/sim_pars_test2.db",
            seed=2,
            sigma=1,
            landscape_type="tiled_fine",
        )
        m.run_mean_distance_travelled()
        self.assertAlmostEqual(4.206153698181416, m.get_mean_distance_travelled(), places=3)
        expected_distances = [
            4.123105625617661,
            6.4031242374328485,
            6.0,
            5.0,
            5.0,
            1.4142135623730951,
            2.23606797749979,
            2.23606797749979,
            2.8284271247461903,
            3.1622776601683795,
        ]

        actual_dispersal = m.get_all_distances()[:10]
        for expected, actual in zip(expected_distances, actual_dispersal):
            self.assertAlmostEqual(expected, actual, places=3)

    def testDispersalSimulationParametersStoredCorrectly(self):
        """
        Tests that simulation parameters are stored correctly in the database.
        """
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map("sample/SA_sample_fine.tif")
        m.set_simulation_parameters(
            number_repeats=100, output_database="output/sim_pars_test1.db", seed=1, sigma=1, landscape_type="tiled_fine"
        )
        m.run_mean_dispersal()
        m.update_parameters(sigma=2, number_steps=10, seed=2)
        m.run_mean_distance_travelled()
        main_dict = m.get_database_parameters()
        comparison_dict = {
            1: {
                "simulation_type": "DISPERSAL_DISTANCES",
                "sigma": 1,
                "tau": 1,
                "cutoff": 100,
                "m_prob": 1.0,
                "dispersal_method": "normal",
                "map_file": "sample/SA_sample_fine.tif",
                "seed": 1,
                "number_steps": 1,
                "number_repeats": 100,
            },
            2: {
                "simulation_type": "DISTANCES_TRAVELLED",
                "sigma": 2,
                "tau": 1,
                "cutoff": 100.0,
                "m_prob": 1.0,
                "dispersal_method": "normal",
                "map_file": "sample/SA_sample_fine.tif",
                "seed": 2,
                "number_steps": 10,
                "number_repeats": 100,
            },
        }
        for key in main_dict.keys():
            for inner_key in main_dict[key].keys():
                self.assertEqual(
                    main_dict[key][inner_key],
                    comparison_dict[key][inner_key],
                    msg="Error in {}, {} != {}".format(
                        inner_key, main_dict[key][inner_key], comparison_dict[key][inner_key]
                    ),
                )

    def testMultipleSimulationsAverages(self):
        """
        Tests that with multiple simulations, the averages are outputted correctly.
        """

        self.assertAlmostEqual(2.5016203799003596, self.m.get_mean_dispersal(parameter_reference=2))
        self.assertAlmostEqual(17.448853121157676, self.m.get_mean_dispersal(parameter_reference=3))
        self.assertAlmostEqual(7.7522237785164885, self.m.get_mean_distance_travelled(parameter_reference=4))
        self.assertAlmostEqual(19.15984097911993, self.m.get_mean_distance_travelled(parameter_reference=5))

    def testStandardDeviationDistances(self):
        """
        Tests that the standard deviation is correctly returned from the simulated database
        """
        self.assertAlmostEqual(1.2537525572724404, self.m.get_stdev_dispersal(parameter_reference=1))
        self.assertAlmostEqual(1.2537525572724404, self.m.get_stdev_dispersal(parameter_reference=2))
        self.assertAlmostEqual(4.545660181734175, self.m.get_stdev_distance_travelled(parameter_reference=4))
        self.assertAlmostEqual(11.1072270911707, self.m.get_stdev_distance_travelled(parameter_reference=5))

    def testDatabaseReferences(self):
        """
        Tests that the database parameters are stored and returned correctly.
        """
        self.assertEqual([x for x in range(1, 7)], self.m.get_database_references())
        expected_dict = {
            "simulation_type": "DISPERSAL_DISTANCES",
            "sigma": 2,
            "tau": 1,
            "m_prob": 1.0,
            "cutoff": 100.0,
            "dispersal_method": "normal",
            "map_file": os.path.join("sample", "SA_sample_fine.tif"),
            "seed": 2,
            "number_steps": 1,
            "number_repeats": 100,
        }
        self.assertEqual(expected_dict, self.m.get_database_parameters()[1])
        self.assertEqual(expected_dict, self.m.get_database_parameters(1))
        for key in range(1, 6):
            self.m.get_database_parameters(key)
        with self.assertRaises(KeyError):
            self.m.get_database_parameters(7)
        with self.assertRaises(KeyError):
            self.m.get_database_parameters("NotAKey")

    def testDispersalMapReading(self):
        """
        Tests that dispersal simulations are correctly read from a completed simulation
        """
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map("sample/SA_sample_fine.tif")
        m.set_simulation_parameters(
            number_repeats=10000,
            output_database="output/realdispersal2.db",
            seed=1,
            sigma=1,
            landscape_type="tiled_fine",
        )
        m.run_mean_dispersal()
        m2 = DispersalSimulation(dispersal_db=m.dispersal_database, logging_level=logging.CRITICAL)
        self.assertAlmostEqual(1.2641113312060646, m2.get_mean_dispersal(), places=4)
        m3 = DispersalSimulation(dispersal_db=m, logging_level=logging.CRITICAL)
        self.assertAlmostEqual(1.2641113312060646, m3.get_mean_dispersal(), places=4)

    def testAlternativeMapFileSetting(self):
        m = DispersalSimulation(file="sample/SA_sample_fine.tif", logging_level=logging.CRITICAL)
        if m.fine_map.file_name is None:
            self.fail("File name not correctly set.")
        m.set_simulation_parameters(
            number_steps=10,
            number_repeats=10,
            output_database="output/realdispersal3.db",
            sigma=1,
            landscape_type="tiled_fine",
            seed=1,
        )
        m.run_mean_distance_travelled()
        m.run_mean_dispersal()
        with self.assertRaises(ValueError):
            m.get_mean_dispersal(parameter_reference=3)
        with self.assertRaises(ValueError):
            m.get_all_dispersal(parameter_reference=3)
        with self.assertRaises(ValueError):
            m.get_mean_distance_travelled(parameter_reference=3)
        with self.assertRaises(ValueError):
            m.get_all_distances(parameter_reference=3)
        self.assertAlmostEqual(1.2892922226992172, m.get_mean_dispersal(parameter_reference=2), places=4)

    def testParameterUpdating(self):
        """
        Tests that a simulation can be run properly with updating parameters in between.
        """
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map("sample/SA_sample_fine.tif")
        m.set_simulation_parameters(
            number_repeats=100, output_database="output/realdispersal4.db", seed=1, sigma=1, landscape_type="tiled_fine"
        )
        m.run_mean_dispersal()
        m.update_parameters(number_repeats=6, sigma=10)
        m.run_mean_dispersal()
        m.update_parameters(dispersal_method="fat-tail", number_steps=10)
        m.run_mean_distance_travelled()
        expected_params = {
            1: {
                "simulation_type": "DISPERSAL_DISTANCES",
                "sigma": 1.0,
                "tau": 1.0,
                "m_prob": 1.0,
                "cutoff": 100.0,
                "dispersal_method": "normal",
                "map_file": "sample/SA_sample_fine.tif",
                "seed": 1,
                "number_steps": 1,
                "number_repeats": 100,
            },
            2: {
                "simulation_type": "DISPERSAL_DISTANCES",
                "sigma": 10.0,
                "tau": 1.0,
                "m_prob": 1.0,
                "cutoff": 100.0,
                "dispersal_method": "normal",
                "map_file": "sample/SA_sample_fine.tif",
                "seed": 1,
                "number_steps": 1,
                "number_repeats": 6,
            },
            3: {
                "simulation_type": "DISTANCES_TRAVELLED",
                "sigma": 10.0,
                "tau": 1.0,
                "m_prob": 1.0,
                "cutoff": 100.0,
                "dispersal_method": "fat-tail",
                "map_file": "sample/SA_sample_fine.tif",
                "seed": 1,
                "number_steps": 10,
                "number_repeats": 6,
            },
        }
        actual_params = m.get_database_parameters()
        for key in expected_params.keys():
            self.assertEqual(expected_params[key], actual_params[key])
        self.assertAlmostEqual(1.245882030374995, m.get_mean_dispersal(parameter_reference=1), places=4)
        self.assertAlmostEqual(12.035293581998125, m.get_mean_dispersal(parameter_reference=2), places=4)
        self.assertAlmostEqual(507.88676714308644, m.get_mean_distance_travelled(parameter_reference=3), places=4)

    def testDispersalWithCoarse(self):
        """Tests a dispersal simulation using a coarse and fine map."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map_files(fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif")
        m.set_simulation_parameters(
            number_repeats=100, output_database="output/realdispersal5.db", seed=1, sigma=1, landscape_type="tiled_fine"
        )
        m.run_mean_dispersal()
        self.assertAlmostEqual(1.2964612543012595, m.get_mean_dispersal(parameter_reference=1), places=4)

    def testDispersalWithSample(self):
        """Tests a dispersal simulation using a sample and fine map."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map_files(fine_file="sample/SA_fine_expanded.tif", sample_file="sample/SA_sample_fine.tif")
        m.set_simulation_parameters(
            number_repeats=100, output_database="output/realdispersal6.db", seed=1, sigma=1, landscape_type="closed"
        )
        m.run_mean_dispersal()
        self.assertAlmostEqual(0.9840668874233433, m.get_mean_dispersal(parameter_reference=1), places=4)

    def testApplyingMultipleNumberSteps(self):
        """Tests running a single simulation with multiple number of steps at once."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map_files(fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif")
        m.set_simulation_parameters(
            number_repeats=100, output_database="output/realdispersal7.db", seed=1, sigma=1, landscape_type="tiled_fine"
        )
        m.run_mean_distance_travelled(number_steps=[10, 20, 30], number_repeats=100, seed=1)
        m.update_parameters(number_steps=[40, 50, 60])
        m.run_mean_distance_travelled()
        for k, v in [(1, 10), (2, 20), (3, 30), (4, 40), (5, 50), (6, 60)]:
            self.assertEqual(v, m.get_database_parameters()[k]["number_steps"])
        self.assertAlmostEqual(4.001297548429019, m.get_mean_distance_travelled(parameter_reference=1), places=6)
        self.assertAlmostEqual(6.1136500795111886, m.get_mean_distance_travelled(parameter_reference=2), places=6)
        self.assertAlmostEqual(7.3630228316363295, m.get_mean_distance_travelled(parameter_reference=3), places=6)
        self.assertAlmostEqual(8.497107432997838, m.get_mean_distance_travelled(parameter_reference=4), places=6)
        self.assertAlmostEqual(9.723744156016298, m.get_mean_distance_travelled(parameter_reference=5), places=6)
        self.assertAlmostEqual(10.81902521181573, m.get_mean_distance_travelled(parameter_reference=6), places=6)

    def testRunMeanDistanceErrors(self):
        """Tests that the mean distance travelled errors are correctly raised."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map_files(fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif")
        with self.assertRaises(ValueError):
            m.run_mean_distance_travelled()
        with self.assertRaises(ValueError):
            m.run_mean_distance_travelled(number_repeats=1)
        with self.assertRaises(ValueError):
            m.run_mean_distance_travelled(number_steps=1, number_repeats=1)

    def testRunMeanDispersalErrors(self):
        """Tests that the mean dispersal errors are correctly raised."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map_files(fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif")
        with self.assertRaises(ValueError):
            m.run_mean_dispersal()

    @skipLongTest
    def testNullDispersalWithCoarse(self):
        """Sanity checks that the distances are calculated properly on a coarse map."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_map_files(fine_file="sample/null.tif", coarse_file="sample/null_large.tif")
        m.set_simulation_parameters(
            number_repeats=100000,
            output_database="output/realdispersal8.db",
            seed=2,
            sigma=2,
            landscape_type="closed",
            number_steps=100,
        )
        m.run_mean_distance_travelled()
        m.update_parameters(sigma=4)
        m.run_mean_distance_travelled()
        m.update_parameters(sigma=8)
        m.run_mean_distance_travelled()
        self.assertAlmostEqual(
            2 * (math.pi * 100 / 2) ** 0.5, m.get_mean_distance_travelled(parameter_reference=1), places=0
        )
        self.assertAlmostEqual(
            4 * (math.pi * 100 / 2) ** 0.5, m.get_mean_distance_travelled(parameter_reference=2), places=0
        )
        self.assertAlmostEqual(
            8 * (math.pi * 100 / 2) ** 0.5, m.get_mean_distance_travelled(parameter_reference=3), places=0
        )

    def testDispersalWithHistoricalMaps(self):
        """Tests that a simulation with a historical map works."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_simulation_parameters(
            number_repeats=2,
            output_database="output/realdispersal9.db",
            seed=2,
            sigma=2,
            landscape_type="closed",
            number_steps=100,
        )
        m1 = Map("sample/SA_sample_fine.tif")
        m.set_map_files(m1)
        m.add_historical_map(fine_file="sample/SA_sample_fine2.tif", coarse_file="none", time=10, rate=0.1)
        m.run_mean_distance_travelled()
        self.assertAlmostEqual(4.3471617258268065, m.get_mean_distance_travelled(parameter_reference=1), places=6)

    def testDispersalDatabaseRemoval(self):
        """Tests that the dispersal database connection can be deleted properly, with simulation variables preserved."""
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_simulation_parameters(
            number_repeats=2,
            output_database="output/realdispersal10.db",
            seed=2,
            sigma=2,
            landscape_type="closed",
            number_steps=100,
        )
        m.set_map("sample/SA_sample_fine.tif")
        m.run_mean_distance_travelled()
        mean_dist1 = m.get_mean_distance_travelled()
        self.assertTrue(os.path.exists(m.dispersal_database))
        m._remove_existing_db()
        self.assertFalse(os.path.exists(m.dispersal_database))
        m.run_mean_distance_travelled()
        self.assertTrue(os.path.exists(m.dispersal_database))
        self.assertEqual(mean_dist1, m.get_mean_distance_travelled())

    def testDispersalDatabaseCreation(self):
        """
        Tests that a dispersal database is created initially before the simulation is run, and re-created, if it
        has been deleted, before any simulations.
        """
        m = DispersalSimulation(logging_level=logging.CRITICAL)
        m.set_simulation_parameters(
            number_repeats=2,
            output_database="output/realdispersal11.db",
            seed=2,
            sigma=2,
            landscape_type="closed",
            number_steps=100,
        )
        m.set_map("sample/SA_sample_fine.tif")
        self.assertTrue(os.path.exists(m.dispersal_database))
        m._remove_existing_db()
        self.assertFalse(os.path.exists(m.dispersal_database))
        m.run_mean_distance_travelled()
        self.assertTrue(os.path.exists(m.dispersal_database))
        self.assertAlmostEqual(4.3471617258268065, m.get_mean_distance_travelled(parameter_reference=1), places=6)

    def testRunMeanDistanceTravelledErrors(self):
        """Tests that run mean distance travelled produces the expected errors."""
        d = DispersalSimulation(dispersal_db=os.path.join("output", "output.db"))
        with self.assertRaises(ValueError):
            d.run_mean_distance_travelled()

    def testCheckBaseParametersErrors(self):
        """Tests that the correct errors are raised when the base parameters are checked."""
        d = DispersalSimulation()
        with self.assertRaises(ValueError):
            d.check_base_parameters()
        d.number_repeats = 1
        with self.assertRaises(ValueError):
            d.check_base_parameters()
        d.seed = 1
        with self.assertRaises(ValueError):
            d.check_base_parameters()
