"""
Tests the coalescence tree object.
"""
import os
import random
import shutil
import sqlite3
import sys
import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from setup_tests import setUpAll, tearDownAll, skipLongTest

from pycoalescence import Simulation
from pycoalescence.coalescence_tree import CoalescenceTree, get_parameter_description
from pycoalescence.sqlite_connection import check_sql_table_exist


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
            t.get_species_richness()
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
            _ = t.get_simulation_parameters()
        with self.assertRaises(RuntimeError):
            t.get_fragment_abundances("null", 1)
        with self.assertRaises(RuntimeError):
            t.get_species_richness()
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
        tmp_dict = {
            "habitat_change_rate": "the rate of change from present density maps to historic density maps",
            "sample_file": "the sample area map for spatially selective sampling. Can be null to sample all " "cells",
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
            "fine_map_y_offset": "the number of cells the fine map is offset from the sample map in the y "
            "dimension, at the fine resolution",
            "gen_since_historical": "the number of generations that occur before the historical, or historic,"
            " state is reached",
            "dispersal_method": "the dispersal method used. Can be one of 'normal', 'norm-uniform' or " "'fat-tail'.",
            "historical_fine_map": "the historical, or historic, coarse density map file location",
            "coarse_map_scale": "the scale of the coarse density map compared to the fine density map. 1 "
            "means equal density",
            "grid_x": "the simulated grid x dimension",
            "coarse_map_file": "the density map file location at the coarser resolution, covering a larger " "area",
            "min_num_species": "the minimum number of species known to exist (currently has no effect)",
            "historical_coarse_map": "the historical, or historic, coarse density map file location",
            "m_probability": "the probability of choosing from the uniform dispersal kernel in normal-uniform"
            " dispersal",
            "sigma": "the sigma dispersal value for normal, fat-tailed and normal-uniform dispersals",
            "deme": "the number of individuals inhabiting a cell at a map density of 1",
            "time_config_file": "will be 'set' if temporal sampling is used, 'null' otherwise",
            "coarse_map_y": "the coarse density map y dimension",
            "fine_map_x": "the fine density map x dimension",
            "coarse_map_y_offset": "the number of cells the coarse map is offset from the fine map in the y "
            "dimension, at the fine resolution",
            "cutoff": "the maximal dispersal distance possible, for normal-uniform dispersal",
            "fine_map_y": "the fine density map y dimension",
            "sample_size": "the proportion of individuals to sample from each cell (0-1)",
            "fine_map_x_offset": "the number of cells the fine map is offset from the sample map in the x "
            "dimension, at the fine resolution",
            "speciation_rate": "the minimum speciation rate the simulation was run with",
            "task": "the job or task reference number given to this simulation",
            "coarse_map_x_offset": "the number of cells the coarse map is offset from the fine map in the x "
            "dimension, at the fine resolution",
            "landscape_type": "if false, landscapes have hard boundaries. Otherwise, can be infinite, "
            "with 1s everywhere, or tiled_coarse or tiled_fine for repeated units of tiled "
            "maps",
            "max_time": "the maximum simulation time to run for (in seconds)",
            "sim_complete": "set to true upon simulation completion, false for incomplete simulations",
            "protracted": "if true, the simulation was run with protracted speciation.",
            "min_speciation_gen": "the minimum number of generations required before speciation can occur",
            "max_speciation_gen": "the maximum number of generations a lineage can exist before it is " "speciated",
            "dispersal_map": "a tif file where rows represent cumulative dispersal probability to every other "
            "cell, using the row number = x + (y * x_max)",
        }
        t = CoalescenceTree("sample/sample.db")
        sim_output = t.get_simulation_parameters()
        for key in sim_output.keys():
            self.assertIn(key, get_parameter_description().keys())
            self.assertEqual(get_parameter_description(key), t.get_parameter_description(key))
        for key in get_parameter_description().keys():
            self.assertIn(key, sim_output.keys())
        for key in tmp_dict.keys():
            self.assertEqual(tmp_dict[key], get_parameter_description(key))
        self.assertDictEqual(tmp_dict, get_parameter_description())
        with self.assertRaises(KeyError):
            get_parameter_description(key="notakey")
        dispersal_parameters = t.dispersal_parameters()
        expected_disp_dict = {
            "dispersal_method": "normal",
            "sigma": 3.55,
            "tau": 0.470149,
            "m_probability": 0,
            "cutoff": 0,
        }
        for key in dispersal_parameters.keys():
            self.assertIn(key, tmp_dict.keys())
            self.assertIn(key, expected_disp_dict.keys())
        for key, val in expected_disp_dict.items():
            self.assertIn(key, dispersal_parameters.keys())
            if isinstance(val, float):
                self.assertAlmostEqual(val, dispersal_parameters[key])
            else:
                self.assertEqual(val, dispersal_parameters[key])


class TestCoalescenceTreeSettingSpeciationParameters(unittest.TestCase):
    """Tests that the correct errors are raised when speciation parameters are supplied incorrectly."""

    @classmethod
    def setUpClass(cls):
        """Generates the temporary databases to attempt analysis on."""
        src = [os.path.join("sample", "sample{}.db".format(x)) for x in [2, 3]]
        cls.dst = [os.path.join("output", "sample{}.db".format(x)) for x in [2, 3]]
        for tmp_src, tmp_dst in zip(src, cls.dst):
            if os.path.exists(tmp_dst):
                os.remove(tmp_dst)
            shutil.copy(tmp_src, tmp_dst)

    def testSetSpeciationRates(self):
        """Tests setting speciation rates works as intended and raises appropriate errors"""
        ct = CoalescenceTree(self.dst[0])
        for attempt in ["a string", ["a", "string"], [["list", "list2"], 0.2, 0.1], [None]]:
            with self.assertRaises(TypeError):
                ct._set_speciation_rates(attempt)
        with self.assertRaises(RuntimeError):
            ct._set_speciation_rates(None)
        for attempt in [-10, -2.0, 1.1, 100, [-1, 0.1, 0.2], [0.2, 0.8, 1.1]]:
            with self.assertRaises(ValueError):
                ct._set_speciation_rates(attempt)
        expected_list = [0.1, 0.2, 0.3]
        ct._set_speciation_rates(expected_list)
        self.assertEqual(expected_list, ct.applied_speciation_rates_list)
        ct._set_speciation_rates(0.2)
        self.assertEqual([0.2], ct.applied_speciation_rates_list)

    def testSetRecordFragments(self):
        """Tests that setting the record_fragments flag works as expected."""
        ct = CoalescenceTree(self.dst[0])
        ct._set_record_fragments(True)
        self.assertEqual("null", ct.record_fragments)
        ct._set_record_fragments(False)
        self.assertEqual("F", ct.record_fragments)
        for each in ["PlotBiodiversityMetrics.db", "doesntexist.csv"]:
            config_path = os.path.join("sample", each)
            with self.assertRaises(IOError):
                ct._set_record_fragments(config_path)
        expected = os.path.join("sample", "FragmentsTest.csv")
        ct._set_record_fragments(expected)
        self.assertEqual(expected, ct.record_fragments)

    def testSetRecordSpatial(self):
        """Tests that the setting the record_spatial flag works as expected"""
        ct = CoalescenceTree(self.dst[0])
        ct._set_record_spatial("T")
        self.assertTrue(ct.record_spatial)
        ct._set_record_spatial("F")
        self.assertFalse(ct.record_spatial)
        with self.assertRaises(TypeError):
            ct._set_record_spatial("nota bool")
        ct._set_record_spatial(True)
        self.assertTrue(ct.record_spatial)

    def testSetMetacommunityParameters(self):
        """Tests that setting the metacommunity parameters works as expected."""
        ct = CoalescenceTree(self.dst[0])
        for size, spec in [[-10, 0.1], [10, -0.1], [10, 1.1]]:
            with self.assertRaises(ValueError):
                ct.fragments = "F"
                ct._set_record_fragments(False)
                ct._set_record_spatial(False)
                ct.times = [0.0]
                ct._set_metacommunity_parameters(size, spec)
        ct._set_metacommunity_parameters()
        self.assertEqual(0.0, ct.metacommunity_size)
        self.assertEqual(0.0, ct.metacommunity_speciation_rate)
        ct._set_metacommunity_parameters(10, 0.1, "simulated")
        self.assertEqual(10, ct.metacommunity_size)
        self.assertEqual(0.1, ct.metacommunity_speciation_rate)

    def testSetProtractedParameters(self):
        """Tests that setting the protracted parameters works as expected."""
        ct = CoalescenceTree(self.dst[0])
        with self.assertRaises(ValueError):
            ct._set_protracted_parameters(0.1, 100)
        ct = CoalescenceTree(self.dst[1])
        ct._set_protracted_parameters(10, 100)
        self.assertEqual((10.0, 100.0), ct.protracted_parameters[0])
        ct.protracted_parameters = []
        for min_proc, max_proc in [[200, 5000], [80, 50], [200, 11000]]:
            with self.assertRaises(ValueError):
                ct._check_protracted_parameters(min_proc, max_proc)
            with self.assertRaises(ValueError):
                ct._set_protracted_parameters(min_proc, max_proc)
            with self.assertRaises(ValueError):
                ct.add_protracted_parameters(min_proc, max_proc)
        ct._set_protracted_parameters(50, 5000)
        self.assertEqual((50.0, 5000.0), ct.protracted_parameters[0])
        ct.protracted_parameters = []
        ct._set_protracted_parameters()
        self.assertEqual((0.0, 0.0), ct.protracted_parameters[0])

    def testSetSampleFile(self):
        """Tests that the sample file is correctly set."""
        ct = CoalescenceTree(self.dst[0])
        for file in ["notafile.tif", os.path.join("sample", "sample.db")]:
            with self.assertRaises(IOError):
                ct._set_sample_file(file)
        ct._set_sample_file()
        self.assertEqual("null", ct.sample_file)
        expected_file = os.path.join("sample", "SA_sample_coarse.tif")
        ct._set_sample_file(expected_file)
        self.assertEqual(expected_file, ct.sample_file)

    def testSetTimes(self):
        """Tests that times are correctly set."""
        ct = CoalescenceTree(self.dst[0])
        ct._set_times(None)
        self.assertEqual(0.0, ct.times[0])
        with self.assertRaises(TypeError):
            ct.add_times(0.5)
        with self.assertRaises(TypeError):
            ct.add_times([0.2, 0.5, "string"])
        ct.times = None
        ct.add_times([0.2, 0.5, 10])
        self.assertEqual([0.0, 0.2, 0.5, 10.0], ct.times)
        ct.times = None
        ct._set_times(0.2)
        self.assertEqual([0.0, 0.2], ct.times)
        ct.times = None
        ct._set_times([0.1, 0.5, 10.0])
        self.assertEqual([0.0, 0.1, 0.5, 10.0], ct.times)


