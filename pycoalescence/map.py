"""
Contains the Map class as part of the PyCoalescence Project.

Operations involve simulating dispersal kernels on maps, detecting map file dimensions and obtaining offsets between
maps.
"""
import copy
import logging
import warnings
import types
import sys
import os
import math

import numpy as np
try:
	NumberTypes = (types.IntType, types.LongType, types.FloatType, types.ComplexType)
except AttributeError:
	# No support for complex numbers compile
	NumberTypes = (int, float)

try:
	from osgeo import gdal
except ImportError as ie:
	try:
		import gdal
	except ImportError:
		gdal = None
		warnings.warn("Problem importing  (gdal) modules. " + str(ie))

necsim_import_success = False
import_warnings = []
try:
	# Python 2
	try:
		from build import Dispersal
	except ImportError as ime:
		import_warnings.append(ime)
		from .build import Dispersal
	DispersalError = Dispersal.DispersalError
	necsim_import_success = True
except (AttributeError, ImportError) as ie:
	logging.warning(
		"Could not import dispersal shared objects. Check compilation has been successfully completed under "
		"same python version.")
	logging.warning(str(ie))
	for each in import_warnings:
		logging.warning(each)
	necsim_import_success = False


	class DispersalError(Exception):
		pass

try:
	try:
		import sqlite3
	except ImportError:
		# Python 3 compatibility
		import sqlite as sqlite3
except ImportError as ie:
	sqlite3 = None
	warnings.warn("Problem importing sqlite module " + str(ie))

from .system_operations import check_file_exists, create_logger, write_to_log, check_parent


