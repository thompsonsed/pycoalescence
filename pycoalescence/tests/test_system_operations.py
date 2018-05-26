"""
Tests system_operations module for basic system routines.
"""
import logging
import unittest

import os

from pycoalescence.system_operations import cantor_pairing, check_file_exists, check_parent, create_logger,\
	elegant_pairing
from pycoalescence.tests.setup import setUpAll, tearDownAll

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

class TestCantorPairing(unittest.TestCase):
	"""
	Tests that cantor pairing successfully creates unique numbers for a very large set of guilds and species
	"""
	def testCantorCreatesUniqueIds(self):
		"""
		Tests that the cantor pairing function creates unique ids for any given pair of numbers.
		Tests up to 1000 individuals in 1000 guilds
		"""
		unique_ids = set()
		for species in range(1000):
			for guild in range(1000):
				ref = cantor_pairing(species, guild)
				self.assertNotIn(ref, unique_ids)
				unique_ids.add(ref)



class TestSystemOperations(unittest.TestCase):
	"""
	Tests the functions associated with the system operations.
	"""
	def testFileExistence(self):
		"""
		Tests that the file existence checks work
		"""
		check_file_exists("null")
		check_file_exists("sample/null.tif")
		check_file_exists("system_operations.py")

	def testFileExistenceErrors(self):
		"""
		Tests that the correct errors are thrown when files don't exist.
		"""
		with self.assertRaises(IOError):
			check_file_exists("not_a_file.tif")
		with self.assertRaises(IOError):
			check_file_exists("sample/not_a_file.tif")
		with self.assertRaises(IOError):
			check_file_exists("sample/also_notta_tile")

	def testCheckDirectory(self):
		"""
		Verifies that the parent directory checks work correctly.
		"""
		with self.assertRaises(ValueError):
			check_parent("")
		with self.assertRaises(ValueError):
			check_parent(None)
		check_parent("sample/not_here.tif")
		check_parent("output/create_me/")
		check_parent("output/create_me_too/file_here.tif")
		self.assertTrue(os.path.exists("output/create_me/"))
		self.assertTrue(os.path.exists("output/create_me_too/"))

	def testFileLogger(self):
		"""
		Tests that the creation of a logger to file works correctly.
		"""
		logger = logging.Logger("temp")
		file_name = "output/log.txt"
		create_logger(logger, file=file_name)
		logger.warning("test output")
		with open(file_name, 'r') as f:
			s = f.readline()
			self.assertTrue("test output" in s)
		handlers = logger.handlers[:]
		for handler in handlers:
			handler.close()
			logger.removeHandler(handler)

	def testCantorPairing(self):
		"""
		Tests that the cantor pairing produces the expected result
		"""
		self.assertEqual(cantor_pairing(10, 100), 6205)
		self.assertEqual(cantor_pairing(0, 1), 2)
		self.assertEqual(cantor_pairing(1, 0), 1)
		self.assertEqual(cantor_pairing(100000, 1000000), 605001550000)

	def testElegantPairing(self):
		"""
		Tests the elegant pairing produces the expected output
		"""
		self.assertEqual(elegant_pairing(10, 100), 10010)
		self.assertEqual(elegant_pairing(0, 1), 1)
		self.assertEqual(elegant_pairing(1, 0), 2)
		self.assertEqual(elegant_pairing(100000, 1000000), 1000000100000)