class TestCoalescenceTreeParameters(unittest.TestCase):
    """Tests that parameters are correctly obtained from the databases and the relevant errors are raised."""

    def testCommunityParameters1(self):
        """Tests the community parameters make sense in a very simple community."""
        shutil.copyfile(os.path.join("sample", "sample3.db"), os.path.join("output", "temp_sample3.db"))
        t = CoalescenceTree(os.path.join("output", "temp_sample3.db"), logging_level=50)
        self.assertEqual([], t.get_metacommunity_references())
        self.assertEqual([1], t.get_community_references())
        params = t.get_community_parameters(1)
        expected_dict = {
            "speciation_rate": 0.001,
            "time": 0.0,
            "fragments": 0,
            "metacommunity_reference": 0,
            "min_speciation_gen": 100.0,
            "max_speciation_gen": 10000.0,
        }
        self.assertEqual(expected_dict, params)
        with self.assertRaises(sqlite3.Error):
            t.get_metacommunity_parameters(1)
        with self.assertRaises(KeyError):
            t.get_community_parameters(2)
        with self.assertRaises(KeyError):
            t.get_community_reference(0.1, 0.0, 0, 0, 0.0, min_speciation_gen=100.0, max_speciation_gen=10000.0)
        with self.assertRaises(KeyError):
            _ = t.get_community_reference(speciation_rate=0.001, time=0.0, fragments=False)
        ref = t.get_community_reference(
            speciation_rate=0.001, time=0.0, fragments=False, min_speciation_gen=100.0, max_speciation_gen=10000.0
        )
        self.assertEqual(1, ref)
        self.assertEqual(expected_dict, t.get_community_parameters(ref))
        t.wipe_data()
        with self.assertRaises(IOError):
            t.get_community_parameters_pd()

    def testCommunityParameters2(self):
        """Tests the community parameters make sense in a very simple community."""
        t = CoalescenceTree(os.path.join("sample", "sample4.db"))
        self.assertEqual([1, 2, 3, 4, 5], t.get_community_references())
        expected_params1 = {"speciation_rate": 0.1, "time": 0.0, "fragments": 0, "metacommunity_reference": 0}
        expected_params2 = {"speciation_rate": 0.1, "time": 0.0, "fragments": 0, "metacommunity_reference": 1}
        expected_params3 = {"speciation_rate": 0.2, "time": 0.0, "fragments": 0, "metacommunity_reference": 1}
        expected_params4 = {"speciation_rate": 0.1, "time": 0.0, "fragments": 0, "metacommunity_reference": 2}
        expected_params5 = {"speciation_rate": 0.2, "time": 0.0, "fragments": 0, "metacommunity_reference": 2}
        expected_meta_params1 = {
            "speciation_rate": 0.001,
            "metacommunity_size": 10000.0,
            "option": "simulated",
            "external_reference": 0,
        }
        expected_meta_params2 = {
            "speciation_rate": 0.001,
            "metacommunity_size": 10000.0,
            "option": "analytical",
            "external_reference": 0,
        }

        params1 = t.get_community_parameters(1)
        params2 = t.get_community_parameters(2)
        params3 = t.get_community_parameters(3)
        params4 = t.get_community_parameters(4)
        params5 = t.get_community_parameters(5)
        params6 = t.get_metacommunity_parameters(1)
        params7 = t.get_metacommunity_parameters(2)
        self.assertEqual([1, 2], t.get_metacommunity_references())
        self.assertEqual(expected_params1, params1)
        self.assertEqual(expected_params2, params2)
        self.assertEqual(expected_params3, params3)
        self.assertEqual(expected_params4, params4)
        self.assertEqual(expected_params5, params5)
        self.assertEqual(expected_meta_params1, params6)
        self.assertEqual(expected_meta_params2, params7)
        with self.assertRaises(KeyError):
            t.get_community_parameters(6)
        with self.assertRaises(KeyError):
            t.get_metacommunity_parameters(3)
        ref1 = t.get_community_reference(speciation_rate=0.1, time=0.0, fragments=False)
        with self.assertRaises(KeyError):
            t.get_community_reference(
                speciation_rate=0.1, time=0.0, fragments=False, min_speciation_gen=0.1, max_speciation_gen=10000.0
            )
        ref2 = t.get_community_reference(
            speciation_rate=0.1,
            time=0.0,
            fragments=False,
            metacommunity_size=10000.0,
            metacommunity_speciation_rate=0.001,
            metacommunity_option="simulated",
        )
        with self.assertRaises(KeyError):
            t.get_community_reference(
                speciation_rate=0.1,
                time=0.0,
                fragments=False,
                metacommunity_size=10000.0,
                metacommunity_speciation_rate=0.01,
                metacommunity_option="simulated",
            )
        ref3 = t.get_community_reference(
            speciation_rate=0.2,
            time=0.0,
            fragments=False,
            metacommunity_size=10000.0,
            metacommunity_speciation_rate=0.001,
            metacommunity_option="simulated",
        )
        ref4 = t.get_community_reference(
            speciation_rate=0.1,
            time=0.0,
            fragments=False,
            metacommunity_size=10000.0,
            metacommunity_speciation_rate=0.001,
            metacommunity_option="analytical",
        )
        ref5 = t.get_community_reference(
            speciation_rate=0.2,
            time=0.0,
            fragments=False,
            metacommunity_size=10000.0,
            metacommunity_speciation_rate=0.001,
            metacommunity_option="analytical",
        )
        self.assertEqual(1, ref1)
        self.assertEqual(2, ref2)
        self.assertEqual(3, ref3)
        self.assertEqual(4, ref4)
        self.assertEqual(5, ref5)
        expected_community_params_list = []
        for reference in t.get_community_references():
            params = t.get_community_parameters(reference)
            params["reference"] = reference
            expected_community_params_list.append(params)
        expected_community_params = pd.DataFrame(expected_community_params_list)
        actual_output = t.get_community_parameters_pd()
        assert_frame_equal(expected_community_params, actual_output, check_like=True)

    def testIsComplete(self):
        """Tests sims are correctly identified as complete."""
        t = CoalescenceTree(os.path.join("sample", "sample4.db"))
        self.assertTrue(t.is_complete)


