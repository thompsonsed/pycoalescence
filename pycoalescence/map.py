"""
Open tif files and detect properties and data using gdal. Detailed :ref:`here <map_reading>`.
"""
import copy
import logging
import math
import os
import platform
import subprocess
import types

import numpy as np
from pycoalescence.spatial_algorithms import convert_coordinates

try:
    from matplotlib import pyplot as plt
except (ImportError, RuntimeError) as ie:  # pragma: no cover
    logging.warning(ie)
try:
    NumberTypes = (types.IntType, types.LongType, types.FloatType, types.ComplexType)
except AttributeError:
    # No support for complex numbers compilation
    NumberTypes = (int, float)
try:
    from osgeo import gdal, ogr, osr

    default_val = gdal.GDT_Float32
except ImportError as ie:  # pragma: no cover
    default_val = 6
    try:
        import gdal
        from gdal import ogr, osr
    except ImportError:
        gdal = None
        raise ie
from .system_operations import check_file_exists, create_logger, check_parent, isclose

from pycoalescence.future_except import FileNotFoundError

# Check to make sure that the GDAL_PATH is in the environmental variables
if "GDAL_DATA" not in os.environ:  # pragma: no cover
    try:
        if platform.system() == "Windows":
            try:
                gdal_dir = (
                    subprocess.check_output(["echo", "%GDAL_DATA%"], shell=True).decode("utf-8").replace("\n", "")
                )
            except (AttributeError, FileNotFoundError):
                conda_dir = (
                    subprocess.check_output(["echo", "%CONDA_PREFIX%"], shell=True).decode("utf-8").replace("\n", "")
                )
                gdal_dir = os.path.join(conda_dir, "Library", "share", "gdal")
        else:
            gdal_dir = subprocess.check_output(["gdal-config", "--datadir"]).decode("utf-8").replace("\n", "")
    except (AttributeError, FileNotFoundError, OSError):
        gdal_dir = None
    if gdal_dir is None:
        raise ImportError("No GDAL_DATA directory detected. " "Please make sure that gdal has installed correctly.")
    if not os.path.exists(gdal_dir):
        raise ImportError(
            "Gdal data directory does not exist at {}. "
            "Check gdal install is completed successfully.".format(gdal_dir)
        )
    os.environ["GDAL_DATA"] = gdal_dir

gdal.UseExceptions()

class GdalErrorHandler(object):
    """
    Custom error handler for GDAL warnings and errors.
    """

    def __init__(self, logger):
        """
        Creates the error handler.
        """
        self.err_level = gdal.CE_None
        self.err_no = 0
        self.err_msg = ''
        self.logger = logger

    def handler(self, err_level, err_no, err_msg):
        """

        :param err_level: the level at which to log outputs
        :param err_no: the error number to use
        :param err_msg: the error message
        :return:
        """
        self.err_level = err_level
        self.err_no = err_no
        self.err_msg = err_msg
        self.logger.log(err_level, err_msg)



def _gdalPushErrorHandler(gdal_err_handler):
    """
    Push a new error handler for gdal to use.
    :param gdal_err_handler: the GdalErrorHandler object to use
    """
    handler = gdal_err_handler.handler
    gdal.PushErrorHandler(handler)

def _gdalPopErrorHandler():
    """
    Pop the error handler for gdal off.
    """
    gdal.PopErrorHandler()

def shapefile_from_wkt(wkts, dest_file, EPSG=4326, fields=None):
    """
    Generates a shape file from a WKT string.

    :param wkts: a list of well-known text polygons to create in the shapefile
    :param dest_file: a destination file to create
    :param EPSG: the EPSG to use for the spatial referencing
    :param fields: list of dictionaries containing fields to add to the geometries

    :rtype: None
    """
    if os.path.exists(dest_file):
        raise IOError("File already exists at {}.".format(dest_file))

    err_handler = GdalErrorHandler(logging.getLogger())
    _gdalPushErrorHandler(err_handler)
    src_file = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(dest_file)
    src_osr = osr.SpatialReference()
    src_osr.ImportFromEPSG(EPSG)
    # Create the layer
    layer = src_file.CreateLayer("WKTImport", src_osr, ogr.wkbPolygon)
    # Import the shapes from the WKT file.
    if fields is None:
        fields = [{"index": x} for x in range(1, len(wkts) + 1)]
    for key in fields[0].keys():
        # Ignore the WKT column
        if key is not "WKT":
            field_defn = ogr.FieldDefn(str(key), ogr.OFTString)
            field_defn.SetWidth(32)
            if layer.CreateField(field_defn) != 0:  # pragma: no cover
                raise ValueError("Could not create field {}".format(key))
    for i, wkt in enumerate(wkts):
        point = ogr.CreateGeometryFromWkt(wkt)
        feature = ogr.Feature(layer.GetLayerDefn())
        for key, val in fields[i].items():
            # Ignore the WKT column
            if key is not "WKT":
                feature.SetField(str(key), val)
        feature.SetGeometry(point)
        layer.CreateFeature(feature)
        feature.Destroy()
    _gdalPopErrorHandler()


