"""Tests the patched landscape routines for generating islands with distinct dispersal probabilities."""
import csv
import os
import unittest

import numpy as np
from setup_tests import setUpAll, tearDownAll

from pycoalescence.map import Map
from pycoalescence.patched_landscape import Patch, PatchedLandscape, convert_index_to_x_y


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


class TestPatchedLandscapeBasicFunctions(unittest.TestCase):
    """
    Tests the free functions within the patched_landscapes file.
    """

    def testConvertIndices(self):
        """
        Tests that indices are correctly converted in a range of parameters.
        """
        x, y = convert_index_to_x_y(10, 3)
        self.assertEqual(1, x)
        self.assertEqual(3, y)
        x, y = convert_index_to_x_y(2, 10)
        self.assertEqual(2, x)
        self.assertEqual(0, y)
        x, y = convert_index_to_x_y(100, 10)
        self.assertEqual(0, x)
        self.assertEqual(10, y)


class TestPatch(unittest.TestCase):
    def testAddingPatches(self):
        """
        Tests that after adding multiple patches, the correct patch probabilities result.
        """
        p = Patch(1, 10)
        p.add_patch(1, 0.5)
        p.add_patch(2, 0.1)
        p.add_patch(3, 0.3)
        p.add_patch(4, 0.1)
        desired_dispersal_probabilities = {1: 0.5, 2: 0.1, 3: 0.3, 4: 0.1}
        self.assertDictEqual(desired_dispersal_probabilities, p.dispersal_probabilities)
        p.re_scale_probabilities()
        desired_dispersal_probabilities = {1: 0.5, 2: 0.1, 3: 0.3, 4: 0.1}
        for k, v in desired_dispersal_probabilities.items():
            self.assertAlmostEqual(p.dispersal_probabilities[k], v, places=4)
        self.assertEqual(desired_dispersal_probabilities.keys(), p.dispersal_probabilities.keys())

    def testAddingPatchesRescaling(self):
        """
        Tests that re-scaling works correctly after adding multiple patches.
        """
        p = Patch(1, 10)
        p.add_patch(1, 0.5)
        p.add_patch(2, 0.1)
        p.add_patch(3, 0.3)
        p.add_patch(4, 0.1)
        p.add_patch(5, 1.0)
        desired_dispersal_probabilities = {1: 0.5, 2: 0.1, 3: 0.3, 4: 0.1, 5: 1.0}
        self.assertDictEqual(desired_dispersal_probabilities, p.dispersal_probabilities)
        p.re_scale_probabilities()
        desired_dispersal_probabilities = {1: 0.25, 2: 0.05, 3: 0.15, 4: 0.05, 5: 0.5}
        for k, v in desired_dispersal_probabilities.items():
            self.assertAlmostEqual(p.dispersal_probabilities[k], v, places=4)
        self.assertEqual(desired_dispersal_probabilities.keys(), p.dispersal_probabilities.keys())

    def testAddingErrors(self):
        p = Patch(1, 10)
        p.dispersal_probabilities = {1: 0, 2: 0}
        with self.assertRaises(ValueError):
            p.re_scale_probabilities()
        p.dispersal_probabilities = {}
        p.add_patch(2, 1)
        with self.assertRaises(ValueError):
            p.re_scale_probabilities()
        p.dispersal_probabilities[2] = -10
        with self.assertRaises(ValueError):
            p.re_scale_probabilities()
        with self.assertRaises(KeyError):
            p.add_patch(2, 1)
        with self.assertRaises(ValueError):
            p.add_patch(3, -10)

    def testBaseFunctions(self):
        """Tests that the Patch object base functions operate correctly."""
        p = Patch(1, 10)
        self.assertEqual("Patch(1, 10)", repr(p))
        p.add_patch(2, 0.1)
        expected_str = "Patch class object with id: 1, density: 10, index: 0 and dispersal probabilities: {2: 0.1}"
        self.assertEqual(expected_str, str(p))