class TestCoalescenceTreeAnalysis(unittest.TestCase):
    """Tests analysis is performed correctly"""

    @classmethod
    def setUpClass(cls):
        """Sets up the Coalescence object test case."""
        dst1 = os.path.join("output", "sampledb0.db")
        for i in range(0, 11):
            dst = os.path.join("output", "sampledb{}.db".format(i))
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copyfile(os.path.join("sample", "sample.db"), dst)
        shutil.copyfile(os.path.join("sample", "nse_reference.db"), os.path.join("output", "nse_reference1.db"))
        random.seed(2)
        cls.test = CoalescenceTree(dst1, logging_level=50)
        cls.test.clear_calculations()
        cls.test.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        cls.test.calculate_fragment_richness()
        cls.test.calculate_fragment_octaves()
        cls.test.calculate_octaves_error()
        cls.test.calculate_alpha_diversity()
        cls.test.calculate_beta_diversity()
        cls.test2 = CoalescenceTree()
        cls.test2.set_database(os.path.join("sample", "sample_nofrag.db"))
        dstx = os.path.join("output", "sampledbx.db")
        shutil.copyfile(dst1, dstx)
        c = CoalescenceTree(dstx)
        c.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        c.calculate_goodness_of_fit()

    @classmethod
    def tearDownClass(cls):
        """
        Removes the files from output."
        """
        cls.test.clear_calculations()

    def testComparisonDataNoExistError(self):
        c = CoalescenceTree(os.path.join("sample", "sample.db"))
        with self.assertRaises(IOError):
            c.import_comparison_data(os.path.join("sample", "doesnotexist.db"))

    def testFragmentOctaves(self):
        num = self.test.cursor.execute(
            "SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'P09' AND octave == 0"
            " AND community_reference == 1"
        ).fetchall()[0][0]
        self.assertEqual(num, 7, msg="Fragment octaves not correctly calculated.")
        num = self.test.cursor.execute(
            "SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'P09' AND octave == 0 "
            " AND community_reference == 2"
        ).fetchall()[0][0]
        self.assertEqual(num, 7, msg="Fragment octaves not correctly calculated.")
        num = self.test.cursor.execute(
            "SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'cerrogalera' AND octave == 1 "
            " AND community_reference == 1"
        ).fetchall()[0][0]
        self.assertEqual(num, 3, msg="Fragment octaves not correctly calculated.")
        num = self.test.cursor.execute(
            "SELECT richness FROM FRAGMENT_OCTAVES WHERE fragment == 'whole' AND octave == 1 "
            " AND community_reference == 2"
        ).fetchall()[0][0]
        self.assertEqual(num, 221, msg="Fragment octaves not correctly calculated.")

    def testFragmentAbundances(self):
        """
        Tests that fragment abundances are produced properly by the fragment detection functions.

        """
        num = self.test.cursor.execute(
            "SELECT COUNT(fragment) FROM FRAGMENT_ABUNDANCES WHERE fragment == 'P09' " " AND community_reference == 1"
        ).fetchall()[0][0]
        self.assertEqual(num, 9, msg="Fragment abundances not correctly calculated.")
        num = self.test.cursor.execute(
            "SELECT COUNT(fragment) FROM FRAGMENT_ABUNDANCES WHERE fragment == 'P09' " " AND community_reference == 2"
        ).fetchall()[0][0]
        self.assertEqual(num, 9, msg="Fragment abundances not correctly calculated.")
        num = self.test.cursor.execute(
            "SELECT COUNT(fragment) FROM FRAGMENT_ABUNDANCES WHERE fragment == 'cerrogalera' "
            " AND community_reference == 1"
        ).fetchall()[0][0]
        self.assertEqual(num, 9, msg="Fragment abundances not correctly calculated.")

    def testSpeciesAbundances(self):
        """Tests that the produced species abundances are correct by comparing species richness."""
        num = self.test.cursor.execute(
            "SELECT COUNT(species_id) FROM SPECIES_ABUNDANCES WHERE community_reference == 2"
        ).fetchall()[0][0]
        self.assertEqual(num, 1029, msg="Species abundances not correctly calculated.")
        num = self.test.cursor.execute(
            "SELECT COUNT(species_id) FROM SPECIES_ABUNDANCES WHERE community_reference == 1"
        ).fetchall()[0][0]
        self.assertEqual(num, 884, msg="Species abundances not correctly calculated.")

    def testGetOctaves(self):
        """Tests getting the octaves."""
        c = CoalescenceTree(os.path.join("output", "sampledb4.db"))
        c.clear_calculations()
        c.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        c.calculate_richness()
        self.assertEqual([[0, 585], [1, 231], [2, 59], [3, 5]], c.get_octaves(1))
        c = CoalescenceTree(os.path.join("output", "sampledb4.db"))
        c.clear_calculations()
        c.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        c.calculate_richness()
        actual = c.get_octaves_pd().head()
        expected = pd.DataFrame(
            [[1, 0, 585], [1, 1, 231], [1, 2, 59], [1, 3, 5], [2, 0, 760]],
            columns=["community_reference", "octave", "richness"],
        )
        assert_frame_equal(actual, expected, check_like=True)

    def testSpeciesLocations(self):
        """
        Tests that species locations have been correctly assigned.
        """
        num = self.test.cursor.execute(
            "SELECT species_id FROM SPECIES_LOCATIONS WHERE x==1662 AND y==4359 " " AND community_reference == 1"
        ).fetchall()
        self.assertEqual(len(set(num)), 2, msg="Species locations not correctly assigned")
        all_list = self.test.get_species_locations()
        select_list = self.test.get_species_locations(community_reference=1)
        self.assertListEqual([1, 1662, 4359, 1], all_list[0])
        self.assertListEqual([1, 1662, 4359], select_list[0])

    def testAlphaDiversity(self):
        """
        Tests that alpha diversity is correctly calculated and fetched for each parameter reference
        """
        c = CoalescenceTree(os.path.join("sample", "sample.db"))
        with self.assertRaises(IOError):
            c.get_alpha_diversity_pd()
        self.assertEqual(9, self.test.get_alpha_diversity(1))
        self.assertEqual(10, self.test.get_alpha_diversity(2))
        expected_alphas_list = []
        for reference in self.test.get_community_references():
            expected_alphas_list.append(
                {"community_reference": reference, "alpha_diversity": self.test.get_alpha_diversity(reference)}
            )
        expected_alphas = pd.DataFrame(expected_alphas_list).reset_index(drop=True)
        actual_alphas = self.test.get_alpha_diversity_pd().reset_index(drop=True)
        assert_frame_equal(expected_alphas, actual_alphas, check_like=True)

    def testBetaDiversity(self):
        """
        Tests that beta diversity is correctly calculated and fetched for the reference
        """
        c = CoalescenceTree(os.path.join("sample", "sample.db"))
        with self.assertRaises(IOError):
            c.get_beta_diversity_pd()
        self.assertAlmostEqual(98.111111111, self.test.get_beta_diversity(1), places=5)
        self.assertAlmostEqual(102.8, self.test.get_beta_diversity(2), places=5)
        expected_betas_list = []
        for reference in self.test.get_community_references():
            expected_betas_list.append(
                {"community_reference": reference, "beta_diversity": self.test.get_beta_diversity(reference)}
            )
        expected_betas = pd.DataFrame(expected_betas_list).reset_index(drop=True)
        actual_betas = self.test.get_beta_diversity_pd().reset_index(drop=True)
        assert_frame_equal(expected_betas, actual_betas, check_like=True)

    def testGetNumberIndividuals(self):
        """Tests that the number of individuals is obtained correctly."""
        c = CoalescenceTree(os.path.join("output", "sampledb7.db"))
        self.assertEqual(1504, c.get_number_individuals(community_reference=1))
        self.assertEqual(12, c.get_number_individuals(fragment="P09", community_reference=1))
        c.wipe_data()
        c.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        with self.assertRaises(IOError):
            c.get_number_individuals(fragment="none")
        with self.assertRaises(IOError):
            c.get_number_individuals()

    def testGetFragmentAbundances(self):
        """Tests that fragment abundances are correctly obtained."""
        c = CoalescenceTree(os.path.join("sample", "sample3.db"))
        with self.assertRaises(IOError):
            c.get_fragment_abundances(fragment="P09", reference=1)
        with self.assertRaises(IOError):
            c.get_fragment_abundances_pd()
        abundances = self.test.get_fragment_abundances(fragment="P09", reference=1)
        expected_abundances = [[302, 1], [303, 1], [304, 1], [305, 1], [306, 1], [307, 1], [546, 2], [693, 1], [732, 3]]
        self.assertEqual(expected_abundances, abundances[:10])
        all_abundances = self.test.get_all_fragment_abundances()
        expected_abundances2 = [
            [1, "P09", 302, 1],
            [1, "P09", 303, 1],
            [1, "P09", 304, 1],
            [1, "P09", 305, 1],
            [1, "P09", 306, 1],
            [1, "P09", 307, 1],
            [1, "P09", 546, 2],
            [1, "P09", 693, 1],
            [1, "P09", 732, 3],
            [1, "cerrogalera", 416, 1],
        ]
        self.assertEqual(expected_abundances2, all_abundances[:10])
        df = pd.DataFrame(
            expected_abundances2, columns=["community_reference", "fragment", "species_id", "no_individuals"]
        )
        actual_df = self.test.get_fragment_abundances_pd().head(n=10)
        assert_frame_equal(df, actual_df, check_like=True)

    def testGetFragmentListErrors(self):
        """Tests the error is raised when obtaining fragment list."""
        c = CoalescenceTree(os.path.join("output", "sampledb8.db"))
        c.wipe_data()
        with self.assertRaises(IOError):
            c.get_fragment_list()

    def testClearGoodnessFit(self):
        """Tests that goodness of fit are correctly cleared."""
        c = CoalescenceTree(os.path.join("output", "sampledbx.db"))
        exec_command = "SELECT * FROM BIODIVERSITY_METRICS WHERE metric LIKE 'goodness_%'"
        self.assertTrue(len(c.cursor.execute(exec_command).fetchall()) >= 1)
        c._clear_goodness_of_fit()
        self.assertFalse(len(c.cursor.execute(exec_command).fetchall()) >= 1)

    def testGetBiodiversityMetrics(self):
        """Tests that biodiversity metrics are correctly obtained from the database."""
        c1 = CoalescenceTree(os.path.join("sample", "sample.db"))
        with self.assertRaises(IOError):
            c1.get_biodiversity_metrics()
        c2 = CoalescenceTree(os.path.join("sample", "sample2.db"))

        expected_biodiversity_metrics = pd.DataFrame(
            [
                [1, "fragment_richness", "fragment2", 129.0, np.NaN, np.NaN],
                [2, "fragment_richness", "fragment2", 130.0, np.NAN, np.NaN],
                [1, "fragment_richness", "fragment1", 174.0, np.NaN, np.NaN],
                [2, "fragment_richness", "fragment1", 175.0, np.NaN, np.NaN],
                [1, "fragment_richness", "whole", 1163.0, np.NaN, np.NaN],
                [2, "fragment_richness", "whole", 1170.0, np.NaN, np.NaN],
            ],
            columns=["community_reference", "metric", "fragment", "value", "simulated", "actual"],
        ).reset_index(drop=True)
        actual_biodiversity_metrics = c2.get_biodiversity_metrics().reset_index(drop=True).fillna(value=np.nan)
        assert_frame_equal(expected_biodiversity_metrics, actual_biodiversity_metrics)

    def testRaisesErrorNoFragmentsAlpha(self):
        """
        Tests that an error is raised when alpha diversity is calculated without any fragment abundance data
        """
        with self.assertRaises(IOError):
            self.test2.calculate_alpha_diversity()

    def testRaisesErrorNoFragmentsBeta(self):
        """
        Tests that an error is raised when alpha diversity is calculated without any fragment abundance data
        """
        with self.assertRaises(IOError):
            self.test2.calculate_beta_diversity()

    def testRaisesErrorNoFragmentsRichness(self):
        """
        Tests that an error is raised when fragment richness is calculated without any fragment abundance data
        """
        with self.assertRaises(IOError):
            self.test2.calculate_fragment_richness()

    def testRaisesErrorNoFragmentsOctaves(self):
        """
        Tests that an error is raised when fragment richness is calculated without any fragment abundance data
        """
        with self.assertRaises(IOError):
            self.test2.calculate_fragment_octaves()

    @unittest.skipIf(sys.version[0] != "3", "Skipping Python 3.x tests")
    def testModelFitting2(self):
        """
        Tests that the goodness-of-fit calculations are correctly performed.
        """
        random.seed(2)
        self.test.calculate_goodness_of_fit()
        self.assertAlmostEqual(self.test.get_goodness_of_fit(), 0.30140801329929373, places=6)
        self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_octaves(), 0.0680205429120108, places=6)
        self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_richness(), 0.9244977999898334, places=6)

    @unittest.skipIf(sys.version[0] == "3", "Skipping Python 2.x tests")
    def testModelFitting3(self):
        """
        Tests that the goodness-of-fit calculations are correctly performed.
        """
        random.seed(2)
        self.test.calculate_goodness_of_fit()
        self.assertAlmostEqual(self.test.get_goodness_of_fit(), 0.30140801329929373, places=6)
        self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_octaves(), 0.0680205429120108, places=6)
        self.assertAlmostEqual(self.test.get_goodness_of_fit_fragment_richness(), 0.9244977999898334, places=6)

    def testErrorIfNotApplied(self):
        """Tests that an error is raised if outputting is attempted without applying any community parameters."""
        c = CoalescenceTree(os.path.join("sample", "sample.db"))
        with self.assertRaises(RuntimeError):
            c.output()

    def testFragmentNumbersMatching(self):
        """Checks behaviour when matching fragment numbers."""
        test = CoalescenceTree(os.path.join("output", "sampledb1.db"), logging_level=50)
        test.clear_calculations()
        with self.assertRaises(RuntimeError):
            test._check_fragment_numbers_match()
        with self.assertRaises(ValueError):
            test.calculate_fragment_abundances()
            test._check_fragment_numbers_match()
        test.comparison_file = os.path.join("sample", "PlotBiodiversityMetrics.db")
        self.assertTrue(test._check_fragment_numbers_match())
        test.fragment_abundances.pop(0)
        self.assertFalse(test._check_fragment_numbers_match())

    def testFragmentNumbersEqualisation(self):
        """Checks behaviour when equalising fragment numbers."""
        test = CoalescenceTree(os.path.join("output", "sampledb2.db"), logging_level=50)
        test.clear_calculations()
        test.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        test.calculate_fragment_richness()
        self.test._equalise_fragment_number("notafrag", 1)
        test.fragment_abundances[0][2] += 1000
        test._equalise_fragment_number("P09", 1)
        self.assertTrue(test._check_fragment_numbers_match())

    def testFragmentNumbersErrors(self):
        """Checks behaviour when equalising fragment numbers."""
        test = CoalescenceTree(os.path.join("output", "sampledb3.db"), logging_level=50)
        test.clear_calculations()
        test.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        test.comparison_abundances = None
        with self.assertRaises(ValueError):
            test._equalise_all_fragment_numbers()

    def testAdjustBiodiversityMetrics(self):
        """Checks that biodiversity metrics are correctly adjusted."""
        test = CoalescenceTree(os.path.join("output", "sampledb5.db"), logging_level=50)
        test.clear_calculations()
        test.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        test.adjust_data()

    def testComparisonOctavesModification(self):
        """Tests that the comparison database is modified."""
        test = CoalescenceTree(os.path.join("output", "sampledb6.db"), logging_level=50)
        dst = os.path.join("output", "PlotBiodiversityMetricsNoAlpha2.db")
        shutil.copy(os.path.join("sample", "PlotBiodiversityMetricsNoAlpha.db"), dst)
        test.import_comparison_data(dst)
        test.calculate_comparison_octaves(store=True)
        self.assertTrue(os.path.exists(dst))

    @unittest.skipIf(sys.version[0] == "2", "Skipping Python 3.x tests")
    def testDownsamplingAndRevert(self):
        """Tests that downsampling works as intended and can be reverted."""
        c = CoalescenceTree(os.path.join("output", "sampledb9.db"))
        random.seed(a=10, version=3)
        original_individuals = c.get_number_individuals()
        original_richness = c.get_species_richness_pd()
        c.wipe_data()
        with self.assertRaises(ValueError):
            c.downsample(sample_proportion=2.0)
        c.downsample(sample_proportion=0.1)
        c.set_speciation_parameters([0.1, 0.2])
        c.apply()
        new_individuals = c.get_number_individuals()
        self.assertEqual(1452, new_individuals)
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST"))
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST_ORIGINAL"))
        c = CoalescenceTree(os.path.join("output", "sampledb9.db"))
        c.revert_downsample()
        c.wipe_data()
        c.set_speciation_parameters([0.1, 0.2])
        c.apply()
        final_individuals = c.get_number_individuals()
        assert_frame_equal(original_richness, c.get_species_richness_pd())
        self.assertEqual(original_individuals, final_individuals)
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST"))
        self.assertFalse(check_sql_table_exist(c.database, "SPECIES_LIST_ORIGINAL"))
        # Now test with NSE sim to ensure correct sampling
        c = CoalescenceTree(os.path.join("output", "nse_reference1.db"))
        nse_richness = c.get_species_richness_pd()
        nse_no_individuals = c.get_number_individuals()
        c.wipe_data()
        c.downsample(sample_proportion=0.1)
        c.set_speciation_parameters([0.000001, 0.999999])
        c.apply()
        new_no_individuals = c.get_number_individuals()
        self.assertAlmostEqual(new_no_individuals / nse_no_individuals, 0.1, 5)
        self.assertEqual(1000, c.get_species_richness(reference=2))
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST"))
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST_ORIGINAL"))
        c = CoalescenceTree(os.path.join("output", "nse_reference1.db"))
        c.revert_downsample()
        c.wipe_data()
        c.set_speciation_parameters([0.000001, 0.999999])
        c.apply_incremental()
        c.set_speciation_parameters([0.5])
        c.apply()
        actual_richness = c.get_species_richness_pd()
        assert_frame_equal(nse_richness, actual_richness)
        self.assertEqual(nse_no_individuals, c.get_number_individuals())
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST"))
        self.assertFalse(check_sql_table_exist(c.database, "SPECIES_LIST_ORIGINAL"))
        with self.assertRaises(IOError):
            c.revert_downsample()

    @unittest.skipIf(sys.version[0] == "2", "Skipping Python 3.x tests")
    def testDownsamplingByLocationAndRevert(self):
        """Tests that downsampling works as intended and can be reverted."""
        c = CoalescenceTree(os.path.join("output", "sampledb10.db"))
        random.seed(a=10, version=3)
        original_individuals = c.get_number_individuals()
        original_richness = c.get_species_richness_pd()
        c.wipe_data()
        with self.assertRaises(ValueError):
            c.downsample_at_locations(fragment_csv=os.path.join("sample", "FragmentsTestFail1.csv"))
        with self.assertRaises(IOError):
            c.downsample_at_locations(fragment_csv="not_a_file.csv")
        c.downsample_at_locations(fragment_csv=os.path.join("sample", "FragmentsTest3.csv"))
        c.set_speciation_parameters([0.1, 0.2])
        c.apply()
        new_individuals = c.get_number_individuals()
        self.assertEqual(2, new_individuals)
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST"))
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST_ORIGINAL"))
        c = CoalescenceTree(os.path.join("output", "sampledb10.db"))
        c.revert_downsample()
        c.wipe_data()
        c.set_speciation_parameters([0.1, 0.2])
        c.apply()
        final_individuals = c.get_number_individuals()
        assert_frame_equal(original_richness, c.get_species_richness_pd())
        self.assertEqual(original_individuals, final_individuals)
        self.assertTrue(check_sql_table_exist(c.database, "SPECIES_LIST"))
        self.assertFalse(check_sql_table_exist(c.database, "SPECIES_LIST_ORIGINAL"))
        c = CoalescenceTree(os.path.join("output", "sampledb10.db"))
        c.wipe_data()
        c.downsample_at_locations(fragment_csv=os.path.join("sample", "FragmentsTest4.csv"), ignore_errors=True)
        c.set_speciation_parameters([0.1, 0.2])
        c.apply()
        new_individuals = c.get_number_individuals()
        self.assertEqual(3, new_individuals)


