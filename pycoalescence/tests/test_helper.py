"""
Tests the helper module for updating old simulation variables.
"""
import logging
import sqlite3
import unittest

import os
import shutil

from pycoalescence.helper import update_parameter_names
from pycoalescence import CoalescenceTree
from pycoalescence.tests.setup import setUpAll, tearDownAll

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

	def testSimulationUpdating(self):
		"""
		Tests that simulation parameters are correctly updated between versions.
		"""
		old1 = "sample/data_old1.db"
		old2 = "sample/data_old2.db"
		old3 = "output/data_old3.db"
		old4 = "output/data_old4.db"
		shutil.copy(old1, old3)
		shutil.copy(old2, old4)
		with self.assertRaises(sqlite3.OperationalError):
			t = CoalescenceTree(old1, logging_level=logging.CRITICAL)
			_ = t.get_simulation_parameters()["gen_since_pristine"]
		with self.assertRaises(sqlite3.OperationalError):
			t = CoalescenceTree(old2, logging_level=logging.CRITICAL)
			_ = t.get_simulation_parameters()["habitat_change_rate"]
		update_parameter_names(old3)
		update_parameter_names(old4)
		t1 = CoalescenceTree(old3)
		t2 = CoalescenceTree(old4)
		self.assertEqual(t1.get_simulation_parameters()["gen_since_pristine"], 2.2)
		self.assertEqual(t2.get_simulation_parameters()["gen_since_pristine"], 2.2)
		self.assertEqual(t1.get_simulation_parameters()["habitat_change_rate"], 0.2)
		self.assertEqual(t2.get_simulation_parameters()["habitat_change_rate"], 0.2)