"""
Runs a variety of high-level tests to ensure that system integration works as intended, mostly utilising the Simulation
and CoalescenceTree
"""
import logging
import os
import platform
import shutil
import sqlite3
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

try:
    from cStringIO import StringIO  # Python 2 string support
except ImportError:
    from io import StringIO

from setup_tests import setUpAll, tearDownAll, skipLongTest

from pycoalescence import Simulation, CoalescenceTree


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


class TestImport(unittest.TestCase):
    """Tests that the extra parts of the package can be imported."""

    def testImportInstaller(self):
        """Tests the installer can be imported correctly."""
        try:
            import pycoalescence.installer
        except ImportError as ie:
            self.fail("Cannot import pycoalescence.installer: {}".format(ie))
        try:
            from pycoalescence.installer import Installer
        except ImportError as ie:
            self.fail("Cannot import Installer from pycoalescence.installer: {}".format(ie))

    def testImportHpcSetup(self):
        """Tests the import of hpc_setup."""
        try:
            import pycoalescence.hpc_setup
        except ImportError as ie:
            self.fail("Cannot import hpc_setup: {}.".format(ie))


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
        self.coal.set_simulation_parameters(
            2,
            5,
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
        self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()
        self.tree.set_database("output/data_5_2.db")
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
        actual_sim_parameters = dict(
            seed=2,
            task=5,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=1.0,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="null",
            coarse_map_x=20,
            coarse_map_y=20,
            coarse_map_x_offset=0,
            coarse_map_y_offset=0,
            coarse_map_scale=1.0,
            fine_map_file="null",
            fine_map_x=10,
            fine_map_y=10,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=10,
            grid_y=10,
            sample_x=10,
            sample_y=10,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key])
        # self.assertDictEqual(params, actual_sim_parameters)
        self.assertEqual(self.tree.get_job()[0], 2)
        self.assertEqual(self.tree.get_job()[1], 5)

    def testRichness(self):
        """
        Tests that the richness stored in the SQL file is correct.
        Note that this is actually a test of both the C++ (necsim) and the Python front-end.
        """
        self.assertEqual(36, self.tree.get_species_richness(1))
        self.assertEqual(53, self.tree.get_species_richness(2))

    def testRichnessLandscape(self):
        """
        Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
        """
        richness_01 = self.tree.get_species_richness(1)
        richness_02 = self.tree.get_species_richness(2)
        self.assertEqual(36, richness_01)
        self.assertEqual(53, richness_02)


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
        self.coal.set_simulation_parameters(
            2,
            2,
            "output",
            0.1,
            4,
            4,
            1,
            1.0,
            2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            m_prob=1,
            landscape_type=True,
        )
        self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()
        self.tree.set_database("output/data_2_2.db")
        self.tree.calculate_octaves()
        self.tree.calculate_richness()

    def testSimParamsStored(self):
        """
        Tests the full simulation setup, checking species richness is correct and species abundance calculations are
        correct.
        :return:
        """
        params = self.tree.get_simulation_parameters()
        actual_sim_parameters = dict(
            seed=2,
            task=2,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=1.0,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="null",
            coarse_map_x=20,
            coarse_map_y=20,
            coarse_map_x_offset=0,
            coarse_map_y_offset=0,
            coarse_map_scale=1.0,
            fine_map_file="null",
            fine_map_x=10,
            fine_map_y=10,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=10,
            grid_y=10,
            sample_x=10,
            sample_y=10,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=1.0,
            cutoff=0.0,
            landscape_type="infinite",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
        self.assertEqual(self.tree.get_job()[0], 2)
        self.assertEqual(self.tree.get_job()[1], 2)

    def testRichness(self):
        """Tests that the richness stored in the SQL file is correct."""
        self.assertEqual(69, self.tree.get_species_richness(1))
        self.assertEqual(73, self.tree.get_species_richness(2))


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
        cls.coal.set_simulation_parameters(
            1,
            1,
            "output",
            0.1,
            4,
            4,
            1,
            1.0,
            2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
            landscape_type=True,
        )
        cls.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "none", "none")
        cls.coal.set_speciation_rates([0.1, 0.2])
        cls.coal.run()
        cls.tree.set_database("output/data_1_1.db")
        cls.tree.calculate_octaves()
        cls.tree.calculate_richness()

    def testSimParamsStored(self):
        """
        Tests the full simulation setup, checking species richness is correct and species abundance calculations are
        correct.
        :return:
        """
        params = self.tree.get_simulation_parameters()
        actual_sim_parameters = dict(
            seed=1,
            task=1,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=1.0,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="null",
            coarse_map_x=20,
            coarse_map_y=20,
            coarse_map_x_offset=0,
            coarse_map_y_offset=0,
            coarse_map_scale=1.0,
            fine_map_file="null",
            fine_map_x=10,
            fine_map_y=10,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=10,
            grid_y=10,
            sample_x=10,
            sample_y=10,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="fat-tail",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="infinite",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key])
        self.assertEqual(self.tree.get_job()[0], 1)
        self.assertEqual(self.tree.get_job()[1], 1)

    def testRichness(self):
        """
        Tests that the richness stored in the SQL file is correct.
        Note that this is actually a test of both the C++ (necsim) and the Python front-end.
        """
        self.assertEqual(80, self.tree.get_species_richness(1))
        self.assertEqual(88, self.tree.get_species_richness(2))

    def testRichnessLandscape(self):
        """
        Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
        """
        richness_01 = self.tree.get_species_richness(1)
        richness_02 = self.tree.get_species_richness(2)
        self.assertEqual(80, richness_01)
        self.assertEqual(88, richness_02)


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
        self.coal.set_simulation_parameters(
            3, 3, "output", 0.1, 4, 4, 1, 0.1, 2, dispersal_relative_cost=1, min_num_species=1, cutoff=0.0
        )
        self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif")
        self.coal.detect_map_dimensions()
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()
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
        actual_sim_parameters = dict(
            seed=3,
            task=3,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=0.1,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="none",
            coarse_map_x=13,
            coarse_map_y=13,
            coarse_map_x_offset=0,
            coarse_map_y_offset=0,
            coarse_map_scale=1.0,
            fine_map_file="sample/SA_sample_fine.tif",
            fine_map_x=13,
            fine_map_y=13,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
        self.assertEqual(self.tree.get_job()[0], 3)
        self.assertEqual(self.tree.get_job()[1], 3)

    def testRichness(self):
        """
        Tests that the richness stored in the SQL file is correct.
        Note that this is actually a test of both the C++ (necsim) and the Python front-end.
        """
        self.assertEqual(2587, self.tree.get_species_richness(1))
        self.assertEqual(3087, self.tree.get_species_richness(2))

    def testRichnessLandscape(self):
        """
        Tests the landscape richness function which calculates landscape richness for each time and speciation rate.
        """
        richness_01 = self.tree.get_species_richness(1)
        richness_02 = self.tree.get_species_richness(2)
        self.assertEqual(2587, richness_01)
        self.assertEqual(3087, richness_02)


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
        self.coal.set_simulation_parameters(
            1,
            29,
            "output",
            0.1,
            4,
            4,
            1,
            0.1,
            2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
            landscape_type="tiled_fine",
        )
        self.coal.set_map_files("null", fine_file="sample/SA_sample_fine.tif")
        self.coal.detect_map_dimensions()
        # self.coal.set_map_parameters("null", 10, 10, "sample/PALSAR_CONGO_SAMPLE.tif", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1,"null", "null")
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()
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
        actual_sim_parameters = dict(
            seed=1,
            task=29,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=0.1,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="none",
            coarse_map_x=13,
            coarse_map_y=13,
            coarse_map_x_offset=0,
            coarse_map_y_offset=0,
            coarse_map_scale=1.0,
            fine_map_file="sample/SA_sample_fine.tif",
            fine_map_x=13,
            fine_map_y=13,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="tiled_fine",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
        self.assertEqual(self.tree.get_job()[0], 1)
        self.assertEqual(self.tree.get_job()[1], 29)

    def testRichness(self):
        """Tests that the richness stored in the SQL file is correct."""
        self.assertEqual(3359, self.tree.get_species_richness(1))
        self.assertEqual(3468, self.tree.get_species_richness(2))


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
        self.coal.set_simulation_parameters(
            1,
            30,
            "output",
            0.1,
            4,
            4,
            1,
            0.1,
            2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
            landscape_type="tiled_coarse",
        )
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal2 = Simulation()
        self.coal2.set_simulation_parameters(
            seed=1,
            task=33,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
            landscape_type="closed",
        )
        self.coal2.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal2.set_speciation_rates([0.1, 0.2])
        self.coal.run()
        self.coal2.run()
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
        actual_sim_parameters = dict(
            seed=1,
            task=30,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=0.1,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="sample/SA_sample_coarse.tif",
            coarse_map_x=35,
            coarse_map_y=41,
            coarse_map_x_offset=11,
            coarse_map_y_offset=14,
            coarse_map_scale=1.0,
            fine_map_file="sample/SA_sample_fine.tif",
            fine_map_x=13,
            fine_map_y=13,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="tiled_coarse",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))
        self.assertEqual(self.tree.get_job()[0], 1)
        self.assertEqual(self.tree.get_job()[1], 30)

    def testRichnessGreater(self):
        """
        Tests that the richness produced by the tiled map is greater than that produced by the closed map.
        """
        self.assertGreater(self.tree.get_species_richness(1), self.tree2.get_species_richness(1))

    def testRichness(self):
        """Tests that the richness stored in the SQL file is correct."""
        self.assertEqual(3460, self.tree.get_species_richness(1))
        self.assertEqual(3613, self.tree.get_species_richness(2))


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
        self.coal.set_simulation_parameters(
            seed=1,
            task=34,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
            landscape_type="closed",
        )
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", death_map="sample/SA_sample_reproduction.tif"
        )
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()
        self.coal2 = Simulation()
        self.tree2 = CoalescenceTree()
        self.coal2.set_simulation_parameters(
            seed=1,
            task=35,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
            landscape_type="closed",
        )
        self.coal2.set_map_files("null", fine_file="sample/SA_sample_fine.tif")
        self.coal2.set_speciation_rates([0.1, 0.2])
        self.coal2.run()
        self.tree.set_database(self.coal)
        self.tree2.set_database(self.coal2)

    def testRichnessDifferent(self):
        """
        Tests that the richness produced by a probability map is not the same as the richness produced without.
        """
        self.assertNotEqual(self.coal.get_species_richness(1), self.coal2.get_species_richness(1))
        self.assertEqual(2621, self.coal.get_species_richness(1))

    def testReproductionMapNullRaisesError(self):
        """
        Tests that an error is raised when the reproduction map has a zero value where the density map does not.
        """
        c = Simulation(logging_level=logging.CRITICAL)
        c.set_simulation_parameters(
            seed=2,
            task=34,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
            landscape_type="closed",
        )
        c.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", death_map="sample/SA_sample_reproduction_invalid.tif"
        )
        with self.assertRaises(RuntimeError):
            c.finalise_setup()


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
        self.coal.set_simulation_parameters(3, 4, "output", 0.1, 4, 4, 1, 1, 2, dispersal_relative_cost=1, cutoff=0.0)
        self.coal.set_map_files("null", fine_file="sample/bytesample.tif")
        self.coal.detect_map_dimensions()
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()

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
        by necsim
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
        self.coal.set_simulation_parameters(
            4,
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
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.detect_map_dimensions()
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.run()
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
        actual_sim_parameters = dict(
            seed=4,
            task=4,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=0.01,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="sample/SA_sample_coarse.tif",
            coarse_map_x=35,
            coarse_map_y=41,
            coarse_map_x_offset=11,
            coarse_map_y_offset=14,
            coarse_map_scale=1.0,
            fine_map_file="sample/SA_sample_fine.tif",
            fine_map_x=13,
            fine_map_y=13,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="fat-tail",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(
                params[key],
                actual_sim_parameters[key],
                msg="Error in {}: {}!={}".format(key, params[key], actual_sim_parameters[key]),
            )
        self.assertEqual(self.tree.get_job()[0], 4, msg="Job number not stored correctly.")
        self.assertEqual(self.tree.get_job()[1], 4, msg="Job number not stored correctly.")

    def testRichness(self):
        """Tests that the richness stored in the SQL file is correct."""
        self.assertEqual(279, self.tree.get_species_richness(1))
        self.assertEqual(281, self.tree.get_species_richness(2))

    def testNumberIndividuals(self):
        """Tests the number of simulated individuals is correct"""
        self.assertEqual(self.tree.get_number_individuals(community_reference=1), 284)


class TestSimulationDemeProportions(unittest.TestCase):
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

        self.coal.set_simulation_parameters(
            seed=5, task=4, output_directory="output", min_speciation_rate=0.1, sigma=4, deme=0.25
        )
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.run()
        self.coal2 = Simulation()

        self.coal2.set_simulation_parameters(
            seed=6, task=4, output_directory="output", min_speciation_rate=0.1, sigma=4, deme=0.01
        )
        self.coal2.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal2.run()
        self.tree = CoalescenceTree(self.coal)
        self.tree2 = CoalescenceTree(self.coal2)

    def testSimParamsStored(self):
        """
        Tests the full simulation setup, checking species richness is correct and species abundance calculations are
        correct.
        :return:
        """
        params = self.tree.get_simulation_parameters()
        actual_sim_parameters = dict(
            seed=5,
            task=4,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=1.0,
            deme=0.25,
            sample_size=1.0,
            max_time=3600.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="sample/SA_sample_coarse.tif",
            coarse_map_x=35,
            coarse_map_y=41,
            coarse_map_x_offset=11,
            coarse_map_y_offset=14,
            coarse_map_scale=1.0,
            fine_map_file="sample/SA_sample_fine.tif",
            fine_map_x=13,
            fine_map_y=13,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(
                params[key],
                actual_sim_parameters[key],
                msg="Error in {}: {}!={}".format(key, params[key], actual_sim_parameters[key]),
            )
        self.assertEqual(self.tree.get_job()[0], 5, msg="Seed not stored correctly.")
        self.assertEqual(self.tree.get_job()[1], 4, msg="Job number not stored correctly.")

    def testNumberIndividuals(self):
        """Tests that the number of simulated individuals is correct"""
        self.assertEqual(396, self.tree2.get_number_individuals(community_reference=1))
        self.assertEqual(9549, self.tree.get_number_individuals(community_reference=1))


class TestSimulationDemeOversampling(unittest.TestCase):
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

        self.coal.set_simulation_parameters(
            seed=7, task=4, output_directory="output", min_speciation_rate=0.1, sigma=4, deme=0.01, sample_size=1.5
        )
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.run()
        self.tree = CoalescenceTree(self.coal)

    def testSimParamsStored(self):
        """
        Tests the full simulation setup, checking species richness is correct and species abundance calculations are
        correct.
        :return:
        """
        params = self.tree.get_simulation_parameters()
        actual_sim_parameters = dict(
            seed=7,
            task=4,
            output_dir="output",
            speciation_rate=0.1,
            sigma=4.0,
            tau=1.0,
            deme=0.01,
            sample_size=1.5,
            max_time=3600.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="null",
            coarse_map_file="sample/SA_sample_coarse.tif",
            coarse_map_x=35,
            coarse_map_y=41,
            coarse_map_x_offset=11,
            coarse_map_y_offset=14,
            coarse_map_scale=1.0,
            fine_map_file="sample/SA_sample_fine.tif",
            fine_map_x=13,
            fine_map_y=13,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
        for key in params.keys():
            self.assertEqual(
                params[key],
                actual_sim_parameters[key],
                msg="Error in {}: {}!={}".format(key, params[key], actual_sim_parameters[key]),
            )
        self.assertEqual(self.tree.get_job()[0], 7, msg="Seed not stored correctly.")
        self.assertEqual(self.tree.get_job()[1], 4, msg="Job number not stored correctly.")

    def testNumberIndividuals(self):
        """Tests that the number of simulated individuals is correct"""
        self.assertEqual(557, self.tree.get_number_individuals(community_reference=1))


class TestSimulationNonSpatial(unittest.TestCase):
    """
    Performs all the sanity checks for non spatially explicit simulations, including protracted sims.
    """

    @classmethod
    def setUpClass(cls):
        """
        Runs the simulations to be used in testing
        :return:
        """
        cls.c = Simulation(logging_level=logging.ERROR)
        cls.c.set_simulation_parameters(
            seed=1, task=39, output_directory="output", min_speciation_rate=1, deme=100, spatial=False
        )
        cls.c.run()
        cls.c2 = Simulation(logging_level=logging.ERROR)
        cls.c2.set_simulation_parameters(
            seed=1, task=40, output_directory="output", min_speciation_rate=0.5, deme=100, spatial=False
        )
        cls.c2.run()
        cls.c3 = Simulation(logging_level=logging.ERROR)
        cls.c3.set_simulation_parameters(
            seed=1,
            task=41,
            output_directory="output",
            min_speciation_rate=0.5,
            deme=100,
            spatial=False,
            protracted=True,
            min_speciation_gen=0,
            max_speciation_gen=1,
        )
        cls.c3.run()
        cls.c4 = Simulation(logging_level=logging.ERROR)
        cls.c4.set_simulation_parameters(
            seed=1,
            task=42,
            output_directory="output",
            min_speciation_rate=0.5,
            deme=100,
            spatial=False,
            protracted=True,
            min_speciation_gen=100,
            max_speciation_gen=1000,
        )
        cls.c4.run()

    def testNSESanityChecks(self):
        """
        Runs the sanity checks for non-spatially explicit simulations
        """
        self.assertEqual(100, self.c.get_species_richness())
        self.assertEqual(67, self.c2.get_species_richness())

    def testNSELocations(self):
        """
        Tests that all locations for lineages is 0
        """
        t = CoalescenceTree(self.c2)
        t.set_speciation_parameters(speciation_rates=[0.6, 0.7], record_spatial=True, record_fragments=False)
        t.apply()
        locations = t.get_species_locations()
        for row in locations:
            self.assertEqual(0, row[1])
            self.assertEqual(0, row[2])

    def testProtractedNSESanityChecks(self):
        """
        Tests that protracted simulations work with NSE sims.
        """
        self.assertGreater(self.c3.get_species_richness(1), self.c2.get_species_richness(1))
        self.assertLess(self.c4.get_species_richness(1), self.c3.get_species_richness(1))


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
        cls.coal.set_simulation_parameters(
            seed=6,
            task=8,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        cls.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        cls.coal.set_speciation_rates([0.5, 0.7])
        cls.coal.run()
        cls.tree.set_database("output/data_8_6.db")
        cls.tree.set_speciation_parameters(
            speciation_rates=[0.6, 0.7],
            record_spatial="T",
            record_fragments="F",
            sample_file="null",
            times=cls.coal.times_list,
        )
        # self.tree.apply()
        cls.tree.calculate_octaves()
        cls.tree.calculate_richness()

    def testSampleRichness(self):
        """
        Tests that the simulation using sampling returns the correct species richness.
        Also tests that both methods of obtaining species richness work.
        """
        self.tree.calculate_richness()
        self.assertEqual(1167, self.tree.get_species_richness(1))
        self.assertEqual(1171, self.tree.get_species_richness(2))
        self.assertEqual(self.tree.get_species_richness(1), self.tree.get_species_richness(1))
        self.assertEqual(self.tree.get_species_richness(2), self.tree.get_species_richness(2))
        self.assertEqual(self.tree.get_species_richness(3), self.tree.get_species_richness(3))


class TestCoalSampling2(unittest.TestCase):
    """
    Sample run with test cases to make sure the sample map relative sampling is taken into account.
    """

    @classmethod
    def setUpClass(cls):
        cls.coal = Simulation(logging_level=logging.CRITICAL)
        cls.coal.set_simulation_parameters(
            seed=7,
            task=8,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            deme=10,
            sample_size=1,
            max_time=2,
            uses_spatial_sampling=True,
        )
        cls.coal.set_map_files(sample_file="sample/null_sample.tif", fine_file="sample/null.tif")
        cls.coal.set_speciation_rates([0.5, 0.6])
        cls.coal.run()
        cls.tree = CoalescenceTree(cls.coal)
        cls.tree.set_speciation_parameters(
            speciation_rates=[0.5, 0.6], record_spatial=True, record_fragments="sample/FragmentsTest.csv"
        )
        cls.tree.apply()
        # Copy the simulation file to a backup
        shutil.copy2(cls.coal.output_database, "output/temp.db")

    def testNumberIndividuals(self):
        """
        Tests that the number of individuals simulated is correct.
        """
        self.assertEqual(356, self.tree.get_number_individuals())
        self.assertEqual(53, self.tree.get_number_individuals(fragment="fragment1"))
        self.assertEqual(53, self.tree.get_number_individuals(fragment="fragment1", community_reference=1))
        self.assertEqual(39, self.tree.get_number_individuals(fragment="fragment2"))
        self.assertEqual(39, self.tree.get_number_individuals(fragment="fragment2", community_reference=1))

    def testIncorrectFragmentsRaisesError(self):
        """
        Tests that having an incorrect fragments file raises an error as expected. Tests if either there are the wrong
        number of columns, or an failed conversion from string to integer/double.
        """
        for f in [1, 2, 3]:
            fragment_file = "sample/FragmentsTestFail{}.csv".format(f)
            with self.assertRaises(RuntimeError):
                t = CoalescenceTree("output/temp.db", logging_level=50)
                t.wipe_data()
                t.set_speciation_parameters(
                    speciation_rates=[0.5, 0.6], record_spatial=False, record_fragments=fragment_file
                )
                t.apply()


class TestCoalSampling3(unittest.TestCase):
    """
    Sample run with test cases to make sure the sample map relative sampling is taken into account, and the offsets
    from the grid are correctly applied.
    """

    @classmethod
    def setUpClass(cls):
        cls.coal = Simulation(logging_level=logging.CRITICAL)
        cls.coal.set_simulation_parameters(
            seed=9,
            task=8,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            deme=1,
            sample_size=0.1,
            max_time=2,
            uses_spatial_sampling=True,
        )
        cls.coal.set_map_files(sample_file="sample/null_sample.tif", fine_file="sample/SA_sample_coarse.tif")
        cls.coal.grid.x_size = 2
        cls.coal.grid.y_size = 2
        cls.coal.sample_map.x_offset = 4
        cls.coal.sample_map.y_offset = 4
        cls.coal.grid.file_name = "set"
        cls.coal.set_speciation_rates([0.5, 0.6])
        cls.coal.run()
        cls.tree = CoalescenceTree(cls.coal)
        cls.tree.set_speciation_parameters(
            speciation_rates=[0.5, 0.6], record_spatial=True, record_fragments="sample/FragmentsTest.csv"
        )
        cls.tree.apply()
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
        cls.coal.set_simulation_parameters(
            seed=10,
            task=8,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            deme=1,
            sample_size=1,
            max_time=2,
            uses_spatial_sampling=False,
        )
        cls.coal.set_map_files(
            sample_file="sample/null_sample.tif",
            fine_file="sample/SA_fine_expanded.tif",
            coarse_file="sample/SA_coarse_expanded.tif",
        )
        cls.coal.grid.x_size = 2
        cls.coal.grid.y_size = 2
        cls.coal.sample_map.x_offset = 4
        cls.coal.sample_map.y_offset = 4
        cls.coal.grid.file_name = "set"
        cls.coal.set_speciation_rates([0.5, 0.6])
        cls.coal.run()
        cls.tree = CoalescenceTree(cls.coal)
        cls.tree.set_speciation_parameters(
            speciation_rates=[0.5, 0.6], record_spatial=True, record_fragments="sample/FragmentsTest.csv"
        )
        cls.tree.apply()
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
        cls.coal = Simulation(logging_level=logging.CRITICAL)
        cls.coal.set_simulation_parameters(
            seed=8,
            task=8,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            deme=10,
            sample_size=1,
            max_time=2,
        )
        cls.coal.set_speciation_rates([0.5, 0.99])
        cls.coal.set_map(map_file="sample/null.tif")
        cls.coal.run()
        cls.tree = CoalescenceTree(cls.coal)
        cls.tree.set_speciation_parameters(
            speciation_rates=[0.5, 0.95], record_spatial=False, record_fragments="sample/FragmentsTest.csv"
        )
        cls.tree.apply()

    def testRichness(self):
        """
        Tests that the richness produced by a landscape is sensible for the relevant speciation rates.
        """
        self.assertEqual(1184, self.tree.get_species_richness(1))
        self.assertEqual(1677, self.tree.get_species_richness(2))

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
        self.coal.set_simulation_parameters(
            seed=6,
            task=6,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            dispersal_method="normal",
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.detect_map_dimensions()
        self.coal.add_sample_time(0.0)
        self.coal.add_sample_time(0.5)
        self.coal.set_speciation_rates([0.5])
        self.coal.run()
        self.tree.set_database(self.coal)
        self.tree.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null", times=[0.0, 0.5]
        )
        self.tree.apply()
        self.tree.calculate_octaves()
        self.tree.calculate_richness()

    def testRaisesErrorFragmentList(self):
        """
        Tests that a RuntimeError is raised when trying to get the fragments list (as none exists).
        """
        with self.assertRaises(IOError):
            self.tree.get_fragment_list()

    def testComplexRichness(self):
        """
        Tests that the complex simulation setup returns the correct species richness.
        """
        self.assertEqual(3645, self.tree.get_species_richness(1))
        self.assertEqual(3669, self.tree.get_species_richness(3))
        self.assertEqual(3688, self.tree.get_species_richness(5))
        self.assertEqual(0, self.tree.get_species_richness(10))

    def testComplexRichness2(self):
        """
        Tests that the later generation of species richness is correct
        """
        self.assertEqual(3649, self.tree.get_species_richness(2))
        self.assertEqual(3670, self.tree.get_species_richness(4))
        self.assertEqual(3690, self.tree.get_species_richness(6))
        self.assertEqual(0, self.tree.get_species_richness(11))

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
        self.assertEqual(
            self.tree.get_species_richness(reference=1),
            self.tree.get_species_richness(reference=1),
            msg="Landscape richness is not as expected.",
        )
        self.assertEqual(
            self.tree.get_species_richness(reference=3),
            self.tree.get_species_richness(reference=3),
            msg="Landscape richness is not as expected.",
        )
        self.assertEqual(
            self.tree.get_species_richness(reference=100),
            self.tree.get_species_richness(reference=100),
            msg="Landscape richness is not as expected.",
        )
        self.assertEqual(
            self.tree.get_species_richness(reference=101),
            self.tree.get_species_richness(reference=101),
            msg="Landscape richness is not as expected.",
        )

    def testComplexAbundances(self):
        """
        Tests that species abundances are correct for a complex case.
        """
        expected_abundances = [[0, 0], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1]]
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
        actual_sim_parameters = dict(
            seed=6,
            task=6,
            output_dir="output",
            speciation_rate=0.5,
            sigma=4.0,
            tau=4.0,
            deme=1,
            sample_size=0.1,
            max_time=10.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
            time_config_file="set",
            coarse_map_file="sample/SA_sample_coarse.tif",
            coarse_map_x=35,
            coarse_map_y=41,
            coarse_map_x_offset=11,
            coarse_map_y_offset=14,
            coarse_map_scale=1.0,
            fine_map_file="sample/SA_sample_fine.tif",
            fine_map_x=13,
            fine_map_y=13,
            fine_map_x_offset=0,
            fine_map_y_offset=0,
            sample_file="null",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=1,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
        )
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
        with self.assertRaises(sqlite3.Error):
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
        self.coal.set_simulation_parameters(
            seed=6,
            task=7,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.detect_map_dimensions()
        self.coal.add_sample_time(0.0)
        self.coal.add_sample_time(1.0)
        self.coal.set_speciation_rates([0.5])
        self.coal.run()
        self.tree.set_database("output/data_7_6.db")
        self.tree.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null", times=[0.0, 1.0]
        )
        self.tree.apply()
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
        self.assertEqual(3605, self.tree.get_species_richness(1))
        self.assertEqual(3645, self.tree.get_species_richness(3))
        self.assertEqual(3677, self.tree.get_species_richness(5))

    def testComplexRichness2(self):
        """
        Tests that the complex simulation setup returns the correct species richness at other time samples
        """
        self.assertEqual(3614, self.tree.get_species_richness(2))
        self.assertEqual(3652, self.tree.get_species_richness(4))
        self.assertEqual(3683, self.tree.get_species_richness(6))

    def testZeroRichness(self):
        """
        Tests that zero richness is produced where expected
        :return:
        """
        self.assertEqual(0, self.tree.get_species_richness(100))
        self.assertEqual(self.tree.get_species_richness(1), self.tree.get_species_richness(1))
        self.assertEqual(self.tree.get_species_richness(3), self.tree.get_species_richness(3))
        self.assertEqual(self.tree.get_species_richness(6), self.tree.get_species_richness(6))
        self.assertEqual(self.tree.get_species_richness(100), self.tree.get_species_richness(100))


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
        self.coal.set_simulation_parameters(
            seed=6,
            task=13,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.add_sample_time(0.0)
        self.coal.add_sample_time(1.0)
        self.coal.set_speciation_rates([0.5])
        self.coal.run()
        self.tree.set_database(self.coal)
        self.tree.set_speciation_parameters(
            speciation_rates=[0.6, 0.7],
            record_spatial=True,
            record_fragments=False,
            sample_file="null",
            times=[0.0, 1.0],
        )
        self.tree.apply()
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
        self.assertEqual(3637, self.tree.get_species_richness(1))
        self.assertEqual(3661, self.tree.get_species_richness(3))
        self.assertEqual(3690, self.tree.get_species_richness(5))
        self.assertEqual(0, self.tree.get_species_richness(8))
        self.assertEqual(self.tree.get_species_richness(1), self.tree.get_species_richness(1))
        self.assertEqual(self.tree.get_species_richness(3), self.tree.get_species_richness(3))
        self.assertEqual(self.tree.get_species_richness(4), self.tree.get_species_richness(4))
        self.assertEqual(self.tree.get_species_richness(7), self.tree.get_species_richness(7))


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
        self.coal.set_simulation_parameters(
            seed=7,
            task=13,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="norm-uniform",
            m_prob=10 ** -8,
            cutoff=160,
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal.set_speciation_rates([0.5])
        self.coal.run()
        self.tree.set_database(self.coal)
        self.tree.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial=True, record_fragments=False, sample_file="null"
        )
        self.tree.apply()
        self.tree.calculate_octaves()
        self.tree.calculate_richness()

    @classmethod
    def tearDownClass(cls):
        """Does nothing"""
        pass  # rmtree("output", True)

    def testComplexRichness(self):
        """
        Tests that the complex simulation setup returns the correct species richness.
        Also tests that both methods of obtaining species richness work.
        """
        self.tree.calculate_richness()
        self.assertEqual(3622, self.tree.get_species_richness(1))
        self.assertEqual(3662, self.tree.get_species_richness(2))
        self.assertEqual(3683, self.tree.get_species_richness(3))
        self.assertEqual(0, self.tree.get_species_richness(7))
        self.assertEqual(self.tree.get_species_richness(1), self.tree.get_species_richness(1))
        self.assertEqual(self.tree.get_species_richness(3), self.tree.get_species_richness(3))
        self.assertEqual(self.tree.get_species_richness(5), self.tree.get_species_richness(5))
        self.assertEqual(self.tree.get_species_richness(7), self.tree.get_species_richness(7))

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

    def testSimCompletes(self):
        """
        Tests that the complex simulation setup returns the correct species richness.
        Also tests that both methods of obtaining species richness work.
        """
        sim = Simulation()
        self.assertEqual(25, sim.run_simple(1, 11, "output", 0.1, 2, 10))

    def raise_ioerror(self):
        raise IOError

    def richness_zero(self):
        return 0

    @patch.object(Simulation, "get_species_richness", richness_zero)
    def testSimpleErrorsZeroRichness(self):
        """Tests that a simple sim raises the correct errors."""
        sim = Simulation()
        with self.assertRaises(AssertionError):
            sim.run_simple(20, 11, "output", 0.1, 2, 10)

    @patch.object(Simulation, "get_species_richness", raise_ioerror)
    def testSimpleErrorsTimeCompletion(self):
        """Tests that a simple sim raises the correct errors."""
        sim = Simulation()
        with self.assertRaises(RuntimeError):
            sim.run_simple(30, 11, "output", 0.1, 2, 10)


class TestSimulationApplySpeciation(unittest.TestCase):
    """
    Tests applying speciation rates works as expected for simple cases, including checking that the errors raised by
    applying the speciation rates make sense.
    """

    @classmethod
    def setUpClass(cls):
        cls.coal = Simulation()
        cls.coal.set_simulation_parameters(
            seed=1,
            task=31,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2 * (2 ** 0.5),
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        cls.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        cls.coal.run()

    def testRaisesErrorWhenNullSamplemaskAndFragments(self):
        """
        Tests that a ValueError is raised when record_fragments is set to true, but the sample file is null.
        :return:
        """
        t = CoalescenceTree(self.coal)
        with self.assertRaises(ValueError):
            t.set_speciation_parameters(
                speciation_rates=[0.5, 0.7], record_spatial="T", record_fragments="T", sample_file="null"
            )

    def testRaisesErrorWhenNoSampleMask(self):
        """
        Tests that an error is raised when the samplemask is null and record_fragments is True
        """
        t = CoalescenceTree(self.coal)
        with self.assertRaises(ValueError):
            t.set_speciation_parameters(
                speciation_rates=[0.5, 0.7], record_spatial="T", record_fragments="T", sample_file="null"
            )

    def testRaisesErrorWhenSpecNotDouble(self):
        t = CoalescenceTree(self.coal)
        with self.assertRaises(TypeError):
            t.set_speciation_parameters(
                speciation_rates=["notdouble"], record_spatial="T", record_fragments="F", sample_file="null"
            )

    def testRaisesErrorWhenSpecNotList(self):
        t = CoalescenceTree(self.coal)

        with self.assertRaises(TypeError):
            t.set_speciation_parameters(
                speciation_rates="string", record_spatial="T", record_fragments="F", sample_file="null"
            )


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
        self.coal.set_simulation_parameters(
            seed=1,
            task=13,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2.0,
            tau=1.0,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail",
            landscape_type=True,
        )
        self.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal.detect_map_dimensions()
        self.coal.run()
        self.coal2.set_simulation_parameters(
            seed=1,
            task=14,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2.0,
            tau=-3.0,
            deme=1,
            sample_size=0.1,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="fat-tail-old",
            landscape_type=True,
        )
        self.coal2.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal2.detect_map_dimensions()
        self.coal2.run()
        self.tree1.set_database(self.coal)
        self.tree1.calculate_richness()
        self.tree2.set_database(self.coal2)
        self.tree2.set_speciation_parameters(
            speciation_rates=[0.1], record_spatial=False, record_fragments=False, sample_file="null"
        )
        # self.tree2.apply()
        self.tree2.calculate_richness()

    def testOldKernelMatchesNewKernelRichness(self):
        """
        Tests that the old dispersal kernel matches the new dispersal kernel in richness
        """
        self.assertEqual(self.tree1.get_species_richness(1), self.tree2.get_species_richness(1))
        self.assertEqual(self.tree1.get_species_richness(1), self.tree2.get_species_richness(1))

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
        self.coal.set_simulation_parameters(
            seed=1,
            task=15,
            output_directory="output",
            min_speciation_rate=0.01,
            sigma=2.0,
            tau=100000000000000000000000,
            deme=1,
            sample_size=0.1,
            max_time=4,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            landscape_type=True,
        )
        self.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal.detect_map_dimensions()
        self.coal.run()
        self.coal2.set_simulation_parameters(
            seed=1,
            task=16,
            output_directory="output",
            min_speciation_rate=0.01,
            sigma=2,
            tau=-4,
            deme=1,
            sample_size=0.1,
            max_time=3,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            landscape_type=True,
        )
        self.coal2.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal2.detect_map_dimensions()
        self.coal2.run()
        # self.coal.set_speciation_rates([0.5, 0.7])
        self.tree1.set_database(self.coal)
        self.tree1.set_speciation_parameters(
            speciation_rates=[0.01], record_spatial=False, record_fragments=False, sample_file="null"
        )
        # self.tree1.apply()
        self.tree1.calculate_richness()
        self.tree2.set_database(self.coal2)
        self.tree2.set_speciation_parameters(
            speciation_rates=[0.01], record_spatial=False, record_fragments=False, sample_file="null"
        )
        # self.tree2.apply()
        self.tree2.calculate_richness()

    def testOldKernelMatchesNewKernelRichness(self):
        """
        Tests that the fat-tailed dispersal kernel matches the normal distribution for extreme tau in richness
        """
        self.assertEqual(self.tree1.get_species_richness(1), self.tree2.get_species_richness(1))
        self.assertEqual(self.tree1.get_species_richness(1), self.tree2.get_species_richness(1))

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
        self.coal.set_simulation_parameters(
            1,
            28,
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
        self.coal.set_map_parameters("null", 10, 10, "null", 10, 10, 0, 0, "null", 20, 20, 0, 0, 1, "null", "null")
        self.coal.set_speciation_rates([0.1, 0.2])
        self.coal.add_sample_time(100000000.0)
        self.coal.run()
        self.tree.set_database(self.coal)

    def testGetsPresentRichness(self):
        """
        Tests that the simulation obtains the present-day richnesses accurately
        """
        self.assertEqual(37, self.coal.get_species_richness(1))
        self.assertEqual(53, self.coal.get_species_richness(3))

    def testGetsHistoricalRichness(self):
        """
        Tests that the simulation obtains the historical richnesses accurately
        """
        self.assertEqual(51, self.coal.get_species_richness(2))
        self.assertEqual(58, self.coal.get_species_richness(4))


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
        self.coal1.set_simulation_parameters(
            seed=1,
            task=19,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=True,
            min_speciation_gen=0,
            max_speciation_gen=2,
        )
        self.coal2.set_simulation_parameters(
            seed=1,
            task=20,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=True,
            min_speciation_gen=10,
            max_speciation_gen=50,
        )
        self.coal3.set_simulation_parameters(
            seed=1,
            task=21,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=True,
            min_speciation_gen=10,
            max_speciation_gen=20,
        )
        self.coal4.set_simulation_parameters(
            seed=1,
            task=22,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=False,
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal1.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal2.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal3.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        self.coal4.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", coarse_file="sample/SA_sample_coarse.tif"
        )
        # self.coal1.set_speciation_rates([0.5])
        # self.coal2.set_speciation_rates([0.5])
        # self.coal3.set_speciation_rates([0.5])
        # self.coal4.set_speciation_rates([0.5])
        self.coal1.run()
        self.coal2.run()
        self.coal3.run()
        self.coal4.run()
        self.tree1.set_database(self.coal1)
        self.tree2.set_database(self.coal2)
        self.tree3.set_database(self.coal3)
        self.tree4.set_database(self.coal4)
        self.tree1.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree2.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree3.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree4.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree1.apply()
        self.tree2.apply()
        self.tree3.apply()
        self.tree4.apply()
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
        self.assertTrue(self.coal1.get_protracted())
        self.assertEqual(self.tree4.get_simulation_parameters()["protracted"], 0)
        self.assertEqual(self.tree4.is_protracted(), False)
        self.assertFalse(self.coal4.get_protracted())

    def testComplexRichness(self):
        """
        Tests that the complex simulation setup returns the correct species richness.
        Also tests that both methods of obtaining species richness work.
        """
        self.assertGreaterEqual(self.tree1.get_species_richness(), self.tree2.get_species_richness())
        self.assertGreaterEqual(self.tree3.get_species_richness(), self.tree2.get_species_richness())
        self.assertGreaterEqual(self.tree1.get_species_richness(), self.tree4.get_species_richness())


class TestSimulationProtractedSpeciationApplication(unittest.TestCase):
    """
    Tests that the protracted speciation is properly applied, post-simulation.
    """

    @classmethod
    def setUpClass(cls):
        """
        Runs the test simulation to test for speciation application.
        """
        cls.sim = Simulation()
        cls.sim.set_simulation_parameters(
            seed=1,
            task=23,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=1.0,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=True,
            min_speciation_gen=50,
            max_speciation_gen=2000,
        )
        cls.sim.set_map("null", 10, 10)
        cls.sim.run()
        cls.c = CoalescenceTree(cls.sim, logging_level=60)
        cls.c.wipe_data()
        for p_min, p_max in [(50, 100), (25, 100), (50, 200), (0.0, 2000)]:
            cls.c.set_speciation_parameters(
                speciation_rates=[0.1, 0.2],
                record_spatial=False,
                record_fragments=False,
                protracted_speciation_min=p_min,
                protracted_speciation_max=p_max,
            )
            cls.c.times = None
            cls.c.apply_incremental()
        cls.c.output()

    def testOutOfRangeParameterRaisesErrors(self):
        """
        Tests that applying speciation rates with out-of-range protracted speciation parameters throws the correct
        errors.
        """
        self.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        self.c.c_community.add_protracted_parameters(70.0, 2000.0)
        with self.assertRaises(RuntimeError):
            self.c.apply()
        self.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        self.c.c_community.add_protracted_parameters(50.0, 2100.0)
        with self.assertRaises(RuntimeError):
            self.c.apply()

    def testProtractedPostApplicationSanityChecks(self):
        """
        Runs some sanity checks to ensure that the post-application of protracted speciation is as expected.
        """
        self.assertLess(self.c.get_species_richness(1), self.c.get_species_richness(3))
        self.assertLess(self.c.get_species_richness(2), self.c.get_species_richness(4))
        self.assertLess(self.c.get_species_richness(5), self.c.get_species_richness(3))
        self.assertLess(self.c.get_species_richness(6), self.c.get_species_richness(4))
        self.assertEqual(4, self.c.get_species_richness(1))
        self.assertEqual(4, self.c.get_species_richness(2))
        self.assertEqual(7, self.c.get_species_richness(3))
        self.assertEqual(7, self.c.get_species_richness(4))
        self.assertEqual(4, self.c.get_species_richness(5))
        self.assertEqual(4, self.c.get_species_richness(6))
        self.assertEqual(21, self.c.get_species_richness(7))
        self.assertEqual(38, self.c.get_species_richness(8))

    def testProtractedCommunityParametersStored(self):
        """
        Tests that the protracted community parameters are stored and returned correctly.
        """
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8], self.c.get_community_references())
        self.assertEqual(
            1, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=100)
        )
        self.assertEqual(
            2, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=100)
        )
        self.assertEqual(
            3, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=25, max_speciation_gen=100)
        )
        self.assertEqual(
            4, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=25, max_speciation_gen=100)
        )
        self.assertEqual(
            5, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=200)
        )
        self.assertEqual(
            6, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=200)
        )
        self.assertEqual(
            7, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=0.0, max_speciation_gen=2000)
        )
        self.assertEqual(
            8, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=0.0, max_speciation_gen=2000)
        )
        ed1 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 100,
        }
        ed2 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 100,
        }
        ed3 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 25,
            "max_speciation_gen": 100,
        }
        ed4 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 25,
            "max_speciation_gen": 100,
        }
        ed5 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 200,
        }
        ed6 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 200,
        }
        ed7 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 0.0,
            "max_speciation_gen": 2000,
        }
        ed8 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 0.0,
            "max_speciation_gen": 2000,
        }
        com1_dict = self.c.get_community_parameters(1)
        com2_dict = self.c.get_community_parameters(2)
        com3_dict = self.c.get_community_parameters(3)
        com4_dict = self.c.get_community_parameters(4)
        com5_dict = self.c.get_community_parameters(5)
        com6_dict = self.c.get_community_parameters(6)
        com7_dict = self.c.get_community_parameters(7)
        com8_dict = self.c.get_community_parameters(8)
        self.assertEqual(ed1, com1_dict)
        self.assertEqual(ed2, com2_dict)
        self.assertEqual(ed3, com3_dict)
        self.assertEqual(ed4, com4_dict)
        self.assertEqual(ed5, com5_dict)
        self.assertEqual(ed6, com6_dict)
        self.assertEqual(ed7, com7_dict)
        self.assertEqual(ed8, com8_dict)