class TestCoalescenceTreeWriteCsvs(unittest.TestCase):
    """Tests that csvs are correctly outputted."""

    @classmethod
    def setUpClass(cls):
        """Creates the CoalescenceTree object."""
        cls.c = CoalescenceTree(os.path.join("sample", "nse_reference.db"))

    def testWriteCommunityParameterToCsv(self):
        """Tests that community parameters are correctly written to a csv."""
        output_csv = os.path.join("output", "community_parameters1.csv")
        self.c.write_to_csv(output_csv, "COMMUNITY_PARAMETERS")
        self.assertTrue(os.path.exists(output_csv))
        import csv

        if sys.version_info[0] < 3:  # pragma: no cover
            infile = open(output_csv, "rb")
        else:
            infile = open(output_csv, "r")
        expected_output = [
            ["reference", "speciation_rate", "time", "fragments", "metacommunity_reference"],
            ["1", "1e-06", "0.0", "0", "0"],
            ["2", "0.99999", "0.0", "0", "0"],
            ["3", "0.5", "0.0", "0", "0"],
        ]
        actual_output = []
        with infile as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                actual_output.append(row)
        self.assertEqual(expected_output, actual_output)
        with self.assertRaises(IOError):
            self.c.write_to_csv(output_csv, "COMMUNITY_PARAMETERS")
        with self.assertRaises(KeyError):
            self.c.write_to_csv("notacsv.csv", "NOTATABLE")

    def testWritesAllCsvs(self):
        """Tests that all csvs write to the output correctly."""
        output_dir = os.path.join("output", "csvdir")
        if os.path.exists(output_dir):
            os.remove(output_dir)
        self.c.write_all_to_csvs(output_dir, "out1")
        expected_tables = ["COMMUNITY_PARAMETERS", "SIMULATION_PARAMETERS", "SPECIES_ABUNDANCES", "SPECIES_LIST"]
        for table in expected_tables:
            self.assertTrue(os.path.exists(os.path.join(output_dir, "out1_{}.csv".format(table))))
        for file in os.listdir(output_dir):
            if ".csv" in file:
                self.assertIn(file, ["out1_{}.csv".format(x) for x in expected_tables])
        self.c.write_all_to_csvs(output_dir, "out2.csv")
        for table in expected_tables:
            self.assertTrue(os.path.exists(os.path.join(output_dir, "out2_{}.csv".format(table))))
        self.c.write_all_to_csvs(output_dir, "out3.")
        for table in expected_tables:
            self.assertTrue(os.path.exists(os.path.join(output_dir, "out3_{}.csv".format(table))))


