"""Tests spatial_algorithms module for spatial routines."""
import unittest

from pycoalescence.spatial_algorithms import *

try:
    import osgeo

    gdal_version = osgeo.__version__
except ImportError as ie:
    gdal_version = "0.0.0"
    logging.warn("Could not import osgeo: {}".format(ie))


class TestSpatialAlgorthims(unittest.TestCase):
    """Tests all the spatial algorithms"""

    def testCalculateDistanceBetween(self):
        """Tests that the distance between points is correctly calculated"""
        self.assertAlmostEqual(calculate_distance_between(0, 0, 1, 1), 2 ** 0.5, places=8)
        self.assertAlmostEqual(calculate_distance_between(1, 10, 8, 10), 7, places=8)
        self.assertAlmostEqual(calculate_distance_between(1, -1, 10, -1), 9, places=8)
        self.assertAlmostEqual(calculate_distance_between(-1, -1, 1, 1), 8 ** 0.5, places=8)

    def testCalculateCentreMass(self):
        """Tests that the centre of mass is correctly calculated for a list of points."""
        points_list = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
        self.assertTupleEqual((0, 0), calculate_centre_of_mass(points_list))
        points_list = [[0, -1], [-1, 0], [0, 1], [1, 0]]
        self.assertTupleEqual((0, 0), calculate_centre_of_mass(points_list))
        with self.assertRaises(ValueError):
            points_list = [[-1, -1], [1, -1], [-1, 1], [1, 1]]
            self.assertListEqual((0, 0), calculate_centre_of_mass(points_list))

    def testReflectDimensions(self):
        """Tests that dimensions are correctly reflected"""
        points = reflect_dimensions([[1, 1], [0.5, 0.5]], maximums=(2, 2))
        expected_points = [[1, 1], [0.5, 0.5]]
        expected_points.extend([[1, -1], [0.5, -0.5], [1, 3], [0.5, 3.5], [-1, 1], [-0.5, 0.5], [3, 1], [3.5, 0.5]])
        for i, each in enumerate(expected_points):
            self.assertAlmostEqual(each[0], points[i][0], places=3)
            self.assertAlmostEqual(each[1], points[i][1], places=3)

    def testArchimedesSpiral(self):
        """Tests a single iteration of the archimedes spiral produces the expected output"""
        self.assertEqual(archimedes_spiral(0, 0, 1, 2 * 3.14)[0], 0)
        self.assertEqual(archimedes_spiral(0, 0, 1, 2 * 3.14)[1], -1)

    def testConvertCoordinates(self):
        """Tests that conversion of coordinates works as expected between two different coordinate systems."""
        input_srs = osr.SpatialReference()
        input_srs.ImportFromWkt(
            'PROJCS["WGS_1984_UTM_Zone_50N",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",'
            'SPHEROID["WGS_84",6378137,298.257223563]],'
            'PRIMEM["Greenwich",0],'
            'UNIT["Degree",0.017453292519943295],'
            'AUTHORITY["EPSG","4326"]],'
            'PROJECTION["Transverse_Mercator"],'
            'PARAMETER["latitude_of_origin",0],'
            'PARAMETER["central_meridian",117],'
            'PARAMETER["scale_factor",0.9996],'
            'PARAMETER["false_easting",500000],'
            'PARAMETER["false_northing",0],'
            'UNIT["Meter",1],'
            'AUTHORITY["EPSG","32650"]]'
        )
        if int(gdal_version[0]) < 3:

            output_srs = osr.SpatialReference(
                wkt='GEOGCS["WGS 84",DATUM["WGS_1984",'
                'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
                'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],'
                'UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'
            )
            x, y = convert_coordinates(600544.9967818621, 644607.5784286809, input_srs, output_srs)
        else:
            # TODO check if this is a bug with gdal 3.0 or gdal 2.0
            output_srs = osr.SpatialReference(
                'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
                'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'
            )
            y, x = convert_coordinates(600544.9967818621, 644607.5784286809, input_srs, output_srs)
        self.assertAlmostEqual(117.9082031776, x)
        self.assertAlmostEqual(5.8310327261971, y)

    def testEstimationSigmaFromDistance(self):
        """Tests the estimation of sigma from a distance travelled and a number of steps."""
        self.assertAlmostEqual(1.0, estimate_sigma_from_distance(1.0 * (math.pi / 2.0) ** 0.5, 1), places=7)
        self.assertAlmostEqual(2.0, estimate_sigma_from_distance(2.0 * (math.pi / 2.0) ** 0.5, 1), places=7)
        self.assertAlmostEqual(4.0, estimate_sigma_from_distance(4.0 * (math.pi / 2.0) ** 0.5, 1), places=7)
        self.assertAlmostEqual(1.0, estimate_sigma_from_distance((2 * math.pi / 2.0) ** 0.5, 2), places=7)
        self.assertAlmostEqual(2.0, estimate_sigma_from_distance(2 * (2 * math.pi / 2.0) ** 0.5, 2), places=7)
        self.assertAlmostEqual(4.0, estimate_sigma_from_distance(4 * (2 * math.pi / 2.0) ** 0.5, 2), places=7)
        self.assertAlmostEqual(2.0, estimate_sigma_from_distance(2 * (100 * math.pi / 2.0) ** 0.5, 100), places=7)
        self.assertAlmostEqual(4.0, estimate_sigma_from_distance(4 * (100 * math.pi / 2.0) ** 0.5, 100), places=7)
