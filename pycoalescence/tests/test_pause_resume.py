"""Tests the pause and resume functionality of simulations to ensure it is the same as a continuous simulation."""
import logging
import os
import platform
import shutil
import sqlite3
import unittest

from setup_tests import setUpAll, tearDownAll, skipLongTest

from pycoalescence import Simulation, CoalescenceTree
from pycoalescence.sqlite_connection import check_sql_table_exist
from pycoalescence.future_except import FileNotFoundError, FileExistsError


def setUpModule():
    """
    Creates the output directory and moves logging files
    """
    setUpAll()
    for path in ["output spaced", "output spaced2"]:
        if os.path.exists(path):
            shutil.rmtree(path)


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
        self.coal = Simulation(logging_level=40)
        self.coal2 = Simulation(logging_level=40)
        self.tree2 = CoalescenceTree()
        self.coal.set_simulation_parameters(
            seed=10,
            task=6,
            output_directory="output",
            min_speciation_rate=0.05,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        self.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal.run()
        self.coal2.set_simulation_parameters(
            seed=10,
            task=7,
            output_directory="output",
            min_speciation_rate=0.05,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        self.coal2.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal2.run()
        self.tree2.set_database(self.coal2)
        self.tree2.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree2.apply()
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
        actual_sim_parameters = dict(
            seed=10,
            task=6,
            output_dir="output",
            speciation_rate=0.05,
            sigma=2.0,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
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
            sample_file="sample/SA_samplemaskINT.tif",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=0,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
            time_config_file="null",
        )
        params = tree2.get_simulation_parameters()
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))

    def testCanResume(self):
        """
        Tests that simulations can resume execution.
        """
        self.coal.resume_coalescence("output", 10, 6, 10, protracted=False, spatial=True)
        self.tree1.set_database(self.coal)
        actual_sim_parameters = dict(
            seed=10,
            task=6,
            output_dir="output",
            speciation_rate=0.05,
            sigma=2.0,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
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
            sample_file="sample/SA_samplemaskINT.tif",
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
            time_config_file="null",
        )
        params = self.tree1.get_simulation_parameters()
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key])

    def testPauseSimMatchesSingleRunSim(self):
        """
        Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
        identical results. Checks using comparison of the SPECIES_LIST tables
        """
        self.tree1.set_database(self.coal)
        self.tree1.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree1.apply()
        dict1 = self.tree1.get_simulation_parameters()
        dict2 = self.tree2.get_simulation_parameters()
        for key in dict1.keys():
            if key != "task" and key != "max_time":
                self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
        self.assertEqual(self.coal.get_species_richness(), self.coal2.get_species_richness())
        single_run_species_list = list(self.tree1.get_species_list())
        pause_sim_species_list = list(self.tree2.get_species_list())
        self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
        self.assertListEqual([x for x in pause_sim_species_list], [x for x in single_run_species_list])