class TestCoalescenceTreeSpeciesDistances(unittest.TestCase):
    """Tests analysis is performed correctly."""

    @classmethod
    def setUpClass(cls):
        """
        Sets up the Coalescence object test case.
        """
        dst = os.path.join("output", "sampledb1.db")
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copyfile(os.path.join("sample", "sample.db"), dst)
        cls.test = CoalescenceTree(dst)
        cls.test.clear_calculations()
        cls.test.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        cls.test.calculate_species_distance_similarity()

    def testSpeciesDistanceSimilarity(self):
        """
        Tests that the species distance similarity function works as intended.
        """
        mean = self.test.cursor.execute(
            "SELECT value FROM BIODIVERSITY_METRICS WHERE community_reference == 1 AND "
            "metric == 'mean_distance_between_individuals'"
        ).fetchone()[0]
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
        dst = os.path.join("output", "sampledb2.db")
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copyfile(os.path.join("sample", "sample.db"), dst)
        cls.test = CoalescenceTree(logging_level=40)
        cls.test.set_database(dst)
        cls.test.import_comparison_data(os.path.join("sample", "PlotBiodiversityMetricsNoAlpha.db"))
        cls.test.calculate_comparison_octaves(False)
        cls.test.clear_calculations()
        cls.test.calculate_fragment_richness()
        cls.test.calculate_fragment_octaves()
        cls.test.calculate_octaves_error()
        cls.test.calculate_alpha_diversity()
        cls.test.calculate_alpha_diversity()
        cls.test.calculate_beta_diversity()
        cls.test2 = CoalescenceTree()
        cls.test2.set_database(os.path.join("sample", "sample_nofrag.db"))

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


class TestSimulationAnalysisTemporal(unittest.TestCase):
    """Tests that applying multiple times works as expected."""

    @classmethod
    def setUpClass(cls):
        """Generates the analysis object."""
        src = os.path.join("sample", "sample2.db")
        dst = os.path.join("output", "sample2.db")
        if not os.path.exists(dst):
            shutil.copy(src, dst)
        cls.tree = CoalescenceTree()
        cls.tree.set_database(dst)
        cls.tree.wipe_data()

    def testTimesWrongFormatError(self):
        """Tests that an error is raised when the times are in the wrong format."""
        with self.assertRaises(TypeError):
            self.tree.set_speciation_parameters([0.4, 0.6], times=[0.1, 0.2, "notafloat"])
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            self.tree.set_speciation_parameters([0.4, 0.6], times="notafloat")
        self.tree.times = []
        self.tree.set_speciation_parameters([0.4, 0.6], times=[0, 1, 10])
        self.assertEqual([0.0, 1.0, 10.0], self.tree.times)


