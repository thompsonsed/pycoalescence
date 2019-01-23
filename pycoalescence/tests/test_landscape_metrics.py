"""
Tests the mean nearest-neighbour dispersal calculator for map files.
"""

import unittest

from pycoalescence.landscape_metrics import LandscapeMetrics


class TestLandscapeMetrics(unittest.TestCase):
    """Tests the MNN calculator with null files, and for randomly distributed landscapes."""

    def testNullLandscape(self):
        """Tests that a null landscape generates a MNN of 1"""
        mnn = LandscapeMetrics("sample/null.tif", logging_level=50)
        self.assertEqual(1.0, mnn.get_mnn())

    def testEvenLandscape(self):
        """Tests that an even landscape generates a MNN of 2."""
        mnn = LandscapeMetrics("sample/even_landscape.tif", logging_level=50)
        self.assertEqual(2.0, mnn.get_mnn())

    def testSampleLandscape(self):
        """Tests that the sample landscape generates the expected mean nearest-neighbour distance."""
        mnn = LandscapeMetrics("sample/SA_sample.tif", logging_level=50)
        self.assertEqual(1.0, mnn.get_mnn())

    def testSampleLandscape2(self):
        """Tests that the sample landscape generates the expected mean nearest-neighbour distance."""
        mnn = LandscapeMetrics("sample/SA_samplemaskINT.tif", logging_level=50)
        self.assertAlmostEqual(1.00618, mnn.get_mnn(), places=5)

    def testClumpyDisaggregated(self):
        """Tests that clumpy produces the expected metric for a fully disaggregated landscape."""
        l = LandscapeMetrics("sample/even_landscape.tif", logging_level=50)
        self.assertEqual(-1.0, l.get_clumpiness())
        l = LandscapeMetrics("sample/null_sample.tif", logging_level=50)
        self.assertEqual(-1.0, l.get_clumpiness())

    def testClumpyAggregated(self):
        """Tests that clumpy produces the expected metric for an aggregated landscape."""
        l = LandscapeMetrics("sample/null.tif", logging_level=50)
        self.assertEqual(1.0, l.get_clumpiness())

    def testClumpyModerate(self):
        """Tests that clumpy produces the expected metric for a moderately aggregated landscape."""
        l = LandscapeMetrics("sample/SA_samplemaskINT.tif", logging_level=50)
        self.assertAlmostEqual(0.445512069369, l.get_clumpiness(), places=5)

    def testMultipleMetrics(self):
        """Tests that multiple landscape metrics can be obtained on the same object."""
        mnn = LandscapeMetrics("sample/null_sample.tif", logging_level=50)
        self.assertAlmostEqual(1.00618, mnn.get_mnn(), places=5)
        self.assertAlmostEqual(-1.0, mnn.get_clumpiness(), places=5)