class TestSimulationProtractedSpeciationApplication2(unittest.TestCase):
    """
    Repeat of the above tests for multiple application method.
    Tests that the protracted speciation is properly applied, post-simulation.
    """

    @classmethod
    def setUpClass(cls):
        """
        Runs the test simulation to test for speciation application.
        """
        cls.sim = Simulation()
        cls.sim.set_simulation_parameters(
            seed=1,
            task=24,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=1.0,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=True,
            min_speciation_gen=50,
            max_speciation_gen=2000,
        )
        cls.sim.set_map("null", 10, 10)
        cls.sim.run()
        cls.c = CoalescenceTree(cls.sim, logging_level=60)
        cls.c.wipe_data()
        cls.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        cls.c.add_multiple_protracted_parameters(speciation_gens=[(50, 100), (25, 100), (50, 200), (0.0, 2000)])
        cls.c.apply()

    def testOutOfRangeParameterRaisesErrors(self):
        """
        Tests that applying speciation rates with out-of-range protracted speciation parameters throws the correct
        errors.
        """
        self.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        self.c.c_community.add_protracted_parameters(70.0, 2000.0)
        with self.assertRaises(RuntimeError):
            self.c.apply()
        self.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        self.c.c_community.add_protracted_parameters(50.0, 2100.0)
        with self.assertRaises(RuntimeError):
            self.c.apply()

    def testProtractedPostApplicationSanityChecks(self):
        """
        Runs some sanity checks to ensure that the post-application of protracted speciation is as expected.
        """
        self.assertLess(self.c.get_species_richness(1), self.c.get_species_richness(3))
        self.assertLess(self.c.get_species_richness(2), self.c.get_species_richness(4))
        self.assertLess(self.c.get_species_richness(5), self.c.get_species_richness(3))
        self.assertLess(self.c.get_species_richness(6), self.c.get_species_richness(4))
        self.assertEqual(4, self.c.get_species_richness(1))
        self.assertEqual(4, self.c.get_species_richness(2))
        self.assertEqual(7, self.c.get_species_richness(3))
        self.assertEqual(7, self.c.get_species_richness(4))
        self.assertEqual(4, self.c.get_species_richness(5))
        self.assertEqual(4, self.c.get_species_richness(6))
        self.assertEqual(21, self.c.get_species_richness(7))
        self.assertEqual(38, self.c.get_species_richness(8))

    def testProtractedCommunityParametersStored(self):
        """
        Tests that the protracted community parameters are stored and returned correctly.
        """
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8], self.c.get_community_references())
        self.assertEqual(
            1, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=100)
        )
        self.assertEqual(
            2, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=100)
        )
        self.assertEqual(
            3, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=25, max_speciation_gen=100)
        )
        self.assertEqual(
            4, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=25, max_speciation_gen=100)
        )
        self.assertEqual(
            5, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=200)
        )
        self.assertEqual(
            6, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=200)
        )
        self.assertEqual(
            7, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=0.0, max_speciation_gen=2000)
        )
        self.assertEqual(
            8, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=0.0, max_speciation_gen=2000)
        )
        ed1 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 100,
        }
        ed2 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 100,
        }
        ed3 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 25,
            "max_speciation_gen": 100,
        }
        ed4 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 25,
            "max_speciation_gen": 100,
        }
        ed5 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 200,
        }
        ed6 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 200,
        }
        ed7 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 0.0,
            "max_speciation_gen": 2000,
        }
        ed8 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 0.0,
            "max_speciation_gen": 2000,
        }
        com1_dict = self.c.get_community_parameters(1)
        com2_dict = self.c.get_community_parameters(2)
        com3_dict = self.c.get_community_parameters(3)
        com4_dict = self.c.get_community_parameters(4)
        com5_dict = self.c.get_community_parameters(5)
        com6_dict = self.c.get_community_parameters(6)
        com7_dict = self.c.get_community_parameters(7)
        com8_dict = self.c.get_community_parameters(8)
        self.assertEqual(ed1, com1_dict)
        self.assertEqual(ed2, com2_dict)
        self.assertEqual(ed3, com3_dict)
        self.assertEqual(ed4, com4_dict)
        self.assertEqual(ed5, com5_dict)
        self.assertEqual(ed6, com6_dict)
        self.assertEqual(ed7, com7_dict)
        self.assertEqual(ed8, com8_dict)


