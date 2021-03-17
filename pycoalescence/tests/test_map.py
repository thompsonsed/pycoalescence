"""Tests the Map object for provision of geospatial data and map manipulation operations."""
import csv
import logging
import os
import shutil
import subprocess
import sys
import unittest

try:
    from osgeo import gdal
except ImportError as ie:
    try:
        import gdal
    except ImportError:
        raise ie
import numpy as np
from osgeo import osr, ogr, gdal

try:
    from unittest.mock import MagicMock, create_autospec, patch
except ImportError:  # pragma: no cover
    from mock import Mock as MagicMock
    from mock import create_autospec, patch

from pycoalescence import Map, FragmentedLandscape
from pycoalescence.map import shapefile_from_wkt, GdalErrorHandler
from setup_tests import setUpAll, tearDownAll, skipGdalWarp

import scipy

try:  # pragma: no cover
    from importlib import reload
except ImportError:  # pragma: no cover
    pass


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


@unittest.skipIf(sys.version[0] == "2", "Skipping Python 3.x tests")
class TestMapImports(unittest.TestCase):
    """Tests that errors are thrown correctly when gdal is not detected."""

    @classmethod
    def setUpClass(cls):
        """Mocks a fake subprocess call"""
        cls.orig_call = subprocess.check_output
        if "GDAL_DATA" in os.environ:
            cls.gdal_dir = os.environ["GDAL_DATA"]
            os.environ.pop("GDAL_DATA")
        else:  # pragma: no cover
            cls.gdal_dir = None

    @classmethod
    def tearDownClass(cls):
        """Re imports the subprocess module to remove the MagicMocking."""
        subprocess.check_output = cls.orig_call
        if cls.gdal_dir:
            os.environ["GDAL_DATA"] = cls.gdal_dir

    def testRaisesImportError(self):
        """Mocks a fake subprocess call to ``gdal-config --datadir`` and checks that the correct errors are raised"""
        subprocess.check_output = create_autospec(subprocess.check_output, return_value=b"/not/a/gdal/dir\n")
        import pycoalescence.map

        with self.assertRaises(ImportError):
            reload(pycoalescence.map)
        subprocess.check_output = self.orig_call
        subprocess.check_output = create_autospec(subprocess.check_output, return_value=None)
        with self.assertRaises(ImportError):
            reload(pycoalescence.map)