class TestSimulationPause2(unittest.TestCase):
    """
    Test a simple run on a landscape using sampling with pause/resume functionality with protractedness
    """

    @classmethod
    def setUpClass(self):
        """
        Sets up the Coalescence object test case.
        """
        self.coal = Simulation(logging_level=logging.CRITICAL)  # TODO set these back
        self.coal2 = Simulation(logging_level=logging.CRITICAL)
        self.tree2 = CoalescenceTree(logging_level=logging.CRITICAL)
        self.coal.set_simulation_parameters(
            seed=10,
            task=26,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
            protracted=True,
            min_speciation_gen=0.0,
            max_speciation_gen=100,
        )
        self.coal3 = Simulation(logging_level=logging.CRITICAL)
        self.coal3.set_simulation_parameters(
            seed=10,
            task=26,
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
            min_speciation_gen=0.0,
            max_speciation_gen=100,
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal3.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        # self.coal.detect_map_dimensions()
        self.coal.run()
        try:
            self.coal3.finalise_setup()
        except FileExistsError:
            pass
        self.coal3.run_coalescence()
        self.coal3.apply_speciation_rates()
        self.coal2.set_simulation_parameters(
            seed=10,
            task=27,
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
            min_speciation_gen=0.0,
            max_speciation_gen=100,
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal2.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal2.set_speciation_rates([0.5])
        self.coal2.run()
        self.tree2.set_database(self.coal2)
        self.tree2.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree2.apply()
        self.tree1 = CoalescenceTree()

    def testCanResume2(self):
        """
        Tests that simulations can resume execution by detecting the paused files
        """
        self.tree1.set_database(self.coal3)
        actual_sim_parameters = dict(
            seed=10,
            task=26,
            output_dir="output",
            speciation_rate=0.5,
            sigma=2.0,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
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
            sample_file="sample/SA_samplemaskINT.tif",
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
            protracted=1,
            min_speciation_gen=0.0,
            max_speciation_gen=100.0,
            dispersal_map="none",
            time_config_file="null",
        )
        params = self.tree1.get_simulation_parameters()
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key])

    def testRaisesErrorOnProtractedResume(self):
        """
        Tests that an error is raise if the protracted simulation is attempted to be run from a non-protracted paused
        file, or visa versa.
        """
        coaltmp = Simulation()
        coaltmp.set_simulation_parameters(
            seed=10,
            task=26,
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
            min_speciation_gen=0.0,
            max_speciation_gen=100,
        )
        with self.assertRaises(RuntimeError):
            coaltmp.resume_coalescence(task=26, seed=10, pause_directory="output", max_time=10, out_directory="output")

    def testPauseSimMatchesSingleRunSim2(self):
        """
        Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
        identical results. Checks using comparison of the SPECIES_LIST tables
        """
        self.tree1.set_database(self.coal3)
        self.tree1.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree1.apply()
        self.assertEqual(self.coal3.get_species_richness(), self.coal2.get_species_richness())
        single_run_species_list = list(self.tree1.get_species_list())
        pause_sim_species_list = list(self.tree2.get_species_list())
        dict1 = self.tree1.get_simulation_parameters()
        dict2 = self.tree2.get_simulation_parameters()
        for key in dict1.keys():
            if key != "task":
                self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
        # print(pause_sim_species_list)
        # print(single_run_species_list)
        self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
        self.assertListEqual([x for x in pause_sim_species_list], [x for x in single_run_species_list])


class TestSimulationPause3(unittest.TestCase):
    """
    Test a simple run on a landscape using sampling, moving the paused files between simulations.
    """

    @classmethod
    def setUpClass(self):
        """
        Sets up the Coalescence object test case.
        """
        self.coal = Simulation(logging_level=40)
        self.coal2 = Simulation(logging_level=40)
        self.tree2 = CoalescenceTree()
        self.coal.set_simulation_parameters(
            seed=10,
            task=16,
            output_directory="output",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        # self.coal.detect_map_dimensions()
        self.coal.run()
        self.coal2.set_simulation_parameters(
            seed=10,
            task=17,
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
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal2.set_map_files(
            sample_file="sample/SA_samplemaskINT.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal2.set_speciation_rates([0.5])
        self.coal2.run()
        self.tree2.set_database(self.coal2)
        self.tree2.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree2.apply()
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
        actual_sim_parameters = dict(
            seed=10,
            task=16,
            output_dir="output",
            speciation_rate=0.5,
            sigma=2.0,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
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
            sample_file="sample/SA_samplemaskINT.tif",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=0,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
            time_config_file="null",
        )
        params = tree2.get_simulation_parameters()
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))

    def testCanResume(self):
        """
        Tests that simulations can resume execution.
        """
        paused_file_list = ["Dump_main_"]
        os.mkdir("output2")
        os.mkdir("output2/Pause")
        for file in paused_file_list:
            os.rename(
                os.path.join("output", "Pause", file + "16_10.csv"),
                os.path.join("output2", "Pause", file + "16_10.csv"),
            )
        if not os.path.exists("output3"):
            os.mkdir("output3")
        self.coal.resume_coalescence("output2", 10, 16, 10, out_directory="output3")
        self.tree1.set_database(self.coal)
        actual_sim_parameters = dict(
            seed=10,
            task=16,
            output_dir="output3",
            speciation_rate=0.5,
            sigma=2.0,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
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
            sample_file="sample/SA_samplemaskINT.tif",
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
            time_config_file="null",
        )
        params = self.tree1.get_simulation_parameters()
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key])

    def testPauseSimMatchesSingleRunSim(self):
        """
        Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
        identical results. Checks using comparison of the SPECIES_LIST tables
        """
        self.tree1.set_database(self.coal)
        self.tree1.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree1.apply()
        self.assertEqual(self.coal.get_species_richness(), self.coal2.get_species_richness())
        dict1 = self.tree1.get_simulation_parameters()
        dict2 = self.tree2.get_simulation_parameters()
        for key in dict1.keys():
            if key != "task" and key != "max_time" and key != "output_dir":
                self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
        single_run_species_list = list(self.tree1.get_species_list())
        pause_sim_species_list = list(self.tree2.get_species_list())
        self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
        self.assertListEqual([x for x in pause_sim_species_list], [x for x in single_run_species_list])