class TestSimulationProtractedSpeciationApplication3(unittest.TestCase):
    """
    Repeat of the above tests for multiple application method.
    Tests that the protracted speciation is properly applied, post-simulation.
    """

    @classmethod
    def setUpClass(cls):
        """
        Runs the test simulation to test for speciation application.
        """
        cls.sim = Simulation()
        cls.sim.set_simulation_parameters(
            seed=1,
            task=25,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=1.0,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=True,
            min_speciation_gen=50,
            max_speciation_gen=2000,
        )
        cls.sim.set_map("null", 10, 10)
        cls.sim.run()
        cls.c = CoalescenceTree(cls.sim, logging_level=60)
        cls.c.wipe_data()
        cls.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        min_speciation_gens = [50, 25, 50, 0]
        max_speciation_gens = [100, 100, 200, 2000]
        cls.c.add_multiple_protracted_parameters(
            min_speciation_gens=min_speciation_gens, max_speciation_gens=max_speciation_gens
        )
        cls.c.apply()

    def testOutOfRangeParameterRaisesErrors(self):
        """
        Tests that applying speciation rates with out-of-range protracted speciation parameters throws the correct
        errors.
        """
        self.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        self.c.c_community.add_protracted_parameters(70.0, 2000.0)
        with self.assertRaises(RuntimeError):
            self.c.apply()
        self.c.set_speciation_parameters(speciation_rates=[0.1, 0.2], record_spatial=False, record_fragments=False)
        self.c.c_community.add_protracted_parameters(50.0, 2100.0)
        with self.assertRaises(RuntimeError):
            self.c.apply()

    def testProtractedPostApplicationSanityChecks(self):
        """
        Runs some sanity checks to ensure that the post-application of protracted speciation is as expected.
        """
        self.assertLess(self.c.get_species_richness(1), self.c.get_species_richness(3))
        self.assertLess(self.c.get_species_richness(2), self.c.get_species_richness(4))
        self.assertLess(self.c.get_species_richness(5), self.c.get_species_richness(3))
        self.assertLess(self.c.get_species_richness(6), self.c.get_species_richness(4))
        self.assertEqual(4, self.c.get_species_richness(1))
        self.assertEqual(4, self.c.get_species_richness(2))
        self.assertEqual(7, self.c.get_species_richness(3))
        self.assertEqual(7, self.c.get_species_richness(4))
        self.assertEqual(4, self.c.get_species_richness(5))
        self.assertEqual(4, self.c.get_species_richness(6))
        self.assertEqual(21, self.c.get_species_richness(7))
        self.assertEqual(38, self.c.get_species_richness(8))

    def testProtractedCommunityParametersStored(self):
        """
        Tests that the protracted community parameters are stored and returned correctly.
        """
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8], self.c.get_community_references())
        self.assertEqual(
            1, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=100)
        )
        self.assertEqual(
            2, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=100)
        )
        self.assertEqual(
            3, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=25, max_speciation_gen=100)
        )
        self.assertEqual(
            4, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=25, max_speciation_gen=100)
        )
        self.assertEqual(
            5, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=200)
        )
        self.assertEqual(
            6, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=50, max_speciation_gen=200)
        )
        self.assertEqual(
            7, self.c.get_community_reference(0.1, 0.0, False, 0, 0.0, min_speciation_gen=0.0, max_speciation_gen=2000)
        )
        self.assertEqual(
            8, self.c.get_community_reference(0.2, 0.0, False, 0, 0.0, min_speciation_gen=0.0, max_speciation_gen=2000)
        )
        ed1 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 100,
        }
        ed2 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 100,
        }
        ed3 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 25,
            "max_speciation_gen": 100,
        }
        ed4 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 25,
            "max_speciation_gen": 100,
        }
        ed5 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 200,
        }
        ed6 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 50,
            "max_speciation_gen": 200,
        }
        ed7 = {
            "speciation_rate": 0.1,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 0.0,
            "max_speciation_gen": 2000,
        }
        ed8 = {
            "speciation_rate": 0.2,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 0.0,
            "max_speciation_gen": 2000,
        }
        com1_dict = self.c.get_community_parameters(1)
        com2_dict = self.c.get_community_parameters(2)
        com3_dict = self.c.get_community_parameters(3)
        com4_dict = self.c.get_community_parameters(4)
        com5_dict = self.c.get_community_parameters(5)
        com6_dict = self.c.get_community_parameters(6)
        com7_dict = self.c.get_community_parameters(7)
        com8_dict = self.c.get_community_parameters(8)
        self.assertEqual(ed1, com1_dict)
        self.assertEqual(ed2, com2_dict)
        self.assertEqual(ed3, com3_dict)
        self.assertEqual(ed4, com4_dict)
        self.assertEqual(ed5, com5_dict)
        self.assertEqual(ed6, com6_dict)
        self.assertEqual(ed7, com7_dict)
        self.assertEqual(ed8, com8_dict)


