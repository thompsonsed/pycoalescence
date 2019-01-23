"""Tests that the fragment config correctly handlers creation of a configuration file from a shapefile and a raster."""
import csv
import os
import unittest

from setup_tests import setUpAll, tearDownAll

from pycoalescence.fragment_config import FragmentConfigHandler, generate_fragment_csv


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


class TestFragmentConfigHandler(unittest.TestCase):
    """
    Tests that the fragment config handler works correctly.
    """

    @classmethod
    def setUpClass(cls):
        """
        Generates the expected dictionary for the object
        """
        cls.fragment_csv = os.path.join("output", "fragment_config1.csv")
        cls.expected_dict = {"fragment1": {"min_x": 8, "max_x": 11, "min_y": 0, "max_y": 4, "area": 40},
                             "fragment2": {"min_x": 1, "max_x": 8, "min_y": 1, "max_y": 8, "area": 10}}

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.fragment_csv):
            os.remove(cls.fragment_csv)

    def testIncorrectParametersRaiseErrors(self):
        """
        Tests that supplying incorrect parameters causes the correct error to be raised.
        """
        f = FragmentConfigHandler()
        with self.assertRaises(ValueError):
            f.generate_config(input_shapefile=os.path.join("output", "not_a_shape.tif"),
                              input_raster=os.path.join("output", "SA_samplemask.tif"))
        with self.assertRaises(ValueError):
            f.generate_config(input_shapefile=os.path.join("output", "not_a_shape.shp"),
                              input_raster=os.path.join("output", "SA_samplemask.tfi"))
        with self.assertRaises(IOError):
            f.generate_config(input_shapefile=os.path.join("output", "not_a_shape.shp"),
                              input_raster=os.path.join("sample", "SA_sample.tif"))
        with self.assertRaises(IOError):
            f.generate_config(input_shapefile=os.path.join("sample", "shape_sample.shp"),
                              input_raster=os.path.join("sample", "SA_samplenot.tif"))
        with self.assertRaises(IOError):
            f.write_csv(output_csv=os.path.join("sample", "FragmentsTest.csv"))
        with self.assertRaises(ValueError):
            f.generate_config(input_shapefile=os.path.join("sample", "shape_sample.shp"),
                              input_raster=os.path.join("sample", "SA_sample.tif"))

    def testGenerateFragments(self):
        """
        Tests that the fragments are correctly generated from the extents on the map.
        """
        f = FragmentConfigHandler()
        f.generate_config(input_shapefile=os.path.join("sample", "shape_sample.shp"),
                          input_raster=os.path.join("sample", "SA_sample_fine.tif"))
        for each in self.expected_dict.keys():
            self.assertDictEqual(self.expected_dict[each], f.fragment_list[each])

    def testWritesCsv(self):
        """
        Test writes the csv correctly.
        """
        f = FragmentConfigHandler()
        f.fragment_list = self.expected_dict
        f.write_csv(self.fragment_csv)
        output = []
        with open(self.fragment_csv, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                output.append(row)
        self.assertListEqual(["fragment1", '8', '0', '11', '4', '40'], output[0])
        self.assertListEqual(["fragment2", '1', '1', '8', '8', '10'], output[1])


class TestFragmentCsvGeneration(unittest.TestCase):
    """
    Tests the generation of the fragment csv using the single function.
    """

    @classmethod
    def setUpClass(cls):
        """
        Defines the output csv.
        """
        cls.fragment_csv = os.path.join("output", "fragment_config1.csv")

    @classmethod
    def tearDownClass(cls):
        """
        Removes the generated csv file.
        """
        if os.path.exists(cls.fragment_csv):
            os.remove(cls.fragment_csv)

    def testGenerateFragmentCsv(self):
        """
        Tests that the fragments are generated correctly using the pipeline.
        """
        generate_fragment_csv(input_shapefile=os.path.join("sample", "shape_sample.shp"),
                              input_raster=os.path.join("sample", "SA_sample_fine.tif"),
                              output_csv=self.fragment_csv)
        output = []
        with open(self.fragment_csv, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                output.append(row)
        self.assertListEqual(["fragment2", '1', '1', '8', '8', '10'], output[1])
        self.assertListEqual(["fragment1", '8', '0', '11', '4', '40'], output[0])