class TestMap(unittest.TestCase):
    """
    Tests the functions for the Map object work properly.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the Map object
        """
        cls.fine_map = Map()
        cls.fine_map.file_name = "sample/SA_sample_fine.tif"
        cls.coarse_map = Map()
        cls.coarse_map.file_name = "sample/SA_sample_coarse.tif"
        cls.fine_offset_map = Map("sample/SA_sample_fine_offset.tif")
        cls.expected_WGS_84 = [
            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]',
            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]',
            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]',
        ]

    def testDetectGeoTransform(self):
        """Tests the fine and coarse map geo transforms."""
        # Test the fine map
        x, y, x_offset, y_offset, xres, yres, ulx, uly = self.fine_map.get_dimensions()
        self.assertEqual(x, 13)
        self.assertEqual(y, 13)
        self.assertAlmostEqual(ulx, -78.375, 8)
        self.assertAlmostEqual(uly, 0.8583333333333, 8)
        self.assertAlmostEqual(xres, 0.00833333333333, 8)
        self.assertAlmostEqual(yres, -0.0083333333333333, 8)
        self.assertEqual(0, x_offset)
        self.assertEqual(0, y_offset)
        x, y, x_offset, y_offset, xres, yres, ulx, uly = self.fine_map.get_dimensions()
        self.assertEqual(x, 13)
        self.assertEqual(y, 13)
        self.assertAlmostEqual(ulx, -78.375, 8)
        self.assertAlmostEqual(uly, 0.8583333333333, 8)
        self.assertAlmostEqual(xres, 0.00833333333333, 8)
        self.assertAlmostEqual(yres, -0.0083333333333333, 8)
        self.assertEqual(0, x_offset)
        self.assertEqual(0, y_offset)
        # Now test the coarse map
        x, y, x_offset, y_offset, xres, yres, ulx, uly = self.coarse_map.get_dimensions()
        self.assertEqual(x, 35)
        self.assertEqual(y, 41)
        self.assertAlmostEqual(ulx, -78.466666666, 8)
        self.assertAlmostEqual(uly, 0.975, 8)
        self.assertAlmostEqual(xres, 0.00833333333333, 8)
        self.assertAlmostEqual(yres, -0.0083333333333333, 8)
        self.assertEqual(0, x_offset)
        self.assertEqual(0, y_offset)

    def testCountBands(self):
        """Tests that the number of bands is correctly identified"""
        self.assertEqual(1, self.fine_map.get_band_number())
        multi_band = Map(os.path.join("sample", "multi_band.tif"))
        self.assertEqual(201, multi_band.get_band_number())

    def testGetXY(self):
        """Tests the raster dimensions are correctly identified."""
        x, y = self.fine_map.get_x_y()
        self.assertEqual(x, 13)
        self.assertEqual(y, 13)
        x, y = self.coarse_map.get_x_y()
        self.assertEqual(x, 35)
        self.assertEqual(y, 41)

    def testSetDimensions(self):
        """
        Tests set_dimensions method
        """
        tmp = Map()
        tmp.set_dimensions("sample/SA_sample_fine.tif")
        x, y, ulx, uly, xres, yres = [
            tmp.x_size,
            tmp.y_size,
            tmp.x_ul,
            tmp.y_ul,
            tmp.x_res,
            tmp.y_res,
        ]
        self.assertEqual(x, 13)
        self.assertEqual(y, 13)
        self.assertAlmostEqual(ulx, -78.375, 8)
        self.assertAlmostEqual(uly, 0.8583333333333, 8)
        self.assertAlmostEqual(xres, 0.00833333333333, 8)
        self.assertAlmostEqual(yres, -0.0083333333333333, 8)

    def testFail(self):
        """
        Tests the correct exceptions are thrown when stupid things are attempted!
        """
        map_fail = Map()
        map_fail.file_name = "sample/not_here.tif"

        with self.assertRaises(IOError):
            map_fail.get_dimensions()
        map_fail.file_name = "sample/SA_sample_fine"
        with self.assertRaises(IOError):
            map_fail.get_dimensions()
        map_fail.file_name = None
        with self.assertRaises(RuntimeError):
            map_fail.set_dimensions()
        with self.assertRaises(RuntimeError):
            map_fail.check_map()

    def testHasEqualDims(self):
        """
        Tests that dimensions are correctly identified when they do or do not match.
        """
        self.assertFalse(self.fine_map.has_equal_dimensions(self.coarse_map))
        self.assertFalse(self.fine_offset_map.has_equal_dimensions(self.fine_map))
        self.assertFalse(self.coarse_map.has_equal_dimensions(self.fine_map))
        m = Map("sample/SA_samplemaskINT.tif")
        self.assertTrue(self.fine_map.has_equal_dimensions(m))
        with self.assertRaises(TypeError):
            self.fine_map.has_equal_dimensions(10)
        m.x_size = "str"
        with self.assertRaises(ValueError):
            m.check_map()

    def testOffset(self):
        """Tests that the offsets are correctly calculated between the fine and coarse maps."""
        self.assertListEqual(self.coarse_map.calculate_offset(self.fine_map), [-11, -14])
        self.assertListEqual(self.coarse_map.calculate_offset(self.fine_map.file_name), [-11, -14])
        self.assertListEqual(self.coarse_map.calculate_offset(self.coarse_map), [0, 0])
        self.assertListEqual(self.fine_map.calculate_offset(self.coarse_map), [11, 14])

    def testScale(self):
        """Tests that the scale is correctly calculated."""
        self.assertEqual(1, self.fine_map.calculate_scale(self.fine_map))
        self.assertEqual(1, self.fine_map.calculate_scale(self.fine_map.file_name))
        self.assertEqual(
            12.99959999999942,
            self.coarse_map.calculate_scale(os.path.join("sample", "null_coarse.tif")),
        )
        with self.assertRaises(ValueError):
            _ = self.coarse_map.calculate_scale(10)

    def testSample(self):
        m = Map(os.path.join("sample", "SA_sample_fine.tif"))
        m.set_sample(True)
        self.assertTrue(m.is_sample)
        self.assertEqual(0, m.x_offset)
        self.assertEqual(0, m.y_offset)

    def testExtents(self):
        """Tests that the extents are correctly calculated for the Map files."""
        self.assertListEqual(
            [
                -78.3750000000000000,
                -78.2666666666666657,
                0.7500000000000009,
                0.8583333333333343,
            ],
            self.fine_map.get_extent(),
        )

    def testIsWithin(self):
        """
        Tests that the maps are correctly identified as within or outside of each other.
        """
        self.assertTrue(self.fine_map.is_within(self.coarse_map))
        self.assertFalse(self.fine_map.is_within(self.fine_offset_map))
        self.assertFalse(self.fine_offset_map.is_within(self.fine_map))
        self.assertFalse(self.coarse_map.is_within(self.fine_map))
        with self.assertRaises(TypeError):
            self.fine_map.is_within(0.111)

    def testCoordinateConversion(self):
        """
        Tests that coordinates are correctly converted between cooridinate types
        """
        m = Map("sample/SA_sample_fine.tif")
        x, y = m.convert_lat_long(0.858333, -78.375)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        x, y = m.convert_lat_long(0.854113550519, -78.3114884325)
        self.assertEqual(x, 7)
        self.assertEqual(y, 0)
        x, y = m.convert_lat_long(0.770653918791, -78.3032713645)
        self.assertEqual(x, 8)
        self.assertEqual(y, 10)

    def testGetSpatialReference(self):
        m = Map("sample/SA_sample_fine.tif")
        proj = m.get_projection()
        self.assertIn(proj, self.expected_WGS_84)

    def testRasteriseShapefile(self):
        """
        Tests basic rasterisation of a shapefile is successful.
        """
        m = Map()
        output_raster = "output/raster_out1.tif"
        m.rasterise(
            shape_file="sample/shape_sample.shp",
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([13, 71, 0, 0, 0.00833333, -0.001]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        self.assertEqual(361, np.sum(m.data))
        self.assertEqual(1, m.data[20, 4])
        self.assertEqual(0, m.data[20, 6])

    def testRasteriseShapefileWithExtent(self):
        """
        Tests rasterisation using an extent is successful.
        """
        m = Map()
        output_raster = "output/raster_out1b.tif"
        new_extent = [-78.363529863, -78.321863213, 0.817435788, 0.850435788]

        m.rasterise(
            shape_file="sample/shape_sample.shp",
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
            extent=new_extent,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([4, 32, 0, 0, 0.00833333, -0.001, -78.36352986307837, 0.8504357884796987]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        self.assertEqual(73, np.sum(m.data))
        self.assertEqual(0, m.data[2, 2])
        self.assertEqual(1, m.data[10, 2])

    def testRasteriseShapefileWithFields(self):
        """
        Tests that values are correctly applied for rasterisation of a shapefile with fields.
        """
        m = Map()
        output_raster = "output/raster_out2.tif"
        m.rasterise(
            shape_file="sample/shape_sample.shp",
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
            field="field1",
            burn_val=100,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([13, 71, 0, 0, 0.00833333, -0.001]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        self.assertEqual(4460, np.sum(m.data))
        self.assertEqual(10, m.data[21, 5])
        self.assertEqual(0, m.data[21, 7])
        self.assertEqual(20, m.data[13, 10])

    def testRasteriseShapefileWithFields2(self):
        """
        Tests that values are correctly applied for rasterisation of a shapefile with fields.
        """
        m = Map()
        output_raster = "output/raster_out3.tif"
        m.rasterise(
            shape_file="sample/shape_sample.shp",
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
            field="field2",
            burn_val=100,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([13, 71, 0, 0, 0.00833333, -0.001]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        self.assertEqual(67705, np.sum(m.data))
        self.assertEqual(245, m.data[20, 4])
        self.assertEqual(0, m.data[21, 7])
        self.assertEqual(1, m.data[13, 10])

    def testRasteriseShapefileWithFields3(self):
        """
        Tests that values are correctly applied for rasterisation of a shapefile with fields.
        """
        m = Map()
        output_raster = "output/raster_out4.tif"
        m.rasterise(
            shape_file="sample/shape_sample.shp",
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
            burn_val=100,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([13, 71, 0, 0, 0.00833333, -0.001]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        self.assertEqual(36100, np.sum(m.data))
        self.assertEqual(100, m.data[20, 4])
        self.assertEqual(0, m.data[21, 7])
        self.assertEqual(100, m.data[13, 10])

    def testRasteriseShapefileWithFields4(self):
        """
        Tests that values are correctly applied for rasterisation of a shapefile with selection of one particular field
        """
        m = Map()
        output_raster = "output/raster_out5.tif"
        m.rasterise(
            shape_file="sample/shape_sample.shp",
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
            attribute_filter="field1=10",
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([10, 65, 0, 0, 0.00833333, -0.001]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        self.assertEqual(274, np.sum(m.data))
        self.assertEqual(1, m.data[1, 4])

    def testRasteriseShapefileWithBuffer(self):
        """
        Tests that the shapefile can be rasterised with an extra buffer around the edge.
        """
        m = Map()
        output_raster = "output/raster_out6.tif"
        m.rasterise(
            shape_file="sample/shape_sample.shp",
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
            x_buffer=2.0,
            y_buffer=3.0,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([15, 75, 0, 0, 0.00833333, -0.001]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        self.assertEqual(361, np.sum(m.data))
        self.assertEqual(1, m.data[20, 4])
        self.assertEqual(0, m.data[21, 7])

    def testRasteriseShapefileWithDataSource(self):
        """
        Tests that a data source can be used for rasterising the shapefile instead of a file path.
        """
        m = Map()
        output_raster = "output/raster_out7.tif"
        output_ds = ogr.Open("sample/shape_sample.shp")
        m.rasterise(
            shape_file=output_ds,
            raster_file=output_raster,
            x_res=0.00833333,
            y_res=0.001,
            x_buffer=2.0,
            y_buffer=3.0,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([15, 75, 0, 0, 0.00833333, -0.001]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        output_ds = None
        self.assertEqual(361, np.sum(m.data))
        self.assertEqual(1, m.data[20, 4])
        self.assertEqual(0, m.data[21, 7])

    def testRasteriseShapefileWithGeotransform(self):
        """
        Tests that a custom geotransform can be provided for during rasterisation.
        """
        m = Map()
        output_raster = "output/raster_out8.tif"
        geo_transform = (-78.375, 0.00833333, 0, 0.858333, 0, -0.00833333)
        output_ds = ogr.Open("sample/shape_sample.shp")
        m.rasterise(shape_file=output_ds, raster_file=output_raster, geo_transform=geo_transform)
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([12, 10, 0, 0, 0.00833333, -0.00833333]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        output_ds = None
        self.assertEqual(53, np.sum(m.data))
        self.assertEqual(1, m.data[5, 4])
        self.assertEqual(0, m.data[0, 0])

    def testRasteriseShapefileWithGeotransformAndDims(self):
        """
        Tests that a custom geotransform and dimensions can be provided for during rasterisation.
        """
        m = Map()
        output_raster = "output/raster_out9.tif"
        geo_transform = (-78.375, 0.00833333, 0, 0.858333, 0, -0.00833333)
        output_ds = ogr.Open("sample/shape_sample.shp")
        m.rasterise(
            shape_file=output_ds,
            raster_file=output_raster,
            geo_transform=geo_transform,
            width=13,
            height=13,
        )
        self.assertTrue(os.path.exists(output_raster))
        dims = m.get_dimensions()
        for i, each in enumerate([13, 13, 0, 0, 0.00833333, -0.00833333]):
            self.assertAlmostEqual(each, dims[i], places=5)
        self.assertIn(m.get_projection(), self.expected_WGS_84)
        m.open()
        output_ds = None
        self.assertEqual(53, np.sum(m.data))
        self.assertEqual(1, m.data[5, 4])
        self.assertEqual(0, m.data[0, 0])

    def testRasteriseErrors(self):
        """
        Tests that rasterise raises the correct errors when files don't exist, or incorrect parameters are provided.
        """
        m = Map()
        with self.assertRaises(IOError):
            m.rasterise(
                shape_file="not_exist",
                raster_file="output.tif",
                x_res=0.00833333,
                y_res=0.001,
                field="field2",
                burn_val=100,
            )
        m = Map()
        with self.assertRaises(IOError):
            m.rasterise(
                shape_file="sample/shape_sample.shp",
                raster_file="sample/SA_sample.tif",
                x_res=0.00833333,
                y_res=0.001,
                field="field2",
                burn_val=100,
            )
        with self.assertRaises(ValueError):
            m.rasterise(
                shape_file="sample/SA_sample.tif",
                raster_file="output.tif",
                x_res=0.00833333,
                y_res=0.001,
                field="field2",
                burn_val=100,
            )
        m = Map()
        with self.assertRaises(ValueError):
            m.rasterise(shape_file="sample/shape_sample.shp", raster_file="no_exist.tif")
        m = Map()
        with self.assertRaises(ValueError):
            m.rasterise(
                shape_file="sample/shape_sample.shp",
                raster_file="output.tif",
                geo_transform=(1, 1, 1, 1, 1, 1),
                x_res=1.0,
                y_res=1.0,
            )

    def testCreateCopy(self):
        """
        Tests that create copy works as intended.
        """
        m = Map()
        src_file = os.path.join("sample", "SA_sample.tif")
        dst_file = os.path.join("output", "copy.tif")
        m2 = Map(src_file)
        m.create_copy(dst_file=dst_file, src_file=src_file)
        self.assertTrue(os.path.exists(dst_file))
        m.file_name = src_file
        with self.assertRaises(IOError):
            m.create_copy(dst_file=dst_file)
        self.assertListEqual(m.get_dimensions(), m2.get_dimensions())
        self.assertEqual(m.get_projection(), m2.get_projection())

    def testCreate(self):
        """
        Tests that create function works properly.
        """
        m = Map()
        output_file = "output/test_create.tif"
        m.data = np.zeros(shape=(10, 10))
        m.create(output_file)
        self.assertTrue(os.path.exists(output_file))
        m2 = Map(output_file)
        m2.open()
        self.assertEqual((10, 10), m2.data.shape)
        self.assertEqual(0, np.sum(m2.data))
        with self.assertRaises(IOError):
            m.create(output_file)
        m.data = None
        with self.assertRaises(ValueError):
            m.create(output_file)

    def testCreateWithGeotransform(self):
        """
        Tests that the create function works properly with setting a geotransform.
        """
        m = Map()
        np.random.seed(1)
        m.data = np.random.rand(10, 10)
        output_file = "output/test_create2.tif"
        gt = (
            -76.54166666666666,
            0.008333333333333333,
            0.0,
            5.024999999999999,
            0.0,
            -0.008333333333333333,
        )
        proj = (
            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
            'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG",'
            '"4326"]]'
        )
        m.create(
            output_file,
            bands=1,
            datatype=gdal.GDT_Float32,
            geotransform=gt,
            projection=proj,
        )
        m2 = Map(output_file)
        m2.open()
        self.assertEqual((10, 10), m2.data.shape)
        self.assertAlmostEqual(48.58779, np.sum(m2.data), places=5)

    def testDataTypeFetch(self):
        """Tests that the data type is correctly obtained."""
        m = Map("sample/SA_sample.tif")
        self.assertEqual(6, m.get_dtype())
        self.assertEqual(6, m.get_dtype(band_no=1))

    def testGetDataset(self):
        """Tests that the dataset is obtained correctly."""
        m = Map(os.path.join("sample", "PlotBiodiversityMetrics.db"))
        with self.assertRaises(IOError):
            m.get_dataset()

    def testCalculateOffset(self):
        """Tests that the calculate offset errors work as intended."""
        m = Map(os.path.join("sample", "SA_sample_fine.tif"))
        m2 = Map(os.path.join("sample", "SA_sample_coarse.tif"))
        x, y = m.calculate_offset(m2)
        self.assertEqual(11, x)
        self.assertEqual(14, y)
        with self.assertRaises(TypeError):
            m.calculate_offset(10)

    def get_null_projection(self):
        """Get null projection for mock testing."""
        a = 0
        while True:
            a += 1
            yield a

    @patch.object(Map, "get_projection", get_null_projection)
    def testCalculateOffsetMixedProjection(self):
        """Tests that the calculate offset errors work as intended."""
        m = Map(os.path.join("sample", "SA_sample_fine.tif"), logging_level=50)
        m2 = Map(os.path.join("sample", "SA_sample_coarse.tif"), logging_level=50)
        with self.assertRaises(TypeError):
            _, _ = m.calculate_offset(m2)

    def testTranslate(self):
        """Tests the translation process works as intended."""
        source_file = os.path.join("sample", "SA_sample_fine.tif")
        dest_file1 = os.path.join("output", "translated1.tif")
        dest_file2 = os.path.join("output", "translated2.tif")
        m = Map(source_file)
        new_x, new_y = 10, 10
        new_proj_win = [-78.375, 0.8583333333333343, -78.3, 0.8]
        expected_extent = [-78.375, -78.3, 0.8, 0.8583333333333343]
        m.translate(dest_file=dest_file1, projWin=new_proj_win)
        with self.assertRaises(ValueError):
            m.translate(dest_file=None, projWin=new_proj_win)
        with self.assertRaises(IOError):
            m.translate(dest_file=dest_file1, projWin=new_proj_win)
        m = Map()
        m.translate(source_file=source_file, dest_file=dest_file2, width=new_x, height=new_y)
        self.assertTrue(os.path.exists(dest_file1))
        m1 = Map(dest_file1)
        actual_extent = m1.get_extent()
        for expected, actual in zip(expected_extent, actual_extent):
            self.assertAlmostEqual(expected, actual, places=5)
        self.assertTrue(os.path.exists(dest_file1))
        m2 = Map(dest_file2)
        self.assertEqual([new_x, new_y], m2.get_x_y())


@unittest.skipUnless(hasattr(gdal, "Warp"), "Skipping reprojection test as gdal.Warp not found.")
@skipGdalWarp
class TestMapReprojection(unittest.TestCase):
    """
    Tests that reprojections work as intended.
    """

    @classmethod
    def setUpClass(cls):
        """
        Performs the initial re-projections.
        """
        cls.map_0 = os.path.join("sample", "multi_band.tif")
        cls.map_1 = os.path.join("sample", "SA_sample.tif")
        cls.map_2 = os.path.join("output", "tmp_map1.tif")
        cls.map_3 = os.path.join("output", "tmp_map2.tif")
        cls.map_4 = os.path.join("output", "tmp_map3.tif")
        cls.map_5 = os.path.join("output", "tmp_map5.tif")
        cls.m0 = Map(cls.map_0)
        cls.m = Map(cls.map_1)
        cls.destination_projection = osr.SpatialReference()
        res = cls.destination_projection.ImportFromEPSG(3857)
        if res != 0:
            raise RuntimeError("Could not import from EPSG in osr.SpatialReference: {}.".format(res))
        cls.proj_wkt = cls.destination_projection.ExportToWkt()
        cls.m.reproject_raster(dest_file=cls.map_2, dest_projection=cls.destination_projection)
        cls.m.reproject_raster(
            dest_file=cls.map_3,
            dest_projection=cls.destination_projection,
            x_scalar=2,
            y_scalar=10,
        )
        cls.m0.reproject_raster(dest_file=cls.map_5, x_scalar=0.1, y_scalar=0.1)
        cls.m_2 = Map(cls.map_2)
        cls.m_3 = Map(cls.map_3)
        cls.m_5 = Map(cls.map_5)

    def testCorrectNewProjection(self):
        """
        Tests that reprojection works correctly, either creating a new file or over-writing the original file
        """

        self.assertNotEqual(self.m.get_projection(), self.proj_wkt)
        self.assertEqual(self.m0.get_projection(), self.m_5.get_projection())
        self.assertEqual(self.proj_wkt, self.m_2.get_projection())
        self.assertEqual(self.proj_wkt, self.m_3.get_projection())
        self.assertEqual(self.proj_wkt, self.m_3.get_projection())

    def testNewDimensions(self):
        """
        Tests that the new dimensions are correctly set
        """

        dims_0 = self.m0.get_dimensions()
        dims_1 = self.m.get_dimensions()
        dims_2 = self.m_2.get_dimensions()
        dims_3 = self.m_3.get_dimensions()
        dims_5 = self.m_5.get_dimensions()
        self.assertListEqual(dims_1[:4], dims_2[:4])
        self.assertAlmostEqual(929.3830958815255, dims_2[4], places=5)
        self.assertAlmostEqual(-929.3830958815255, dims_2[5], places=5)
        self.assertAlmostEqual(-8520579.357801815, dims_2[6], places=5)
        self.assertAlmostEqual(560098.928515636, dims_2[7], places=5)
        self.assertAlmostEqual(dims_2[4] * 2, dims_3[4], places=5)
        self.assertAlmostEqual(dims_2[5] * 10, dims_3[5], places=5)
        self.assertAlmostEqual(dims_0[0] * 10, dims_5[0], places=5)
        self.assertAlmostEqual(dims_0[1] * 10, dims_5[1], places=5)
        self.assertAlmostEqual(dims_0[4] * 0.1, dims_5[4], places=5)
        self.assertAlmostEqual(dims_0[5] * 0.1, dims_5[5], places=5)
        shutil.copy2(self.map_1, self.map_4)
        m_4 = Map(self.map_4)
        m_4.reproject_raster(dest_projection=self.destination_projection)
        self.assertListEqual(m_4.read_dimensions(), dims_2)
        self.assertEqual(m_4.get_projection(), self.proj_wkt)

    def testNewValues(self):
        """
        Tests that the new values are correctly stored in the raster file
        """
        self.m.open()
        self.m_2.open()
        for i in range(self.m.data.shape[0]):
            for j in range(self.m.data.shape[1]):
                self.assertEqual(self.m.data[i, j], self.m_2.data[i, j])
        self.m_3.open()
        self.assertEqual(444, self.m_3.data[0, 0])
        self.assertEqual(258, self.m_3.data[1, 11])

    def testDownscaling(self):
        """
        Tests that re-scaling works without trying to reproject the raster.
        """
        map_6 = "output/tmp_map6.tif"
        shutil.copy2(self.map_2, map_6)
        m_6 = Map(map_6, logging_level=20)
        m_6.reproject_raster(x_scalar=2.0, y_scalar=3.0)
        m_4 = Map(self.map_2)
        dims = m_6.read_dimensions()
        dims_2 = m_4.get_dimensions()
        for i, each in enumerate(dims_2[6:]):
            self.assertAlmostEqual(each, dims[i + 6])
        self.assertAlmostEqual(dims[4], 2 * dims_2[4])
        self.assertAlmostEqual(dims[5], 3 * dims_2[5])

    def testUpScaling(self):
        """
        Tests that re-scaling works without trying to reproject the raster.
        """
        map_5 = "output/tmp_map5.tif"
        shutil.copy2(self.map_2, map_5)
        m_5 = Map(map_5)
        m_5.reproject_raster(x_scalar=0.5, y_scalar=0.5)
        m_4 = Map(self.map_2)
        dims = m_5.read_dimensions()
        dims_2 = m_4.get_dimensions()
        for i, each in enumerate(dims_2[6:]):
            self.assertAlmostEqual(each, dims[i + 6])
        self.assertAlmostEqual(dims[4], 0.5 * dims_2[4])
        self.assertAlmostEqual(dims[5], 0.5 * dims_2[5])

    def testNoData(self):
        """
        Tests that no data values are correctly read from tif files.
        """
        m = Map("sample/large_mask.tif")
        self.assertEqual(-99.0, m.get_no_data())
        self.assertEqual(-99.0, m.get_no_data(1))
        m2 = Map("sample/bytesample.tif")
        self.assertIsNone(m2.get_no_data())
        m3 = Map("sample/example_historical_fine.tif")
        self.assertAlmostEqual(-3.4028234663852886e38, m3.get_no_data(), places=7)

    def testMultiBandsExist(self):
        """Tests that the correct number of bands exist in the output raster."""
        self.assertEqual(201, self.m_5.get_band_number())
        # Test that the first 5 bands contain non-zero data (as this is what was in the original)
        for i in range(1, 5, 1):
            self.m_5.open(band_no=i)
            self.assertGreater(np.sum(self.m_5.data), 0)
            self.m0.open(band_no=i)
            self.assertAlmostEqual(np.sum(self.m0.data) * 100, np.sum(self.m_5.data), places=5)


class MapAssignment(unittest.TestCase):
    """
    Asserts that the Map class correctly reads and writes data properly.
    """

    @classmethod
    def setUpClass(cls):
        shutil.copy(os.path.join("sample", "null.tif"), "output")
        cls.map = Map(file=os.path.join("output", "null.tif"))
        cls.map.open()
        cls.map.data[0:5, 0:2] = 10
        cls.map.write(band_no=1)

    def testBaseMap(self):
        """
        Just a double check to make sure that the base map file is correct (not really a test of this code at all).
        """
        ds = gdal.Open(os.path.join("sample", "null.tif"))
        arr = ds.GetRasterBand(1).ReadAsArray()
        self.assertEqual(np.sum(arr), 169)
        ds = None

    def testMapUpdates(self):
        ds = gdal.Open(os.path.join("output", "null.tif"))
        arr = ds.GetRasterBand(1).ReadAsArray()
        self.assertEqual(np.sum(arr), 259)
        ds = None

    def testWriteError(self):
        """Tests that the write function raises the expected errors."""
        m = Map("none.tif")
        with self.assertRaises(IOError):
            m.write()
        m = Map(os.path.join("sample", "null.tif"))
        with self.assertRaises(ValueError):
            m.write()
        m = Map()
        with self.assertRaises(ValueError):
            m.map_exists()


@unittest.skipUnless(
    hasattr(scipy.spatial, "Voronoi"),
    "Skipping reprojection test as scipy.spatial.Voronoi not found.",
)
class TestFragmentedLandscape(unittest.TestCase):
    """
    Tests that the fragmented landscape generation creates successfully for a range of fragment numbers and sizes.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the class object by creating the required maps
        :return:
        """
        if os.path.exists("landscapes"):
            shutil.rmtree("landscapes")
        cls.l1 = FragmentedLandscape(
            size=10,
            number_fragments=2,
            total=4,
            output_file=os.path.join("landscapes", "l1.tif"),
        )
        cls.l2 = FragmentedLandscape(
            size=100,
            number_fragments=57,
            total=150,
            output_file=os.path.join("landscapes", "l2.tif"),
        )
        cls.l3 = FragmentedLandscape(
            size=24,
            number_fragments=5,
            total=5,
            output_file=os.path.join("landscapes", "l3.tif"),
        )
        cls.l1.generate()
        cls.l2.generate()
        cls.l3.generate()
        cls.l4 = FragmentedLandscape(
            size=10,
            number_fragments=1,
            total=2,
            output_file=os.path.join("landscapes", "l4.tif"),
        )
        cls.l4.generate()
        cls.l5 = FragmentedLandscape(
            size=100,
            number_fragments=100,
            total=2000,
            output_file=os.path.join("landscapes", "l5.tif"),
        )
        cls.l5.generate()

    @classmethod
    def tearDownClass(cls):
        # pass
        if os.path.exists("landscapes"):
            shutil.rmtree("landscapes")

    def testCreateFragmentedLandscapes(self):
        self.assertEqual(self.l1.output_file, os.path.join("landscapes", "l1.tif"))
        self.assertTrue(os.path.exists(self.l1.output_file))
        self.assertEqual(self.l2.output_file, os.path.join("landscapes", "l2.tif"))
        self.assertTrue(os.path.exists(self.l2.output_file))
        self.assertEqual(self.l3.output_file, os.path.join("landscapes", "l3.tif"))
        self.assertTrue(os.path.exists(self.l3.output_file))
        self.assertEqual(self.l4.output_file, os.path.join("landscapes", "l4.tif"))
        self.assertTrue(os.path.exists(self.l4.output_file))

    def testDimensionsCorrect1(self):
        """
        Checks that the saved dimensions are correct.
        """
        m1 = Map(logging_level=logging.CRITICAL)
        m1.file_name = self.l1.output_file
        m1.set_dimensions()
        self.assertEqual(m1.x_size, 10)
        self.assertEqual(m1.y_size, 10)
        m1 = Map(logging_level=logging.CRITICAL)
        m1.file_name = self.l1.output_file
        m1.set_dimensions(x_size=10)
        self.assertEqual(m1.x_size, 10)
        self.assertEqual(m1.y_size, 10)

    def testDimensionsCorrect2(self):
        """
        Checks that the saved dimensions are correct.
        """
        m2 = Map()
        m2.file_name = self.l2.output_file
        m2.set_dimensions()
        self.assertEqual(m2.x_size, 100)
        self.assertEqual(m2.y_size, 100)

    def testDimensionsCorrect3(self):
        """
        Checks that the saved dimensions are correct.
        """
        m3 = Map()
        m3.file_name = self.l3.output_file
        m3.set_dimensions()
        self.assertEqual(m3.x_size, 24)
        self.assertEqual(m3.y_size, 24)

    def testDimensionsCorrect5(self):
        """
        Checks that the saved dimensions are correct.
        """
        m5 = Map()
        m5.file_name = self.l5.output_file
        m5.set_dimensions()
        self.assertEqual(m5.x_size, 100)
        self.assertEqual(m5.y_size, 100)


class TestSubsettingMaps(unittest.TestCase):
    """
    Tests the reading of tif files works correctly, including subsetting and cached-subsetting to obtain selections from
    the maps.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the map object for reading from.
        """
        cls.m = Map("sample/SA_sample_fine.tif")

    def testSubsetting(self):
        """
        Tests the basic subsetting functionality works as intended.
        :return:
        """
        arr = self.m.get_subset(x_offset=0, y_offset=0, x_size=13, y_size=13)
        with self.assertRaises(ValueError):
            self.m.get_subset(-1, -1, 13, 13)
        with self.assertRaises(ValueError):
            self.m.get_subset(0, 0, 14, 14)
        with self.assertRaises(ValueError):
            self.m.get_subset(14, 14, 1, 1)
        self.assertEqual(arr[0, 0], 231)
        self.assertEqual(arr[1, 0], 296)
        self.assertEqual(arr[0, 1], 303)
        arr2 = self.m.get_subset(x_offset=5, y_offset=5, x_size=2, y_size=2)
        self.assertEqual(arr2[0, 0], 288)
        self.assertEqual(arr2[1, 0], 263)
        self.assertEqual(arr2[0, 1], 286)

    def testCachedSubsetting(self):
        """
        Tests that the cached subsetting functionality works as intended.
        :return:
        """
        arr = self.m.get_cached_subset(x_offset=0, y_offset=0, x_size=13, y_size=13)
        self.assertEqual(arr[0, 0], 231)
        self.assertEqual(arr[1, 0], 296)
        self.assertEqual(arr[0, 1], 303)
        arr2 = self.m.get_cached_subset(x_offset=5, y_offset=5, x_size=2, y_size=2)
        self.assertEqual(arr2[0, 0], 288)
        self.assertEqual(arr2[1, 0], 263)
        self.assertEqual(arr2[0, 1], 286)

    def testSubsettingNoData(self):
        """
        Tests that the correct array is returned when using a no data value.
        """
        m = Map("sample/large_mask.tif")
        self.assertEqual(-243335289.0, np.sum(m.get_subset(0, 0, 1818, 1695)))
        self.assertEqual(375, np.sum(m.get_subset(0, 0, 1818, 1695, 0)))

    def testWritingSubset(self):
        """Tests that writing a subset of the gdal raster works as intended."""
        m = Map()
        tmp_file = "output/writesubset.tif"
        m.data = np.ones((10, 10))
        m.create(tmp_file)
        m = Map(tmp_file)
        tmp_array = np.ones((5, 5)) + 1
        m.write_subset(tmp_array, 2, 2)
        m.file_name = "none.tif"
        with self.assertRaises(IOError):
            m.write_subset(tmp_array, 2, 2)
        tmp_array = np.ones((10000, 10000))
        m.file_name = tmp_file
        with self.assertRaises(ValueError):
            m.write_subset(tmp_array, 2, 2)

        m = Map(tmp_file)
        m.open()
        expected_array = np.ones((10, 10))
        expected_array[2:7, 2:7] = 2
        self.assertTrue(np.array_equal(expected_array, m.data))


class TestWKTFunctions(unittest.TestCase):
    """Tests converting WKTs in csvs to shapefiles"""

    def testDefaultShapefileFromWKT(self):
        """Tests the default conversion of WKT to shapefile."""
        output_shapefile1 = os.path.join("output", "wkt_shapefile1.shp")
        output_shapefile2 = os.path.join("output", "wkt_shapefile2.shp")
        with open(os.path.join("sample", "wkt_test.csv"), "r") as input_file:
            csv_reader = csv.DictReader(input_file)
            lines = [x for x in csv_reader]
            wkts = [[z for x, z in y.items() if x == "WKT"][0] for y in lines]
            shapefile_from_wkt(wkts=wkts, dest_file=output_shapefile1)
            shapefile_from_wkt(wkts=wkts, dest_file=output_shapefile2, fields=lines)
            with self.assertRaises(IOError):
                shapefile_from_wkt(wkts=wkts, dest_file=output_shapefile1)
        self.assertTrue(os.path.exists(output_shapefile1))
        self.assertTrue(os.path.exists(output_shapefile2))


class TestGdalErrorHandler(unittest.TestCase):
    def testErrorHandler(self):
        class TempLogger(object):
            """Test logger for testing outputting."""

            def __init__(self):
                self.logs = []

            def log(self, err_level, err_msg):
                self.logs.append([err_level, err_msg])

        tl = TempLogger()
        geh = GdalErrorHandler(tl)
        geh.handler(10, 1, "test message")
        geh.handler(20, 2, "test message 2")
        expected_output = [[10, "test message"], [20, "test message 2"]]
        self.assertEqual(expected_output, tl.logs)
        self.assertEqual("test message 2", geh.err_msg)
        self.assertEqual(20, geh.err_level)
        self.assertEqual(2, geh.err_no)
