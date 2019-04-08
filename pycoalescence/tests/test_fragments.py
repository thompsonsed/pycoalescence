"""Tests that the development and creation of fragments works as intended."""
import os
import unittest

import numpy as np
from setup_tests import setUpAll, tearDownAll

from pycoalescence.fragments import FragmentedLandscape, Fragment


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


class TestBasicFragmentedLandscape(unittest.TestCase):
    """Tests that a basic fragmented landscape works as intended."""

    def testPrecursoryValidation(self):
        """Tests that the precursory validation makes sense."""
        fl = FragmentedLandscape()
        with self.assertRaises(ValueError):
            fl._precursory_validation(number_fragments=100000, size=10, total=1)
        with self.assertRaises(ValueError):
            fl._precursory_validation(number_fragments=2, size=100, total=1)
        with self.assertRaises(ValueError):
            fl._precursory_validation(number_fragments=1, size=10, total=100000)

    def testAddRemaindersError(self):
        """Tests that adding the remainders works as intended."""
        fl = FragmentedLandscape()
        fl.total_added = 1
        fl.remainder = 1
        fl.number_fragments = 10
        with self.assertRaises(ValueError):
            fl._add_remainders()

    def testCheckPathAndFile(self):
        """Tests that an error is raised if the output file already exists."""
        fl = FragmentedLandscape()
        with self.assertRaises(IOError):
            fl._check_file_and_path()
        fl.output_file = os.path.join("sample", "SA_sample_fine.tif")
        with self.assertRaises(IOError):
            fl._check_file_and_path()

    def testDisabledSmoothing(self):
        """Tests that smoothing can be disabled correctly"""
        output = os.path.join("output", "frag_gen1.tif")
        fl = FragmentedLandscape(number_fragments=10, size=100, total=1000, output_file=output)
        fl.generate(override_smoothing=False)
        self.assertTrue(os.path.exists(output))

    def testEnabledSmoothing(self):
        """Tests that smoothing can be disabled correctly"""
        output = os.path.join("output", "frag_gen2.tif")
        fl = FragmentedLandscape(number_fragments=10, size=100, total=1000, output_file=output)
        fl.generate(override_smoothing=True)
        self.assertTrue(os.path.exists(output))

    def testFinalValidation(self):
        """Tests the errors raised during final validation."""
        fl = FragmentedLandscape()
        f1 = Fragment(1, 1)
        f2 = Fragment(-2, 2)
        f3 = Fragment(2, 2)
        fl.fragments = [f1, f2]
        fl.total_added = 1
        with self.assertRaises(ValueError):
            fl._final_validation()
        fl.total_added = 2
        with self.assertRaises(ValueError):
            fl._final_validation()
        fl.fragments = [f1, f3]
        fl.size = 3
        fl.remainder = 1
        with self.assertRaises(ValueError):
            fl._final_validation()
        fl.remainder = 0
        fl.grid = np.ones(shape=(2, 2))
        fl.total = 3
        with self.assertRaises(ValueError):
            fl._final_validation()
