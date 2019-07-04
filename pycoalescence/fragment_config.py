"""
Generate the fragment config files from a supplied shapefile and a raster file to offset from.

The function :func:`generate_fragment_csv()` contains the full pipeline to generate the fragment csv.
"""
import csv

import os
import sys

try:
    from osgeo import gdal, ogr, osr
except ImportError as ie:  # pragma: no cover
    try:
        import gdal
        from gdal import ogr, osr
    except ImportError:
        gdal = None
        raise ie

from .future_except import FileNotFoundError, FileExistsError
from .map import Map


def generate_fragment_csv(input_shapefile, input_raster, output_csv, field_name="fragment", field_area="area"):
    """
    Generates the fragment csv from the provided shapefile and raster file. Coordinates for outputted to the csv are
    calculated from the extent of each polygon in the shapefile as their relative position on the input raster.

    The fragment extents are used solely, so overlapping extents of fragments results in individuals in those areas
    appearing in both fragments. Therefore, rectangular fragments alone should be used.

    .. important:: The input shapefile and raster must have the same projection.

    :param input_shapefile: the shapefile containing polygons defining fragments. Should contain fields of field_name
                            and field_area
    :param input_raster: raster file to calculate the relative coordinates on
    :param output_csv: output csv to create
    :param field_name: name of the field in the shapefile to acquire fragment names from
    :param field_area: name of the field in the shapefile to acquire the number of individuals from
    """
    f = FragmentConfigHandler()
    f.generate_config(input_shapefile, input_raster, field_name, field_area)
    f.write_csv(output_csv)


class FragmentConfigHandler(object):
    """
    Contains routines for calculating the offsets from a config file.
    """

    def __init__(self):
        self.fragment_list = {}

    def generate_config(self, input_shapefile, input_raster, field_name="fragment", field_area="area"):
        """
        Generates the config file from the shapefile containing the fragments, writing the coordinates of the extent of
        each fragment to the output csv. The coordinates are calculated from their relevant position on the input
        raster.

        :param str input_shapefile: shapefile containing the fragments in a "fragments" field, with each defined as a
                                polygon.
        :param str input_raster: the raster to calculate the coordinates from
        :param str field_name: optionally provide a field to extract fragment names from
        :param str field_area: optionally provide a field to extract fragment areas from (the number of individuals that
                               exist in the fragment.
        """
        if not input_shapefile.endswith(".shp"):
            raise ValueError("Input file {} is not a shape file (.shp).".format(input_shapefile))
        if not input_raster.endswith(".tif"):
            raise ValueError("Input raster {} is not a tif file (.tif).".format(input_raster))
        if not os.path.exists(input_shapefile):
            raise FileNotFoundError("Input shapefile {} does not exist.".format(input_shapefile))
        if not os.path.exists(input_raster):
            raise FileNotFoundError("input raster {} does not exist.".format(input_raster))
        m = Map(input_raster)
        dim_x, dim_y = m.get_x_y()
        # Read the input Layer
        src_driver = ogr.GetDriverByName("ESRI Shapefile")
        src_ds = src_driver.Open(input_shapefile, gdal.GA_ReadOnly)
        if src_ds is None:  # pragma: no cover
            raise IOError("Could not open {}".format(input_shapefile))
        src_layer = src_ds.GetLayer()
        for feature in src_layer:
            geom = feature.GetGeometryRef()
            fragment = feature.GetField(field_name)
            area = feature.GetField(field_area)
            min_long, max_long, min_lat, max_lat = geom.GetEnvelope()
            min_x, min_y = m.convert_lat_long(max_lat, min_long)
            max_x, max_y = m.convert_lat_long(min_lat, max_long)
            if (
                    min_x < 0
                    or min_y < 0
                    or max_x < 0
                    or max_y < 0
                    or min_x > dim_x
                    or min_y > dim_y
                    or max_x > dim_x
                    or max_y > dim_y
            ):
                src_ds = None
                raise ValueError("Shapefile is not contained within the raster - cannot generate fragment config.")
            self.fragment_list[fragment] = {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y,
                "area": area,
            }
        src_ds = None

    def read_csv(self, input_csv):
        """
        Reads the input csv file into the fragments object.

        :param input_csv: the csv file to read in

        :return: None
        :rtype: None
        """
        if not os.path.exists(input_csv):
            raise FileNotFoundError("Input csv does not exist at {}.".format(input_csv))
        if sys.version_info[0] < 3:  # pragma: no cover
            infile = open(input_csv, "rb")
        else:
            infile = open(input_csv, "r", newline="")
        with infile as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if len(row) != 6:
                    raise IOError("Csv file {} does not contain 6 elements in row ({}).".format(input_csv, len(row)))
                fragment, min_x, min_y, max_x, max_y, area = row
                self.fragment_list[fragment] = {
                    "min_x": int(min_x),
                    "max_x": int(max_x),
                    "min_y": int(min_y),
                    "max_y": int(max_y),
                    "area": int(area),
                }

    def write_csv(self, output_csv):
        """
        Writes the fragments to the output csv.

        :param str output_csv: the csv to write the output to

        """
        if os.path.exists(output_csv):
            raise FileExistsError("Output csv {} already exists. Please remove first.".format(output_csv))
        if sys.version_info[0] < 3:  # pragma: no cover
            infile = open(output_csv, "wb")
        else:
            infile = open(output_csv, "w", newline="")
        with infile as csv_file:
            csv_writer = csv.writer(csv_file)
            for key, value in sorted(self.fragment_list.items()):
                csv_writer.writerow(
                    [key, value["min_x"], value["min_y"], value["max_x"], value["max_y"], value["area"]]
                )