class TestSimulationAnalysis(unittest.TestCase):
    """
    Tests that the simulation can perform all required analyses, and that the correct errors are thrown if the object
    does not exist.
    """

    @classmethod
    def setUpClass(cls):
        """Copies the sample databases and applies a basic set of community parameters."""
        src = os.path.join("sample", "sample2.db")
        dst = os.path.join("output", "sample2.db")
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy(src, dst)
        cls.tree = CoalescenceTree()
        cls.tree.set_database(dst)
        cls.tree.wipe_data()
        cls.tree.set_speciation_parameters(
            speciation_rates=[0.5, 0.7],
            record_spatial="T",
            record_fragments=os.path.join("sample", "FragmentsTest.csv"),
            sample_file=os.path.join("sample", "SA_samplemaskINT.tif"),
        )
        cls.tree.apply()
        cls.tree.calculate_fragment_richness()
        cls.tree.calculate_fragment_octaves()
        np.random.seed(100)

    def testSetDatabaseErrors(self):
        """Tests that the set database errors are correctly raised."""
        sim = Simulation()
        c = CoalescenceTree()
        with self.assertRaises(RuntimeError):
            c.set_database(sim)
        c = CoalescenceTree()
        with self.assertRaises(IOError):
            c.set_database(os.path.join("sample", "failsampledoesntexist.db"))

    def testFragmentConfigNoExistError(self):
        """Tests that an error is raised if the fragment config file does not exist."""
        tree = CoalescenceTree(self.tree.file)
        with self.assertRaises(IOError):
            tree.set_speciation_parameters(
                speciation_rates=[0.5, 0.7],
                record_spatial="T",
                record_fragments=os.path.join("sample", "notafragmentconfig.csv"),
                sample_file=os.path.join("sample", "SA_samplemaskINT.tif"),
            )
        with self.assertRaises(IOError):
            tree.set_speciation_parameters(
                speciation_rates=[0.5, 0.7],
                record_spatial="T",
                record_fragments=os.path.join("sample", "example_historical_fine.tif"),
                sample_file=os.path.join("sample", "SA_samplemaskINT.tif"),
            )

    def testReadsFragmentsRichness(self):
        """
        Tests that the fragment richness can be read correctly
        """
        sim_params = self.tree.get_simulation_parameters()
        expected_params = dict(
            seed=9,
            task=1,
            output_dir="output",
            speciation_rate=0.5,
            sigma=2.828427,
            tau=2.0,
            deme=1,
            sample_size=0.1,
            max_time=2.0,
            dispersal_relative_cost=1.0,
            min_num_species=1,
            habitat_change_rate=0.0,
            gen_since_historical=200.0,
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
        )
        for key in sim_params.keys():
            self.assertEqual(
                sim_params[key],
                expected_params[key],
                msg="Error in {}: {} != {}".format(key, sim_params[key], expected_params[key]),
            )
        fragment2_richness = ["fragment2", 1, 129]
        self.assertEqual(self.tree.get_fragment_richness(fragment="fragment2", reference=1), 129)
        self.assertEqual(self.tree.get_fragment_richness(fragment="fragment1", reference=2), 175)
        octaves = self.tree.get_fragment_richness()
        self.assertListEqual(fragment2_richness, [list(x) for x in octaves if x[0] == "fragment2" and x[1] == 1][0])
        expected_fragment_richness = []
        for reference in self.tree.get_community_references():
            for fragment in self.tree.get_fragment_list(reference):
                fragment_richness = self.tree.get_fragment_richness(fragment=fragment, reference=reference)
                expected_fragment_richness.append(
                    {"fragment": fragment, "community_reference": reference, "fragment_richness": fragment_richness}
                )
        expected_fragment_richness_df = (
            pd.DataFrame(expected_fragment_richness)
            .sort_values(by=["fragment", "community_reference"])
            .reset_index(drop=True)
        )
        actual_fragment_richness = self.tree.get_fragment_richness_pd().reset_index(drop=True)
        assert_frame_equal(expected_fragment_richness_df, actual_fragment_richness, check_like=True)

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
        expected_abundances = [
            [610, 1],
            [611, 1],
            [612, 1],
            [613, 1],
            [614, 1],
            [615, 1],
            [616, 1],
            [617, 1],
            [618, 1],
            [619, 1],
        ]
        actual_abundances = self.tree.get_species_abundances(fragment="fragment2", reference=1)
        for i, each in enumerate(expected_abundances):
            self.assertListEqual(actual_abundances[i], each)
        with self.assertRaises(ValueError):
            self.tree.get_species_abundances(fragment="fragment2")
        expected_fragment_abundances_list = []
        for reference in self.tree.get_community_references():
            for fragment in self.tree.get_fragment_list(reference):
                fragment_abundances = self.tree.get_fragment_abundances(fragment=fragment, reference=reference)
                for species_id, abundance in fragment_abundances:
                    expected_fragment_abundances_list.append(
                        {
                            "fragment": fragment,
                            "community_reference": reference,
                            "species_id": species_id,
                            "no_individuals": abundance,
                        }
                    )
        expected_fragment_abundances = (
            pd.DataFrame(expected_fragment_abundances_list)
            .sort_values(by=["fragment", "community_reference", "species_id"])
            .reset_index(drop=True)
        )
        actual_fragment_abundances = (
            self.tree.get_fragment_abundances_pd()
            .sort_values(by=["fragment", "community_reference", "species_id"])
            .reset_index(drop=True)
        )
        assert_frame_equal(expected_fragment_abundances, actual_fragment_abundances, check_like=True)

    def testFragmentRichnessRaiseError(self):
        """
        Tests that the correct errors are raised when no fragment exists with that name, or with the specified
        speciation rate, or time. Also checks SyntaxErrors and sqlite3.Errors when no FRAGMENT_RICHNESS table
        exists.
        """
        failtree = CoalescenceTree()
        failtree.set_database(os.path.join("sample", "failsample.db"))
        with self.assertRaises(IOError):
            failtree.get_fragment_richness()
        with self.assertRaises(IOError):
            failtree.get_fragment_richness_pd()
        with self.assertRaises(IOError):
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
        desired = ["fragment1", 1, 0, 173]
        self.assertListEqual([0, 128], octaves[0])
        self.assertListEqual([0, 173], octaves2[0])
        self.assertListEqual(desired, [x for x in all_octaves if x[0] == "fragment1" and x[1] == 1 and x[2] == 0][0])
        expected_fragment_octaves_list = []
        for reference in self.tree.get_community_references():
            fragment_list = self.tree.get_fragment_list(reference)
            fragment_list.append("whole")
            for fragment in fragment_list:
                try:
                    octaves = self.tree.get_fragment_octaves(fragment=fragment, reference=reference)
                    for octave, richness in octaves:
                        expected_fragment_octaves_list.append(
                            {
                                "fragment": fragment,
                                "community_reference": reference,
                                "octave": octave,
                                "richness": richness,
                            }
                        )
                except RuntimeError:
                    continue
        expected_fragment_octaves = (
            pd.DataFrame(expected_fragment_octaves_list)
            .sort_values(["fragment", "community_reference", "octave"], axis=0)
            .reset_index(drop=True)
        )
        actual_fragment_octaves = (
            self.tree.get_fragment_octaves_pd()
            .sort_values(["fragment", "community_reference", "octave"], axis=0)
            .reset_index(drop=True)
        )
        assert_frame_equal(expected_fragment_octaves, actual_fragment_octaves, check_like=True)

    def testFragmentOctavesRaiseError(self):
        """
        Tests that the correct errors are raised for different situations for reading fragment octaves
        """
        failtree = CoalescenceTree()
        try:
            failtree.set_database("sample/failsample.db")
        except sqlite3.Error:
            pass
        with self.assertRaises(sqlite3.Error):
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
        self.assertEqual(
            10,
            self.tree.sample_fragment_richness(
                fragment="fragment1", number_of_individuals=10, n=1, community_reference=2
            ),
        )
        self.assertEqual(
            10,
            self.tree.sample_fragment_richness(
                fragment="fragment2", number_of_individuals=10, n=10, community_reference=2
            ),
        )

    def testLandscapeSampling(self):
        """Tests that the sampling from the landscape works as intended."""
        number_dict = {"fragment1": 3, "fragment2": 10}
        np.random.seed(100)
        self.assertEqual(
            13, self.tree.sample_landscape_richness(number_of_individuals=number_dict, n=1, community_reference=2)
        )
        self.assertAlmostEqual(
            99.9, self.tree.sample_landscape_richness(number_of_individuals=100, n=10, community_reference=1), places=3
        )

    def testRaisesSamplingErrors(self):
        """Tests that sampling errors are correctly raised"""
        number_dict = {"fragment1": 3000000, "fragment2": 10}
        with self.assertRaises(KeyError):
            self.assertEqual(
                13, self.tree.sample_landscape_richness(number_of_individuals=number_dict, n=1, community_reference=2)
            )
        number_dict2 = {"fragment": 10, "fragment2": 10}
        with self.assertRaises(KeyError):
            self.assertEqual(
                13, self.tree.sample_landscape_richness(number_of_individuals=number_dict2, n=1, community_reference=2)
            )

    def testSpeciesRichness(self):
        """Tests that the simulation species richness is read correctly."""
        actual_species_richness = (
            self.tree.get_species_richness_pd().sort_values(by=["community_reference"]).reset_index(drop=True)
        )
        expected_species_richness_list = []
        for reference in self.tree.get_community_references():
            expected_species_richness_list.append(
                {"community_reference": reference, "richness": self.tree.get_species_richness(reference=reference)}
            )
        expected_species_richness = pd.DataFrame(expected_species_richness_list)
        assert_frame_equal(actual_species_richness, expected_species_richness, check_like=True)

    def testOctaves(self):
        """Tests that the simulation octave classes are correctly calculated."""
        actual_species_octaves = (
            self.tree.get_octaves_pd().sort_values(by=["community_reference", "octave"]).reset_index(drop=True)
        )
        expected_species_octaves_list = []
        for reference in self.tree.get_community_references():
            for octave, richness in self.tree.get_octaves(reference):
                expected_species_octaves_list.append(
                    {"community_reference": reference, "octave": octave, "richness": richness}
                )
        expected_species_octaves = pd.DataFrame(expected_species_octaves_list)
        assert_frame_equal(actual_species_octaves, expected_species_octaves, check_like=True)


