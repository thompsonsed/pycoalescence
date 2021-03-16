"""
Contains relatively high-level tests of Simulation object, testing a variety of simulation parameter combinations
to assert simulation outputs are as expected.
"""
import logging
import os
import sys
import unittest
from configparser import ConfigParser

import numpy as np

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

try:
    from io import StringIO
except ImportError as ie:  # Python 2.x support
    from cStringIO import StringIO

from pycoalescence.simulation import Simulation
from pycoalescence.coalescence_tree import CoalescenceTree
from pycoalescence import __version__ as pycoalescence_version
from pycoalescence.map import Map
from setup_tests import setUpAll, tearDownAll, skipLongTest


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
        self.coal.set_simulation_parameters(
            10,
            38,
            "output/test_output/test_output2/",
            0.1,
            4,
            4,
            deme=1,
            sample_size=1.0,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        self.coal.set_map_parameters(
            "null",
            10,
            10,
            "null",
            10,
            10,
            0,
            0,
            "null",
            20,
            20,
            0,
            0,
            1,
            "null",
            "null",
        )
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()

    def testFileCreation(self):
        """
        Checks that outputting is to the correct place and folder structure is created properly.
        """
        self.assertTrue(os.path.isfile(self.coal.output_database))
        self.assertEqual(
            os.path.join(self.coal.output_database),
            os.path.join(
                self.coal.output_directory,
                "data_{}_{}.db".format(self.coal.task, self.coal.seed),
            ),
        )


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
        coal.set_simulation_parameters(
            100000,
            10000,
            "output",
            0.1,
            4,
            4,
            deme=1,
            sample_size=1.0,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        with self.assertRaises(ValueError):
            coal.set_map_files(sample_file="null", fine_file="null")


class TestSetSeed(unittest.TestCase):
    """Tests that seeds are correctly set, and errors are thrown where appropriate."""

    def testIncorrectSeedRaisesErrors(self):
        """Tests that an error is raised if the seed is too large."""
        s = Simulation()
        with self.assertRaises(ValueError):
            s.set_seed(2147483647)
        with self.assertRaises(ValueError):
            s.set_simulation_parameters(
                seed=2147483647,
                task=1,
                output_directory="output",
                min_speciation_rate=0.1,
            )

    def testBasicSeedSetting(self):
        """Tests that the basic seed setting works as intended."""
        s = Simulation()
        s.set_seed(1)
        self.assertEqual(1, s.seed)
        s = Simulation()
        s.set_simulation_parameters(
            seed=1,
            task=1,
            output_directory="output",
            min_speciation_rate=0.1,
            spatial=False,
        )
        self.assertEqual(1, s.seed)

    def testModifiedSeedSetting(self):
        """Tests that the modification to seed setting works as intended."""
        s = Simulation(logging_level=60)
        s.set_seed(0)
        self.assertEqual(1073741823, s.seed)
        s = Simulation(logging_level=60)
        s.set_simulation_parameters(
            seed=0,
            task=1,
            output_directory="output",
            min_speciation_rate=0.1,
            spatial=False,
        )
        self.assertEqual(1073741823, s.seed)
        s = Simulation(logging_level=60)
        s.set_seed(-1)
        self.assertEqual(1073741824, s.seed)
        s = Simulation(logging_level=60)
        s.set_seed(-2)
        self.assertEqual(1073741825, s.seed)
        s = Simulation(logging_level=60)
        s.set_seed(-300)
        self.assertEqual(1073742123, s.seed)


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
        cls.coal1.set_simulation_parameters(
            seed=1,
            task=38,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
        )
        cls.coal2 = Simulation()
        cls.coal2.set_simulation_parameters(
            seed=1,
            task=38,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
        )

    def testRaisesErrorFineSampleOffset(self):
        """
        Tests the correct error is raised when offsetting is incorrect
        """
        with self.assertRaises(ValueError):
            self.coal1.set_map_files(
                sample_file="sample/SA_samplemaskINT.tif",
                fine_file="sample/SA_sample_fine_offset.tif",
            )

    def testRaisesErrorFineSampleOffset2(self):
        """
        Tests the correct error is raised when offsetting is incorrect
        """
        with self.assertRaises(ValueError):
            self.coal2.set_map_files(
                sample_file="null",
                fine_file="sample/SA_sample_fine_offset.tif",
                coarse_file="sample/SA_sample_coarse.tif",
            )

    def testRaisesErrorAfterIncorrectSamplegridBoundaries(self):
        """
        Checks that setting incorrect limits for the sample grid outside of the fine map causes an error to be thrown.
        """
        sim = Simulation()
        sim.set_simulation_parameters(
            seed=1,
            task=1,
            output_directory="output",
            min_speciation_rate=0.001,
            sigma=2,
        )
        sim.set_map_files(
            sample_file="null",
            fine_file="sample/SA_sample_fine_offset.tif",
            coarse_file="none",
        )
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
    Tests that protracted and normal simulations raise the correct errors.
    """

    def testNormalRaisesError(self):
        """
        Tests a normal simulation raises an error when no files exist
        """
        c = Simulation()
        c.set_simulation_parameters(
            5,
            4,
            "output",
            0.1,
            4,
            4,
            1,
            0.01,
            2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
        )
        c.set_map_files(
            "null",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
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
        c.set_simulation_parameters(
            6,
            4,
            "output",
            0.1,
            4,
            4,
            1,
            0.01,
            2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
            protracted=True,
        )
        c.set_map_files(
            "null",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
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
        self.coal.set_simulation_parameters(
            1,
            23,
            "output",
            0.1,
            4,
            4,
            1,
            1.0,
            max_time=200,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
        )
        self.coal.set_map_files(
            "null",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal.add_sample_time(0.0)
        self.coal.add_sample_time(1.0)
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.create_config("output/conf1.txt")

    def testConfigWriteMain(self):
        """
        Tests that the main configuration file has been correctly generated.
        """
        with open("output/conf1.txt", "r") as mapconf:
            lines = mapconf.readlines()
            lines = [x.strip() for x in lines]
            self.assertEqual(lines[0], "[main]")
            self.assertEqual(lines[1].replace(" ", ""), "seed=1")
            self.assertEqual(lines[2].replace(" ", ""), "task=23")

    def testMapConfigWrite(self):
        """
        Tests the map config output to check output is correct.
        """
        self.coal.add_historical_map(
            fine_file="sample/SA_sample_fine_historical1.tif",
            coarse_file="sample/SA_sample_coarse_historical1.tif",
            time=1,
            rate=0.5,
        )
        self.coal.add_historical_map(
            fine_file="sample/SA_sample_fine_historical2.tif",
            coarse_file="sample/SA_sample_coarse_historical2.tif",
            time=4,
            rate=0.7,
        )
        self.coal.create_map_config("output/mapconf2.txt")
        with open("output/mapconf2.txt", "r") as mapconf:
            lines = mapconf.readlines()
            lines = [x.strip() for x in lines]
            self.assertEqual(lines[21], "[sample_grid]")
            self.assertEqual(
                lines[22].replace(" ", ""),
                "path=null",
                msg="Config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[27].replace(" ", ""),
                "[fine_map]",
                msg="Config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[28].replace(" ", ""),
                "path=sample/SA_sample_fine.tif",
                msg="Config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[29].replace(" ", ""),
                "x=13",
                msg="Config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[30].replace(" ", ""),
                "y=13",
                msg="Config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[31].replace(" ", ""),
                "x_off=0",
                msg="Config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[32].replace(" ", ""),
                "y_off=0",
                msg="Config file doesn't produce expected output.",
            )

    def testConfigOverwrite(self):
        """Tests that the config file overwrites the output."""
        config_output = os.path.join("output", "conf_test_create.txt")
        config_output2 = os.path.join("output", "notexist", "conf_test_create2.txt")
        sim = Simulation(logging_level=logging.CRITICAL)
        sim.set_simulation_parameters(1, 23, "output", 0.1, 4, 4, 1, 1.0, max_time=200, spatial=False)
        self.assertFalse(os.path.exists(os.path.dirname(config_output2)))
        sim.write_config(config_output2)
        self.assertTrue(os.path.exists(os.path.dirname(config_output2)))
        with open(config_output, "a"):
            pass
        sim = Simulation(logging_level=logging.CRITICAL)
        sim.set_simulation_parameters(
            1,
            23,
            "output",
            0.1,
            4,
            4,
            1,
            1.0,
            max_time=200,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
            restrict_self=True,
        )
        sim.set_map_files(
            "null",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        sim.sample_map.file_name = None
        sim.coarse_map.file_name = None
        sim.add_sample_time(0.0)
        sim.add_sample_time(1.0)
        sim.set_speciation_rates([0.1, 0.2])
        self.assertTrue(os.path.exists(config_output))
        sim.write_config(config_output)
        self.assertTrue(os.path.exists(config_output))
        with open(config_output, "r") as mapconf:
            lines = mapconf.readlines()
            lines = [x.strip() for x in lines]
            self.assertEqual(lines[0], "[main]")
            self.assertEqual(lines[1].replace(" ", ""), "seed=1")
            self.assertEqual(lines[2].replace(" ", ""), "task=23")

    def testTimeConfigWrite(self):
        """
        Tests the map config writing is correct.
        """
        with open("output/conf1.txt", "r") as f:
            lines = f.readlines()
            lines = [x.strip().replace(" ", "") for x in lines]
            self.assertEqual(
                lines[17],
                "[times]",
                msg="Time config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[18],
                "time0=0.0",
                msg="Time config file doesn't produce expected output.",
            )
            self.assertEqual(
                lines[19],
                "time1=1.0",
                msg="Time config file doesn't produce expected output.",
            )

    def testConfigWrite(self):
        """Tests that the config parser correctly writes all simulation parameters to memory."""
        coal = Simulation(logging_level=logging.CRITICAL)
        coal.set_simulation_parameters(
            seed=1,
            task=23,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=1.0,
            max_time=200,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
        )
        coal.set_map_files(
            "null",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        coal.add_sample_time(0.0)
        coal.add_sample_time(1.0)
        coal.set_speciation_rates([0.1, 0.2])
        coal.write_config("output/conf1b.txt")
        coal.write_config("output/output2/conf1b.txt")
        self.assertTrue(os.path.exists("output/conf1b.txt"))
        self.assertTrue(os.path.exists("output/output2/conf1b.txt"))
        ref_config_parser = ConfigParser()
        ref_config_parser.read("output/conf1b.txt")
        for section in ["sample_grid", "fine_map", "coarse_map", "main"]:
            self.assertTrue(ref_config_parser.has_section(section))

    def testConfigWriteErrors(self):
        """Tests that the config parser correctly writes all simulation parameters to memory."""
        coal = Simulation(logging_level=logging.CRITICAL)
        with self.assertRaises(RuntimeError):
            coal.create_config()
        coal.set_simulation_parameters(
            seed=1,
            task=23,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=1.0,
            max_time=200,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
        )
        with self.assertRaises(RuntimeError):
            coal.create_map_config()
        coal.set_map_files(
            "null",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        coal.add_historical_map(
            fine_file="sample/SA_sample_fine_historical1.tif",
            coarse_file="sample/SA_sample_coarse_historical1.tif",
            time=1,
            rate=0.5,
        )
        coal.add_historical_map(
            fine_file="sample/SA_sample_fine_historical2.tif",
            coarse_file="sample/SA_sample_coarse_historical2.tif",
            time=4,
            rate=0.7,
        )
        coal.rates_list = [0.5]
        with self.assertRaises(ValueError):
            coal.write_config("output/conf1c.txt")

    def testConfigRead(self):
        """Tests that the config parser correctly reads simulation parameters from the file."""
        coal = Simulation(logging_level=logging.CRITICAL)
        coal.load_config(os.path.join("sample", "conf_example1.txt"))
        self.assertEqual(1, coal.seed)
        self.assertEqual(23, coal.task)
        self.assertEqual("output", coal.output_directory)
        self.assertEqual(0.1, coal.min_speciation_rate)
        self.assertEqual(4, coal.sigma)
        self.assertEqual(4, coal.tau)
        self.assertEqual(1.0, coal.sample_size)
        self.assertEqual(200, coal.max_time)
        self.assertEqual(1, coal.dispersal_relative_cost)
        self.assertEqual(1, coal.min_num_species)
        self.assertEqual("fat-tail", coal.dispersal_method)
        self.assertEqual("null", coal.sample_map.file_name)
        self.assertEqual("pycoalescence/tests/sample/SA_sample_fine.tif", coal.fine_map.file_name)
        self.assertEqual("pycoalescence/tests/sample/SA_sample_coarse.tif", coal.coarse_map.file_name)
        self.assertEqual(
            "pycoalescence/tests/sample/SA_sample_fine_pristine1.tif",
            coal.historical_fine_list[0],
        )
        self.assertEqual(
            "pycoalescence/tests/sample/SA_sample_fine_pristine2.tif",
            coal.historical_fine_list[1],
        )
        self.assertEqual(
            "pycoalescence/tests/sample/SA_sample_coarse_pristine1.tif",
            coal.historical_coarse_list[0],
        )
        self.assertEqual(
            "pycoalescence/tests/sample/SA_sample_coarse_pristine2.tif",
            coal.historical_coarse_list[1],
        )
        self.assertEqual([10, 10], coal.times_list)
        self.assertEqual([0.5, 0.5], coal.rates_list)
        self.assertEqual([0.0, 1.0], coal.times)
        self.assertEqual([0.1, 0.2], coal.speciation_rates)


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
        cls.c.set_simulation_parameters(
            seed=1,
            task=12,
            output_directory="output",
            min_speciation_rate=0.01,
            sigma=2,
        )
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
        self.assertEqual(4, self.c.get_species_richness())

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


@unittest.skipIf(sys.version[0] == "2", "Skipping Python 3.x tests")
class TestLoggingOutputsCorrectly(unittest.TestCase):
    """Basic test for expected logging outputs."""

    def testOutputStreamerInfo(self):
        """
        Tests that info output streaming works as intended (skipping the timing information)
        """
        log_stream = StringIO()
        with open("sample/log_12_2.txt", "r") as content_file:
            expected_log = content_file.read().replace("\r", "\n").split("\n")[:-6]
            expected_log[0] = expected_log[0].format(pycoalescence_version)
        s = Simulation(logging_level=logging.INFO, stream=log_stream)
        s.set_simulation_parameters(seed=2, task=12, output_directory="output", min_speciation_rate=0.1)
        s.set_map("null", 10, 10)
        s.run()
        log = log_stream.getvalue().replace("\r", "\n").split("\n")[:-6]
        self.assertEqual(expected_log, log)

    def testOutputStreamerWarning(self):
        """
        Tests that warning output streaming works as intended.
        """
        log_stream = StringIO()
        s = Simulation(logging_level=logging.WARNING, stream=log_stream)
        s.set_simulation_parameters(seed=3, task=12, output_directory="output", min_speciation_rate=0.1)
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
        s.set_simulation_parameters(seed=4, task=12, output_directory="output", min_speciation_rate=0.1)
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
        s.set_simulation_parameters(seed=5, task=12, output_directory="output", min_speciation_rate=0.1)
        s.set_map_files(sample_file="null", fine_file="sample/large_fine.tif")
        s.sample_map.x_size = 10
        s.sample_map.y_size = 10
        s.fine_map.x_offset = 100
        s.fine_map.y_offset = 120
        s.finalise_setup()
        s.run_coalescence()
        self.assertEqual("", log_stream.getvalue())


class TestSimulationDimensionsAndOffsets(unittest.TestCase):
    """Test the dimension detection and offsets of Simulation."""

    @classmethod
    def setUpClass(cls):
        cls.coal = Simulation()
        cls.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        cls.coal2 = Simulation()
        cls.coal2.set_map_files(
            sample_file="null",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )

    def testFineMapDimensions(self):
        """Checks that the dimensions and offsets are properly calculated."""
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
        """Checks that the dimensions and offsets are properly calculated."""
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
        """Checks that the correct exceptions are raised when simulation is started without being properly setup."""
        with self.assertRaises(RuntimeError):
            self.coal.run_coalescence()

    def testDimensionsCheckingError(self):
        """Tests that an error is raised if the dimensions don't match."""
        sim = Simulation()
        sim.fine_map = Map(file=os.path.join("sample", "SA_sample_fine.tif"))
        sim.fine_map.set_dimensions()
        with self.assertRaises(ValueError):
            sim.check_dimensions_match_fine(map_to_check=Map(file=os.path.join("sample", "SA_sample_coarse.tif")))


class TestSimulationExtremeSpeciation(unittest.TestCase):
    """Tests extreme speciation values to ensure that either 1 or maximal numbers of species are produced."""

    def testZeroSpeciation(self):
        """Tests that running a simulation with a zero speciation rate produces a single species."""
        c = Simulation()
        c.set_simulation_parameters(
            seed=1,
            task=17,
            output_directory="output",
            min_speciation_rate=0.0,
            sigma=2.0,
            tau=1,
            deme=1,
            sample_size=1,
            max_time=4,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            landscape_type=False,
        )
        c.set_map("null", 10, 10)
        c.run()
        self.assertEqual(c.get_species_richness(), 1)

    def testMaxSpeciation(self):
        """Tests that running a simulation with a zero speciation rate produces a single species."""
        c = Simulation()
        c.set_simulation_parameters(
            seed=1,
            task=18,
            output_directory="output",
            min_speciation_rate=1.0,
            sigma=2.0,
            tau=1,
            deme=1,
            sample_size=1,
            max_time=4,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            landscape_type=False,
        )
        c.set_map("null", 10, 10)
        c.run()
        self.assertEqual(c.get_species_richness(), 100)

    def testApplySpeciation(self):
        """Tests that speciation rates can be applied post-simulation."""
        c = Simulation()
        c.set_simulation_parameters(
            seed=2,
            task=18,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2.0,
            tau=1,
            deme=1,
            sample_size=1,
            max_time=4,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            landscape_type=False,
        )
        c.set_map("null", 10, 10)
        c.finalise_setup()
        self.assertTrue(c.run_coalescence())
        c.apply_speciation_rates(speciation_rates=[0.1, 0.5, 0.9999])
        self.assertEqual(25, c.get_species_richness(reference=1))
        self.assertEqual(69, c.get_species_richness(reference=2))
        self.assertEqual(100, c.get_species_richness(reference=3))


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
        cls.c.set_simulation_parameters(
            seed=1,
            task=36,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=64000,
            sample_size=0.00005,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        cls.c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")

    def testActualDensity(self):
        """
        Tests the actual density
        """
        self.assertEqual(
            self.c.grid_density_actual(0, 0, self.c.sample_map.x_size, self.c.sample_map.y_size),
            531,
        )

    def testEstimateDensity(self):
        """
        Tests the estimate density for the sample grid
        """
        self.assertEqual(
            self.c.grid_density_estimate(0, 0, self.c.sample_map.x_size, self.c.sample_map.y_size),
            375,
        )

    def testFineAverageMap(self):
        """
        Tests the average density of the fine map is correct.
        """
        self.assertAlmostEqual(self.c.get_average_density(), 38339.499790687034, 3)

    def testCountIndividuals(self):
        """Tests that the count of numbers of individuals is roughly accurate"""
        self.assertTrue(self.c.count_individuals() - 12381 < 2200)
        self.assertTrue(self.c.count_individuals() - 12381 < 2200)
        c = Simulation()
        c.set_simulation_parameters(
            seed=1,
            task=36,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=64000,
            sample_size=0.00005,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        c.set_map_files(sample_file="null", fine_file="sample/large_fine.tif")
        self.assertAlmostEqual(5907177.600000001, c.count_individuals(), places=2)

    def testSampleMapMatchingTest(self):
        """Tests that sample map equals the sample grid."""
        self.assertEqual(False, self.c.check_sample_map_equals_sample_grid())

    def testImportingMapArrays(self):
        """Tests that importing the map arrays works correctly."""
        self.c.import_fine_map_array()
        self.assertAlmostEqual(1845993, np.sum(self.c.fine_map_array), places=2)

    def testImportingNullMapArrays(self):
        """Tests that importing the map arrays works correctly."""
        sim = Simulation()
        sim.set_map("null", 10, 10)
        sim.import_fine_map_array()
        sim.import_sample_map_array()
        self.assertEqual(100, np.sum(sim.fine_map_array))
        self.assertEqual(100, np.sum(sim.sample_map_array))
        self.assertEqual(100, sim.grid_density_estimate(0, 0, 2, 2))
        self.assertEqual(4, sim.grid_density_actual(0, 0, 2, 2))
        sim = Simulation()
        sim.uses_spatial_sampling = True
        sim.set_map_files(
            sample_file=os.path.join("sample", "SA_sample_fine.tif"),
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
        )
        sim.import_sample_map_array()
        self.assertEqual(38098, np.sum(sim.sample_map_array))


class TestHistoricalMapsAlterResult(unittest.TestCase):
    """
    Makes sure that historical maps correctly alter the result of the simulation.
    """

    @classmethod
    def setUpClass(cls):
        cls.base_sim = Simulation()
        cls.hist_sim = Simulation()
        cls.base_sim.set_simulation_parameters(
            seed=4,
            task=17,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2,
            sample_size=0.1,
        )
        cls.base_sim.set_map("sample/SA_sample_fine.tif")
        cls.base_sim.run()
        cls.hist_sim.set_simulation_parameters(
            seed=4,
            task=18,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2,
            sample_size=0.1,
        )
        cls.hist_sim.set_map("sample/SA_sample_fine.tif")
        cls.hist_sim.add_historical_map(
            fine_file="sample/example_historical_fine.tif",
            coarse_file="none",
            time=10,
            rate=0.2,
        )
        cls.hist_sim.run()
        cls.hist_sim2 = Simulation()
        cls.hist_sim2.set_simulation_parameters(
            seed=4,
            task=19,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2,
            sample_size=0.1,
        )
        cls.hist_sim2.set_map("sample/SA_sample_fine.tif")
        cls.hist_sim2.add_historical_map(
            fine_file="sample/example_historical_fine.tif",
            coarse_file="none",
            time=10,
            rate=0.2,
        )
        cls.hist_sim2.add_historical_map(fine_file="sample/SA_sample_fine.tif", coarse_file="none", time=20, rate=0.2)
        cls.hist_sim2.run()

    def testSpeciesRichnessDiffer(self):
        """
        Tests that the species richness differs between the two simulations
        """
        self.assertNotEqual(self.base_sim.get_species_richness(), self.hist_sim.get_species_richness())
        self.assertNotEqual(self.hist_sim.get_species_richness(), self.hist_sim2.get_species_richness())
        self.assertEqual(2673, self.base_sim.get_species_richness())
        self.assertEqual(2515, self.hist_sim2.get_species_richness())
        self.assertEqual(2450, self.hist_sim.get_species_richness())


@skipLongTest
class TestExpansionOverTime(unittest.TestCase):
    """Tests that large expansions over time are dealt with properly when sampling multiple time points."""

    @classmethod
    def setUpClass(cls):
        """Run the simulation for expansion over time."""
        cls.sim = Simulation(logging_level=60)
        cls.sim.set_simulation_parameters(
            seed=5,
            task=17,
            output_directory="output",
            min_speciation_rate=0.0001,
            sigma=1,
            deme=100,
            sample_size=1.0,
            landscape_type="infinite",
        )
        cls.sim.set_map_files("null", "sample/null.tif", "sample/null_large.tif")
        cls.sim.add_historical_map("sample/null.tif", "sample/null_large.tif", time=500, rate=0.5)
        cls.sim.add_sample_time([0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
        cls.sim.run()

    def testSpeciesRichnessAtTimes(self):
        """Checks the species richness is correct for each time point."""
        self.assertEqual(336, self.sim.get_species_richness(1))
        self.assertEqual(332, self.sim.get_species_richness(2))
        self.assertEqual(332, self.sim.get_species_richness(3))
        self.assertEqual(357, self.sim.get_species_richness(4))
        self.assertEqual(340, self.sim.get_species_richness(5))
        self.assertEqual(343, self.sim.get_species_richness(6))


class TestSimulationParameters(unittest.TestCase):
    """Tests that parameters are correctly set."""

    def testAddingTimes(self):
        """Tests times are correctly added."""
        sim = Simulation()
        sim.set_simulation_parameters(
            seed=10000,
            task=1000000,
            output_directory="output",
            min_speciation_rate=0.1,
            times=0.1,
        )
        self.assertEqual([0.0, 0.1], sim.times)
        sim = Simulation()
        sim.set_simulation_parameters(
            seed=10000,
            task=1000000,
            output_directory="output",
            min_speciation_rate=0.1,
            times=[10, 100],
        )
        self.assertEqual([0.0, 10.0, 100.0], sim.times)
        sim = Simulation()
        sim.set_simulation_parameters(
            seed=10000,
            task=1000000,
            output_directory="output",
            min_speciation_rate=0.1,
            times=[100.0],
        )
        self.assertEqual([0.0, 100.0], sim.times)

    def testProtractedParameters(self):
        """Tests that the protracted paramaters are obtained correctly."""

        sim = Simulation()
        sim.protracted = True
        self.assertTrue(sim.get_protracted())
        sim = Simulation()
        self.assertEqual(27, sim.run_simple(6, 17, "output", 0.1, 4, 10))
        self.assertFalse(sim.get_protracted())

    def raise_ioerror(self, path):
        """For mocking modules."""
        raise IOError

    def return_true(self):
        """For mocking modules"""
        return True

    @patch.object(CoalescenceTree, "set_database", raise_ioerror)
    @patch.object(CoalescenceTree, "is_protracted", return_true)
    def testGetProtractedFailure(self):
        """Tests that errors while opening the database are handled correctly."""
        sim = Simulation()
        sim.output_database = os.path.join("sample", "data_old1.db")
        self.assertTrue(sim.get_protracted())

    def testCheckReproductionMap(self):
        """Tests that the reproduction map configuration is correctly identified"""
        sim = Simulation()
        sim.reproduction_map.file_name = "path"
        sim.coarse_map.file_name = "path"
        with self.assertRaises(ValueError):
            sim.check_reproduction_map()

    def testCheckDeathMap(self):
        """Tests that the death map configuration is correctly identified"""
        sim = Simulation()
        sim.death_map.file_name = "path"
        sim.coarse_map.file_name = "path"
        with self.assertRaises(ValueError):
            sim.check_death_map()

    def mock_check_map(self):
        """For mocking checking if map exists"""
        pass

    @patch.object(Simulation, "check_dispersal_map", mock_check_map)
    def testAddDispersalMap(self):
        """Tests that a dispersal map can be added correctly."""
        sim = Simulation()
        sim.add_dispersal_map("a_map.tif")
        self.assertEqual("a_map.tif", sim.dispersal_map.file_name)
        m = Map()
        m.file_name = "a_map.tif"
        sim = Simulation()
        sim.add_dispersal_map(m)
        self.assertEqual("a_map.tif", sim.dispersal_map.file_name)

    @patch.object(Simulation, "check_reproduction_map", mock_check_map)
    def testAddReproductionMap(self):
        """Tests that a dispersal map can be added correctly."""
        sim = Simulation()
        sim.add_reproduction_map("a_map.tif")
        self.assertEqual("a_map.tif", sim.reproduction_map.file_name)
        m = Map()
        m.file_name = "a_map.tif"
        sim = Simulation()
        sim.add_reproduction_map(m)
        self.assertEqual("a_map.tif", sim.reproduction_map.file_name)

    @patch.object(Simulation, "check_death_map", mock_check_map)
    def testAddDeathMap(self):
        """Tests that a death map can be added correctly."""
        sim = Simulation()
        sim.add_death_map("a_map.tif")
        self.assertEqual("a_map.tif", sim.death_map.file_name)
        m = Map()
        m.file_name = "a_map.tif"
        sim = Simulation()
        sim.add_death_map(m)
        self.assertEqual("a_map.tif", sim.death_map.file_name)

    def testSpatialErrors(self):
        """Tests that an error is raised for spatial sampling a non-spatial simulation."""
        sim = Simulation()
        with self.assertRaises(ValueError):
            sim.set_simulation_parameters(
                seed=10000,
                task=1000000,
                output_directory="output",
                min_speciation_rate=0.1,
                spatial=False,
                uses_spatial_sampling=True,
            )
        sim = Simulation()
        with self.assertRaises(ValueError):
            sim.set_simulation_parameters(
                seed=10000,
                task=1000000,
                output_directory="output",
                min_speciation_rate=0.1,
                landscape_type="bleh",
            )
        sim = Simulation(logging_level=40)
        sim.set_simulation_parameters(
            seed=10000,
            task=1000000,
            output_directory="output",
            min_speciation_rate=0.1,
        )
        sim.set_simulation_parameters(
            seed=10000,
            task=1000000,
            output_directory="output",
            min_speciation_rate=0.1,
        )

    def testParametersNotSetError(self):
        """Tests that an error is raised when the parameters aren't set."""
        sim = Simulation()
        with self.assertRaises(RuntimeError):
            sim.check_simulation_parameters()
        sim.full_config_file = os.path.join("output", "tmp_output2", "full_config.txt")
        sim.is_setup_param = True
        with self.assertRaises(RuntimeError):
            sim.check_simulation_parameters()
        sim.seed = 1
        # sim.output_directory = None
        with self.assertRaises(RuntimeError):
            sim.check_simulation_parameters()
        sim.output_directory = os.path.join("output", "tmp_output")

        sim.set_map("null", 10, 10)
        sim.check_simulation_parameters()
        self.assertTrue(os.path.exists(sim.output_directory))
        self.assertTrue(os.path.exists(os.path.join("output", "tmp_output2")))

    def testResumeError(self):
        """Tests that resuming fails if the output directory doesn't exist"""
        sim = Simulation()
        with self.assertRaises(IOError):
            sim.resume_coalescence("notadir", 1, 1, 10)

    def testDatabaseSettingErrors(self):
        """Tests that the database can be set correctly."""
        sim = Simulation()
        sim.output_database = os.path.join("sample", "sample.db")
        with self.assertRaises(IOError):
            sim.check_sql_database()
        sim.output_database = os.path.join("sample", "not_a_file.db")
        with self.assertRaises(IOError):
            sim.check_sql_database(expected=True)

    def testRunChecksErrors(self):
        """Tests errors are raised when checks are not complete."""
        sim = Simulation()
        with self.assertRaises(RuntimeError):
            sim.check_file_parameters()

    def testRunCoalescenceCreatesOutput(self):
        """Tests that running coalescence creates output before running."""
        sim = Simulation()
        sim.is_setup_complete = True
        sim.output_directory = os.path.join("output", "tmp_output3")

        class tmp:
            pass

        sim.c_simulation = tmp
        sim.c_simulation.run = self.return_true
        self.assertTrue(sim.run_coalescence())
        self.assertTrue(os.path.exists(os.path.join("output", "tmp_output3")))


class TestRamEstimation(unittest.TestCase):
    """Tests that the RAM estimation works as intended"""

    def testPersistentRamEstimation(self):
        """Tests the calculations for persistent RAM usage."""
        sim = Simulation()
        sim.set_simulation_parameters(1, 1000, output_directory="output", min_speciation_rate=0.1)
        sim.set_map_files(
            "null",
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )
        sim.add_historical_map(
            fine_file=os.path.join("sample", "SA_sample_fine_pristine1.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse_pristine1.tif"),
            time=10,
            rate=0.0,
        )
        self.assertEqual(9689724, sim.persistent_ram_usage())
        sim = Simulation()
        sim.set_simulation_parameters(1, 1000, output_directory="output", min_speciation_rate=0.1)
        sim.set_map_files(
            sample_file=os.path.join("sample", "SA_sample_coarse.tif"),
            fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )
        sim.add_dispersal_map(dispersal_map=os.path.join("sample", "dispersal_fine.tif"))
        sim.add_death_map(death_map=os.path.join("sample", "SA_sample_coarse_pristine.tif"))
        sim.add_reproduction_map(reproduction_map=os.path.join("sample", "SA_sample_coarse_pristine.tif"))
        self.assertEqual(30135, sim.persistent_ram_usage())


class TestRamOptimistation(unittest.TestCase):
    """Tests that the RAM optimisation works as intended."""

    def testBasicOptimisation(self):
        """Test that a basic optimisation process works."""
        sim = Simulation()
        sim.set_simulation_parameters(seed=1, task=2, output_directory="output", min_speciation_rate=0.1)
        sim.set_map_files(
            "null",
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )
        sim.optimise_ram(0.0005)
        self.assertEqual(1, sim.grid.x_size)
        expected_dict = {
            "grid_x_size": 1,
            "grid_y_size": 1,
            "sample_x_offset": 0,
            "sample_y_offset": 0,
            "grid_file_name": "set",
        }
        self.assertEqual(expected_dict, sim.get_optimised_solution())
        expected_dict2 = {
            "grid_x_size": 10,
            "grid_y_size": 10,
            "sample_x_offset": 0,
            "sample_y_offset": 0,
            "grid_file_name": "set",
        }
        sim.set_optimised_solution(expected_dict2)
        self.assertEqual(expected_dict2, sim.get_optimised_solution())

    def testOptimisationRaisesError(self):
        """Tests that errors are raised correctly."""
        sim = Simulation()
        sim.set_simulation_parameters(seed=1, task=2, output_directory="output", min_speciation_rate=0.1)
        sim.set_map_files(
            "null",
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )
        sim.deme = 0
        with self.assertRaises(ValueError):
            sim.optimise_ram(0.1)
        sim.deme = 1
        with self.assertRaises(MemoryError):
            sim.optimise_ram(0.00001)
        with self.assertRaises(MemoryError):
            sim.optimise_ram(0.0000001)
        sim = Simulation()
        sim.set_simulation_parameters(seed=1, task=2, output_directory="output", min_speciation_rate=0.1)
        sim.set_map_files(
            "null",
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )


@skipLongTest
class TestSimulationUsingGillespieEquality(unittest.TestCase):
    """
    Tests simulations using the gillespie algorithm match equivalent simulations not using the Gillespie algorithm.
    """

    @classmethod
    def setUpClass(cls):
        cls.baseline_richness_values = []
        speciation_rates = [0.001, 0.01, 0.1, 0.9]
        for seed in range(10, 20):
            baseline_simulation = Simulation(logging_level=50)
            baseline_simulation.set_simulation_parameters(
                seed=seed,
                task=2,
                output_directory="output",
                min_speciation_rate=0.001,
                deme=1,
                sample_size=0.01,
            )
            baseline_simulation.set_map_files(
                sample_file="null",
                fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
                coarse_file="none",
            )
            baseline_simulation.add_dispersal_map(dispersal_map=os.path.join("sample", "dispersal_fine2.tif"))
            baseline_simulation.set_speciation_rates(speciation_rates=speciation_rates)
            baseline_simulation.run()
            for ref in range(1, len(speciation_rates) + 1):
                cls.baseline_richness_values.append((ref, baseline_simulation.get_species_richness(ref)))
        cls.gillespie_richness_values = []
        for seed, gillespie_generation in zip(range(10, 20), range(10, 2020, 200)):
            gillespie_simulation = Simulation(logging_level=50)
            gillespie_simulation.set_simulation_parameters(
                seed=seed,
                task=3,
                output_directory="output",
                min_speciation_rate=0.001,
                deme=1,
                sample_size=0.01,
            )
            gillespie_simulation.set_speciation_rates(speciation_rates=speciation_rates)
            gillespie_simulation.set_map_files(
                sample_file="null",
                fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
                coarse_file="none",
            )
            gillespie_simulation.add_dispersal_map(dispersal_map=os.path.join("sample", "dispersal_fine2.tif"))
            gillespie_simulation.add_gillespie(gillespie_generation)
            gillespie_simulation.run()
            for ref in range(1, len(speciation_rates) + 1):
                cls.gillespie_richness_values.append((ref, gillespie_simulation.get_species_richness(ref)))

    @staticmethod
    def setupGillespie(**kwargs):
        """Sets up a simple Gillespie simulation."""
        s = Simulation()
        s.set_simulation_parameters(
            seed=12, task=3, output_directory="output", min_speciation_rate=0.001, deme=1, sample_size=0.01, **kwargs
        )
        return s

    def testChecksForGillespieCompability(self):
        """Checks that simulations which can't use Gillespie throw the correct errors."""
        coarse_maps = ["null", os.path.join("sample", "SA_sample_coarse.tif")]
        for coarse_map in coarse_maps:
            s = self.setupGillespie()
            with self.assertRaises(RuntimeError):
                s.add_gillespie(10)
            s.set_map_files(
                sample_file="null",
                fine_file=os.path.join("sample", "SA_sample_fine.tif"),
                coarse_file=coarse_map,
            )
            s.add_dispersal_map("null")
            with self.assertRaises(ValueError):
                s.add_gillespie(10)
        s = self.setupGillespie()
        s.set_map("null", 10, 10)
        s.add_dispersal_map("null")
        with self.assertRaises(ValueError):
            s.add_gillespie(-10)

    def testCheckCanUseGillespie(self):
        """Checks that the Gillespie checks are accurate."""
        s = Simulation()
        with self.assertRaises(RuntimeError):
            s.check_can_use_gillespie()
        s = self.setupGillespie()
        with self.assertRaises(RuntimeError):
            s.check_can_use_gillespie()
        s.set_map("null", 10, 10)
        self.assertFalse(s.check_can_use_gillespie())
        s.add_dispersal_map("null")
        self.assertTrue(s.check_can_use_gillespie())
        s = Simulation()
        s.set_simulation_parameters(
            seed=10,
            task=3,
            output_directory="output",
            min_speciation_rate=0.000001,
            deme=1000,
            sample_size=0.00001,
            spatial=False,
        )
        self.assertFalse(s.check_can_use_gillespie())
        s = Simulation()
        s.set_simulation_parameters(
            seed=10,
            task=3,
            output_directory="output",
            min_speciation_rate=0.000001,
            deme=1000,
            sample_size=0.00001,
            protracted=True,
            min_speciation_gen=10.0,
            max_speciation_gen=100.0,
        )
        s.set_map("null", 10, 10)
        s.add_dispersal_map("null")
        self.assertFalse(s.check_can_use_gillespie())
        s = self.setupGillespie()
        s.set_map_files(
            "null",
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )
        s.add_dispersal_map("null")
        self.assertFalse(s.check_can_use_gillespie())

    def testSpeciesRichnessValuesSimilar(self):
        """Checks that the species richness values are similar between implementations of Gillespie."""
        baseline_mean_values = {}
        baseline_all_values = {}
        for i in set(x for x, _ in self.baseline_richness_values):
            vals = [richness for ref, richness in self.baseline_richness_values if ref == i]
            baseline_all_values[i] = vals
            baseline_mean_values[i] = sum(vals) / len(vals)

        gillespie_mean_values = {}
        gillespie_all_values = {}
        for i in set(x for x, _ in self.gillespie_richness_values):
            vals = [richness for ref, richness in self.gillespie_richness_values if ref == i]
            gillespie_all_values[i] = vals
            gillespie_mean_values[i] = sum(vals) / len(vals)
        for k, v in baseline_mean_values.items():
            self.assertAlmostEqual(v, gillespie_mean_values[k], delta=v / 10)


@skipLongTest
class TestSimulationUsingGillespieDeathMaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline_richness_values = []
        speciation_rates = [0.001, 0.01, 0.1, 0.9]
        for seed in range(40, 50):
            baseline_simulation = Simulation(logging_level=50)
            baseline_simulation.set_simulation_parameters(
                seed=seed,
                task=2,
                output_directory="output",
                min_speciation_rate=0.001,
                deme=2,
                sample_size=0.01,
            )
            baseline_simulation.set_map_files(
                sample_file="null",
                fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
                coarse_file="none",
            )
            baseline_simulation.add_dispersal_map(dispersal_map=os.path.join("sample", "dispersal_fine2.tif"))
            baseline_simulation.add_death_map(os.path.join("sample", "SA_death.tif"))
            baseline_simulation.set_speciation_rates(speciation_rates=speciation_rates)
            baseline_simulation.run()
            for ref in range(1, len(speciation_rates) + 1):
                cls.baseline_richness_values.append((ref, baseline_simulation.get_species_richness(ref)))
        cls.gillespie_richness_values = []
        for seed, gillespie_generation in zip(range(40, 50), range(10, 2020, 200)):
            gillespie_simulation = Simulation(logging_level=50)
            gillespie_simulation.set_simulation_parameters(
                seed=seed,
                task=3,
                output_directory="output",
                min_speciation_rate=0.001,
                deme=2,
                sample_size=0.01,
            )
            gillespie_simulation.set_speciation_rates(speciation_rates=speciation_rates)
            gillespie_simulation.set_map_files(
                sample_file="null",
                fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
                coarse_file="none",
            )
            gillespie_simulation.add_dispersal_map(dispersal_map=os.path.join("sample", "dispersal_fine2.tif"))
            gillespie_simulation.add_death_map(os.path.join("sample", "SA_death.tif"))
            gillespie_simulation.add_gillespie(gillespie_generation)
            gillespie_simulation.run()
            for ref in range(1, len(speciation_rates) + 1):
                cls.gillespie_richness_values.append((ref, gillespie_simulation.get_species_richness(ref)))

    def testSpeciesRichnessValuesSimilar(self):
        """Checks that the species richness values are similar between implementations of Gillespie."""
        baseline_mean_values = {}
        baseline_all_values = {}
        for i in set(x for x, _ in self.baseline_richness_values):
            vals = [richness for ref, richness in self.baseline_richness_values if ref == i]
            baseline_all_values[i] = vals
            baseline_mean_values[i] = sum(vals) / len(vals)

        gillespie_mean_values = {}
        gillespie_all_values = {}
        for i in set(x for x, _ in self.gillespie_richness_values):
            vals = [richness for ref, richness in self.gillespie_richness_values if ref == i]
            gillespie_all_values[i] = vals
            gillespie_mean_values[i] = sum(vals) / len(vals)
        for k, v in baseline_mean_values.items():
            self.assertAlmostEqual(v, gillespie_mean_values[k], delta=v / 10)


@skipLongTest
class TestSimulationUsingGillespieLarge(unittest.TestCase):
    """Tests simulations using the gillespie algorithm."""

    @classmethod
    def setUpClass(cls):
        cls.gillespie_simulation = Simulation(logging_level=50)
        cls.gillespie_simulation.set_simulation_parameters(
            seed=21,
            task=3,
            output_directory="output",
            min_speciation_rate=0.000001,
            deme=100,
            sample_size=0.001,
        )
        cls.gillespie_simulation.set_map_files(
            sample_file="null",
            fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
            coarse_file="none",
        )
        cls.gillespie_simulation.add_dispersal_map(dispersal_map=os.path.join("sample", "dispersal_fine3.tif"))
        cls.gillespie_simulation.add_gillespie(10)
        cls.gillespie_simulation.run()
        cls.gillespie_simulation2 = Simulation()
        cls.gillespie_simulation2.set_simulation_parameters(
            seed=21,
            task=4,
            output_directory="output",
            min_speciation_rate=0.000001,
            deme=100,
            sample_size=0.001,
        )
        cls.gillespie_simulation2.set_map_files(
            sample_file="null",
            fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
            coarse_file="none",
        )
        cls.gillespie_simulation2.add_dispersal_map(dispersal_map=os.path.join("sample", "dispersal_fine3.tif"))

        cls.gillespie_simulation2.add_gillespie(0)
        cls.gillespie_simulation2.run()

    def testSpeciesRichnessValuesSimilar(self):
        """Checks that the species richness values are similar between implementations of Gillespie."""
        self.assertEqual(208, self.gillespie_simulation.get_species_richness())
        self.assertEqual(208, self.gillespie_simulation2.get_species_richness())
