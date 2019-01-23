"""
Tests the helper module for updating old simulation variables.
"""
import logging
import os
import shutil
import sqlite3
import unittest

from setup_tests import setUpAll, tearDownAll

from pycoalescence import CoalescenceTree
from pycoalescence.helper import update_parameter_names


class TestHelperUpdate(unittest.TestCase):
    """
    Tests the helper module, with functions for changing simulations between versions
    """

    @classmethod
    def setUpClass(cls):
        """
        Creates the output directory
        """
        setUpAll()

    @classmethod
    def tearDownClass(cls):
        """
        Removes output directory
        """
        tearDownAll()

    def testSimulationUpdateErrors(self):
        """Tests that updating simulation parameters raises the correct errors."""
        with self.assertRaises(IOError):
            update_parameter_names(os.path.join("sample", "PlotBiodiversityMetrics.db"))

    def testDoesntAlterCorrectSim(self):
        """Tests that updating doesn't alter a correct sim."""
        sample_db = os.path.join("sample", "sample.db")
        t = CoalescenceTree(sample_db)
        params1 = t.get_simulation_parameters()
        update_parameter_names(sample_db)
        t = CoalescenceTree(sample_db)
        params2 = t.get_simulation_parameters()
        self.assertEqual(params1, params2)

    def testSimulationUpdating(self):
        """
        Tests that simulation parameters are correctly updated between versions.
        """
        old1 = "sample/data_old1.db"
        old2 = "sample/data_old2.db"
        old3 = "sample/data_old3.db"
        old1a = "output/data_old3.db"
        old2a = "output/data_old4.db"
        old3a = "output/data_old5.db"
        shutil.copy(old1, old1a)
        shutil.copy(old2, old2a)
        shutil.copy(old3, old3a)
        with self.assertRaises(sqlite3.Error):
            t = CoalescenceTree(old1, logging_level=logging.CRITICAL)
            _ = t.get_simulation_parameters()["gen_since_historical"]
        with self.assertRaises(sqlite3.Error):
            t = CoalescenceTree(old2, logging_level=logging.CRITICAL)
            _ = t.get_simulation_parameters()["habitat_change_rate"]
        with self.assertRaises(sqlite3.Error):
            t = CoalescenceTree(old2, logging_level=logging.CRITICAL)
            _ = t.get_simulation_parameters()["habitat_change_rate"]
        update_parameter_names(old1a)
        update_parameter_names(old2a)
        update_parameter_names(old3a)
        t1 = CoalescenceTree(old1a)
        t2 = CoalescenceTree(old2a)
        t3 = CoalescenceTree(old3a)
        self.assertEqual(t1.get_simulation_parameters()["gen_since_historical"], 2.2)
        self.assertEqual(t2.get_simulation_parameters()["gen_since_historical"], 2.2)
        self.assertEqual(t3.get_simulation_parameters()["gen_since_historical"], 2.2)
        self.assertEqual(t1.get_simulation_parameters()["habitat_change_rate"], 0.2)
        self.assertEqual(t2.get_simulation_parameters()["habitat_change_rate"], 0.2)
        self.assertEqual(t3.get_simulation_parameters()["habitat_change_rate"], 0.2)