class TestPatchedLandscapeFunctions(unittest.TestCase):
    """Tests that the patched landscape generation works correctly."""

    def testBaseFunctions(self):
        """Tests the base functions from the PatchedLandscape class."""
        fine_map = os.path.join("output", "none.tif")
        dispersal_map = os.path.join("output", "dispersal_none.tif")
        pl = PatchedLandscape(output_fine_map=fine_map, output_dispersal_map=dispersal_map)
        self.assertEqual("PatchedLandscape({}, {})".format(fine_map, dispersal_map), repr(pl))

    def testPatchedLandscapeInit(self):
        """
        Tests that the correct errors are raised when conditions are not correctly met, and the patched landscape is
        appropriately set up.
        """
        with self.assertRaises(IOError):
            pl = PatchedLandscape(
                output_fine_map=os.path.join("sample", "SA_sample_fine.tif"), output_dispersal_map="notexist"
            )
        with self.assertRaises(IOError):
            pl = PatchedLandscape(
                output_dispersal_map=os.path.join("sample", "SA_sample_fine.tif"), output_fine_map="notexist"
            )
        pl = PatchedLandscape(
            output_fine_map=os.path.join("output", "patched1", "patched1.tif"),
            output_dispersal_map=os.path.join("output", "patched2", "patched2.tif"),
        )
        self.assertTrue(os.path.exists(os.path.join("output", "patched2")))
        self.assertTrue(os.path.exists(os.path.join("output", "patched2")))

    def testAddPatch(self):
        """Asserts that adding a patch works correctly."""
        pl = PatchedLandscape("not_exist", "not_exist")
        pl.add_patch(1, 1, 0.1)
        with self.assertRaises(KeyError):
            pl.add_patch(1, 1, 0.1)
        pl.add_patch(2, 1, 0.5, dispersal_probabilities={1: 0.3})
        expected_dict = {1: {1: 0.1}, 2: {1: 0.3, 2: 0.5}}
        for k1, v1 in expected_dict.items():
            for k2, v2 in v1.items():
                self.assertAlmostEqual(pl.patches[k1].dispersal_probabilities[k2], v2, places=4)
        self.assertEqual(expected_dict.keys(), pl.patches.keys())

    def testAddDispersal(self):
        """Tests that dispersal values are correctly added."""
        pl = PatchedLandscape("not_exist", "not_exist")
        pl.add_patch(2, 10, 0.3)
        pl.add_patch(1, 10, 0.1)
        pl.add_dispersal(1, 2, 0.4)
        pl.add_dispersal(2, 1, 0.7)
        expected_dict = {1: {1: 0.1, 2: 0.4}, 2: {1: 0.7, 2: 0.3}}
        for k1, v1 in expected_dict.items():
            for k2, v2 in v1.items():
                self.assertAlmostEqual(pl.patches[k1].dispersal_probabilities[k2], v2, places=4)
        self.assertEqual(expected_dict.keys(), pl.patches.keys())

    def testGenerateFromMatrix(self):
        """Tests that the patched landscapes are correctly generated from matrices."""
        m_fine = os.path.join("output", "matrix_pl_fine.tif")
        m_dispersal = os.path.join("output", "matrix_pl_dispersal.tif")
        pl = PatchedLandscape(m_fine, m_dispersal)
        density_matrix = np.asarray([[1, 2, 3], [40, 50, 60], [700, 800, 900]])
        density_matrix_out = np.asarray([[1, 2, 3, 40, 50, 60, 700, 800, 900]])
        dispersal_matrix = np.asarray(
            [
                [1, 0, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 1, 1],
            ]
        )
        dispersal_matrix_out = np.asarray(
            [
                [0.1666666, 0.0, 0.0, 0.16666673, 0.16666667, 0.0, 0.1666666, 0.16666673, 0.16666667],
                [0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.25, 0.25, 0.25, 0.25, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.1666666, 0.16666673, 0.16666667, 0.1666666, 0.1666667, 0.1666667],
                [0.0, 0.0, 0.0, 0.1666666, 0.16666673, 0.16666667, 0.1666666, 0.1666667, 0.1666667],
                [0.0, 0.0, 0.0, 0.1666666, 0.16666673, 0.16666667, 0.1666666, 0.1666667, 0.1666667],
                [0.0, 0.0, 0.0, 0.1666666, 0.16666673, 0.16666667, 0.1666666, 0.1666667, 0.1666667],
                [0.0, 0.0, 0.0, 0.1666666, 0.16666673, 0.16666667, 0.1666666, 0.1666667, 0.1666667],
                [0.0, 0.0, 0.0, 0.1666666, 0.16666673, 0.16666667, 0.1666666, 0.1666667, 0.1666667],
            ]
        )
        pl.generate_from_matrix(density_matrix, dispersal_matrix)
        dispersal_matrix2 = np.ones((2, 2))
        with self.assertRaises(TypeError):
            pl.generate_from_matrix(10, 10)
        with self.assertRaises(ValueError):
            pl.generate_from_matrix(density_matrix, dispersal_matrix2)
        fine_map = Map(m_fine)
        dispersal_map = Map(m_dispersal)
        fine_map.open()
        x, y = fine_map.get_x_y()
        self.assertEqual(9, x)
        self.assertEqual(1, y)
        dispersal_map.open()
        x, y = dispersal_map.get_x_y()
        self.assertEqual(9, x)
        self.assertEqual(9, y)
        for i in range(9):
            self.assertEqual(density_matrix_out[0, i], fine_map.data[0, i])
        for i in range(9):
            for j in range(9):
                self.assertAlmostEqual(dispersal_matrix_out[j, i], dispersal_map.data[j, i], places=4)

    def testPatchesDispersalProbabilitiesUsingDictOnly(self):
        """Tests that the patched landscape is correctly generated using a dictionary of dispersal probabilities only"""
        pl = PatchedLandscape("not_exist", "not_exist")
        pl.add_patch(1, 10, dispersal_probabilities={1: 0.7, 2: 0.3})
        pl.add_patch(2, 10, dispersal_probabilities={1: 0.1, 2: 0.4})
        expected_dict = {1: {1: 0.1, 2: 0.4}, 2: {1: 0.7, 2: 0.3}}
        for k1, v1 in pl.patches.items():
            for k2, v2 in v1.dispersal_probabilities.items():
                self.assertEqual(v2, pl.patches[k1].dispersal_probabilities[k2])

    def testErrorGeneration(self):
        """Tests that the appropriate errors are thrown when using the different methods of providing self-dispersal."""
        pl = PatchedLandscape("not_exist", "not_exist")
        with self.assertRaises(KeyError):
            pl.add_patch(1, 10, dispersal_probabilities={2: 5, 3: 4})
        with self.assertRaises(ValueError):
            pl.add_dispersal(1, 2, 0.1)
        with self.assertRaises(ValueError):
            pl.add_patch(2, 2, -0.1)
        with self.assertRaises(ValueError):
            pl.add_patch(2, -2, 0.1)
        with self.assertRaises(TypeError):
            pl.add_patch(3, 1, 0.1, "not a dict")
        with self.assertRaises(TypeError):
            pl.add_patch(2, 10)
        pl.add_patch(1, 10, self_dispersal=0.1)
        with self.assertRaises(ValueError):
            pl.add_dispersal(1, 2, 0.7)

    def testPatchedLandscapeFragmentGeneration(self):
        """Tests that fragments are correctly generated from the patched landscape."""
        pl = PatchedLandscape("not_exist", "not_exist")
        patch1 = Patch("patch1", 10)
        patch1.index = 1
        patch2 = Patch("patch2", 200)
        patch2.index = 2
        pl.patches = {"patch1": patch1, "patch2": patch2}
        output_csv = os.path.join("output", "fragment_csv", "generated_fragment.csv")
        pl.generate_fragment_csv(output_csv)
        self.assertTrue(os.path.exists(os.path.dirname(output_csv)))
        self.assertTrue(os.path.exists(output_csv))
        with self.assertRaises(IOError):
            pl.generate_fragment_csv(output_csv)
        expected_output = [[str(x) for x in ["patch1", 1, 0, 1, 0, 10]], [str(x) for x in ["patch2", 2, 0, 2, 0, 200]]]
        with open(output_csv, "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            for i, row in enumerate(csv_reader):
                self.assertEqual(expected_output[i], row)


class TestPatchedLandscapeSystems(unittest.TestCase):
    """
    Tests that the patched landscape correctly generates the desired files.
    """

    @classmethod
    def setUpClass(cls):
        """Generates the patched landscape files."""
        cls.fine = Map("output/patched_fine.tif")
        cls.dispersal = Map("output/patched_dispersal.tif")
        pl = PatchedLandscape(cls.fine.file_name, cls.dispersal.file_name)
        pl.add_patch(1, 10, 0.4)
        pl.add_patch(2, 20, 0.3)
        pl.add_patch(3, 10, 0.1)
        pl.add_dispersal(1, 2, 0.6)
        pl.add_dispersal(1, 3, 0.0)
        pl.add_dispersal(2, 1, 0.7)
        pl.add_dispersal(2, 3, 0.0)
        pl.add_dispersal(3, 1, 1.8)
        pl.add_dispersal(3, 2, 0.1)
        pl.generate_files()
        cls.pl = pl

    def testPatchGeneration(self):
        """Tests that patches are generated correctly."""
        fine = Map("output/patched_fine2.tif")
        dispersal = Map("output/patched_dispersal2.tif")
        pl = PatchedLandscape(fine.file_name, dispersal.file_name)
        pl.add_patch(1, 10, 0.4)
        pl.add_patch(2, 20, 0.3)
        pl.add_patch(3, 10, 0.1)
        pl.add_dispersal(1, 2, 0.6)
        pl.add_dispersal(1, 3, 0.0)
        pl.add_dispersal(2, 1, 0.7)
        pl.add_dispersal(2, 3, 0.0)
        pl.add_dispersal(3, 1, 1.8)
        pl.add_dispersal(3, 2, 0.1)
        p = Patch(4, 0.0)
        p.dispersal_probabilities = {}
        pl.patches[4] = p
        with self.assertRaises(ValueError):
            pl.generate_files()
        _ = pl.patches.pop(4)
        _ = pl.patches[1].dispersal_probabilities.pop(3)
        pl.generate_files()
        expected_dict = {1: {1: 0.4, 2: 0.6, 3: 0.0}, 2: {1: 0.7, 2: 0.3, 3: 0.0}, 3: {1: 0.9, 2: 0.05, 3: 0.05}}
        for k1, v1 in expected_dict.items():
            for k2, v2 in v1.items():
                self.assertAlmostEqual(self.pl.patches[k1].dispersal_probabilities[k2], v2, places=4)
        self.assertEqual(expected_dict.keys(), self.pl.patches.keys())

    def testGeneratesFilesExist(self):
        """Tests that patches landscape files are correctly created and have the desired dimensions."""
        self.assertTrue(os.path.exists(self.fine.file_name))
        self.assertTrue(os.path.exists(self.dispersal.file_name))

    def testMapDimensions(self):
        """Tests that the fine file is 1x3 and the dispersal file is 3x3"""
        x, y = self.fine.get_x_y()
        self.assertEqual(3, x)
        self.assertEqual(1, y)
        x, y = self.dispersal.get_x_y()
        self.assertEqual(3, x)
        self.assertEqual(3, y)

    def testFineMapValues(self):
        """Tests that the fine map values are correct."""
        self.fine.open()
        expected_data = np.array([[10, 20, 10]])
        for i in range(3):
            self.assertEqual(expected_data[0, i], self.fine.data[0, i])

    def testDispersalMapValues(self):
        """Tests that the dispersal map values are correct."""
        self.dispersal.open()
        expected_data = np.array([[0.4, 0.6, 0.0], [0.7, 0.3, 0.0], [0.9, 0.05, 0.05]])
        for x in range(3):
            for y in range(3):
                self.assertAlmostEqual(expected_data[y, x], self.dispersal.data[y, x], places=5)