class TestMetacommunityApplication(unittest.TestCase):
    """
    Tests that a metacommunity can be applied correctly under the three different scenarios. Note that this does not
    test edge cases, just that the parameters are correctly stored and the different application methods work as
    intended.
    """

    @classmethod
    def setUpClass(cls):
        """Initialises the three database files to use."""
        src = os.path.join("sample", "sample.db")
        for i in range(6):
            dst = os.path.join("output", "sample_{}.db".format(i))
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy2(src, dst)

    def testMetacommunityAddingInvalidParameters(self):
        """Tests that adding invalid parameter for a metacommunity raises the appropriate errors."""
        tree = CoalescenceTree(os.path.join("output", "sample_0.db"))
        tree.wipe_data()
        with self.assertRaises(IOError):
            tree.get_metacommunity_parameters_pd()
        tree.set_speciation_parameters([0.1, 0.2])
        for size, spec, opt, ref in [
            [0, 0.1, "simulated", None],
            [10, 0.0, "analytical", None],
            [None, None, "analytical", None],
            [10, 0.0, "path/to/file", None],
            [0, 0.0, "path/to/file", None],
            [0, 0.0, "path/to/not/a/file.db", 1],
        ]:
            with self.assertRaises(ValueError):
                tree.add_metacommunity_parameters(
                    metacommunity_size=size,
                    metacommunity_speciation_rate=spec,
                    metacommunity_option=opt,
                    metacommunity_reference=ref,
                )
        with self.assertRaises(IOError):
            tree.add_metacommunity_parameters(metacommunity_option="not/a/file/db.db", metacommunity_reference=1)

    def testMetacommunitySimulation(self):
        """Tests that a simulated metacommunity works as intended."""
        tree = CoalescenceTree(os.path.join("output", "sample_1.db"))
        tree.wipe_data()
        tree.set_speciation_parameters(
            [0.1, 0.2], metacommunity_size=10000, metacommunity_speciation_rate=0.001, metacommunity_option="simulated"
        )
        tree.add_metacommunity_parameters(
            metacommunity_size=15000, metacommunity_speciation_rate=0.1, metacommunity_option="simulated"
        )
        tree.add_metacommunity_parameters(
            metacommunity_size=100000, metacommunity_speciation_rate=0.001, metacommunity_option="simulated"
        )
        tree.apply()
        params_1 = tree.get_metacommunity_parameters(1)
        params_2 = tree.get_metacommunity_parameters(2)
        params_3 = tree.get_metacommunity_parameters(3)
        self.assertEqual(10000, params_1["metacommunity_size"])
        self.assertEqual(0.001, params_1["speciation_rate"])
        self.assertEqual("simulated", params_1["option"])
        self.assertEqual(0, params_1["external_reference"])
        self.assertEqual(15000, params_2["metacommunity_size"])
        self.assertEqual(0.1, params_2["speciation_rate"])
        self.assertEqual("simulated", params_2["option"])
        self.assertEqual(0, params_2["external_reference"])
        self.assertEqual(100000, params_3["metacommunity_size"])
        self.assertEqual(0.001, params_3["speciation_rate"])
        self.assertEqual("simulated", params_3["option"])
        self.assertEqual(0, params_3["external_reference"])
        self.assertEqual(51, tree.get_species_richness(1))
        self.assertEqual(47, tree.get_species_richness(2))
        self.assertEqual(681, tree.get_species_richness(3))
        self.assertEqual(783, tree.get_species_richness(4))
        self.assertEqual(247, tree.get_species_richness(5))
        self.assertEqual(241, tree.get_species_richness(6))
        expected_metacommunity_parameters_list = []
        for reference in tree.get_community_references():
            try:
                params = tree.get_metacommunity_parameters(reference)
                params["reference"] = reference
                expected_metacommunity_parameters_list.append(params)
            except KeyError:
                continue
        expected_metacommunity_parameters = pd.DataFrame(expected_metacommunity_parameters_list).sort_values(
            ["reference"]
        )
        actual_metacommunity_parameters = tree.get_metacommunity_parameters_pd().sort_values(["reference"])
        assert_frame_equal(expected_metacommunity_parameters, actual_metacommunity_parameters, check_like=True)

    def testMetacommunityAnalytical(self):
        """Tests that an analytical metacommunity works as intended."""
        tree = CoalescenceTree(os.path.join("output", "sample_2.db"))
        tree.wipe_data()
        tree.set_speciation_parameters(
            [0.1, 0.2], metacommunity_size=10000, metacommunity_speciation_rate=0.001, metacommunity_option="analytical"
        )
        tree.add_metacommunity_parameters(
            metacommunity_size=15000, metacommunity_speciation_rate=0.1, metacommunity_option="analytical"
        )
        tree.add_metacommunity_parameters(
            metacommunity_size=100000, metacommunity_speciation_rate=0.001, metacommunity_option="analytical"
        )
        tree.apply()
        params_1 = tree.get_metacommunity_parameters(1)
        params_2 = tree.get_metacommunity_parameters(2)
        params_3 = tree.get_metacommunity_parameters(3)
        self.assertEqual(10000, params_1["metacommunity_size"])
        self.assertEqual(0.001, params_1["speciation_rate"])
        self.assertEqual("analytical", params_1["option"])
        self.assertEqual(0, params_1["external_reference"])
        self.assertEqual(15000, params_2["metacommunity_size"])
        self.assertEqual(0.1, params_2["speciation_rate"])
        self.assertEqual("analytical", params_2["option"])
        self.assertEqual(0, params_2["external_reference"])
        self.assertEqual(100000, params_3["metacommunity_size"])
        self.assertEqual(0.001, params_3["speciation_rate"])
        self.assertEqual("analytical", params_3["option"])
        self.assertEqual(0, params_3["external_reference"])
        self.assertEqual(51, tree.get_species_richness(1))
        self.assertEqual(57, tree.get_species_richness(2))
        self.assertEqual(694, tree.get_species_richness(3))
        self.assertEqual(760, tree.get_species_richness(4))
        self.assertEqual(222, tree.get_species_richness(5))
        self.assertEqual(234, tree.get_species_richness(6))

    def testMetacommunityExternal(self):
        """Tests that an external metacommunity works as intended."""
        tree = CoalescenceTree(os.path.join("output", "sample_3.db"))
        tree.wipe_data()
        tree.set_speciation_parameters([0.1, 0.2], metacommunity_option=os.path.join("sample", "nse_reference.db"))
        tree.add_metacommunity_parameters(
            metacommunity_option=os.path.join("sample", "nse_reference.db"), metacommunity_reference=2
        )
        tree.apply()
        params_1 = tree.get_metacommunity_parameters(1)
        params_2 = tree.get_metacommunity_parameters(2)
        self.assertEqual(0, params_1["metacommunity_size"])
        self.assertEqual(0.0, params_1["speciation_rate"])
        self.assertEqual(os.path.join("sample", "nse_reference.db"), params_1["option"])
        self.assertEqual(1, params_1["external_reference"])
        self.assertEqual(0, params_2["metacommunity_size"])
        self.assertEqual(0.0, params_2["speciation_rate"])
        self.assertEqual(os.path.join("sample", "nse_reference.db"), params_2["option"])
        self.assertEqual(2, params_2["external_reference"])
        self.assertEqual(1, tree.get_species_richness(1))
        self.assertEqual(1, tree.get_species_richness(2))
        self.assertEqual(850, tree.get_species_richness(3))
        self.assertEqual(975, tree.get_species_richness(4))

    def testMetacommunityAnalyticalMethodDetection(self):
        """Tests that the analytical method detection works correctly."""
        tree = CoalescenceTree(os.path.join("output", "sample_4.db"))
        tree.wipe_data()
        tree.set_speciation_parameters(
            [0.1, 0.2], metacommunity_size=110000, metacommunity_speciation_rate=0.5, metacommunity_option="none"
        )
        tree.add_metacommunity_parameters(
            metacommunity_speciation_rate=0.5, metacommunity_size=120000, metacommunity_option="none"
        )
        tree.apply()
        params_1 = tree.get_metacommunity_parameters(1)
        params_2 = tree.get_metacommunity_parameters(2)
        self.assertEqual(110000, params_1["metacommunity_size"])
        self.assertEqual(0.5, params_1["speciation_rate"])
        self.assertEqual("analytical", params_1["option"])
        self.assertEqual(120000, params_2["metacommunity_size"])
        self.assertEqual(0.5, params_2["speciation_rate"])
        self.assertEqual("analytical", params_2["option"])

    def testMetacommunitySimulatedMethodDetection(self):
        """Tests that the simulated method detection works correctly."""
        tree = CoalescenceTree(os.path.join("output", "sample_5.db"))
        tree.wipe_data()
        tree.set_speciation_parameters(
            [0.1, 0.2], metacommunity_size=1000, metacommunity_speciation_rate=0.5, metacommunity_option="none"
        )
        tree.add_metacommunity_parameters(
            metacommunity_speciation_rate=0.5, metacommunity_size=2000, metacommunity_option="none"
        )
        tree.apply()
        params_1 = tree.get_metacommunity_parameters(1)
        params_2 = tree.get_metacommunity_parameters(2)
        self.assertEqual(1000, params_1["metacommunity_size"])
        self.assertEqual(0.5, params_1["speciation_rate"])
        self.assertEqual("simulated", params_1["option"])
        self.assertEqual(2000, params_2["metacommunity_size"])
        self.assertEqual(0.5, params_2["speciation_rate"])
        self.assertEqual("simulated", params_2["option"])


