"""
Tests the Landscape class for controlling combinations of Map files. Only some minor test cases are here - the remainder
are contained within the child classes.
"""
import logging
import os
import unittest

from pycoalescence.landscape import Landscape


class TestLandscape(unittest.TestCase):
    """Tests that the Landscape object behaves correctly."""

    def testCreateLogger(self):
        """Tests the logger object is created properly."""
        l = Landscape()
        l._create_logger(logging_level=None)
        self.assertTrue(isinstance(l.logger, logging.Logger))

    def testSetMapErrors(self):
        """Tests that setting the map dimensions generates the expected errors."""
        l = Landscape()
        with self.assertRaises(ValueError):
            l.set_map("null", 10)

    def testCheckMaps(self):
        """Tests that the map checks work as intended."""
        l = Landscape()
        l.set_map_files(
            sample_file="null",
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )
        l.historical_coarse_map_file = "null"
        with self.assertRaises(ValueError):
            l.check_maps()
        l.historical_coarse_map_file = None
        l.historical_fine_map_file = "null"
        with self.assertRaises(ValueError):
            l.check_maps()
        l.historical_fine_map_file = "null"
        l.historical_coarse_map_file = "null"
        l.coarse_map.file_name = None
        with self.assertRaises(ValueError):
            l.check_maps()
        l2 = Landscape()
        with self.assertRaises(ValueError):
            l2.set_map_files(
                sample_file="null",
                fine_file=os.path.join("sample", "SA_sample_coarse.tif"),
                coarse_file=os.path.join("sample", "SA_sample_fine.tif"),
            )
        l2.fine_map.file_name = "none"
        with self.assertRaises(ValueError):
            l2.check_maps()
        l3 = Landscape()
        with self.assertRaises(ValueError):
            l3.set_map_files(
                sample_file=os.path.join("sample", "SA_sample_coarse.tif"),
                fine_file=os.path.join("sample", "SA_sample_fine.tif"),
                coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
            )
        l3.landscape_type = "tiled_fine"
        with self.assertRaises(ValueError):
            l3.check_maps()
        l4 = Landscape()
        l4.set_map_files(sample_file="null", fine_file=os.path.join("sample", "SA_sample_fine.tif"))
        l4.landscape_type = "tiled_coarse"
        with self.assertRaises(ValueError):
            l4.check_maps()
        l5 = Landscape()
        l5.set_map_files(
            sample_file="null",
            fine_file=os.path.join("sample", "SA_sample_fine.tif"),
            coarse_file=os.path.join("sample", "SA_sample_coarse.tif"),
        )
        l5.landscape_type = "tiled_fine"
        with self.assertRaises(ValueError):
            l5.check_maps()