@skipLongTest
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
        self.coal.set_simulation_parameters(
            seed=11,
            task=16,
            output_directory="output spaced",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        # self.coal.set_simulation_parameters(6, 6, "output", 0.5, 4, 4, 1, 0.1, 1, 1, 200, 0, 200, "null")
        self.coal.set_map_files(
            sample_file="sample/SA_samplemaskINT spaced.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        # self.coal.detect_map_dimensions()
        self.coal.run()
        self.coal2.set_simulation_parameters(
            seed=11,
            task=17,
            output_directory="output spaced",
            min_speciation_rate=0.5,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        self.coal2.set_map_files(
            sample_file="sample/SA_samplemaskINT spaced.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        self.coal2.set_speciation_rates([0.5])
        self.coal2.run()
        self.tree2.set_database(self.coal2)
        self.tree2.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree2.apply()

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
        actual_sim_parameters = dict(
            seed=11,
            task=16,
            output_dir="output spaced",
            speciation_rate=0.5,
            sigma=2.0,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
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
            sample_file="sample/SA_samplemaskINT spaced.tif",
            grid_x=13,
            grid_y=13,
            sample_x=13,
            sample_y=13,
            sample_x_offset=0,
            sample_y_offset=0,
            historical_coarse_map="none",
            historical_fine_map="none",
            sim_complete=0,
            dispersal_method="normal",
            m_probability=0.0,
            cutoff=0.0,
            landscape_type="closed",
            protracted=0,
            min_speciation_gen=0.0,
            max_speciation_gen=0.0,
            dispersal_map="none",
            time_config_file="null",
        )
        params = tree1.get_simulation_parameters()
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key], msg="Error in {}".format(key))

    def testCanResume(self):
        """
        Tests that simulations can resume execution.
        """
        if not os.path.exists("output2 spaced"):
            os.mkdir("output2 spaced")
        self.coal3.resume_coalescence(
            pause_directory="output spaced", seed=11, task=16, max_time=10, out_directory="output2 spaced"
        )
        self.tree3.set_database(self.coal3)
        actual_sim_parameters = dict(
            seed=11,
            task=16,
            output_dir="output2 spaced",
            speciation_rate=0.5,
            sigma=2.0,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=10,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=0.0,
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
            sample_file="sample/SA_samplemaskINT spaced.tif",
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
            time_config_file="null",
        )
        params = self.tree3.get_simulation_parameters()
        for key in params.keys():
            self.assertEqual(params[key], actual_sim_parameters[key])

    def testPauseSimMatchesSingleRunSim(self):
        """
        Tests that the two simulations (either pausing, then resuming, or just running straight to completion) produce
        identical results. Checks using comparison of the SPECIES_LIST tables
        """
        self.tree3.set_database(self.coal3)
        self.tree3.set_speciation_parameters(
            speciation_rates=[0.6, 0.7], record_spatial="T", record_fragments="F", sample_file="null"
        )
        self.tree3.apply()
        self.assertEqual(self.tree3.get_species_richness(), self.tree2.get_species_richness())
        dict1 = self.tree3.get_simulation_parameters()
        dict2 = self.tree2.get_simulation_parameters()
        for key in dict1.keys():
            if key != "task" and key != "max_time" and key != "output_dir":
                self.assertEqual(dict1[key], dict2[key], "{} not equal.".format(key))
        single_run_species_list = list(self.tree3.get_species_list())
        pause_sim_species_list = list(self.tree2.get_species_list())
        # print(pause_sim_species_list)
        # print(single_run_species_list)
        self.assertAlmostEqual(single_run_species_list[0][9], pause_sim_species_list[0][9], 16)
        self.assertListEqual([x for x in pause_sim_species_list], [x for x in single_run_species_list])


class TestPauseSpeciateRemaining(unittest.TestCase):
    """Tests functionality relating to termination of a paused simulation by speciating every remaining lineage."""

    @classmethod
    def setUpClass(cls):
        """Runs a simulation to pause and restart from."""
        cls.sim = Simulation(logging_level=50)
        cls.sim.set_simulation_parameters(
            seed=14,
            task=17,
            output_directory="output",
            min_speciation_rate=0.00000000001,
            sigma=2,
            tau=2,
            deme=1,
            sample_size=0.1,
            max_time=0,
            dispersal_relative_cost=1,
            min_num_species=1,
            dispersal_method="normal",
        )
        cls.sim.set_map_files(
            sample_file="sample/SA_samplemaskINT spaced.tif",
            fine_file="sample/SA_sample_fine.tif",
            coarse_file="sample/SA_sample_coarse.tif",
        )
        cls.sim.run()
        shutil.copy(cls.sim.output_database, os.path.join("output", "data_17_14b.db"))
        cls.ct = CoalescenceTree()
        cls.ct.speciate_remaining(cls.sim)

    def testPausedSimulationExists(self):
        """Tests that the paused simulation exists and the tables have been stored properly."""
        paused_db = os.path.join("output", "data_{}_{}b.db".format(17, 14))
        self.assertTrue(os.path.exists(paused_db))
        with self.assertRaises(IOError):
            ct = CoalescenceTree(paused_db)
        ct = None
        database = sqlite3.connect(paused_db)
        self.assertTrue(check_sql_table_exist(database, "SPECIES_LIST"))
        self.assertTrue(check_sql_table_exist(database, "SIMULATION_PARAMETERS"))
        self.assertFalse(
            bool(database.cursor().execute("SELECT sim_complete FROM SIMULATION_PARAMETERS").fetchall()[0][0])
        )

    @unittest.skipIf(platform.system() == "Windows", "Skipping tests not compatible with Windows.")
    def testForcedSpeciation(self):
        """Tests that the forced speciation of remaining lineages works as expected."""
        ct = CoalescenceTree(self.sim)
        ct.set_speciation_parameters(speciation_rates=[0.1, 0.5, 0.95])
        ct.apply()
        # if "win" in sys.platform:
        # 	self.assertEqual(1171, ct.get_species_richness(1))
        # 	self.assertEqual(1172, ct.get_species_richness(2))
        # 	self.assertEqual(1173, ct.get_species_richness(3))
        # else:
        self.assertEqual(1170, ct.get_species_richness(1))
        self.assertEqual(1170, ct.get_species_richness(2))
        self.assertEqual(1173, ct.get_species_richness(3))
        ct = CoalescenceTree()
        with self.assertRaises(FileNotFoundError):
            ct.speciate_remaining("notafile.db")
        with self.assertRaises(IOError):
            ct.speciate_remaining(self.sim)
