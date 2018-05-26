"""
Tests the mean nearest-neighbour dispersal calculator for map files.
"""

import unittest
import logging
from pycoalescence.landscape_metrics import LandscapeMetrics

class TestLandscapeMetrics(unittest.TestCase):
	"""
	Tests the MNN calculator with null files, and for randomly distributed landscapes.
	"""

	def testNullLandscape(self):
		"""
		Tests that a null landscape generates a MNN of 1
		"""
		mnn = LandscapeMetrics("sample/null.tif", logging_level=30)
		self.assertEqual(1.0, mnn.get_mnn())

	def testEvenLandscape(self):
		"""
		Tests that an even landscape generates a MNN of 2.
		"""
		mnn = LandscapeMetrics("sample/even_landscape.tif", logging_level=50)
		self.assertEqual(2.0, mnn.get_mnn())

	def testSampleLandscape(self):
		"""
		Tests that the sample landscape generates the expected mean nearest-neighbour distance.
		"""
		mnn = LandscapeMetrics("sample/SA_sample.tif", logging_level=50)
		self.assertEqual(1.0, mnn.get_mnn())

	def testSampleLandscape2(self):
		"""
		Tests that the sample landscape generates the expected mean nearest-neighbour distance.
		"""
		mnn = LandscapeMetrics("sample/SA_samplemaskINT.tif", logging_level=50)
		self.assertAlmostEqual(1.00618, mnn.get_mnn(), places=5)