class Map(object):
    """
    Contains the file name and the variables associated with this map object.

    The internal array of the tif file is stored in self.data, and band 1 of the file can be opened by using
    open()

    .. important:: Currently, Map does not support skewed rasters (not north/south).

    :ivar data: if the map file has been opened, contains the full tif data as a numpy array.
    """

    def __init__(self, file=None, is_sample=None, logging_level=logging.WARNING):
        """
        Constructor for the Map class, optionally setting the sample map, the logging level and the dispersal database
        location (if a dispersal simulation has already been run).

        :param file: sets the filename for reading tif files.
        :param is_sample: sets the sample mask to true, if it is a sampled file
        :param logging_level: the level of logging to output during dispersal simulations
        """
        self.data = None
        self.file_name = file
        self.band_number = None
        self.x_size = 0
        self.y_size = 0
        self.x_offset = 0
        self.y_offset = 0
        self.x_res = 0
        self.y_res = 0
        self.y_ul = 0
        self.x_ul = 0
        self.dimensions_set = False
        self.is_sample = is_sample
        self.logging_level = logging_level
        self.logger = logging.Logger("pycoalescence.map")
        self._create_logger()
        self._gdal_error_handler = GdalErrorHandler(self.logger)
        _gdalPushErrorHandler(self._gdal_error_handler)

    def __del__(self):
        """
        Overriding the destructor for proper destruction of the logger object
        """
        _gdalPopErrorHandler()
        if hasattr(self, "logger"):
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)


    def __deepcopy__(self, memo):
        """
        Overriding the default deep copy operator to ignore copying the logger object

        :param dict memo: the memorised key values

        :return: the copy of the Map object
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ["logger", "_gdal_error_handler"]:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def _create_logger(self, file=None, logging_level=None):
        """
        Creates the logger for use with dispersal tests. Note you can supply your own logger by over-riding
        self.logger. This function should only be run during self.__init__()

        :param file: file to write output to. If None, outputs to terminal
        :param logging_level: the logging level to use (defaults to INFO)

        :return: None
        """
        if logging_level is None:
            logging_level = self.logging_level
        self.logger = create_logger(self.logger, file, logging_level)

    def open(self, file=None, band_no=1):
        """
        Reads the raster file from memory into the data object.
        This allows direct access to the internal numpy array using the data object.

        :param str file: path to file to open (or None to use self.file_name
        :param int band_no: the band number to read from

        :rtype: None
        """
        ds = self.get_dataset(file=file)
        self.band_number = band_no
        self.data = np.array(ds.GetRasterBand(self.band_number).ReadAsArray(), dtype=np.float)
        ds = None

    def get_dataset(self, file=None, permissions=gdal.GA_Update):
        """
        Gets the dataset from the file.

        :param str file: path to the file to open
        :param int permissions: the gdal permission reference to open the dataset

        :raises ImportError: if the gdal module has not been imported correctly
        :raises IOError: if the supplied filename is not a tif or vrt
        :raises IOError: if the map does not exist

        :return: an opened dataset object
        """
        if not self.map_exists(file):
            raise IOError(
                "File {} does not exist or is not accessible." " Check read/write access.".format(self.file_name)
            )
        _, ext = os.path.splitext(self.file_name)
        if ext not in [".tif", ".vrt"]:
            raise IOError("File {} is not a tif or vrt file.".format(self.file_name))
        ds = gdal.Open(self.file_name, permissions)
        if ds is None:  # pragma: no cover
            raise IOError("Gdal could not open the file {}.".format(self.file_name))
        return ds

    def get_dtype(self, band_no=None):
        """
        Gets the data type of the provided band number

        :param band_no: band number to obtain the data type of

        :rtype: int
        :return: the gdal data type number in the raster file
        """
        if band_no is None:
            if self.band_number is None:
                self.band_number = 1
        else:
            self.band_number = band_no
        ds = self.get_dataset()
        data_type = ds.GetRasterBand(self.band_number).DataType
        ds = None
        return data_type

    def get_no_data(self, band_no=None):
        """
        Gets the no data value for the tif map.

        :param band_no: the band number to obtain the no data value from

        :return: the no data value

        :rtype: float
        """
        if band_no is None:
            if self.band_number is None:
                self.band_number = 1
        else:
            self.band_number = band_no
        ds = self.get_dataset()
        no_data = ds.GetRasterBand(self.band_number).GetNoDataValue()
        return no_data

    def map_exists(self, file=None):
        """
        Checks if the output (or provided file) exists.

        If file is provided, self.file_name is set to file.

        :param file: optionally, the file to check exists

        :return: true if the output file does exist
        :rtype bool:
        """
        if file is not None:
            self.file_name = file
        if self.file_name is None:
            raise ValueError("Cannot check existence of {}".format(self.file_name))
        return os.path.exists(self.file_name)

    def write(self, file=None, band_no=None):
        """
        Writes the array in self.data to the output array.
        The output file must exist, and the array will be overridden in the band.
        Intended for writing changes to the same file the data was read from.

        :param file: the path to the file to write to
        :param band_no: the band number to write into

        :rtype None
        """
        if band_no:
            self.band_number = band_no
        if not self.map_exists(file):
            raise IOError("File {} does not exist for writing.".format(self.file_name))
        ds = gdal.Open(self.file_name, gdal.GA_Update)
        if not ds:  # pragma: no cover
            raise IOError("Could not open tif file {}.".format(self.file_name))
        if self.data is None:
            raise ValueError("Cannot output None to tif file.")
        ds.GetRasterBand(self.band_number).WriteArray(self.data, 0, 0)
        ds.FlushCache()
        ds = None

    def write_subset(self, array, x_off, y_off):
        """
        Writes over a subset of the array to file. The size of the overwritten area is detected from the inputted array,
        and the offsets describe the location in the output map to overwrite.

        The output map must file must exist and be larger than the array.

        :param numpy.ndarray array: the array to write out
        :param int x_off: the x offset to begin writing out from
        :param int y_off: the y offset to begin writing out from

        :rtype: None
        """
        if not self.map_exists(self.file_name):
            raise IOError("File {} does not exist for writing.".format(self.file_name))
        x, y = self.get_x_y()
        if array.shape[1] > x or array.shape[0] > y:
            raise ValueError(
                "Array of size {}, {} is larger than map of size {}, {}.".format(array.shape[0], array.shape[1], x, y)
            )
        ds = gdal.Open(self.file_name, gdal.GA_Update)
        if not ds:  # pragma: no cover
            raise IOError("Could not open tif file {}.".format(self.file_name))
        if self.band_number is None:
            self.band_number = 1
        ds.GetRasterBand(self.band_number).WriteArray(array, x_off, y_off)
        ds.FlushCache()
        ds = None

    def create(self, file, bands=1, datatype=gdal.GDT_Byte, geotransform=None, projection=None):
        """
        Create the file output and writes the data to the output.

        :param str file: the output file to create
        :param int bands: optionally provide a number of bands to create
        :param gdal.GDT_Byte datatype: the databae of the output
        :param tuple geotransform: optionally provide a geotransform to set for the raster - defaults to (0, 1, 0, 0,
        0, -1)
        :param string projection: optionally provide a projection to set for the raster, in WKT format
        """
        if self.data is None:
            raise ValueError("Data is None for writing to file.")
        if geotransform is None:
            geotransform = (0, 1, 0, 0, 0, -1)
        if self.map_exists(file):
            raise IOError("File already exists at {}.".format(file))
        check_parent(self.file_name)
        output_raster = gdal.GetDriverByName("GTiff").Create(
            self.file_name, self.data.shape[1], self.data.shape[0], bands, datatype
        )
        if not output_raster:  # pragma: no cover
            raise IOError("Could not create tif file at {}.".format(self.file_name))
        output_raster.SetGeoTransform(geotransform)
        if projection:
            output_raster.SetProjection(projection)
        out_band = output_raster.GetRasterBand(1)
        out_band.WriteArray(self.data)
        out_band.FlushCache()
        out_band.SetNoDataValue(-99)
        del output_raster

    def create_copy(self, dst_file, src_file=None):
        """
        Creates a file copying projection and other attributes over from the desired copy

        :param dst_file: existing file to create
        :param src_file: the source file to copy from
        """
        if src_file is None:
            src_file = self.file_name
        if self.map_exists(dst_file):
            raise IOError("File already exists at {}.".format(dst_file))
        src_ds = self.get_dataset(src_file)
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.CreateCopy(dst_file, src_ds, strict=0)
        # Once we're done, close properly the dataset
        dst_ds = None
        src_ds = None

    def set_dimensions(self, file_name=None, x_size=None, y_size=None, x_offset=None, y_offset=None):
        """ Sets the dimensions and file for the Map object

        :param str/pycoalescence.Map file_name: the location of the map object (a csv or tif file). If None, required
        that file_name is already provided.
        :param int x_size: the x dimension
        :param int y_size: the y dimension
        :param int x_offset: the x offset from the north-west corner
        :param int y_offset: the y offset from the north-west corner

        :return: None
        """
        self.dimensions_set = False
        if file_name is not None:
            if isinstance(file_name, Map):
                self.file_name = file_name.file_name
            else:
                self.file_name = file_name
        elif self.file_name is None:
            raise RuntimeError("No file name provided when trying to set dimensions.")
        if (y_size is None and x_size is not None) or (x_size is None and y_size is not None):
            self.logger.warning(
                "Attempt to specify size, but x_size or y_size not provided. Trying to read dimensions from file.",
                RuntimeWarning,
            )
            x_size = None
            y_size = None
        if x_size is None:
            self.x_size, self.y_size, _, _, self.x_res, self.y_res, self.x_ul, self.y_ul = self.read_dimensions()
            self.dimensions_set = True
        else:
            self.x_size = x_size
            self.y_size = y_size
            # Make sure the x_offsets are set if not none, otherwise default to 0
            if x_offset is not None:
                self.x_offset = x_offset
            else:
                self.x_offset = 0
            if y_offset is not None:
                self.y_offset = y_offset
            else:
                self.y_offset = 0
            self.dimensions_set = True

    def set_sample(self, is_sample):
        """Set the is_sample attribute to true if this is a sample mask rather than an offset map

        :param bool is_sample: indicates this is a sample mask rather than offset map
        """
        if is_sample:
            self.zero_offsets()
            self.is_sample = True

    def zero_offsets(self):
        """
        Sets the x and y offsets to 0
        """
        self.x_offset = 0
        self.y_offset = 0

    def check_map(self):
        """Checks that the dimensions for the map have been set and that the map file exists"""
        if not (
                isinstance(self.x_size, NumberTypes)
                and isinstance(self.y_size, NumberTypes)
                and isinstance(self.x_offset, NumberTypes)
                and isinstance(self.y_offset, NumberTypes)
                and isinstance(self.x_res, NumberTypes)
                and isinstance(self.y_res, NumberTypes)
        ):
            raise ValueError(
                "Values not set as numbers in {}: "
                "{}, {} | {}, {} | {}, {}.".format(
                    self.file_name, self.x_size, self.y_size, self.x_offset, self.y_offset, self.x_res, self.y_res
                )
            )
        if not self.dimensions_set:
            raise RuntimeError("Dimensions for map file {} not set.".format(self.file_name))
        check_file_exists(self.file_name)

    def read_dimensions(self):
        """
        Return a list containing the geospatial coordinate system for the file.

        :return: a list containing [0] x, [1] y, [2] upper left x, [3] upper left y, [4] x resolution, [5] y resolution
        """
        ulx, xres, xskew, uly, yskew, yres = self.get_geo_transform()
        x, y = self.get_x_y()
        return [x, y, self.x_offset, self.y_offset, xres, yres, ulx, uly]

    def get_x_y(self):
        """
        Simply returns the x and y dimension of the file.

        :return: the x and y dimensions
        """
        if self.dimensions_set:
            return [self.x_size, self.y_size]
        ds = self.get_dataset()
        x = ds.RasterXSize
        y = ds.RasterYSize
        ds = None
        return [x, y]

    def get_geo_transform(self):
        """
        Gets the geotransform of the file.

        :return: list containing the geotransform parameters
        """
        ds = self.get_dataset()
        ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform()
        ds = None
        return [ulx, xres, xskew, uly, yskew, yres]

    def get_dimensions(self):
        """
        Calls read_dimensions() if dimensions have not been read, or reads stored information.

        :return: a list containing [0] x, [1] y, [2] x offset, [3] y offset, [4] x resolution, [5] y resolution,
                 [6] upper left x, [7] upper left y
        """
        if self.x_size == 0 and self.y_size == 0:
            return self.read_dimensions()
        else:
            return [
                self.x_size,
                self.y_size,
                self.x_offset,
                self.y_offset,
                self.x_res,
                self.y_res,
                self.x_ul,
                self.y_ul,
            ]

    def get_projection(self):
        """
        Gets the projection of the map.

        :return: the projection object of the map in WKT format

        :rtype: str
        """
        ds = self.get_dataset()
        sr = ds.GetProjection()
        ds = None
        return sr

    def get_band_number(self):
        """
        Gets the number of raster bands in the file.

        :rtype: int
        :return: the number of bands in the raster
        """
        ds = self.get_dataset()
        band_number = ds.RasterCount
        ds = None
        return band_number

    def get_cached_subset(self, x_offset, y_offset, x_size, y_size):
        """
        Gets a subset of the map file, BUT rounds all numbers to integers to save RAM and keeps the entire array in
        memory to speed up fetches.

        :param int x_offset: the x offset from the top left corner of the map
        :param int y_offset: the y offset from the top left corner of the map
        :param int x_size: the x size of the subset to obtain
        :param int y_size: the y size of the subset to obtain

        :return: a numpy array containing the subsetted data
        """
        if self.data is None:
            self.open()
        return self.data[y_offset: (y_offset + y_size), x_offset: (x_offset + x_size)]

    def get_subset(self, x_offset, y_offset, x_size, y_size, no_data_value=None):
        """
        Gets a subset of the map file

        :param int x_offset: the x offset from the top left corner of the map
        :param int y_offset: the y offset from the top left corner of the map
        :param int x_size: the x size of the subset to obtain
        :param int y_size: the y size of the subset to obtain
        :param float/int no_data_value: optionally provide a value to replace all no data values with.

        :return: a numpy array containing the subsetted data
        """
        ds = self.get_dataset()
        x, y = self.get_x_y()
        if not 0 <= x_size + x_offset <= x or not 0 <= y_size + y_offset <= y or x_offset < 0 or y_offset < 0:
            raise ValueError(
                "Requested x, y subset of [{}:{}, {}:{}]"
                " not within array of dimensions ({}, {})".format(
                    x_offset, x_offset + x_size, y_offset, y_offset + y_size, x, y
                )
            )
        to_return = np.array(ds.GetRasterBand(1).ReadAsArray(x_offset, y_offset, x_size, y_size), dtype=np.float)
        ds = None
        if no_data_value is not None:
            to_return[to_return == self.get_no_data()] = no_data_value
        return to_return

    def convert_lat_long(self, lat, long):
        """
        Converts the input latitude and longitude to x, y coordinates on the Map

        :param lat: the latitude to obtain the y coordinate of
        :param long: the longitude to obtain the x coordinate of

        :raises IndexError: if the provided coordinates are outside the Map object.

        :return: [x, y] coordinates on the Map
        """
        _, _, _, _, pixel_width, pixel_height, x_origin, y_origin = self.get_dimensions()
        x = int((long - x_origin) / pixel_width)
        y = int((y_origin - lat) / (-pixel_height))
        return [x, y]

    def calculate_scale(self, file_scaled):
        """
        Calculates the scale of map object from the supplied file_scaled.

        :param str/Map file_scaled: the path to the file to calculate the scale.

        :return: the scale (of the x dimension)
        """
        if isinstance(file_scaled, str):
            scaled = Map()
            scaled.set_dimensions(file_scaled)
        elif isinstance(file_scaled, Map):
            scaled = file_scaled
        else:
            raise ValueError("supplied argument is not a string or Map type: {}".format(file_scaled))
        src = np.array(self.read_dimensions())
        dst = np.array(scaled.read_dimensions())
        # Check that each of the dimensions matches
        out = dst[4:6] / src[4:6]
        if out[0] != out[1]:
            self.logger.info("Inequal scaling of x and y dimensions. Check map files.")
        return out[0]

    def calculate_offset(self, file_offset):
        """
        Calculates the offset of the map object from the supplied file_offset.

        The self map should be the smaller

        :param str/Map file_offset: the path to the file to calculate the offset.
            Can also be a Map object with the filename contained.

        :raises TypeError: if the spatial reference systems of the two files do not match

        :return: the offset x and y (at the resolution of the file_home) in integers
        """
        if isinstance(file_offset, str):
            offset = Map()
            offset.set_dimensions(file_offset)
        elif isinstance(file_offset, Map):
            offset = file_offset
        else:
            raise TypeError("file_offset type must be Map or str. Type provided: " + str(type(file_offset)))
        try:
            if offset.get_projection() != self.get_projection():
                self.logger.error(
                    "Projection of {} does not match projection of {}.\n".format(self.file_name, offset.file_name)
                )
                self.logger.error("{} = {}.\n".format(self.file_name, self.get_projection()))
                self.logger.error("{} = {}.\n".format(self.file_name, offset.get_projection()))
                raise TypeError("Projections and spatial reference systems of two maps do not match.")
        except IOError:
            pass
        try:
            src = np.array(self.read_dimensions())
        except IOError:  # pragma: no cover
            src = np.array(self.get_dimensions())
        try:
            off = np.array(offset.read_dimensions())
        except IOError:
            off = np.array(offset.get_dimensions())
        diff = [int(round(x, 0)) for x in (src[6:] - off[6:]) / src[4:6]]
        return diff

    def get_extent(self):
        """
        Gets the min and max x, and min and max y values, including accounting for skew
        :return: list of the x min, x max, y min, y max values.
        :rtype: list
        """
        x_up, x_res, x_skew, y_up, y_skew, y_res = self.get_geo_transform()
        x_dim, y_dim = self.get_x_y()

        ul_x = x_up + 0 * x_res + 0 * x_skew
        ul_y = y_up + 0 * y_skew + 0 * y_res

        ll_x = x_up + 0 * x_res + y_dim * x_skew
        ll_y = y_up + 0 * y_skew + y_dim * y_res

        lr_x = x_up + x_dim * x_res + y_dim * x_skew
        lr_y = y_up + x_dim * y_skew + y_dim * y_res

        ur_x = x_up + x_dim * x_res + 0 * x_skew
        ur_y = y_up + x_dim * y_skew + 0 * y_res
        return [min(ul_x, ll_x), max(lr_x, ur_x), min(ll_y, lr_y), max(ul_y, ur_y)]

    def is_within(self, outside_map):
        """
        Checks if the object is within the provided Map object.

        .. note:: Uses the extents of the raster file for checking location, ignoring any offsetting

        :type outside_map: Map
        :param outside_map: the Map object to check if this class is within

        :return: true if this Map is entirely within the supplied Map
        :rtype: bool
        """
        if not isinstance(outside_map, Map):
            raise TypeError("Supplied object must be of Map class.")
        outer_x_min, outer_x_max, outer_y_min, outer_y_max = outside_map.get_extent()
        inner_x_min, inner_x_max, inner_y_min, inner_y_max = self.get_extent()
        smaller_list = [outer_x_min, outer_y_min, inner_x_max, inner_y_max]
        larger_list = [inner_x_min, inner_y_min, outer_x_max, outer_y_max]
        for i, smaller in enumerate(smaller_list):
            if smaller > larger_list[i]:
                if not isclose(smaller, larger_list[i], rel_tol=1e-5):
                    return False
        return True

    def has_equal_dimensions(self, equal_map):
        """
        Checks if the supplied Map has equal dimensions to this Map.

        .. note:: Dimension matching uses an absolute value (0.0001) for latitude/longitude, and relative value for
                  pixel resolution. The map sizes must fit perfectly.


        :type equal_map: Map
        :param equal_map: the Map object to check if dimensions match

        :return: true if the dimensions match, false otherwise
        :rtype: bool
        """
        if not isinstance(equal_map, Map):
            raise TypeError("Supplied object must be of Map class.")
        this_dims = self.get_dimensions()
        other_dims = equal_map.get_dimensions()
        for i, size in enumerate(this_dims[0:2]):
            if other_dims[i] != size:
                return False
        for i, coordinate in enumerate(this_dims[2:4]):
            if not isclose(other_dims[i + 2], coordinate, abs_tol=0.0001):  # pragma: no cover
                return False
        for i, dimension in enumerate(this_dims[4:]):
            if not isclose(other_dims[i + 4], dimension, rel_tol=1e-4):
                return False
        return True

    def rasterise(
            self,
            shape_file,
            raster_file=None,
            x_res=None,
            y_res=None,
            output_srs=None,
            geo_transform=None,
            field=None,
            burn_val=None,
            data_type=default_val,
            attribute_filter=None,
            x_buffer=None,
            y_buffer=None,
            extent=None,
            **kwargs
    ):
        """
        Rasterises the provided shape file to produce the output raster.

        If x_res or y_res are not provided, self.x_res and self.y_res will be used.

        If a field is provided, the value in that field will become the value in the raster.

        If a geo_transform is provided, it overrides the x_res, y_res, x_buffer and y_buffer.

        :param str/os.path shape_file: path to the .shp vector file to rasterise, or an ogr.DataSource object contain
        the shape file
        :param str/os.path raster_file: path to the output raster file (should not already exist)
        :param int/float x_res: the x resolution of the output raster
        :param int/float y_res: the y resolution of the output raster
        :param str/osr.SpatialReference output_srs: optionally define the output projection of the raster file
        :param list/tuple geo_transform: optionally define the geotransform of the raster file (cannot use resolution or
                                         buffer arguments with this option)
        :param str field: the field to set as raster values
        :param list/int burn_val: the r,g,b value to use if there is no field for the location
        :param int data_type: the gdal type for output data
        :param str attribute_filter: optionally provide a filter to extract features by, of the form "field=fieldval"
        :param int/float x_buffer: number of extra pixels to include at left and right sides
        :param int/float y_buffer: number of extra pixels to include at top and bottom
        :param list extent: list containing the new extent, provided as [ulx, lrx, uly, lry] (output from get_extent())
        :param kwargs: additional options to provide to gdal.RasterizeLayer

        :raises IOError: if the shape file does not exist
        :raises IOError: if the output raster already exists
        :raises ValueError: if the provided shape_file is not a .shp file
        :raises RuntimeError: if gdal throws an error during rasterisation

        :rtype: None
        """
        if x_buffer is None:
            if extent is None:
                if geo_transform is None:
                    x_buffer = 1
                else:
                    x_buffer = 0.5
            else:
                x_buffer = 0

        if y_buffer is None:
            if extent is None:
                if geo_transform is None:
                    y_buffer = 1
                else:
                    y_buffer = 0.5
            else:
                y_buffer = 0
        if burn_val is None:
            burn_val = [1]
        if self.map_exists(raster_file):
            raise IOError("File already exists at {}".format(self.file_name))
        check_parent(self.file_name)
        if x_res is not None and y_res is not None:
            self.x_res = x_res
            self.y_res = y_res
            if geo_transform:
                raise ValueError("Cannot provide both an x,y resolution and a geotransform.")
        if geo_transform is None and (self.x_res is None or self.y_res is None or self.x_res == 0 or self.y_res == 0):
            raise ValueError("Must provide both an x and y resolution, or a geo-transform.")
        if geo_transform is not None:
            self.x_res = geo_transform[1]
            self.y_res = -geo_transform[5]
        if not isinstance(shape_file, ogr.DataSource):
            if not os.path.exists(shape_file):
                raise IOError("Shape file does not exist at {}".format(shape_file))
            if not shape_file.endswith(".shp") and not shape_file.endswith("gpkg"):
                raise ValueError("Provided shape file is not .shp file: {}".format(shape_file))
            orig_data_src = ogr.Open(shape_file)
        else:
            orig_data_src = shape_file
        if not isinstance(output_srs, osr.SpatialReference):
            if output_srs:  # pragma: no cover
                output_srs = osr.SpatialReference(wkt=output_srs)
        if isinstance(burn_val, int) or isinstance(burn_val, float):
            burn_val = [burn_val]

        # Make a copy of the layer's data source because we'll need to
        # modify its attributes table
        source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_src, "")
        source_layer = source_ds.GetLayer(0)
        if attribute_filter is not None:
            source_layer.SetAttributeFilter(attribute_filter)
        source_srs = source_layer.GetSpatialRef()
        if extent is not None:
            x_min, x_max, y_min, y_max = extent
        else:
            x_min, x_max, y_min, y_max = source_layer.GetExtent()
        if output_srs and output_srs != source_srs:  # pragma: no cover
            x_min, y_min = convert_coordinates(x_min, y_min, source_srs, output_srs)
            x_max, y_max = convert_coordinates(x_max, y_max, source_srs, output_srs)
        x_dim = int(math.ceil((x_max - x_min) / self.x_res) + (2 * x_buffer))
        y_dim = int(math.ceil((y_max - y_min) / self.y_res) + (2 * y_buffer))
        # Correct for the extent being an inclusive boundary
        if extent is not None:
            x_dim -= 1
            y_dim -= 1
        if "width" in kwargs:
            x_dim = kwargs["width"]
        if "height" in kwargs:
            y_dim = kwargs["height"]
        target_ds = gdal.GetDriverByName("GTiff").Create(self.file_name, x_dim, y_dim, 1, data_type)
        if target_ds is None:  # pragma: no cover
            raise IOError(
                "Could not create raster file at {} with dimensions {}, {} and data type {}".format(
                    self.file_name, x_dim, y_dim, data_type
                )
            )
        if output_srs:  # pragma: no cover
            target_ds.SetProjection(output_srs.ExportToWkt())
        else:
            if source_srs:
                # Make the target raster have the same projection as the source
                target_ds.SetProjection(source_srs.ExportToWkt())
            else:  # pragma: no cover
                # Source has no projection (needs GDAL >= 1.7.0 to work)
                target_ds.SetProjection('LOCAL_CS["arbitrary"]')
        if geo_transform is None:
            geo_transform = (
                x_min - (self.x_res * x_buffer),
                self.x_res,
                0,
                y_max + (self.y_res * y_buffer),
                0,
                -self.y_res,
            )
        target_ds.SetGeoTransform(geo_transform)
        # Generate the keyword arguments to pass to RasterizeLayer
        opts = []
        kw = {}
        if "allTouched" not in kwargs:
            opts.append("allTouched=FALSE")
        for key in kwargs:
            opts.append("{}={}".format(key, kwargs[key]))
        if field is not None and "ATTRIBUTE" not in kwargs:
            opts.append("attribute={}".format(field))
        else:
            kw["burn_values"] = burn_val
        kw["options"] = opts
        err = gdal.RasterizeLayer(target_ds, [1], source_layer, **kw)
        target_ds.FlushCache()
        del target_ds
        if err != 0:  # pragma: no cover
            raise RuntimeError("Error rasterising layer. Gdal error code: {}".format(err))

    def reproject_raster(
            self,
            dest_projection=None,
            source_file=None,
            dest_file=None,
            x_scalar=1.0,
            y_scalar=1.0,
            resample_algorithm=gdal.GRA_NearestNeighbour,
            warp_memory_limit=0.0,
    ):
        """
        Re-writes the file with a new projection.

        .. note:: Writes to an in-memory file which then overwrites the original file, unless dest_file is not None.

        :param str/os.path dest_projection: the destination file projection, can only be None if rescaling
        :param str/os.path source_file: optionally provide a file name to reproject. Defaults to self.file_name
        :param str/os.path dest_file: the destination file to output to (if None, overwrites original file)
        :param float x_scalar: multiplier to change the x resolution by, defaults to 1
        :param float y_scalar: multiplier to change the y resolution by, defaults to 1
        :param gdal.GRA resample_algorithm: should be one of the gdal.GRA algorithms
        :param float warp_memory_limit: optionally provide a memory cache limit (uses default if 0.0)
        """
        if source_file is not None:  # pragma: no cover
            self.file_name = source_file
        if dest_projection is None:
            if x_scalar == 1.0 and y_scalar == 1.0:  # pragma: no cover
                raise ValueError("Destination projection not provided and no re-scaling - no reprojection possible.")
            dest_projection = osr.SpatialReference(wkt=self.get_projection())
        source_ds = self.get_dataset(permissions=gdal.GA_ReadOnly)
        # Create the VRT for obtaining the new geotransform
        tmp_ds = gdal.AutoCreateWarpedVRT(
            source_ds,
            None,  # src_wkt : left to default value --> will use the one from source
            dest_projection.ExportToWkt(),
            resample_algorithm,
            0,
        )
        dst_gt = list(tmp_ds.GetGeoTransform())
        dst_gt[1] = dst_gt[1] * x_scalar
        dst_gt[5] = dst_gt[5] * y_scalar
        tmp_ds.SetGeoTransform(dst_gt)
        data_type = self.get_dtype()
        if dest_file is not None and os.path.exists(dest_file):  # pragma: no cover
            raise IOError("Destination file already exists at {}.".format(dest_file))
        try:
            dest = gdal.Warp(
                "", source_ds, dstSRS=dest_projection, format="VRT",
                xRes=dst_gt[1], yRes=dst_gt[5],
                outputType=data_type, resampleAlg=resample_algorithm, warpMemoryLimit=warp_memory_limit
            )
        except AttributeError as ae:  # pragma: no cover
            dest = None
            raise AttributeError(
                "Cannot find the gdal.Warp functionality - it is possible this function is not "
                "provided by your version of gdal, or that your gdal installation is incomplete:"
                " {}".format(ae)
            )
        dest.FlushCache()
        source_ds = None
        tmp_ds = None
        if dest_file is None:
            if os.path.exists(self.file_name):
                os.remove(self.file_name)
            output_name = self.file_name
        else:
            output_name = dest_file
        dst_ds = gdal.GetDriverByName("GTiff").CreateCopy(output_name, dest)
        dst_ds.FlushCache()
        dst_ds = None
        dest = None

    def translate(self, dest_file, source_file=None, **kwargs):
        """
        Translates the provided source file to the output file, given a set of options to pass to gdal.Translate()

        :param str dest_file: the destination file to create
        :param str source_file: the source file to translate, or None to translate this file
        :param kwargs: additional keywords to pass to gdal.Translate()

        :rtype: None
        """
        if source_file is not None:  # pragma: no cover
            self.file_name = source_file
        if dest_file is None:
            raise ValueError("Must supply a destination file.")
        if os.path.exists(dest_file):
            raise IOError("Destination file already exists at {}.".format(dest_file))
        source_ds = self.get_dataset(permissions=gdal.GA_ReadOnly)
        output_ds = gdal.Translate(destName=dest_file, srcDS=source_ds, **kwargs)
        if output_ds is None:  # pragma: no cover
            raise SystemError("Could not create file at {} using translation options of {}.".format(dest_file, kwargs))
        output_ds.FlushCache()
        output_ds = None
        source_ds = None

    def plot(self):  # pragma: no cover
        """
        Returns a matplotlib.pyplot.figure object containing an image of the fragmented landscape (with axes removed).

        Requires that the fragmented landscape has been created already using :meth:`~create`.

        :return: figure object containing the fragmented landscape.
        :rtype: matplotlib.pyplot.figure
        """
        fig = plt.figure()
        opened_here = False
        if self.data is None:
            opened_here = True
            self.open()
        fig.figimage(self.data, cmap="Greys_r", resize=True)
        if opened_here:
            self.data = None
        return fig