@unittest.skipIf(platform.system() == "Windows", "Skipping tests not compatible with Windows.")
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
        self.c = Simulation(logging_level=50)
        self.c.set_simulation_parameters(
            seed=1,
            task=32,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        self.c.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_coarse.tif",
            dispersal_map="sample/dispersal_fine.tif",
        )
        self.c.run()

    def testDispersalSimulation(self):
        """
        Tests that running a simulation with a dispersal map produces the expected output.
        """
        self.assertEqual(715, self.c.get_species_richness(1))

    def testDispersalParamStorage(self):
        """
        Tests that the dispersal parameters are stored correctly
        """
        t = CoalescenceTree(self.c)
        self.assertEqual(t.get_simulation_parameters()["dispersal_map"], "sample/dispersal_fine.tif")

    def testDispersalDimensionsErrorCoarse(self):
        """
        Tests that an error is raised if a coarse map is provided, but a dispersal map is also chosen.
        """
        c = Simulation(logging_level=logging.CRITICAL)
        c.set_simulation_parameters(
            seed=2,
            task=32,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        with self.assertRaises(ValueError):
            c.set_map_files(
                sample_file="sample/SA_samplemaskINT.tif",
                fine_file="sample/SA_sample_coarse.tif",
                coarse_file="sample/SA_sample_coarse.tif",
                dispersal_map="sample/dispersal_fine.tif",
            )

    def testDispersalDimensionsErrorMismatch(self):
        """
        Tests that an error is raised if the dispersal map does not match the dimensions of the fine map, calculated
        as a map of maps.
        """
        c = Simulation(logging_level=logging.CRITICAL)
        c.set_simulation_parameters(
            seed=3,
            task=32,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        with self.assertRaises(ValueError):
            c.set_map_files(
                sample_file="sample/SA_samplemaskINT.tif",
                fine_file="sample/SA_sample_fine.tif",
                dispersal_map="sample/dispersal_fine.tif",
            )


class TestSimulationDispersalMapsSumming(unittest.TestCase):
    """
    Tests the dispersal maps to ensure that values are read properly, and using dispersal maps for simulations works as
    intended.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the objects for running coalescence simulations on dispersal maps.
        """
        cls.c = Simulation(logging_level=logging.CRITICAL)
        cls.c.set_simulation_parameters(
            seed=2,
            task=32,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        cls.c.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_coarse.tif",
            dispersal_map="sample/dispersal_fine_cumulative.tif",
        )
        cls.c.run()

    def testDispersalSimulation(self):
        """
        Tests that running a simulation with a dispersal map produces the expected output.
        """
        self.assertEqual(1172, self.c.get_species_richness(1))

    def testDispersalParamStorage(self):
        """
        Tests that the dispersal parameters are stored correctly
        """
        t = CoalescenceTree(self.c)
        self.assertEqual(t.get_simulation_parameters()["dispersal_map"], "sample/dispersal_fine_cumulative.tif")

    def testRaisesErrorValueMismatch(self):
        """
        Tests that an error is raised when dispersal is possible to a cell with 0 density.
        """
        c = Simulation(logging_level=logging.CRITICAL)
        c.set_simulation_parameters(
            seed=4,
            task=32,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        c.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_coarse_zeros.tif",
            dispersal_map="sample/dispersal_fine_cumulative.tif",
        )
        with self.assertRaises(RuntimeError):
            c.run()


class TestSimulationDispersalMapsNoData(unittest.TestCase):
    """
    Tests the dispersal maps to ensure that values are read properly, and using dispersal maps for simulations works as
    intended.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the objects for running coalescence simulations on dispersal maps.
        """
        cls.c = Simulation(logging_level=logging.CRITICAL)
        cls.c.set_simulation_parameters(
            seed=3,
            task=32,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
        )
        cls.c.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_coarse.tif",
            dispersal_map="sample/dispersal_fine_nodata.tif",
        )
        cls.c.run()

    def testDispersalMapSimulation(self):
        """
        Tests that running a simulation with a dispersal map produces the expected output.
        """
        self.assertEqual(701, self.c.get_species_richness(1))

    def testDispersalParamStorage(self):
        """
        Tests that the dispersal parameters are stored correctly
        """
        t = CoalescenceTree(self.c)
        self.assertEqual(t.get_simulation_parameters()["dispersal_map"], "sample/dispersal_fine_nodata.tif")


@skipLongTest
class TestDetectRamUsage(unittest.TestCase):
    """
    Class for testing the RAM detection and utilisation of pycoalescence
    """

    @classmethod
    def setUpClass(cls):
        cls.c = Simulation(logging_level=logging.CRITICAL)
        cls.c.set_simulation_parameters(
            seed=1,
            task=36,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1000,
            sample_size=0.01,
            max_time=100,
            dispersal_relative_cost=1,
            min_num_species=1,
            landscape_type=False,
        )
        cls.c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
        cls.c.add_sample_time(1.0)
        try:
            cls.c.optimise_ram(ram_limit=0.03)
            cls.c.run()
        except MemoryError as me:
            cls.fail(
                msg="Cannot run a larger scale simulation. This should require around 500MB of RAM. If your computer"
                "does not have these requirements, ignore this failure: {}".format(me)
            )

    def testExcessiveRamUsage(self):
        """
        Tests that an exception is raised if there is not enough RAM to complete the simulation.
        """
        c = Simulation()
        c.set_simulation_parameters(
            seed=1,
            task=36,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=100000000000,
            sample_size=0.1,
            max_time=10,
        )
        c.set_map_files(sample_file="sample/large_mask.tif", fine_file="sample/large_fine.tif")
        with self.assertRaises(MemoryError):
            c.optimise_ram(ram_limit=16)

    def testGridOffsetApplyingSpeciation(self):
        """
        Tests that additional speciation rates are correctly applied when using an offsetted grid
        """
        t = CoalescenceTree(self.c)
        t.set_speciation_parameters(
            speciation_rates=[0.6, 0.7],
            record_spatial="T",
            record_fragments="sample/FragmentsTest2.csv",
            sample_file="null",
        )
        t.apply()
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
        sim.set_simulation_parameters(
            seed=11,
            task=36,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.01,
            max_time=100,
        )
        sim.set_map_files(sample_file="null", fine_file="sample/SA_sample.tif")
        sim.optimise_ram(ram_limit=10000)
        self.assertEqual(sim.fine_map.x_size, sim.sample_map.x_size)
        self.assertEqual(sim.fine_map.y_size, sim.sample_map.y_size)
        self.assertEqual(0, sim.sample_map.x_offset)
        self.assertEqual(0, sim.sample_map.y_offset)
        self.assertEqual(sim.fine_map.x_size, sim.grid.x_size)
        self.assertEqual(sim.fine_map.y_size, sim.grid.y_size)
        self.assertEqual("null", sim.grid.file_name)
        sim.run()

    def testExcessiveRamReallocation(self):
        """
        Tests that in a system with excessive RAM usage, the map file structure is rearranged for lower performance,
        but optimal RAM usage.
        """
        self.assertEqual(1769, self.c.get_species_richness(1))
        self.assertEqual(1769, self.c.get_species_richness(2))

    @skipLongTest
    def testSingleLargeRun(self):
        """
        Tests a single run with a huge number of individuals in two cells
        """
        c = Simulation()
        c.set_simulation_parameters(
            seed=1,
            task=37,
            output_directory="output",
            min_speciation_rate=0.95,
            sigma=1,
            tau=2,
            deme=70000,
            sample_size=1,
            max_time=100,
        )
        c.set_map_parameters(
            sample_file="null",
            sample_x=2,
            sample_y=1,
            fine_file="null",
            fine_x=2,
            fine_y=1,
            fine_x_offset=0,
            fine_y_offset=0,
            coarse_file="none",
            coarse_x=2,
            coarse_y=1,
            coarse_x_offset=0,
            coarse_y_offset=0,
            coarse_scale=1.0,
            historical_fine_map="none",
            historical_coarse_map="none",
        )
        c.run()
        self.assertEqual(136415, c.get_species_richness(1))

    def testReadWriteSaveState(self):
        saved_state = self.c.get_optimised_solution()
        c = Simulation()
        c.set_simulation_parameters(
            seed=1,
            task=36,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=100000000000,
            sample_size=0.1,
            max_time=10,
        )
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
        Runs the default simulation and the metacommunities to compare against.
        """
        cls.c = Simulation()
        cls.c.set_simulation_parameters(
            seed=1,
            task=43,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=1,
            tau=2,
            deme=1,
            sample_size=1,
            max_time=100,
            landscape_type=False,
        )
        cls.c.set_map("null", 10, 10)
        cls.c.run()
        cls.t1 = CoalescenceTree(cls.c)
        cls.t1.set_speciation_parameters(speciation_rates=[0.5], record_spatial=False, record_fragments=False)
        cls.t1.apply()
        cls.c2 = Simulation()
        cls.c2.set_simulation_parameters(
            seed=1,
            task=44,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=1,
            tau=2,
            deme=1,
            sample_size=1,
            max_time=100,
            landscape_type=False,
        )
        cls.c2.set_map("null", 10, 10)
        cls.c2.run()
        cls.t2 = CoalescenceTree(cls.c)
        cls.t2.set_speciation_parameters(
            speciation_rates=[0.5],
            record_spatial=False,
            record_fragments=False,
            metacommunity_size=1,
            metacommunity_speciation_rate=0.5,
            metacommunity_option="simulated",
        )
        cls.t2.apply()
        cls.t3 = CoalescenceTree(cls.c)
        cls.t3.set_speciation_parameters(
            speciation_rates=[0.5],
            record_spatial=False,
            record_fragments=False,
            metacommunity_size=1,
            metacommunity_speciation_rate=1.0,
        )
        cls.t3.apply()
        cls.t4 = CoalescenceTree(cls.c)
        cls.t4.set_speciation_parameters(
            speciation_rates=[0.5],
            record_spatial=False,
            record_fragments=False,
            metacommunity_size=1000000,
            metacommunity_speciation_rate=0.95,
        )
        cls.t4.apply()

    def testSanityChecksMetacommunityApplication(self):
        """
        Tests that the metacommunity application makes sense.
        """
        self.assertEqual(self.t1.get_species_richness(), self.t4.get_species_richness(4))
        self.assertEqual(74, self.t4.get_species_richness(4))
        self.assertEqual(1, self.t2.get_species_richness(2))
        self.assertEqual(self.t2.get_species_richness(2), self.t3.get_species_richness(3))

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
        comparison_dict2 = {
            "speciation_rate": 0.5,
            "metacommunity_size": 1.0,
            "option": "simulated",
            "external_reference": 0,
        }
        comparison_dict3 = {
            "speciation_rate": 1.0,
            "metacommunity_size": 1.0,
            "option": "simulated",
            "external_reference": 0,
        }
        comparison_dict4 = {
            "speciation_rate": 0.95,
            "metacommunity_size": 1000000.0,
            "option": "analytical",
            "external_reference": 0,
        }
        self.assertDictEqual(comparison_dict2, metacommunity_dict2)
        self.assertDictEqual(comparison_dict3, metacommunity_dict3)
        self.assertDictEqual(comparison_dict4, metacommunity_dict4)


class TestMetacommunityMethodsMatch(unittest.TestCase):
    """Tests that the different methods of generating metacommunities work as intended."""

    @classmethod
    def setUpClass(cls):
        """Run the simulations to generate the required metacommunities."""
        cls.tree_ref = CoalescenceTree(os.path.join("sample", "nse_reference.db"))
        cls.speciation_rates = [0.0000001, 0.5, 0.99999]
        cls.metacomm_sim = Simulation()
        cls.metacomm_sim.set_simulation_parameters(
            seed=3, task=44, output_directory="output", min_speciation_rate=0.0001, sigma=4
        )
        cls.metacomm_sim.set_map("null", 100, 100)
        cls.metacomm_sim.run()
        for i in range(3):
            dst = os.path.join("output", "data_3_44_{}.db".format(i))
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy2(cls.metacomm_sim.output_database, dst)
        cls.tree_sim = CoalescenceTree(os.path.join("output", "data_3_44_0.db"))
        cls.tree_sim.set_speciation_parameters(
            0.0001,
            metacommunity_size=10000,
            metacommunity_speciation_rate=cls.speciation_rates[0],
            metacommunity_option="simulated",
        )
        cls.tree_sim.apply()
        cls.tree_analytical = CoalescenceTree(os.path.join("output", "data_3_44_1.db"))
        cls.tree_analytical.set_speciation_parameters(
            0.0001,
            metacommunity_size=10000,
            metacommunity_speciation_rate=cls.speciation_rates[0],
            metacommunity_option="analytical",
        )
        cls.tree_analytical.apply()
        cls.tree_external = CoalescenceTree(os.path.join("output", "data_3_44_2.db"))
        cls.tree_external.set_speciation_parameters(
            0.0001, metacommunity_option=os.path.join("sample", "nse_reference.db"), metacommunity_reference=1
        )
        cls.tree_external.apply()

    def testApplyingExternalFile(self):
        """Basic tests that applying an external file works as intended."""
        tree_external = CoalescenceTree(os.path.join("output", "data_3_44_2.db"))
        tree_external.set_speciation_parameters(
            0.0001, metacommunity_option=os.path.join("sample", "nse_reference.db"), metacommunity_reference=1
        )
        tree_external.apply()

    def testBadOptionsRaisesErrors(self):
        """Tests that the having invalid options raises the appropriate error."""
        with self.assertRaises(ValueError):
            self.tree_external2 = CoalescenceTree(os.path.join("output", "data_3_44_2.db"))
            self.tree_external2.set_speciation_parameters(
                0.0001,
                metacommunity_size=10000,
                metacommunity_speciation_rate=self.speciation_rates[0],
                metacommunity_option=os.path.join("sample", "nse_reference.db"),
                metacommunity_reference=0,
            )
            self.tree_external2.apply()

    def testSpeciesRichnessClose(self):
        """
        Tests that the species richness values produced by the different methods (analytical, simulated and from
        an external database) are all close with equivalent parameters.
        """
        self.assertEqual(self.tree_analytical.get_species_richness(1), self.tree_sim.get_species_richness(1))
        self.assertEqual(self.tree_external.get_species_richness(1), self.tree_sim.get_species_richness(1))


class TestProtractedSimsWithMetacommunity(unittest.TestCase):
    """Tests that protracted speciation simulations work properly with metacommunities."""

    @classmethod
    def setUpClass(cls):
        cls.sim = Simulation(logging_level=50)
        cls.sim.set_simulation_parameters(
            seed=2,
            task=44,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=2,
            protracted=True,
            min_speciation_gen=1000,
            max_speciation_gen=10000,
        )
        cls.sim.set_map("sample/SA_sample_fine.tif")
        cls.sim.set_speciation_rates([0.1, 0.5, 0.9])
        cls.sim.run()
        cls.tree = CoalescenceTree(cls.sim, logging_level=50)
        cls.tree.set_speciation_parameters(
            speciation_rates=[0.1, 0.5, 0.9],
            protracted_speciation_min=1000,
            protracted_speciation_max=10000,
            metacommunity_size=10000,
            metacommunity_speciation_rate=0.001,
        )
        cls.tree.apply()

    def testSpeciesRichnessValuesAsExpected(self):
        """Tests that the speciation rates can be successfully applied to the coalescence tree."""
        self.assertEqual(69, self.tree.get_species_richness(1))
        self.assertEqual(69, self.tree.get_species_richness(2))
        self.assertEqual(69, self.tree.get_species_richness(3))
        self.assertEqual(22, self.tree.get_species_richness(4))
        self.assertEqual(19, self.tree.get_species_richness(5))
        self.assertEqual(25, self.tree.get_species_richness(6))

    def testParametersCorrectlyStored(self):
        """Tests that the community parameters are correctly stored."""
        params = self.tree.get_community_parameters(1)
        self.assertEqual(0.1, params["speciation_rate"])
        self.assertEqual(0, params["metacommunity_reference"])
        params = self.tree.get_community_parameters(2)
        self.assertEqual(0.5, params["speciation_rate"])
        self.assertEqual(0, params["metacommunity_reference"])
        params = self.tree.get_community_parameters(3)
        self.assertEqual(0.9, params["speciation_rate"])
        self.assertEqual(0, params["metacommunity_reference"])
        params = self.tree.get_community_parameters(4)
        self.assertEqual(0.1, params["speciation_rate"])
        self.assertEqual(1, params["metacommunity_reference"])
        params = self.tree.get_community_parameters(5)
        self.assertEqual(0.5, params["speciation_rate"])
        self.assertEqual(1, params["metacommunity_reference"])
        params = self.tree.get_community_parameters(6)
        self.assertEqual(0.9, params["speciation_rate"])
        self.assertEqual(1, params["metacommunity_reference"])


class TestTemporalSamplingProportion(unittest.TestCase):
    """Tests that the number of individuals sampled across multiple time points is correct, and random."""

    @classmethod
    def setUpClass(cls):
        """Runs the simulation for the number of individuals sampled"""
        cls.sim = Simulation(logging_level=40)
        cls.sim.set_simulation_parameters(
            seed=1, task=45, output_directory="output", min_speciation_rate=0.01, sigma=1, deme=40, sample_size=0.25
        )
        cls.sim.set_map("null", 10, 10)
        cls.sim.add_sample_time([0, 0.01, 0.02, 0.03])
        cls.sim.run()
        cls.coal = CoalescenceTree(cls.sim)

    def testNumberIndividualsCorrect(self):
        """Tests that the number of individuals at each time slice is correct."""
        for ref in self.coal.get_community_references():
            self.assertEqual(1000, self.coal.get_number_individuals(community_reference=ref))

    def testSpeciesRichnessCorrect(self):
        """Tests that the number of species is correct across the time slices."""
        self.assertEqual(136, self.coal.get_species_richness(1))
        self.assertNotEqual(self.coal.get_species_richness(2), self.coal.get_species_richness(1))
        self.assertNotEqual(self.coal.get_species_richness(3), self.coal.get_species_richness(2))


class TestLongTermSpeciesRichness(unittest.TestCase):
    """Tests the long-term species richness is produced correctly with a variety of time-spacing."""

    @classmethod
    def setUpClass(cls):
        """Runs the sim for long-term biodiversity."""
        cls.times = [0, 1000000, 2000000, 2000000.01]
        cls.sim = Simulation()
        cls.sim.set_simulation_parameters(
            seed=2,
            task=45,
            output_directory="output",
            min_speciation_rate=0.01,
            sigma=1,
            deme=10,
            landscape_type="tiled_fine",
        )
        cls.sim.set_map(os.path.join("sample", "SA_samplemaskINT.tif"))
        cls.sim.add_historical_map("null", "none", 2000000, 0.0)
        cls.sim.add_sample_time(cls.times)
        cls.sim.run()
        cls.coal = CoalescenceTree(cls.sim)
        cls.coal.set_speciation_parameters(speciation_rates=[0.01, 0.02, 0.03, 0.04], times=cls.times)
        cls.coal.apply()
        cls.coal.calculate_richness()

    def testAllTimesExists(self):
        """Tests that all times exist properly"""
        times = []
        for ref in self.coal.get_community_references():
            times.append(self.coal.get_community_parameters(ref)["time"])
        for time in times:
            self.assertTrue(time in self.times, msg="Time {} not in times.".format(time))
        for time in self.times:
            self.assertTrue(time in times, msg="Time {} not in times.".format(time))

    def testSpeciesRichness(self):
        """Tests that the species richness is correct at each time"""
        self.assertEqual(66, self.coal.get_species_richness(1))
        self.assertEqual(56, self.coal.get_species_richness(2))
        self.assertEqual(125, self.coal.get_species_richness(3))
        self.assertEqual(168, self.coal.get_species_richness(4))
        self.assertEqual(102, self.coal.get_species_richness(5))
        self.assertEqual(80, self.coal.get_species_richness(6))
        self.assertEqual(169, self.coal.get_species_richness(7))
        self.assertEqual(244, self.coal.get_species_richness(8))
        self.assertEqual(126, self.coal.get_species_richness(9))
        self.assertEqual(100, self.coal.get_species_richness(10))
        self.assertEqual(196, self.coal.get_species_richness(11))
        self.assertEqual(299, self.coal.get_species_richness(12))
        self.assertEqual(145, self.coal.get_species_richness(13))
        self.assertEqual(118, self.coal.get_species_richness(14))
        self.assertEqual(218, self.coal.get_species_richness(15))
        self.assertEqual(345, self.coal.get_species_richness(16))


@skipLongTest
class TestSamplingGridNumber(unittest.TestCase):
    """Tests that the number of individuals simulated when using an optimised grid is identical to a full simulation."""

    @classmethod
    def setUpClass(cls):
        """Runs simulations for optimised and full grids."""
        cls.sim1 = Simulation(logging_level=50)
        cls.sim1.set_simulation_parameters(
            seed=1, task=46, output_directory="output", min_speciation_rate=0.9, sigma=2, deme=1, sample_size=0.01
        )
        cls.sim1.set_map_files("null", "sample/high_density.tif")
        cls.sim1.run()
        cls.sim2 = Simulation(logging_level=50)
        cls.sim2.set_simulation_parameters(
            seed=2, task=46, output_directory="output", min_speciation_rate=0.9, sigma=2, deme=1, sample_size=0.01
        )
        cls.sim2.set_map_files("null", "sample/high_density.tif")
        optim_sol = {
            "grid_x_size": 10,
            "grid_y_size": 10,
            "sample_x_offset": 10,
            "sample_y_offset": 10,
            "grid_file_name": "set",
        }
        cls.sim2.set_optimised_solution(optim_sol)
        cls.sim2.run()
        cls.tree1 = CoalescenceTree(cls.sim1)
        cls.tree2 = CoalescenceTree(cls.sim2)

    def testNumberIndividuals(self):
        """Tests that the number of individuals simulated is identical."""
        self.assertEqual(self.tree1.get_number_individuals(), self.tree2.get_number_individuals())
        self.assertEqual(472518, self.tree1.get_number_individuals())

    def testSpeciesRichnessNear(self):
        """Tests that the two species richness values are near one another."""
        self.assertAlmostEqual(1.0, self.tree1.get_number_individuals() / self.tree2.get_number_individuals(), 0)


class TestReproductionMaps(unittest.TestCase):
    """Tests a simulation with the  maps."""

    @classmethod
    def setUpClass(cls):
        """Runs the simulations using reproduction maps."""
        cls.sim1 = Simulation(logging_level=50)
        cls.sim1.set_simulation_parameters(
            seed=1, task=47, output_directory="output", min_speciation_rate=0.01, sigma=2, deme=1, sample_size=0.01
        )
        cls.sim1.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", reproduction_map="sample/SA_sample_reproduction.tif"
        )
        cls.sim1.run()
        cls.sim2 = Simulation(logging_level=50)
        cls.sim2.set_simulation_parameters(
            seed=1, task=48, output_directory="output", min_speciation_rate=0.01, sigma=2, deme=1, sample_size=0.01
        )
        cls.sim2.set_map_files("null", fine_file="sample/SA_sample_fine.tif")
        cls.sim2.run()
        cls.sim3 = Simulation(logging_level=50)
        cls.sim3.set_simulation_parameters(
            seed=2, task=47, output_directory="output", min_speciation_rate=0.01, sigma=2, deme=1, sample_size=0.01
        )
        cls.sim3.set_map_files(
            "null",
            fine_file="sample/SA_sample_fine.tif",
            death_map="sample/SA_sample_reproduction.tif",
            reproduction_map="sample/SA_sample_reproduction.tif",
        )
        cls.sim3.run()
        cls.sim4 = Simulation(logging_level=50)
        cls.sim4.set_simulation_parameters(
            seed=4, task=47, output_directory="output", min_speciation_rate=0.01, sigma=2, deme=1, sample_size=0.01
        )
        cls.sim4.set_map_files("null", fine_file="sample/SA_sample_coarse_pristine.tif")
        cls.sim4.add_reproduction_map(reproduction_map="sample/SA_reproduction_coarse.tif")
        cls.sim4.add_death_map(death_map="sample/SA_death.tif")
        cls.sim4.add_dispersal_map(dispersal_map="sample/dispersal_fine2.tif")
        cls.sim4.run()
        cls.coal1 = CoalescenceTree(cls.sim1)
        cls.coal2 = CoalescenceTree(cls.sim2)
        cls.coal3 = CoalescenceTree(cls.sim3)
        cls.coal4 = CoalescenceTree(cls.sim4)

    def testDeathMapNullRaisesError(self):
        """Tests that an error is raised when the reproduction map has a zero value where the density map does not."""
        c = Simulation(logging_level=logging.CRITICAL)
        c.set_simulation_parameters(
            seed=3,
            task=47,
            output_directory="output",
            min_speciation_rate=0.1,
            sigma=4,
            tau=4,
            deme=1,
            sample_size=0.01,
            max_time=2,
            dispersal_relative_cost=1,
            min_num_species=1,
            cutoff=0.0,
            landscape_type="closed",
        )

        with self.assertRaises(RuntimeError):
            c.set_map_files(
                "null",
                fine_file="sample/SA_sample_fine.tif",
                reproduction_map="sample/SA_sample_reproduction_invalid.tif",
            )
            c.run()

    def testOutputRichness(self):
        """Tests the output richness is as expected"""
        self.assertEqual(176, self.coal1.get_species_richness())
        self.assertEqual(215, self.coal2.get_species_richness())
        self.assertEqual(211, self.coal3.get_species_richness())
        self.assertNotEqual(self.coal1.get_species_richness(), self.coal2.get_species_richness())
        self.assertNotEqual(self.coal1.get_species_richness(), self.coal3.get_species_richness())
        self.assertNotEqual(1214, self.coal4.get_species_richness())

    def testOutputNumberIndividuals(self):
        """Tests that the number of individuals simulated in each scenario is correct."""
        self.assertEqual(284, self.coal1.get_number_individuals())
        self.assertEqual(self.coal1.get_number_individuals(), self.coal2.get_number_individuals())
        self.assertEqual(self.coal2.get_number_individuals(), self.coal3.get_number_individuals())
        self.assertEqual(2150, self.coal4.get_number_individuals())

    def testReproductionMapZeroDensity(self):
        """Tests reproduction map works when the density map has zero values."""
        log_stream1 = StringIO()
        sim1 = Simulation(logging_level=50, stream=log_stream1)
        sim1.set_simulation_parameters(
            seed=5, task=47, output_directory="output", min_speciation_rate=0.01, sigma=2, deme=1, sample_size=0.01
        )
        sim1.set_map_files(
            "null", fine_file="sample/SA_sample_fine2.tif", reproduction_map="sample/SA_sample_reproduction.tif"
        )
        sim1.run()
        sim2 = Simulation(logging_level=60)
        sim2.set_simulation_parameters(
            seed=6, task=47, output_directory="output", min_speciation_rate=0.01, sigma=2, deme=1, sample_size=0.01
        )
        sim2.set_map_files(
            "null", fine_file="sample/SA_sample_fine.tif", reproduction_map="sample/SA_sample_reproduction.tif"
        )
        sim2.add_historical_map("sample/SA_sample_fine2.tif", "none", 10.0, 0.0)
        sim2.run()
        log1 = log_stream1.getvalue().replace("\r", "").replace("\n", "")
        self.assertEqual(186, sim1.get_species_richness())
        self.assertEqual(195, sim2.get_species_richness())
        self.assertEqual("Density is zero where reproduction map is non-zero. This is likely incorrect.", log1)


class TestAnalyticalMetacommunityLimits(unittest.TestCase):
    """Tests that the limits on the analytical method for supplying a metacommunity work as intended."""

    @classmethod
    def setUpClass(cls):

        cls.sim = Simulation(logging_level=50)
        cls.sim.set_simulation_parameters(
            seed=10, task=48, output_directory="output", min_speciation_rate=0.000001, sigma=1
        )
        cls.sim.set_map("null", 10, 10)
        cls.sim.run()
        cls.ct = CoalescenceTree(cls.sim)
        cls.ct.wipe_data()
        cls.speciation_rates = [0.001, 0.5, 0.999]
        cls.metacommunity_speciation_rates = [0.000000001, 0.5, 0.99999999]
        cls.ct.set_speciation_parameters(speciation_rates=cls.speciation_rates)
        for metacommunity_speciation_rate in cls.metacommunity_speciation_rates:
            for option in ["simulated", "analytical"]:
                cls.ct.add_metacommunity_parameters(
                    metacommunity_option=option,
                    metacommunity_size=100000,
                    metacommunity_speciation_rate=metacommunity_speciation_rate,
                )
        cls.ct.apply()

    def testMetacommunityParameters(self):
        """Tests that the metacommunity parameters are correctly set"""
        community_reference = 0
        expected_community_parameters = []

        for speciation_rate in self.speciation_rates:
            community_reference += 1
            expected_community_parameters.append(
                {"community_reference": community_reference, "speciation_rate": speciation_rate}
            )
        expected_metacommunity_parameters = {}
        metacommunity_reference = 0
        for metacommunity_speciation_rate in self.metacommunity_speciation_rates:
            for option in ["simulated", "analytical"]:
                metacommunity_reference += 1
                expected_metacommunity_parameters[metacommunity_reference] = {
                    "speciation_rate": metacommunity_speciation_rate,
                    "option": option,
                }
        for each in expected_community_parameters:
            community_parameters = self.ct.get_community_parameters(each["community_reference"])
            self.assertEqual(each["speciation_rate"], community_parameters["speciation_rate"])
            metacommunity_reference = community_parameters["metacommunity_reference"]
            expected_metacommunity_parameters_local = expected_metacommunity_parameters[metacommunity_reference]
            metacommunity_parameters = {
                k: v
                for k, v in self.ct.get_metacommunity_parameters(metacommunity_reference).items()
                if k in expected_metacommunity_parameters_local.keys()
            }

            self.assertEqual(expected_metacommunity_parameters_local, metacommunity_parameters)

    def testSpeciesRichnessMetacommunity(self):
        """Tests that the species richness is correctly reproduced by the metacommunity."""
        expected_richnesses = [1, 1, 1, 1, 1, 1, 2, 69, 100, 2, 69, 100, 2, 69, 100, 2, 69, 100]
        actual_richnesses = []
        for ref in self.ct.get_community_references():
            actual_richnesses.append(self.ct.get_species_richness(ref))
        self.assertEqual(expected_richnesses, actual_richnesses)


@skipLongTest
class TestAnalyticalMatchesSimulated(unittest.TestCase):
    """Tests that the analytical result closely matches the simulated result at large scales"""

    @classmethod
    def setUpClass(cls):
        """Runs the simulations to test matching between the analytical and simulated methods - this takes some time."""
        cls.species_richnesses_local = {0.01: [], 0.1: [], 0.5: [], 0.9: []}
        cls.species_richnesses_sim = {0.01: [], 0.1: [], 0.5: [], 0.9: []}
        cls.species_richnesses_ana = {0.01: [], 0.1: [], 0.5: [], 0.9: []}
        for i in range(1, 11, 1):
            s = Simulation()
            s.set_simulation_parameters(
                seed=i, task=49, output_directory="output", min_speciation_rate=0.01, deme=10000, spatial=False
            )
            s.set_speciation_rates([0.01, 0.1, 0.5, 0.9])
            s.run()
            c = CoalescenceTree(s)
            c.set_speciation_parameters(
                [0.01, 0.1, 0.5, 0.9],
                metacommunity_size=1000000,
                metacommunity_speciation_rate=0.0001,
                metacommunity_option="simulated",
            )
            c.add_metacommunity_parameters(
                metacommunity_size=1000000, metacommunity_speciation_rate=0.0001, metacommunity_option="analytical"
            )
            c.apply()
            c.calculate_richness()
            cls.species_richnesses_local[0.01].append(c.get_species_richness(1))
            cls.species_richnesses_local[0.1].append(c.get_species_richness(2))
            cls.species_richnesses_local[0.5].append(c.get_species_richness(3))
            cls.species_richnesses_local[0.9].append(c.get_species_richness(4))
            cls.species_richnesses_sim[0.01].append(c.get_species_richness(5))
            cls.species_richnesses_sim[0.1].append(c.get_species_richness(6))
            cls.species_richnesses_sim[0.5].append(c.get_species_richness(7))
            cls.species_richnesses_sim[0.9].append(c.get_species_richness(8))
            cls.species_richnesses_ana[0.01].append(c.get_species_richness(9))
            cls.species_richnesses_ana[0.1].append(c.get_species_richness(10))
            cls.species_richnesses_ana[0.5].append(c.get_species_richness(11))
            cls.species_richnesses_ana[0.9].append(c.get_species_richness(12))
        cls.means_sim = {}
        cls.means_ana = {}
        for k in [0.01, 0.1, 0.5, 0.9]:
            cls.means_sim[k] = sum(cls.species_richnesses_sim[k]) / len(cls.species_richnesses_sim[k])
            cls.means_ana[k] = sum(cls.species_richnesses_ana[k]) / len(cls.species_richnesses_ana[k])

    def testSpeciesRichness(self):
        """Quick test to make sure species richnesses are as expected."""
        c1 = CoalescenceTree(os.path.join("output", "data_49_1.db"))
        c2 = CoalescenceTree(os.path.join("output", "data_49_6.db"))
        c3 = CoalescenceTree(os.path.join("output", "data_49_10.db"))
        self.assertEqual(451, c1.get_species_richness(1))
        self.assertEqual(2623, c1.get_species_richness(2))
        self.assertEqual(6957, c1.get_species_richness(3))
        self.assertEqual(9486, c1.get_species_richness(4))
        self.assertEqual(153, c1.get_species_richness(5))
        self.assertEqual(332, c1.get_species_richness(6))
        self.assertEqual(438, c1.get_species_richness(7))
        self.assertEqual(470, c1.get_species_richness(8))
        self.assertEqual(159, c1.get_species_richness(9))
        self.assertEqual(314, c1.get_species_richness(10))
        self.assertEqual(424, c1.get_species_richness(11))
        self.assertEqual(459, c1.get_species_richness(12))
        self.assertEqual(167, c2.get_species_richness(5))
        self.assertEqual(334, c2.get_species_richness(6))
        self.assertEqual(413, c2.get_species_richness(7))
        self.assertEqual(470, c2.get_species_richness(8))
        self.assertEqual(164, c2.get_species_richness(9))
        self.assertEqual(338, c2.get_species_richness(10))
        self.assertEqual(424, c2.get_species_richness(11))
        self.assertEqual(464, c2.get_species_richness(12))
        self.assertEqual(163, c3.get_species_richness(5))
        self.assertEqual(318, c3.get_species_richness(6))
        self.assertEqual(439, c3.get_species_richness(11))
        self.assertEqual(446, c3.get_species_richness(12))

    def testMeansClose(self):
        """Tests that the means are roughly equivalent between the simulated and the analytical methods."""
        mean_sim = {}
        mean_ana = {}
        expected_sim = {0.01: 168.0, 0.1: 327.2, 0.5: 433.8, 0.9: 466.0}
        expected_ana = {0.01: 175.0, 0.1: 328.9, 0.5: 430.2, 0.9: 457.5}
        for k in self.species_richnesses_sim.keys():
            mean_sim[k] = float(sum(self.species_richnesses_sim[k])) / float(len(self.species_richnesses_sim[k]))
            mean_ana[k] = float(sum(self.species_richnesses_ana[k])) / float(len(self.species_richnesses_ana[k]))
        self.assertEqual(expected_sim, mean_sim)
        self.assertEqual(expected_ana, mean_ana)


@skipLongTest
class TestLargeScaleAnalytical(unittest.TestCase):
    """Tests a single large-scale analytical run matches the expected result."""

    def testLargeScaleAnalyticalResult(self):
        s = Simulation()
        s.set_simulation_parameters(
            seed=1, task=50, output_directory="output", min_speciation_rate=0.5, spatial=False, deme=100000
        )
        s.run()
        c = CoalescenceTree(s)
        c.set_speciation_parameters([0.5, 0.9])
        c.add_metacommunity_parameters(
            metacommunity_size=10000000, metacommunity_speciation_rate=0.001, metacommunity_option="simulated"
        )
        c.add_metacommunity_parameters(
            metacommunity_size=10000000, metacommunity_speciation_rate=0.001, metacommunity_option="analytical"
        )
        c.apply()
        self.assertEqual(69311, c.get_species_richness(1))
        self.assertEqual(20626, c.get_species_richness(2))
        self.assertEqual(23362, c.get_species_richness(3))
        self.assertEqual(20690, c.get_species_richness(4))
        self.assertEqual(23495, c.get_species_richness(5))