class Map(object):
	"""
	A class for the map object, containing the file name and the variables associated with this map object.

	The internal array of the tif file is stored in self.data, and band 1 of the file can be opened by using
	open()

	:ivar data: if the map file has been opened, contains the full tif data as a numpy array.
	"""

	def __init__(self, file=None, is_sample=None, logging_level=logging.WARNING, dispersal_db=None):
		"""
		Constructor for the Map class, optionally setting the sample map, the logging level and the dispersal database
		location (if a dispersal simulation has already been run).

		:param file: sets the filename for reading tif files.
		:param is_sample: sets the sample mask to true, if it is a sampled file
		:param logging_level: the level of logging to output during dispersal simulations
		:param dispersal_db: path to a complete dispersal simulation database. Can also be a Map object containing the
		completed simulation
		"""
		self._db_conn = None
		self.data = None
		self.file_name = file
		self.band_number = None
		self.x_size = 0
		self.y_size = 0
		self.x_offset = 0
		self.y_offset = 0
		self.x_res = 0
		self.y_res = 0
		self.dimensions_set = False
		self.is_sample = is_sample
		self.logging_level = logging_level
		self.logger = logging.Logger("maplogger")
		self._create_logger()
		# The dispersal simulation data
		if isinstance(dispersal_db, Map):
			self.dispersal_database = dispersal_db.dispersal_database
		else:
			self.dispersal_database = dispersal_db

	def __del__(self):
		"""
		Overriding the destructor for proper destruction of the logger object
		"""
		if hasattr(self, "logger"):
			for handler in self.logger.handlers:
				handler.close()
				self.logger.removeHandler(handler)

	def __deepcopy__(self, memo):
		"""
		Overriding the default deep copy operator to ignore copying the logger object
		:param memo: the memorised key values
		:return: the copy of the Map object
		"""
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result
		for k, v in self.__dict__.items():
			if k != "logger":
				setattr(result, k, copy.deepcopy(v, memo))
		return result

	def open(self, file=None, band_no=1):
		"""
		Reads the raster file from memory into the data object.
		This allows direct access to the internal numpy array using the data object.

		:param str file: path to file to open (or None to use self.file_name
		:param int band_no: the band number to read from

		:rtype: None
		"""
		if file:
			self.file_name = file
		if self.file_name is None:
			raise ValueError("Cannot open file as it is {}".format(self.file_name))
		if not os.path.exists(self.file_name):
			raise IOError("File {} does not exist for reading.".format(self.file_name))
		ds = gdal.Open(self.file_name)
		self.band_number = band_no
		self.data = np.array(ds.GetRasterBand(self.band_number).ReadAsArray(),
							 dtype=np.float)
		ds = None

	def write(self, file=None, band_no=None):
		"""
		Writes the array in self.data to the output array.
		The output file must exist, and the array will be overridden in the band.
		Intended for writing changes to the same file the data was read from.

		:param file: the path to the file to write to
		:param band_no: the band number to write into

		:rtype None
		"""
		if file:
			self.file_name = file
		if band_no:
			self.band_number = band_no
		if self.file_name is None:
			raise ValueError("Cannot open file as it is {}".format(self.file_name))
		if not os.path.exists(self.file_name):
			raise IOError("File {} does not exist for writing.".format(self.file_name))
		ds = gdal.Open(self.file_name, gdal.GA_Update)
		if not ds:
			raise IOError("Could not open tif file {}.".format(self.file_name))
		if self.data is None:
			raise ValueError("Cannot output None to tif file.")
		ds.GetRasterBand(self.band_number).WriteArray(self.data, 0, 0)
		ds.FlushCache()
		ds = None

	def create(self, file):
		"""
		Create the file output and writes the grid to the output.
		:param file: the output file to create
		"""
		#TODO unittests for this
		if self.data is None:
			raise ValueError("Data is None for writing to file.")
		geotransform = (0, 1, 0, 0, 0, -1)
		if os.path.exists(file):
			raise IOError("File already exists at {}.".format(file))
		self.file_name = file
		check_parent(self.file_name)
		output_raster = gdal.GetDriverByName('GTiff').Create(self.file_name,
															 self.data.shape[0], self.data.shape[1], 1,
															 gdal.GDT_Byte)
		if not output_raster:
			raise IOError("Could not create tif file at {}.".format(self.file_name))
		output_raster.SetGeoTransform(geotransform)
		out_band = output_raster.GetRasterBand(1)
		out_band.WriteArray(self.data)
		out_band.FlushCache()
		out_band.SetNoDataValue(-99)
		del output_raster

	def set_dimensions(self, file_name=None, x_size=None, y_size=None, x_offset=None, y_offset=None):
		""" Sets the dimensions and file for the Map object

		:param str file_name: the location of the map object (a csv or tif file). If None, required that file_name is already provided.
		:param int x_size: the x dimension
		:param int y_size: the y dimension
		:param int x_offset: the x offset from the north-west corner
		:param int y_offset: the y offset from the north-west corner

		:return: None
		"""
		if file_name is not None:
			self.file_name = file_name
		elif self.file_name is None:
			raise RuntimeError("No file name provided when trying to set dimensions.")
		if (y_size is None and x_size is not None) or (x_size is None and y_size is not None):
			self.logger.warning(
				"Attempt to specify size, but x_size or y_size not provided. Trying to read dimensions from file.",
				RuntimeWarning)
			x_size = None
			y_size = None
		if x_size is None:
			self.x_size, self.y_size, self.x_offset, self.y_offset, self.x_res, self.y_res = self.read_dimensions()
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
			self.zero_offset()
			self.is_sample = True

	def zero_offsets(self):
		"""
		Sets the x and y offsets to 0
		"""
		self.x_offset = 0
		self.y_offset = 0

	def check_map(self):
		"""Checks that the dimensions for the map have been set and that the map file exists"""
		if not (isinstance(self.x_size, NumberTypes) and isinstance(self.y_size, NumberTypes) and
					isinstance(self.x_offset, NumberTypes) and isinstance(self.y_offset, NumberTypes) and
					isinstance(self.x_res, NumberTypes) and isinstance(self.y_res, NumberTypes)):
			raise ValueError(
				"values not set as numbers in " + self.file_name + ": " + str(self.x_size) + ", " + str(self.y_size) +
				" | " + str(self.x_offset) + ", " + str(self.y_offset) +
				" | " + str(self.x_res) + ", " + str(self.y_res))
		if not self.dimensions_set:
			err = "Dimensions for map file " + str(self.file_name) + " not set."
			raise RuntimeError(err)
		check_file_exists(self.file_name)

	def read_dimensions(self):
		"""
		Return a list containing the geospatial coordinate system for the file.

		:return: a list containing [0] x, [1] y, [2] upper left x, [3] upper left y, [4] x resolution, [5] y resolution
		"""
		if gdal is None:
			raise ImportError("Gdal module not imported correctly: cannot read tif files")
		if ".tif" not in self.file_name:
			raise IOError("tif file not detected - dimensions cannot be read: " + self.file_name)
		if not os.path.exists(self.file_name):
			raise IOError(
				"File " + str(self.file_name) + " does not exist or is not accessible. Check read/write access.")
		ds = gdal.Open(self.file_name)
		x = ds.RasterXSize
		y = ds.RasterYSize
		ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform()
		ds = None
		return [x, y, ulx, uly, xres, yres]

	def get_dimensions(self):
		"""
		Calls read_dimensions() if dimensions have not been read, or reads stored information.

		:return: a list containing [0] x, [1] y, [2] upper left x, [3] upper left y, [4] x resolution, [5] y resolution
		.. note:: the returned list will contain the x and y offset values instead of the ulx and uly values if the
				  dimensions have already been set (i.e. self.x_size != 0 and self.y_size != 0)
		"""
		if self.x_size == 0 and self.y_size == 0:
			return self.read_dimensions()
		else:
			return [self.x_size, self.y_size, self.x_offset, self.y_offset, self.x_res, self.y_res]

	def get_cached_subset(self, x_offset, y_offset, x_size, y_size):
		"""
		Gets a subset of the map file, BUT rounds all numbers to integers to save RAM and keeps the entire array in
		memory to speed up fetches.

		:param x_offset: the x offset from the top left corner of the map
		:param y_offset: the y offset from the top left corner of the map
		:param x_size: the x size of the subset to obtain
		:param y_size: the y size of the subset to obtain
		:return: a numpy array containing the subsetted data
		"""
		if gdal is None:
			raise ImportError("Gdal module not imported correctly: cannot read tif files")
		if ".tif" not in self.file_name:
			raise IOError("tif file not detected - dimensions cannot be read: " + self.file_name)
		if not os.path.exists(self.file_name):
			raise IOError(
				"File " + str(self.file_name) + " does not exist or is not accessible. Check read/write access.")
		if self.data is None:
			self.open()
		return self.data[y_offset:(y_offset + y_size), x_offset:(x_offset + x_size)]

	def get_subset(self, x_offset, y_offset, x_size, y_size):
		"""
		Gets a subset of the map file

		:param x_offset: the x offset from the top left corner of the map
		:param y_offset: the y offset from the top left corner of the map
		:param x_size: the x size of the subset to obtain
		:param y_size: the y size of the subset to obtain
		:return: a numpy array containing the subsetted data
		"""
		if gdal is None:
			raise ImportError("Gdal module not imported correctly: cannot read tif files")
		if ".tif" not in self.file_name:
			raise IOError("tif file not detected - dimensions cannot be read: " + self.file_name)
		if not os.path.exists(self.file_name):
			raise IOError(
				"File " + str(self.file_name) + " does not exist or is not accessible. Check read/write access.")
		ds = gdal.Open(self.file_name)
		to_return = np.array(ds.GetRasterBand(1).ReadAsArray(x_offset, y_offset, x_size, y_size))
		ds = None
		return to_return

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
			raise ValueError("supplied argument is not a string or Map type: " + str(file_scaled))
		src = np.array(self.read_dimensions())
		dst = np.array(scaled.read_dimensions())
		# Check that each of the dimensions matches
		out = dst[4:] / src[4:]
		if out[0] != out[1]:
			warnings.warn('Inequal scaling of x and y dimensions. Check map files.')
		return out[0]

	def calculate_offset(self, file_offset):
		"""
		Calculates the offset of the map object from the supplied file_offset.

		:param str/Map file_offset: the path to the file to calculate the offset.
			Can also be a Map object with the filename contained.

		:return: the offset x and y (at the resolution of the file_home) in integers
		"""
		if isinstance(file_offset, str):
			offset = Map()
			offset.set_dimensions(file_offset)
		elif isinstance(file_offset, Map):
			offset = file_offset
		else:
			raise ValueError("file_offset type must be Map or str. Type provided: " + str(type(file_offset)))
		try:
			src = np.array(self.read_dimensions())
		except IOError:
			src = np.array(self.get_dimensions())
		try:
			off = np.array(offset.read_dimensions())
		except IOError:
			off = np.array(offset.get_dimensions())
		diff = [int(round(x, 0)) for x in (src[2:4] - off[2:4]) / src[4:]]
		return diff

	def get_x_y(self):
		"""
		Simply returns the x and y dimension of the file.

		:return: the x and y dimensions
		"""
		if self.dimensions_set:
			return [self.x_size, self.y_size]
		return self.read_dimensions()[:2]

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

	def _open_database_connection(self, database=None):
		"""
		Opens the connection to the database, raising the appropriate errors if the database does not exist
		Should have a matching call to _close_database_connection() for safely destroying the connection to the database
		file.
		"""
		if database is not None:
			if self.dispersal_database is not None:
				self._close_database_connection()
			self.dispersal_database = database
		if self.dispersal_database is None:
			raise ValueError("Dispersal database is not set, run test_average_dispersal() first or set dispersal_db.")
		if not os.path.exists(self.dispersal_database):
			raise IOError("Dispersal database does not exist: " + self.dispersal_database)
		# Open the SQLite connection
		try:
			self._db_conn = sqlite3.connect(self.dispersal_database)
		except sqlite3.OperationalError as e:
			self._db_conn = None
			raise IOError("Error opening SQLite database: " + str(e))

	def _close_database_connection(self):
		"""
		Safely closes the database connection
		"""
		if self._db_conn is not None:
			try:
				self._db_conn.close()
				self._db_conn = None
			except sqlite3.OperationalError as e:
				self._db_conn = None
				raise IOError("Could not close database: " + str(e))

	def _check_table_exists(self, database=None, table_name = "DISPERSAL_DISTANCES"):
		"""
		Checks that the dispersal distances table exits, and returns true/false.

		:param database: the database to open
		:return: true if the DISPERSAL_DISTANCES table exists in the output database
		:rtype bool
		"""
		self._open_database_connection(database)
		existence = self._db_conn.cursor().execute("SELECT name FROM sqlite_master WHERE type='table' AND"
												   " name='{}';".format(table_name)).fetchone() is not None
		self._close_database_connection()
		return existence

	def _setup_dispersal(self, map_file=None):
		"""
		Checks that the map file makes sense, and the map file exists.

		:param map_file:
		:return:
		"""
		if map_file is None:
			if self.file_name is None:
				raise ValueError("No map file set and none supplied to function.")
			else:
				self.file_name = map_file
		else:
			self.file_name = map_file
		# Now calculate dimensions if the map file is not null
		if self.file_name != "null":
			self.set_dimensions()
		elif not self.dimensions_set:
			raise ValueError("Null map dimensions must be set manually before attemting to simulate dispersal.")
		# Check the map file exists and dimensions are correct
		self.check_map()

	def test_mean_distance_travelled(self, number_repeats, number_steps, output_database="output.db", map_file=None,
									 seed=1, dispersal_method="normal", landscape_type="tiled", sigma=1, tau=1,
									 m_prob=0.0, cutoff=100):
		"""
		Tests the dispersal kernel on the provided map, producing a database containing the average distance travelled
		after number_steps have been moved.

		.. note::

				mean distance travelled with number_steps=1 should be equivalent to running
				:func:`~test_mean_dispersal`

		:param int number_repeats: the number of times to iterate on the map
		:param int number_steps: the number of steps to take each time before recording the distance travelled
		:param str output_database: the path to the output database
		:param str map_file: the path to the map file to iterate on
		:param int seed: the random seed
		:param str dispersal_method: the dispersal method to use ("normal", "fat-tailed" or "norm-uniform")
		:param str landscape_type: the landscape type to use ("infinite", "tiled" or "closed")
		:param float sigma: the sigma value to use for normal and norm-uniform dispersal
		:param float tau: the tau value to use for fat-tailed dispersal
		:param float m_prob: the m_prob to use for norm-uniform dispersal
		:param float cutoff: the cutoff value to use for norm-uniform dispersal
		:return:
		"""
		self._setup_dispersal(map_file=map_file)
		if output_database == "output.db" and self.file_name is not None:
			output_database = self.file_name
		# Delete the file if it exists, and recursively create the folder if it doesn't
		check_parent(output_database)
		if necsim_import_success:
			Dispersal.set_logger(self.logger)
			Dispersal.set_log_function(write_to_log)
			Dispersal.test_mean_distance_travelled(output_database, self.file_name, dispersal_method, landscape_type,
												   sigma, tau, m_prob, cutoff, number_repeats, number_steps, seed,
												   self.x_size, self.y_size)
			self.dispersal_database = output_database
		else:
			raise ImportError("Successful c++ module import required for testing dispersal functions.")

	def test_mean_dispersal(self, number_repeats, output_database="output.db", map_file=None, seed=1,
							dispersal_method="normal", landscape_type="tiled", sigma=1, tau=1, m_prob=0.0, cutoff=100,
							sequential=False):
		"""
		Tests the dispersal kernel on the provided map, producing a database containing each dispersal distance for
		analysis purposes.

		.. note:: should be equivalent to :func:`~test_mean_distance_travelled` with number_steps = 1

		:param int number_repeats: the number of times to iterate on the map
		:param str output_database: the path to the output database
		:param str map_file: the path to the map file to iterate on
		:param int seed: the random seed
		:param str dispersal_method: the dispersal method to use ("normal", "fat-tailed" or "norm-uniform")
		:param str landscape_type: the landscape type to use ("infinite", "tiled" or "closed")
		:param float sigma: the sigma value to use for normal and norm-uniform dispersal
		:param float tau: the tau value to use for fat-tailed dispersal
		:param float m_prob: the m_prob to use for norm-uniform dispersal
		:param float cutoff: the cutoff value to use for norm-uniform dispersal
		:param bool sequential: if true, end locations of one dispersal event are used as the start for the next. Otherwise,
		a new random cell is chosen
		"""
		self._setup_dispersal(map_file=map_file)
		if output_database == "output.db" and self.file_name is not None:
			output_database = self.file_name
		# Delete the file if it exists, and recursively create the folder if it doesn't
		check_parent(output_database)
		if necsim_import_success:
			Dispersal.set_logger(self.logger)
			Dispersal.set_log_function(write_to_log)
			Dispersal.test_mean_dispersal(output_database, self.file_name, dispersal_method, landscape_type, sigma, tau,
										  m_prob, cutoff, number_repeats, seed, self.x_size, self.y_size,
										  int(sequential))
			self.dispersal_database = output_database
		else:
			raise ImportError("Successful c++ module import required for testing dispersal functions.")

	def get_mean_dispersal(self, database=None, parameter_reference = 1):
		"""
		Gets the mean dispersal for the map if test_mean_dispersal has already been run.

		:raises: ValueError if dispersal_database is None and so test_average_dispersal() has not been run
		:raises: IOError if the output database does not exist

		:param str database: the database to open
		:param int parameter_reference: the parameter reference to use (or 1 for default parameter reference).
		:return: mean dispersal from the database
		"""
		if not self._check_table_exists(database=database, table_name="DISPERSAL_DISTANCES"):
			raise IOError("Database {} does not have a DISPERSAL_DISTANCES table".format(self.dispersal_database))
		try:
			self._open_database_connection(database=database)
			cursor = self._db_conn.cursor()
			sql_fetch = cursor.execute("SELECT AVG(distance) FROM DISPERSAL_DISTANCES WHERE parameter_reference = ?",
									   (parameter_reference, )).fetchall()[0][0]
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
		self._close_database_connection()
		return sql_fetch

	def get_mean_distance_travelled(self, database=None, parameter_reference=1):
		"""
		Gets the mean dispersal for the map if test_mean_dispersal has already been run.

		:raises: ValueError if dispersal_database is None and so test_average_dispersal() has not been run
		:raises: IOError if the output database does not exist

		:param str database: the database to open
		:param int parameter_reference: the parameter reference to use (or 1 for default parameter reference).
		:return: mean of dispersal from the database
		"""
		if not self._check_table_exists(database=database, table_name="DISTANCES_TRAVELLED"):
			raise IOError("Database {} does not have a DISTANCES_TRAVELLED table".format(self.dispersal_database))
		try:
			self._open_database_connection(database=database)
			cursor = self._db_conn.cursor()
			sql_fetch = cursor.execute("SELECT AVG(distance) FROM DISTANCES_TRAVELLED WHERE parameter_reference = ?",
									   (parameter_reference, )).fetchall()[0][0]
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
		self._close_database_connection()
		return sql_fetch

	def get_stdev_dispersal(self, database=None, parameter_reference=1):
		"""
		Gets the standard deviation of dispersal for the map if test_mean_dispersal has already been run.

		:raises: ValueError if dispersal_database is None and so test_average_dispersal() has not been run
		:raises: IOError if the output database does not exist

		:param str database: the database to open
		:param int parameter_reference: the parameter reference to use (or 1 for default parameter reference).
		:return: standard deviation of dispersal from the database
		"""
		if not self._check_table_exists(database=database, table_name="DISPERSAL_DISTANCES"):
			raise IOError("Database {} does not have a DISPERSAL_DISTANCES table".format(self.dispersal_database))
		try:
			self._open_database_connection(database=database)
			cursor = self._db_conn.cursor()
			sql_fetch = [x[0] for x in cursor.execute("SELECT distance FROM DISPERSAL_DISTANCES "
													  "WHERE parameter_reference = ?",
													  (parameter_reference, )).fetchall()]
			if len(sql_fetch) == 0:
				raise ValueError("No distances in DISPERSAL_DISTANCES, cannot find standard deviation.")
			stdev_distance = np.std(sql_fetch)
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
		self._close_database_connection()
		return stdev_distance


	def get_stdev_distance_travelled(self, database=None, parameter_reference=1):
		"""
		Gets the standard deviation of the  distance travelled for the map if test_mean_distance_travelled has already
		been run.

		:raises: ValueError if dispersal_database is None and so test_average_dispersal() has not been run
		:raises: IOError if the output database does not exist

		:param str database: the database to open
		:param int parameter_reference: the parameter reference to use (or 1 for default parameter reference).

		:return: standard deviation of dispersal from the database
		"""
		if not self._check_table_exists(database=database, table_name="DISTANCES_TRAVELLED"):
			raise IOError("Database {} does not have a DISTANCES_TRAVELLED table".format(self.dispersal_database))
		try:
			self._open_database_connection(database=database)
			cursor = self._db_conn.cursor()
			sql_fetch = [x[0] for x in cursor.execute("SELECT distance FROM DISTANCES_TRAVELLED"
													  " WHERE parameter_reference = ?",
													  (parameter_reference, )).fetchall()]
			if len(sql_fetch) == 0:
				raise ValueError("No distances in DISTANCES_TRAVELLED, cannot find standard deviation.")
			stdev_distance = np.std(sql_fetch)
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
		self._close_database_connection()
		return stdev_distance

	def get_database_parameters(self):
		"""
		Gets the dispersal simulation parameters from the dispersal_db
		:return: the dispersal simulation parameters
		"""
		self._open_database_connection()
		try:
			cursor = self._db_conn.cursor()
			cursor.execute("SELECT ref, simulation_type, sigma, tau, m_prob, cutoff, dispersal_method, map_file, seed,"
						   " number_steps, number_repeats FROM PARAMETERS")
		except sqlite3.OperationalError as e:
			raise IOError("Could not get dispersal simulation parameters from database: {}".format(e))
		column_names = [member[0] for member in cursor.description]
		main_dict = {}
		for row in cursor.fetchall():
			values = [x for x in row]
			if sys.version_info[0] != 3:
				for i, each in enumerate(values):
					if isinstance(each, unicode):
						values[i] = each.encode('ascii')
			main_dict[values[0]] = dict(zip(column_names[1:], values[1:]))
		# Now convert it into a dictionary
		self._close_database_connection()
		return main_dict