@skipLongTest
class TestMetacommunityApplicationSpeciesAbundances(unittest.TestCase):
    """Tests that the metacommunity application produces the expected species abundance distribution."""

    @classmethod
    def setUpClass(cls):
        """Run a non-spatial sim and apply a metacommunity."""
        cls.sim = Simulation()
        cls.sim.set_simulation_parameters(
            seed=11, task=110, output_directory="output", min_speciation_rate=0.1, spatial=False, deme=20541
        )
        cls.sim.run()
        cls.ct = CoalescenceTree(cls.sim)
        cls.ct.wipe_data()
        cls.ct.set_speciation_parameters(speciation_rates=0.1)
        cls.ct.add_metacommunity_parameters(
            metacommunity_option="analytical", metacommunity_size=1000000, metacommunity_speciation_rate=0.00005
        )
        cls.ct.add_metacommunity_parameters(
            metacommunity_option="simulated", metacommunity_size=1000000, metacommunity_speciation_rate=0.00005
        )
        # This just tests that it doesn't take forever and produces a sensible output
        cls.ct.add_metacommunity_parameters(
            metacommunity_option="analytical", metacommunity_size=1000000000, metacommunity_speciation_rate=0.1
        )
        cls.ct.apply()

    def testRichnessMatchness(self):
        """Tests that the species richness is roughly equivalent between the two methods."""
        self.assertAlmostEqual(244, self.ct.get_species_richness(2), delta=10)
        self.assertAlmostEqual(self.ct.get_species_richness(1), self.ct.get_species_richness(2), delta=30)
        self.assertEqual(5212, self.ct.get_species_richness(3))

    def testSpeciesAbundances(self):
        """Tests the species abundance distribution is roughly equivalent between the two methods."""
        sad_1 = [x[1] for x in self.ct.get_species_abundances(reference=1)]
        sad_2 = [x[1] for x in self.ct.get_species_abundances(reference=2)]
        mean_1 = sum(sad_1) / len(sad_1)
        mean_2 = sum(sad_2) / len(sad_2)
        # Check the mean abundance is roughly equivalent
        self.assertAlmostEqual(mean_1, mean_2, delta=10)
        # Check that the variances are roughly equivalent
        var_list_1 = [abs(x - mean_1) for x in sad_1]
        var_list_2 = [abs(x - mean_2) for x in sad_2]
        var_1 = sum(var_list_1) / len(var_list_1)
        var_2 = sum(var_list_2) / len(var_list_2)
        self.assertAlmostEqual(var_1, var_2, delta=5)
        expected_abundances_list = []
        for reference in self.ct.get_community_references():
            for species_id, abundance in self.ct.get_species_abundances(reference=reference):
                expected_abundances_list.append(
                    {"community_reference": reference, "species_id": species_id, "no_individuals": abundance}
                )
        expected_abundances = pd.DataFrame(expected_abundances_list)
        actual_abundances = self.ct.get_species_abundances_pd()
        assert_frame_equal(actual_abundances, expected_abundances, check_like=True)


class TestMetacommunityApplicationOrdering(unittest.TestCase):
    """Tests that the ordering of adding parameters to the metacommunity does not matter."""

    @classmethod
    def setUpClass(cls):
        """Generates the test databases."""
        src = os.path.join("sample", "sample3.db")
        for i in [1, 2]:
            dst = os.path.join("output", "sample_order_{}.db".format(i))
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy(src, dst)
        src = os.path.join("sample", "sample5.db")
        for i in range(3, 6):
            dst = os.path.join("output", "sample_order_{}.db".format(i))
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy(src, dst)
        cls.c1 = CoalescenceTree(os.path.join("output", "sample_order_1.db"))
        cls.c2 = CoalescenceTree(os.path.join("output", "sample_order_2.db"))
        cls.proc1 = CoalescenceTree(os.path.join("output", "sample_order_3.db"))
        cls.proc2 = CoalescenceTree(os.path.join("output", "sample_order_4.db"))
        cls.proc3 = CoalescenceTree(os.path.join("output", "sample_order_5.db"))
        cls.c1.set_speciation_parameters(
            [0.1, 0.5, 0.9],
            metacommunity_speciation_rate=0.001,
            metacommunity_option="simulated",
            metacommunity_size=10000,
        )
        cls.c1.apply()
        cls.c2.set_speciation_parameters([0.1, 0.5, 0.9])
        cls.c2.add_metacommunity_parameters(
            metacommunity_size=10000, metacommunity_speciation_rate=0.001, metacommunity_option="simulated"
        )
        cls.c2.apply()
        cls.proc1.set_speciation_parameters(
            [0.1, 0.5, 0.9],
            protracted_speciation_min=5,
            protracted_speciation_max=1000,
            metacommunity_option="simulated",
            metacommunity_speciation_rate=0.001,
            metacommunity_size=10000,
        )
        cls.proc1.apply()
        cls.proc2.set_speciation_parameters([0.1, 0.5, 0.9])
        cls.proc2.add_metacommunity_parameters(
            metacommunity_size=10000, metacommunity_speciation_rate=0.001, metacommunity_option="simulated"
        )
        cls.proc2.add_protracted_parameters(min_speciation_gen=5, max_speciation_gen=1000)
        cls.proc2.apply()
        cls.proc3.set_speciation_parameters([0.1, 0.5, 0.9])
        cls.proc3.add_protracted_parameters(min_speciation_gen=5, max_speciation_gen=1000)
        cls.proc3.add_metacommunity_parameters(
            metacommunity_size=10000, metacommunity_speciation_rate=0.001, metacommunity_option="simulated"
        )
        cls.proc3.apply()

    def testEquivalentMethodsMatch(self):
        """Tests that equivalent methods of applying metacommunities produce equivalent results."""
        for i in range(1, 4):
            self.assertEqual(self.c1.get_species_richness(i), self.c2.get_species_richness(i))
            self.assertEqual(self.proc1.get_species_richness(i), self.proc2.get_species_richness(i))
            self.assertEqual(self.proc2.get_species_richness(i), self.proc3.get_species_richness(i))

    def testMultipleProtractedError(self):
        """Tests that adding multiple protracted speciation parameters raises the correct error."""
        with self.assertRaises(ValueError):
            self.proc2.add_multiple_protracted_parameters()


class TestProtractedSpeciationEquality(unittest.TestCase):
    """Tests that analysis performs as expected when protracted speciation parameters match the minimums."""

    @classmethod
    def setUpClass(cls):
        """Copy the sample database."""
        dst = os.path.join("output", "sample_protracted3.db")
        shutil.copy(os.path.join("sample", "sample3.db"), dst)
        cls.ct = CoalescenceTree(dst)
        cls.ct.wipe_data()

    def testApplyEqualParameters(self):
        """Tests that equal protracted parameters can be applied"""
        self.ct.set_speciation_parameters(
            [0.001, 0.1], protracted_speciation_min=100.0, protracted_speciation_max=10000.0
        )
        self.ct.apply()
        self.assertEqual(1, self.ct.get_species_richness(1))
        self.assertEqual(3, self.ct.get_species_richness(2))
