"""
Contains the Simulation class as part of the pycoalescence package.

Operations involve setting up and running simulations, plus basic tree generation after simulations have been completed.
"""
from __future__ import absolute_import
from __future__ import print_function

import logging
import sys

import copy
import math
import numpy as np
import os
import types

from .map import Map
from .system_operations import execute_log_info, create_logger, write_to_log, check_file_exists
from .future_except import FileNotFoundError, FileExistsError

global sqlite_import, config_success
try:
	if sys.version_info[0] == 3:
		import configparser as ConfigParser
	else:
		import ConfigParser

		ConfigParser.ConfigParser.read_file = ConfigParser.ConfigParser.read
	config_success = True
except ImportError as ie:
	ConfigParser = None
	logging.warning("Could not import ConfigParser. Config options disabled.")
	logging.warning(str(ie))
	config_success = False

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
		logging.warning("Problem importing  (gdal) modules. " + str(ie))

try:
	import sqlite3
	sqlite_import = True
	from .coalescence_tree import CoalescenceTree
except ImportError as ie:
	sqlite_import = False
	CoalescenceTree = None
	sqlite3 = None
	logging.warning("Problem importing sqlite module " + str(ie))

necsim_import_success = False
import_warnings = []
try:
	# Python 2
	try:
		from build import necsimmodule
	except ImportError as ime:
		import_warnings.append(ime)
		from .build import necsimmodule
	NECSimError = necsimmodule.NECSimError
	necsim_import_success = True
except (AttributeError, ImportError) as ie:
	logging.warning("Could not import necsim shared objects. Check compilation has been successfully completed under "
					"same python version.")
	logging.warning(str(ie))
	for each in import_warnings:
		logging.warning(each)
	necsim_import_success = False


	# Create the empty classes if the import fails
	class NECSimError(Exception):
		pass


class Simulation:
	"""
	A class containing routines to set up and run simulations, including detecting map dimensions from tif files.
	"""

	def __init__(self, logging_level=logging.WARNING,
				 log_output=None, **kwargs):
		"""
		Sets up the simulation object, setting the logging object and assigning default variables.

		:param int logging_level: the minimal level of logging to display
		:param string log_output: a file to output log data to. Use None for writing to console.
		:param kwargs: additional keyword arguments to supply to logging.basicConfig()
		"""
		# All the parameters used for the simulation
		self._fine_map_sum_res = None
		self.count_total = None
		self.logging_level = logging_level
		self.logger = logging.Logger("necsimlogger")
		self._create_logger(file=log_output)
		self.output_directory = ""
		self.pause_directory = ""
		self.map_config = ''
		self.full_config_file = ''
		self.is_setup = False
		self.is_setup_param = False
		self.is_setup_map = False
		self.is_setup_complete = False
		self.seed = 0
		self.fine_map = Map()
		self.coarse_map = Map()
		self.sample_map = Map()
		self.coarse_scale = 1
		self.min_speciation_rate = 0
		self.sigma = 2
		self.deme = 1
		self.sample_size = 1
		self.max_time = 100
		self.dispersal_relative_cost = 1  # the relative cost of moving through non-matrix
		self.job_type = 0
		self.min_num_species = 1
		self.pristine_fine_map_file = None
		self.pristine_coarse_map_file = None
		# amount of habitat change that occurs before pristine state (there will be a jump to pristine at the pristine time
		self.habitat_change_rate = 0
		self.time_since_pristine = 1  # The number of generations ago a habitat was pristine
		self.tau = 0
		self.time_config_file = ""
		# the optional parameters specifying the location (i.e. where in the world the simulation is of
		# and the compute node (such as NUS_HPC or LOCAL_MACBOOK)
		self.sim_location = None
		self.sim_compute_node = None
		self.speciation_rates = []
		# parameters for the application of speciation rates
		self.is_setup_speciation = False
		self.speciation_file = ""
		self.record_spatial = False
		self.record_fragments = False
		self.speciation_time_config_file = ""
		self.speciation_sample_file = ""
		self.is_full = True
		self.pristine_fine_list = []
		self.pristine_coarse_list = []
		self.times_list = []  # this is the times for the maps to change (in generations)
		self.rates_list = []
		self.sample_time_list = []  # this is the list of temporal sampling points (in generations)
		# The output database location
		self.output_database = None
		self.dispersal_method = None
		self.m_prob = 0
		self.cutoff = 0
		self.restrict_self = False
		self.infinite_landscape = False
		# The protracted variables
		self.protracted = False
		self.min_speciation_gen = 0.0
		self.max_speciation_gen = 0.0
		# This variable stores whether a new config file has been opened or not
		self.config_open = False
		# Stores our necsim object for running the c++ code
		if necsim_import_success:
			self.necsim = necsimmodule
		# Grid dimensions sizing
		self.grid = Map()
		# Dispersal map data
		self.dispersal_map = Map()
		self.reproduction_map = Map()
		self.fine_map_array = None
		self.sample_map_array = None
		self.fine_map_average = None
		self.is_spatial = True;
		self.uses_spatial_sampling = False

	def __del__(self):
		"""
		Overriding the destructor for proper destruction of the logger object
		"""
		handlers = copy.copy(self.logger.handlers)
		for handler in handlers:
			handler.close()
			self.logger.removeHandler(handler)
		self.necsim = None
		self.logger = None

	def setup_necsim(self):
		"""
		Sets the logging function and the logger object for the necsim object. Enforcing this function is always called
		ensures no seg faults occur.
		"""
		self.necsim.set_logger(self.logger)
		self.necsim.set_log_function(write_to_log)

	def add_pristine_map(self, fine_map, coarse_map, time, rate):
		"""
		Adds an extra map to the list of pristine maps.

		:param fine_map: the pristine fine map file to add
		:param coarse_map: the pristine coarse map file to add
		:param time: the time to add (when the map is accurate)
		:param rate: the rate to add (the rate of habitat change at this time)
		"""
		self.pristine_fine_list.append(fine_map)
		self.pristine_coarse_list.append(coarse_map)
		self.times_list.append(time)
		self.rates_list.append(rate)

	def add_sample_time(self, time):
		"""
		Adds an extra sample time to the list of times.

		This allows for multiple temporal sample points from within the same simulation.

		:param time: the sample time to add
		"""
		if isinstance(time, list):
			[self.add_sample_time(x) for x in time]
		else:
			if len(self.sample_time_list) == 0:
				self.sample_time_list.append(0.0)
			self.sample_time_list.append(time)

	def create_temporal_sampling_config(self, config_file=None):
		"""
		Creates the time-sampling config file

		:param config_file: the config file to output to
		"""
		if config_file is None:
			config_file = os.path.join(self.output_directory,
									   "timeconf_{}_{}.txt".format(str(self.job_type), str(self.seed)))
		if not os.path.exists(os.path.dirname(config_file)):
			self.logger.info(
				'Path {} does not exist for writing output to, creating.'.format(os.path.dirname(config_file)))
			os.makedirs(os.path.dirname(config_file))
		if len(self.sample_time_list) != 0:
			config = ConfigParser.ConfigParser()
			config.add_section("main")
			for i, j in enumerate(sorted(set(self.sample_time_list))):
				config.set("main", "time" + str(i), str(j))
			with open(config_file, "w") as conf:
				config.write(conf)
			self.time_config_file = config_file

	def create_map_config(self, output_file=None):
		"""
		Generates the map config file from reading the spatial structure of each of the provided files.

		:param str output_file: the file to output configuration data to (the map config file)
		"""
		if output_file is None:
			output_file = os.path.join(self.output_directory,
									   "mainconf_{}_{}.txt".format(str(self.job_type), str(self.seed)))
		if not config_success:
			raise ImportError("ConfigParser import was unsuccessful: cannot create config file.")
		if not os.path.exists(os.path.dirname(output_file)):
			self.logger.info(
				'Path {} does not exist for writing output to, creating.'.format(os.path.dirname(output_file)))
			os.makedirs(os.path.dirname(output_file))
		config = ConfigParser.ConfigParser()
		if os.path.exists(output_file) and not self.config_open:
				os.remove(output_file)
		self.config_open = True
		if self.is_setup_map:
			if self.is_spatial:
				config = ConfigParser.ConfigParser()
				config.add_section("sample_grid")
				config.set("sample_grid", "path", self.sample_map.file_name)
				x, y = map(str, self.sample_map.get_x_y())
				config.set("sample_grid", "x", str(x))
				config.set("sample_grid", "y", str(y))
				if self.sample_map.file_name is None:
					config.set("sample_grid", "mask", "null")
				else:
					config.set("sample_grid", "mask", self.sample_map.file_name)
					config.set("sample_grid", "uses_spatial_sampling", str(int(self.uses_spatial_sampling)))
				config.add_section("fine_map")
				config.set("fine_map", "path", self.fine_map.file_name)
				x, y = map(str, self.fine_map.get_x_y())
				config.set("fine_map", "x", str(x))
				config.set("fine_map", "y", str(y))
				config.set("fine_map", "x_off", str(self.fine_map.x_offset))
				config.set("fine_map", "y_off", str(self.fine_map.y_offset))
				config.add_section("coarse_map")
				if self.coarse_map.file_name is not None:
					config.set("coarse_map", "path", self.coarse_map.file_name)
					x, y = map(str, self.coarse_map.get_x_y())
					config.set("coarse_map", "x", str(x))
					config.set("coarse_map", "y", str(y))
					config.set("coarse_map", "x_off", str(self.coarse_map.x_offset))
					config.set("coarse_map", "y_off", str(self.coarse_map.y_offset))
					config.set("coarse_map", "scale", str(self.coarse_scale))
				else:
					config.set("coarse_map", "path", "none")
					config.set("coarse_map", "x", 0)
					config.set("coarse_map", "y", 0)
					config.set("coarse_map", "x_off", 0)
					config.set("coarse_map", "y_off", 0)
					config.set("coarse_map", "scale", 1)
				if len(self.pristine_coarse_list) != 0 and len(self.pristine_fine_list) != 0:
					for i, t in enumerate(self.times_list):
						try:
							tmp_fine = "pristine_fine" + str(i)
							config.add_section(tmp_fine)
							config.set(tmp_fine, "path", self.pristine_fine_list[i])
							config.set(tmp_fine, "number", str(i))
							config.set(tmp_fine, "time", str(t))
							config.set(tmp_fine, "rate", str(self.rates_list[i]))
							tmp_coarse = "pristine_coarse" + str(i)
							config.add_section(tmp_coarse)
							config.set(tmp_coarse, "path", self.pristine_coarse_list[i])
							config.set(tmp_coarse, "number", str(i))
							config.set(tmp_coarse, "time", str(t))
							config.set(tmp_coarse, "rate", str(self.rates_list[i]))
						except IndexError as ie:
							self.logger.warning('Discrepancy between pristine file list, time list or rate list. Check inputs: ' +
										  ie.message)
							break
				if self.grid.file_name == "set":
					config.add_section("grid_map")
					config.set("grid_map", "x", str(self.grid.x_size))
					config.set("grid_map", "y", str(self.grid.y_size))
					config.set("sample_grid", "x_off", str(self.sample_map.x_offset))
					config.set("sample_grid", "y_off", str(self.sample_map.y_offset))
				if self.reproduction_map.file_name not in [None, "none", "null"]:
					config.add_section("reproduction")
					config.set("reproduction", "map", self.reproduction_map.file_name)
				if self.dispersal_method is not None:
					config.add_section("dispersal")
					config.set("dispersal", "method", self.dispersal_method)
					config.set("dispersal", "m_probability", str(self.m_prob))
					config.set("dispersal", "cutoff", str(self.cutoff))
				if self.restrict_self:
					if not config.has_section("dispersal"):
						config.add_section("dispersal")
					config.set("dispersal", "restrict_self", str(int(self.restrict_self)))
				if self.infinite_landscape != "closed":
					if not config.has_section("dispersal"):
						config.add_section("dispersal")
					config.set("dispersal", "infinite_landscape", self.infinite_landscape)
				if self.dispersal_map.file_name not in ["none", None]:
					if not config.has_section("dispersal"):
						config.add_section("dispersal")
					config.set("dispersal", "dispersal_file", self.dispersal_map.file_name)
				with open(output_file, "a") as f:
					config.write(f)
				self.map_config = output_file
		else:
			raise RuntimeError("Cannot generate map config file without setting up map variables")

	def run_simple(self, seed, task, output, alpha, sigma, size):
		"""
		Runs a simple coalescence simulation on a square infinite landscape with the provided parameters.
		This requires a separate compilation of the inf_land version of the coalescence simulator.

		Note that this function returns richness=0 for failure to read from the file. It is assumed that there will
		be at least one species in the simulation.

		Note that the maximum time for this function is set as 10 hours (36000 seconds) and will raise an exception if
		the simulation does not complete in this time).

		:raises RuntimeError: if the simulation didn't complete in time.

		:param seed: the simulation seed
		:param task: the task (for file naming)
		:param output: the output directory
		:param alpha: the speciation rate
		:param sigma: the normal distribution sigma value for dispersal
		:param size: the size of the world (so there will be size^2 individuals simulated)

		:return: the species richness in the simulation
		"""
		self.set_simulation_params(seed=seed, job_type=task, output_directory=output, min_speciation_rate=alpha,
								   sigma=sigma, tau=1, deme=1, sample_size=1.0, max_time=36000,
								   dispersal_relative_cost=1,
								   min_num_species=1, habitat_change_rate=0.0, gen_since_pristine=1,
								   time_config_file="null")
		self.set_map_parameters("null", size, size, "null", size, size, 0, 0, "null", size, size, 0, 0, 1, "null",
								"null")
		self.set_speciation_rates([alpha])
		self.finalise_setup()
		self.run_coalescence()
		# Now read the species richness from the database
		try:
			richness = self.get_richness()
			if richness == 0:
				raise AssertionError("Richness is 0, error in program. This should never be the case for a complete "
									 "sim.")
			return richness
		except IOError:
			raise RuntimeError("Simulation didn't complete in 10 hours (maximum time for run_simple). Try running a "
							   "custom simulation instead.")

	def get_richness(self, reference=1):
		"""
		Calls coal_analyse.get_richness() with the supplied variables.

		Requires successful import of coal_analyse and sqlite3.

		:param speciation_rate: the speciation rate to extract system richness from.
		:param time: the time to extract system richness from

		:return: the species richness.
		"""
		if not sqlite_import:
			raise ImportError("sqlite3 module required for obtaining richness from database files.")
		else:
			db = os.path.join(self.output_directory,
							  "SQL_data/data_" + str(self.job_type) + "_" + str(self.seed) + ".db")
			t = CoalescenceTree()
			t.set_database(db)
			return t.get_richness(reference)

	def get_protracted(self):
		"""
		Gets whether the simulation pointed to by this object is a protracted simulation or not.
		"""
		if self.output_database is None or not os.path.exists(self.output_database):
			return self.protracted
		else:
			t = CoalescenceTree()
			try:
				t.set_database(self.output_database)
			except IOError:
				# Catches errors thrown if the simulation is paused
				pass
			return t.is_protracted()

	def load_config(self, config_file):
		"""
		Loads the config file by reading the lines in order.

		:param str config_file: the config file to read in.
		"""
		# New method using ConfigParser
		if not config_success:
			raise ImportError("Failure to import ConfigParser: cannot load config file")
		else:
			config = ConfigParser.ConfigParser()
			with open(config_file, "wa") as f:
				config.read_file(f)
			self.seed = config.getint("main", "seed")
			self.job_type = config.getint("main", "job_type")
			self.map_config = config.get("main", "map_config")
			self.output_directory = config.get("main", "output_directory")
			self.min_speciation_rate = config.getfloat("main", "min_spec_rate")
			self.sigma = config.getfloat("main", "sigma")
			self.tau = config.getfloat("main", "tau")
			self.deme = config.getint("main", "deme")
			self.sample_size = config.getfloat("main", "sample_size")
			self.max_time = config.getint("main", "max_time")
			self.dispersal_relative_cost = config.getfloat("main", "lambda")
			self.time_config_file = config.get("main", "time_config")
			self.min_num_species = config.getint("main", "min_species")
			self.full_config_file = config_file
			if config.has_section("spec_rate"):
				opts = config.options("spec_rate")
				for each in opts:
					self.speciation_rates.append(config.getfloat("spec_rate", each))

	def create_config(self, output_file=None):
		"""
		Generates the output config files. This version creates the concise version of the config file.

		:param str output_file: the file to generate the config option. Must be a path to a .txt file.
		"""
		if output_file is None:
			output_file = os.path.join(self.output_directory,
									   "mainconf_{}_{}.txt".format(str(self.job_type), str(self.seed)))
		if not config_success:
			raise ImportError("ConfigParser import was unsuccessful: cannot create config file.")
		if not os.path.exists(os.path.dirname(output_file)):
			self.logger.info(
				'Path {} does not exist for writing output to, creating.'.format(os.path.dirname(output_file)))
			os.makedirs(os.path.dirname(output_file))
		config = ConfigParser.ConfigParser()
		if os.path.exists(output_file) and not self.config_open:
			os.remove(output_file)
		self.config_open = True
		if self.is_setup_map and self.is_setup_param:
			# New method using ConfigParser
			config.add_section("main")
			config.set("main", "seed", str(self.seed))
			config.set("main", "job_type", str(self.job_type))
			config.set("main", "output_directory", self.output_directory)
			config.set("main", "min_spec_rate", str(self.min_speciation_rate))
			if self.is_spatial:
				if self.map_config in [None, ""]:
					raise RuntimeError("Cannot create config without map configuration options set.")
				else:
					config.set("main", "map_config", self.map_config)
				config.set("main", "sigma", str(self.sigma))
				config.set("main", "tau", str(self.tau))
				config.set("main", "dispersal_relative_cost", str(self.dispersal_relative_cost))
			config.set("main", "deme", str(self.deme))
			config.set("main", "sample_size", str(self.sample_size))
			config.set("main", "max_time", str(self.max_time))
			config.set("main", "time_config", self.time_config_file)
			config.set("main", "min_species", str(self.min_num_species))
			if self.protracted:
				config.add_section("protracted")
				config.set("protracted", "has_protracted", str(int(self.protracted)))
				config.set("protracted", "min_speciation_gen", str(self.min_speciation_gen))
				config.set("protracted", "max_speciation_gen", str(self.max_speciation_gen))
			if len(self.speciation_rates) != 0:
				config.add_section("spec_rates")
				for i, j in enumerate(set([x for x in self.speciation_rates])):
					spec_rate = "spec_" + str(i)
					config.set("spec_rates", spec_rate, str(j))
			with open(output_file, "a") as config_file:
				config.write(config_file)
			self.full_config_file = output_file
		else:
			raise RuntimeError("Setup has not been completed, cannot create config file")

	# TODO remove this functionality as dual-config file usage is now deprecated (there was absolutely no point to it)
	def set_map_config(self, file):
		"""
		Sets a specific map config and tells the program that full commmand-line parsing is not required.

		:param str file: the file to read map config options from
		"""
		self.map_config = file
		self.is_full = False

	def set_map_files(self, sample_file, fine_file=None, coarse_file=None, pristine_fine_file=None,
					  pristine_coarse_file=None, dispersal_map=None, reproduction_map=None):
		"""
		Sets the map files (or to null, if none specified). It then calls detect_map_dimensions() to correctly read in
		the specified dimensions.

		If sample_file is "null", dimension values will remain at 0.
		If coarse_file is "null", it will default to the size of fine_file with zero offset.
		If the coarse file is "none", it will not be used.
		If the pristine fine or coarse files are "none", they will not be used.

		.. note:: the dispersal map should be of dimensions xy by xy where x, y are the fine map dimensions. Dispersal
				  probabilities should sum to 1 across each row, and each row/column index represents dispersal from the
				  row index to the column index according to index = x+(y*xdim), where x,y are the coordinates of the
				  cell and xdim is the x dimension of the fine map. See the
				  :class:`PatchedLandscape class <pycoalescence.patched_landscape.PatchedLandscape>` for routines for
				  generating these landscapes.

		:param str sample_file: the sample map file. Provide "null" if on samplemask is required
		:param str fine_file: the fine map file. Defaults to "null" if none provided
		:param str coarse_file: the coarse map file. Defaults to "none" if none provided
		:param str pristine_fine_file: the pristine fine map file. Defaults to "none" if none provided
		:param str pristine_coarse_file: the pristine coarse map file. Defaults to "none" if none provided
		:param str dispersal_map: the dispersal map for reading dispersal values. Default to "none" if none provided
		:param str reproduction_map: a map of relative reproduction probabilities, at the scale of the fine map

		:rtype: None

		:return: None
		"""
		if fine_file in [None, "null", "none"]:
			raise ValueError("Fine map file cannot be 'none' or 'null' for automatic parameter detection."
							 "Use set_map_parameters() instead.")
		if coarse_file is None:
			coarse_file = "none"
		if pristine_fine_file is None:
			pristine_fine_file = "none"
		if pristine_coarse_file is None:
			pristine_coarse_file = "none"
		if dispersal_map is None:
			self.dispersal_map.file_name = "none"
		else:
			self.dispersal_map.file_name = dispersal_map
		if reproduction_map is None:
			self.reproduction_map.file_name = "none"
		else:
			self.reproduction_map.file_name = reproduction_map
		self.set_map_parameters(sample_file, 0, 0, fine_file, 0, 0, 0, 0, coarse_file, 0, 0, 0, 0, 0,
								pristine_fine_file, pristine_coarse_file)
		try:
			self.detect_map_dimensions()
		except Exception as e:
			self.is_setup_map = False
			raise e

	def detect_map_dimensions(self):
		"""
		Detects all the map dimensions for the provided files (where possible) and sets the respective values.
		This is intended to be run after set_map_files()

		:raises TypeError: if a dispersal map or reproduction map is specified, we must have a fine map specified, but
		not a coarse map.

		:raises IOError: if one of the required maps does not exist
		
		:raises ValueError: if the dimensions of the dispersal map do not make sense when used with the fine map
		provided

		:return: None
		"""
		self.fine_map.set_dimensions()
		if self.sample_map.file_name == "null":
			self.sample_map.set_dimensions(x_size=self.fine_map.x_size, y_size=self.fine_map.y_size,
										   x_offset=self.fine_map.x_offset, y_offset=self.fine_map.y_offset)
			self.sample_map.x_ul = self.fine_map.x_ul
			self.sample_map.y_ul = self.fine_map.y_ul
		else:
			self.sample_map.set_dimensions()
		x, y = self.fine_map.calculate_offset(self.sample_map)[0:2]
		self.fine_map.x_offset = -x
		self.fine_map.y_offset = -y
		if self.coarse_map.file_name in ["null", "none"]:
			tmpname = copy.deepcopy(self.coarse_map.file_name)
			self.coarse_map = copy.deepcopy(self.fine_map)
			self.coarse_scale = 1
			self.coarse_map.x_offset = 0
			self.coarse_map.y_offset = 0
			self.coarse_map.file_name = tmpname
		else:
			self.coarse_map.set_dimensions()
			self.coarse_map.x_offset = -self.coarse_map.calculate_offset(self.fine_map)[0]
			self.coarse_map.y_offset = -self.coarse_map.calculate_offset(self.fine_map)[1]
			self.coarse_scale = self.fine_map.calculate_scale(self.coarse_map)
		# Now do detection for dispersal map
		if self.dispersal_map.file_name not in {"none", "null", None}:
			self.dispersal_map.set_dimensions()
			if self.dispersal_map.x_size != self.fine_map.x_size * self.fine_map.y_size or \
							self.dispersal_map.y_size != self.fine_map.x_size * self.fine_map.y_size:
				raise ValueError("Dimensions of dispersal map do not match dimensions of fine map. This is currently"
								 " unsupported.")
		if self.reproduction_map.file_name not in {"none", "null", None}:
			self.reproduction_map.set_dimensions()
			if not self.reproduction_map.has_equal_dimensions(self.fine_map):
				# if the sizes match, then proceed with a warning
				if self.reproduction_map.x_size == self.fine_map.x_size and \
					self.reproduction_map.y_size == self.fine_map.y_size:
					self.logger.warning("Coordinates of reproduction map did not match fine map.")
					self.reproduction_map.x_offset = self.fine_map.x_offset
					self.reproduction_map.y_offset = self.fine_map.y_offset
					self.reproduction_map.x_res = self.fine_map.x_res
					self.reproduction_map.y_res = self.fine_map.y_res
				else:
					raise ValueError("Dimensions of the reproduction map do not match the fine map. This is currently "
								     "unsupported.")
		self.check_maps()

	def set_map(self, map_file, x_size=None, y_size=None):
		"""
		Quick function for setting a single map file for both the sample map and fine map, of dimensions x and y.
		Sets the sample file to "null" and coarse file and pristine files to "none".

		:param str map_file: path to the map file
		:param x_size: the x dimension, or None to detect automatically from the ".tif" file
		:param y_size: the y dimension, or None to detect automatically from the ".tif" file
		"""
		if (x_size is None or y_size is None) and (x_size is not None or y_size is not None):
			raise ValueError("Must specify both a map x and y dimension.")
		self.fine_map.set_dimensions(map_file, x_size=x_size, y_size=y_size)
		self.fine_map.zero_offsets()
		self.sample_map.set_dimensions("null", self.fine_map.x_size, self.fine_map.y_size)
		self.sample_map.zero_offsets()
		self.coarse_map.set_dimensions("none", self.fine_map.x_size, self.fine_map.y_size)
		self.coarse_map.zero_offsets()
		self.is_setup_map = True
		self.coarse_scale = 1.0

	def set_map_parameters(self, sample_file, sample_x, sample_y, fine_file, fine_x, fine_y, fine_x_offset,
						   fine_y_offset, coarse_file, coarse_x, coarse_y,
						   coarse_x_offset, coarse_y_offset, coarse_scale, pristine_fine_map, pristine_coarse_map):
		"""

		Set up the map objects with the required parameters. This is required for csv file usage.

		Note that this function is not recommended for tif file usage, as it is much simpler to call set_map_files() and
		which should automatically calculate map offsets, scaling and dimensions.

		:param sample_file: the sample file to use, which should contain a boolean mask of where to sample
		:param sample_x: the x dimension of the sample file
		:param sample_y: the y dimension of the sample file
		:param fine_file: the fine map file to use (must be equal to or larger than the sample file)
		:param fine_x: the x dimension of the fine map file
		:param fine_y: the y dimension of the fine map file
		:param fine_x_offset: the x offset of the fine map file
		:param fine_y_offset: the y offset of the fine map file
		:param coarse_file: the coarse map file to use (must be equal to or larger than fine map file)
		:param coarse_x: the x dimension of the coarse map file
		:param coarse_y: the y dimension of the coarse map file
		:param coarse_x_offset: the x offset of the coarse map file at the resolution of the fine map
		:param coarse_y_offset: the y offset of the coarse map file at the resoultion of the fine map
		:param coarse_scale: the relative scale of the coarse map compared to the fine map (must match x and y scaling)
		:param pristine_fine_map: the pristine fine map file to use (must have dimensions equal to fine map)
		:param pristine_coarse_map: the pristine coarse map file to use (must have dimensions equal to coarse map)
		"""
		if not self.is_setup_map:
			self.sample_map.set_dimensions(sample_file, sample_x, sample_y)
			self.fine_map.set_dimensions(fine_file, fine_x, fine_y, fine_x_offset, fine_y_offset)
			self.coarse_map.set_dimensions(coarse_file, coarse_x, coarse_y, coarse_x_offset, coarse_y_offset)
			self.coarse_scale = coarse_scale
			self.pristine_fine_map_file = pristine_fine_map
			self.pristine_coarse_map_file = pristine_coarse_map
			self.is_setup_map = True
		else:
			err = "Map objects are already set up."
			self.logger.warning(err)

	def set_simulation_params(self, seed, job_type, output_directory, min_speciation_rate, sigma=1.0, tau=1.0, deme=1,
							  sample_size=1.0, max_time=3600, dispersal_method=None, m_prob=0.0, cutoff=0,
							  dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0.0,
							  gen_since_pristine=1,
							  time_config_file="null", restrict_self=False, infinite_landscape=False, protracted=False,
							  min_speciation_gen=None, max_speciation_gen=None, spatial=True, uses_spatial_sampling=False):
		"""
		Set all the simulation parameters apart from the map objects.

		:param int seed: the unique job number for this simulation set
		:param int job_type: the job type (used for easy file identification after simulations are complete)
		:param str output_directory: the output directory to store the SQL database
		:param float min_speciation_rate: the minimum speciation rate to simulate
		:param float sigma: the dispersal sigma value
		:param float tau: the fat-tailed dispersal tau value
		:param int deme: the deme size (in individuals per cell)
		:param float sample_size: the sample size of the deme (decimal 0-1)
		:param float max_time: the maximum allowed simulation time (in seconds)
		:param str dispersal_method: the dispersal kernel method. Should be one of [normal, fat-tail, norm-uniform]
		:param float m_prob: the probability of drawing from the uniform dispersal. Only relevant for uniform dispersals
		:param float cutoff: the maximum value for the uniform dispersal. Only relevant for uniform dispersals.
		:param float dispersal_relative_cost: the relative cost of travelling through non-habitat (defaults to 1)
		:param int min_num_species: the minimum number of species known to exist (defaults to 1
		:param float habitat_change_rate: the rate of habitat change over time
		:param float gen_since_pristine: the time in generations since a pristine state was achieved
		:param str time_config_file: the path to the time config file (or null)
		:param bool restrict_self: if true, restricts dispersal from own cell
		:param bool/str infinite_landscape: if false or "closed", restricts dispersal to the provided maps, otherwise
		can be "infinite", or a tiled landscape using "tiled_coarse" or "tiled_fine".
		:param bool protracted: if true, uses protracted speciation application
		:param float min_speciation_gen: the minimum amount of time a lineage must exist before speciation occurs.
		:param float max_speciation_gen: the maximum amount of time a lineage can exist before speciating.
		:param bool spatial: if true, means that the simulation is spatial
		:param bool uses_spatial_sampling: if true, the sample mask is interpreted as a proportional sampling mask,
			where the number of individuals sampled in the cell is equal to the
			density * deme_sample * cell sampling proportion
		"""
		if not self.is_setup_param:
			self.seed = seed
			self.output_directory = output_directory
			self.job_type = job_type
			self.min_speciation_rate = min_speciation_rate
			self.sigma = sigma
			self.tau = tau
			self.deme = deme
			self.sample_size = sample_size
			self.max_time = max_time
			self.dispersal_relative_cost = dispersal_relative_cost
			self.min_num_species = min_num_species
			self.habitat_change_rate = habitat_change_rate
			self.time_since_pristine = gen_since_pristine
			self.time_config_file = time_config_file
			self.dispersal_method = dispersal_method
			self.m_prob = m_prob
			self.cutoff = cutoff
			self.calculate_sql_database()
			self.is_setup_param = True
			self.restrict_self = restrict_self
			self.is_spatial = spatial
			if uses_spatial_sampling and not spatial:
				raise ValueError("Must use a spatial simulation to define spatial samplign regime.")
			self.uses_spatial_sampling = uses_spatial_sampling
			if not spatial:
				self.is_setup_map = True
				self.map_config = self.full_config_file
			if infinite_landscape in {False, "closed"}:
				self.infinite_landscape = "closed"
			elif infinite_landscape in {True, "infinite"}:
				self.infinite_landscape = "infinite"
			elif infinite_landscape in {"tiled_coarse", "tiled_fine"}:
				self.infinite_landscape = infinite_landscape
			else:
				raise ValueError("Supplied landscape type is not recognised: {}".format(infinite_landscape))
			if protracted:
				self.protracted = True
				if max_speciation_gen is None:
					self.logger.warning("Using protracted speciation, but no maximum speciation generation supplied."
									" Default to 10^100")
					self.max_speciation_gen = 10 ** 100
				else:
					self.max_speciation_gen = max_speciation_gen
				if min_speciation_gen is None:
					self.logger.warning("Using protracted speciation, but no minimum speciation generation supplied."
									" Default to 0.0")
					self.min_speciation_gen = 0.0
				else:
					self.min_speciation_gen = min_speciation_gen
		else:
			err = "Parameters already set up."
			self.logger.warning(err)

	def check_simulation_params(self):
		"""
		Checks that simulation parameters have been correctly set and the program is ready for running.
		Note that these checks have not been fully tested and are probably unnecessary in a large number of cases.
		"""
		if not self.is_setup_param:
			# print(self.output_directory)
			if self.output_directory in {"", None, 'null'}:
				raise RuntimeError('Output directory not set.')
			else:
				self.is_setup_param = True

	def resume_coalescence(self, pause_directory, seed, job_type, max_time, out_directory=None,
						   protracted=None, spatial=None):
		"""
		Resumes the simulation from the specified directory, looking for the simulation with the specified seed and task
		referencing.

		:param pause_directory: the directory to search for the paused simulation
		:param seed: the seed of the paused simulation
		:param job_type: the task of the paused simulation
		:param max_time: the maximum time to run simulations for
		:param out_directory: optionally provide an alternative output location. Defaults to same location as
		pause_directory
		:param bool protracted: protractedness of the simulation
		:param bool spatial: if the simulation is to be run with spatial complexity

		.. note: A max time of 0 uses the previous simulation maximum time.

		:return: None
		"""
		if protracted is not None:
			self.protracted = protracted
		if spatial is not None:
			self.is_spatial = spatial
		if out_directory is None:
			out_directory = pause_directory
		self.output_directory = out_directory
		self.pause_directory = pause_directory
		self.seed = seed
		self.job_type = job_type
		self.max_time = max_time
		self.calculate_sql_database()
		file_path = [
			os.path.join(pause_directory, "Pause", str("Dump_" + x + "_" + str(job_type) + "_" + str(seed) + ".csv"))
			for x in
			["active", "data", "map"]]
		for each in file_path:
			if not os.path.exists(each):
				raise IOError(
					"Paused file " + each + " not found. Ensure pause directory is correct and is accessible.")
		if necsim_import_success:
			self.setup_necsim()
			try:
				if self.protracted and self.is_spatial:
					self.necsim.resume_spatial_protracted(pause_directory, out_directory, seed, job_type, max_time)
				elif self.is_spatial:
					self.necsim.resume_spatial(pause_directory, out_directory, seed, job_type, max_time)
				elif self.protracted:
					self.necsim.resume_NSE_protracted(pause_directory, out_directory, seed, job_type, max_time)
				else:
					self.necsim.resume_NSE(pause_directory, out_directory, seed, job_type, max_time)
			except Exception as e:
				raise self.necsim.NECSimError(str(e))
		else:
			self.logger.warning("Using deprecated method.")
			raise ImportError("Cannot run simulation without successful import of necsim module")

	def persistent_ram_usage(self):
		"""
		This is the persistent RAM usage which cannot be optimised by the program for a particular set of maps
		:return: the total persistent RAM usage in bytes
		"""
		total_ram = 0
		total_ram += self.fine_map.x_size * self.fine_map.y_size * 4
		# First add the maps
		if self.coarse_map.file_name not in [None, "none"]:
			total_ram += self.coarse_map.x_size * self.coarse_map.y_size * 4
		if self.pristine_fine_map_file not in [None, "none"] or len(self.pristine_fine_list) != 0:
			total_ram += self.fine_map.x_size * self.fine_map.y_size * 4
		if self.pristine_coarse_map_file not in [None, "none"] or len(self.pristine_coarse_list) != 0:
			total_ram += self.coarse_map.x_size * self.coarse_map.y_size * 4
		if self.reproduction_map.file_name not in [None, "none"]:
			total_ram += self.reproduction_map.x_size * self.reproduction_map.y_size * 8
		if self.sample_map.file_name not in [None, "none", "null"]:
			total_ram += self.sample_map.x_size * self.sample_map.y_size * 1
		if self.dispersal_map.file_name not in [None, "none"]:
			total_ram += self.fine_map.x_size * self.fine_map.y_size * 8
		# Now add the other large memory objects
		# The data object
		total_ram += 2 * self.count_individuals() * 91 * min(len(self.times_list), 1)
		# The active object
		total_ram += 72 * self.count_individuals() * min(len(self.times_list), 1)
		return total_ram

	def estimate_ram_usage(self, grid_individuals):
		"""
		Estimates the RAM usage for the program with the current parameters.

		Note this estimates the upper bound of memory usage and is likely inaccurate, especially for simulations with
		multiple time sampling points.

		:param grid_individuals: the number of individuals existing on the grid

		:return: the estimated RAM usage in bytes

		:rtype: float
		"""
		total_ram = self.persistent_ram_usage()
		# The grid object
		if self.grid.file_name not in [None, "none", "null"]:
			total_ram += (13 * (self.grid.x_size + self.grid.y_size)) + 8 * grid_individuals

	def count_individuals(self):
		"""
		Estimates the number of individuals to be simulated. This may be inaccurate if using multiple time points and
		historical maps.

		:return: a count of the number of individuals to be simulated

		:rtype: float
		"""
		if self.count_total is None:
			if self.sample_map.file_name in [None, "none", "null"]:
				ds = gdal.Open(self.fine_map.file_name)
			else:
				ds = gdal.Open(self.sample_map.file_name)
			self.count_total = np.sum(ds.GetRasterBand(1).ReadAsArray()) * \
							   self.sample_size * self.get_average_density()
			if len(self.times_list) > 0:
				self.count_total *= len(self.times_list)
			return self.count_total
		else:
			return self.count_total

	def import_fine_map_array(self):
		"""
		Imports the fine map array to the in-memory object, subsetted to the same size as the sample grid.
		:rtype: None
		"""
		if self.fine_map_array is None:
			ds = gdal.Open(self.fine_map.file_name)
			self.fine_map_array = ds.GetRasterBand(1).ReadAsArray(self.fine_map.x_offset,
																  self.fine_map.y_offset,
																  self.sample_map.x_size,
																  self.sample_map.y_size)
			ds = None

	def import_sample_map_array(self):
		"""
		Imports the sample map array to the in-memory object.
		:rtype: None
		"""
		if self.sample_map_array is None:
			ds2 = gdal.Open(self.sample_map.file_name)
			self.sample_map_array = (ds2.GetRasterBand(1).ReadAsArray() >= 0.5) * 1
			ds2 = None

	def grid_density_estimate(self, x_off, y_off, x_dim, y_dim):
		"""
		Counts the density total for a subset of the grid by sampling from the fine map

		Note that this function is an approximation (based on the average density of the fine map) and does not produce
		a perfect value. This is done for performance reasons. The actual value can be obtained with
		grid_density_actual().

		:param x_off: the x offset of the grid map subset
		:param y_off: the y offset of the grid map subset
		:param x_dim: the x dimension of the grid map subset
		:param y_dim: the y dimension of the grid map subset

		:return: an estimate of the total individuals that exist in the subset.
		:rtype: int
		"""
		self.import_fine_map_array()
		if self.sample_map.file_name not in ["none", "null", None] and \
						self.sample_map.file_name != self.fine_map.file_name:
			self.import_sample_map_array()
			# Less accurate, but faster way.
			arr_subset = self.sample_map_array[x_off:x_off + x_dim, y_off:y_off + y_dim]
			return int(np.sum(np.floor(arr_subset * self.get_average_density() * self.sample_size)))
		return int(np.sum(np.floor(self.fine_map_array * self.deme * self.sample_size)))

	def grid_density_actual(self, x_off, y_off, x_dim, y_dim):
		"""
		Counts the density total for a subset of the grid by sampling from the fine map.

		Note that for large maps this can take a very long time.

		:param x_off: the x offset of the grid map subset
		:param y_off: the y offset of the grid map subset
		:param x_dim: the x dimension of the grid map subset
		:param y_dim: the y dimension of the grid map subset

		:return: the total individuals that exist in the subset.
		:rtype: int
		"""
		self.import_fine_map_array()
		if self.sample_map.file_name not in ["none", "null", None] and \
						self.sample_map.file_name != self.fine_map.file_name:
			self.import_sample_map_array()
			# Less accurate, but faster way.
			return int(np.sum(np.floor(np.multiply(self.fine_map_array[x_off:x_off + x_dim, y_off:y_off + y_dim],
												   self.sample_map_array[x_off:x_off + x_dim, y_off:y_off + y_dim]) *
									   self.deme * self.sample_size)))
		else:
			return int(np.sum(np.floor(self.fine_map_array[x_off:x_off + x_dim, y_off:y_off + y_dim] *
									   self.deme * self.sample_size)))

	def get_average_density(self):
		"""
		Gets the average density across the fine map, subsetted for the sample grid.
		"""
		if self.fine_map_average is None:
			self.import_fine_map_array()
			self.fine_map_average = self.deme * np.mean(self.fine_map_array)
		return self.fine_map_average

	def check_sample_map_equals_sample_grid(self):
		"""
		Checks if the grid and sample map are the same size and offset (in which case, future operations can be
		simplified).

		:return: true if the grid and sample map dimensions and offsets are equal
		:rtype: bool
		"""
		return self.grid.x_size == self.sample_map.x_size and self.grid.y_size == self.sample_map.x_size and \
			   self.grid.x_offset == 0 and self.grid.y_offset == 0

	def optimise_ram(self, ram_limit=None):
		"""
		Optimises the maps for a specific RAM usage.

		If ram_limit is None, this function does nothing.

		:note Assumes that the c++ compiler has sizeof(long) = 8 bytes for calculating space usage.

		:note Only optimises RAM for a square area of the map. For rectangular shapes, will use the shortest length as
			  a maximum size.

		:param ram_limit: the desired amount of RAM to limit to, in GB

		:raises MemoryError: if the desired simulation cannot be compressed into available RAM
		"""
		if self.sample_size <= 0 or self.deme <= 0:
			raise ValueError("Sample size is 0, or deme is 0. set_simulation_params() before optimising RAM.")
		if ram_limit is not None:
			self.grid = copy.deepcopy(self.sample_map)
			# Over-estimate static usage slightly
			static_usage = 1.1 * self.persistent_ram_usage() / 1024 ** 3
			if static_usage > ram_limit:
				raise MemoryError(
					"Cannot achieve RAM limit: minimum requirements are {}GB.".format(round(static_usage, 2)))
			remaining_space = (ram_limit - static_usage) * 1024 ** 3
			self.logger.info("Remaining space is {}GB.\n".format(round(remaining_space/1024**3, 2)))
			# Rough calculation of number of cells we have remaining (aim for 75% to be sure)
			average_density = self.get_average_density()
			# This is the size of the grid object in memory
			tmp_space = 0.95 * (remaining_space / ((16 * average_density) + 32))
			size = int(np.rint(tmp_space ** 0.5))
			if size < self.sample_map.x_size or size < self.sample_map.y_size:
				if size > self.sample_map.x_size or size > self.sample_map.y_size:
					size = min(self.sample_map.x_size, self.sample_map.y_size)
				if size < 2:
					raise MemoryError("Could not find square grid to achieve RAM limit. Please set this manually.")
				if size > self.sample_map.x_size or size > self.sample_map.y_size:
					self.logger.info("Memory limit high enough for full spatial simulation. No optimisation necessary.")
				max_attained = 0
				max_x = 0
				max_y = 0
				# Now loop over every square of the required size on the grid, until we find one with the maximum density
				if (self.sample_map.x_size * self.sample_map.y_size) > 1000000:
					printing = True
				else:
					printing = False
				end_x = self.sample_map.x_size - size - 1
				if size < 10:
					self.logger.warning("Extremely small grid size: {}. Disabling maximum density checking.".format(size))
					max_x = int(self.sample_map.x_size / 2)
					max_y = int(self.sample_map.y_size / 2)
					max_attained = 1
				else:
					for x in range(0, max(self.sample_map.x_size - size - 1, 1), int(round(max(10.0, size / 10)))):
						if printing:
							self.logger.info("\rChecking {} / {} : {}%".format(x, end_x, round(100 * x / end_x)))
						for y in range(0, max(self.sample_map.y_size - size - 1, 1), int(round(max(10.0, size / 10)))):
							# print("x, y: {}, {}".format(x, y))
							tmp_total = self.grid_density_actual(x, y, size, size)
							if tmp_total > max_attained:
								max_x = x
								max_y = y
								max_attained = tmp_total
					if printing:
						self.logger.info("\rChecking complete               \n")
				if max_attained > 0:
					# Now do one last check for consistency
					while self._fine_map_check(max_x, max_y, size):
						if printing:
							printing = False
							self.logger.info("Shrinking due to high densities in sample zone.\n")
						# Brute-force dividing by 2 each time
						size = max(1, int(size/2))
					if max_x + size > self.sample_map.x_size or max_y + size > self.sample_map.y_size:
						self.logger.debug("Max x,y: {}, {}".format(max_x, max_y))
						self.logger.debug("Size: {}".format(size))
						self.logger.debug("Fine map size: {}, {}".format(self.fine_map.x_size,
																		 self.fine_map.y_size))
						self.logger.debug("Sample map size: {}, {}".format(self.sample_map.x_size,
																		   self.sample_map.y_size))
						raise RuntimeError("Incorrect dimension setting - please report this bug")
					self.grid.x_size = size
					self.grid.y_size = size
					self.sample_map.x_offset = max_x
					self.sample_map.y_offset = max_y
					self.grid.file_name = "set"
					if self.check_sample_map_equals_sample_grid():
						self.grid.file_name = "none"
				else:
					raise MemoryError("Could not optimise maps for desired memory usage. "
								  	  "Attempted grid size of {} and achived max of {}".format(size, max_attained))
			self._wipe_objects()

	def get_optimised_solution(self):
		"""
		Gets the optimised solution as a dictionary containing the important optimised variables.
		This can be read back in with set_optimised_solution

		:return: dict containing the important optimised variables
		:rtype: dict
		"""
		return {"grid_x_size": self.grid.x_size,
				"grid_y_size": self.grid.y_size,
				"sample_x_offset": self.sample_map.x_offset,
				"sample_y_offset": self.sample_map.y_offset,
				"grid_file_name": self.grid.file_name}.copy()

	def set_optimised_solution(self, dict_in):
		"""
		Sets the optimised RAM solution from the variables in the provided dictionary.
		This should contain the grid_x_size, grid_y_size, grid_file_name, sample_x_offset and sample_y_offset.

		:param dict dict_in: the dictionary containing the optimised RAM solution variables
		:rtype: None
		"""
		self.grid.x_size = dict_in["grid_x_size"]
		self.grid.y_size = dict_in["grid_y_size"]
		self.sample_map.x_offset = dict_in["sample_x_offset"]
		self.sample_map.y_offset = dict_in["sample_y_offset"]
		self.grid.file_name = dict_in["grid_file_name"]

	def finalise_setup(self, config_default=True, expected=False, ignore_errors=False):
		"""
		Runs all setup routines to provide a complete simulation. Should be called immediately before run_coalescence()
		to ensure the simulation setup is complete.
		Calls check_simulation_params, generate_command() and run_checks()

		:param config_default: set to false if want config file to only be created if necessary. Defaults to True
		:param ignore_errors: if true, any FileNotFoundError and FileExistsError raised by checking the output database
		are ignored
		:param expected: set to true if we expect the output file to exist

		"""
		self.check_simulation_params()
		try:
			self.run_checks(expected=expected)
		except (FileExistsError, FileNotFoundError) as err:
			if not ignore_errors:
				raise err
			else:
				self.logger.info(str(err))
		# Now check if config files need to be written.
		config_require = config_default
		if self.full_config_file != '' and not self.is_full:
			config_require = True
		if self.dispersal_method is not None or self.infinite_landscape:
			config_require = True
		if config_require:
			if self.pristine_fine_map_file is not None and self.pristine_fine_map_file != "":
				self.add_pristine_map(self.pristine_fine_map_file, self.pristine_coarse_map_file,
									  self.time_since_pristine, self.habitat_change_rate)
		if (self.map_config != '' or len(self.pristine_coarse_list) > 0) or config_require:
			self.create_map_config()
		if (self.time_config_file != '' or len(self.times_list) > 0) or config_require:
			self.create_temporal_sampling_config()
		if config_require:
			self.is_full = False
			self.create_config()
		self.is_setup_complete = True
		self.calculate_sql_database()

	def generate_command(self):
		"""Completes the setup process by creating the list that will be passed to the c++ executable"""
		if (self.is_setup_map or self.is_full) and self.is_setup_param:
			if self.is_setup_complete:
				err = "Set up already completed"
				self.logger.warning(err)
			else:
				if not self.is_full:
					tmp_call_list = [self.coalescence_simulator, self.seed, self.job_type, self.map_config,
									 self.output_directory, self.min_speciation_rate, self.tau,
									 self.sigma,
									 self.deme, self.sample_size, self.max_time, self.dispersal_relative_cost,
									 self.time_config_file,
									 self.min_num_species]
				# print(tmp_call_list)
				else:
					tmp_call_list = [self.coalescence_simulator, "-f", self.seed, self.sample_map.x_size,
									 self.sample_map.y_size,
									 self.fine_map.file_name,
									 self.fine_map.x_size, self.fine_map.y_size, self.fine_map.x_offset,
									 self.fine_map.y_offset,
									 self.coarse_map.file_name, self.coarse_map.x_size, self.coarse_map.y_size,
									 self.coarse_map.x_offset,
									 self.coarse_map.y_offset, self.coarse_scale,
									 self.output_directory, self.min_speciation_rate, self.tau,
									 self.deme, self.sample_size, self.max_time,
									 self.dispersal_relative_cost, self.job_type, self.min_num_species,
									 self.pristine_fine_map_file,
									 self.pristine_coarse_map_file,
									 self.habitat_change_rate, self.time_since_pristine, self.sigma,
									 self.sample_map.file_name,
									 self.time_config_file]
				# print(tmp_call_list)
				# Make sure that there is no empty list appended if there are no speciation rates supplied.
				if len(self.speciation_rates) != 0:
					tmp_call_list.extend([str(x) for x in self.speciation_rates])
				self.call_list = [str(x) for x in tmp_call_list]
			# print self.call_list
			self.is_setup_complete = True
			self.calculate_sql_database()
		else:
			err = "Set up is incomplete: Map/Full: " + str(self.is_setup_map or self.is_full) + " Param: "
			err += str(self.is_setup_param) + " Setup: " + str(self.is_setup)
			raise RuntimeError(err)

	def set_speciation_rates(self, speciation_rates):
		"""Add speciation rates for analysis at the end of the simulation. This is optional

		:param list speciation_rates: a list of speciation rates to apply at the end of the simulation
		"""
		self.speciation_rates.extend(speciation_rates)

	def calculate_sql_database(self):
		"""
		Saves the output database location to self.output_database.
		"""
		self.output_database = os.path.join(self.output_directory,
											"SQL_data", "data_{}_{}.db".format(str(self.job_type), str(self.seed)))

	def check_sql_database(self, expected=False):
		"""
		Checks whether the output database exists. If the existance does not match the expected variable, raises an
		error.

		:raises FileExistsError: if the file already exists when it's not expected to
		:raises FileNotExistsError: if the file does not exist when we expect it to

		:param expected: boolean for expected existance of the output file

		:rtype: None
		"""
		if not expected:
			if os.path.exists(self.output_database):
				try:
					t = CoalescenceTree(self.output_database)
				except IOError:
					pass
				else:
					raise FileExistsError("Output sql database already exists.")
		else:
			if not os.path.exists(self.output_database):
				raise FileNotFoundError("Output sql database {} not found.".format(self.output_database))

	def check_maps(self):
		"""
		Checks that the maps all exist and that the file structure makes sense.

		:raises TypeError: if a dispersal map or reproduction map is specified, we must have a fine map specified, but
			not a coarse map.

		:raises IOError: if one of the required maps does not exist

		:return: None
		"""
		if self.is_spatial:
			for map_file in [self.coarse_map, self.fine_map, self.sample_map]:
				map_file.check_map()
			for map_file in [self.pristine_fine_map_file, self.pristine_fine_map_file]:
				check_file_exists(map_file)
			# Now check that the rest of the map naming structures make sense.
			if self.pristine_fine_map_file in {"none", None} and len(self.pristine_fine_list) == 0:
				if self.pristine_coarse_map_file not in {"none", None} or len(self.pristine_coarse_list) > 1:
					self.logger.warning(
						"Pristine fine file is 'none' but pristine coarse file is not none. Check file names.")
					self.logger.warning("Defaulting to pristine_coarse_map_file = 'none'")
					self.pristine_coarse_map_file = "none"
					self.pristine_coarse_list = []
				if len(self.pristine_fine_list) > 1:
					self.logger.warning(
						"Set pristine fine map file to 'none', but then added other pristine maps. Changing.")
					self.pristine_fine_list = []
			if self.coarse_map.file_name in {"none", None}:
				if self.pristine_coarse_map_file not in {"none", None}:
					self.logger.warning("Coarse file is 'none' but pristine coarse file is not none. Check file names.")
					self.logger.warning("Defaulting to pristine_coarse_map_file = 'none'")
					self.pristine_coarse_map_file = "none"
					self.pristine_coarse_list = []
			else:
				if self.coarse_map.file_name != "null" and not self.fine_map.is_within(self.coarse_map):
					raise ValueError("Offsets mean that coarse map does not fully encompass fine map. Check that your"
									 " maps exist at the same spatial coordinates.")
			if self.fine_map.file_name == "none":
				self.logger.warning("Fine map file cannot be 'none', changing to 'null'.")
				self.fine_map.file_name = "null"
			# Check offset of sample mask with fine map
			if self.sample_map.file_name != "null" and not self.sample_map.is_within(self.fine_map):
				raise ValueError(
					"Offsets mean that fine map does not fully encompass sample map. Check that your maps exist"
					" at the same spatial coordinates.")
			if self.grid.file_name == "set" and \
				self.sample_map.x_offset + self.grid.x_size > self.sample_map.x_size or \
				self.sample_map.y_offset + self.grid.y_size > self.sample_map.y_size:
				raise ValueError("Grid is not within the sample map - please check offsets of sample map.")
			# Now check our combination of dispersal map, reproduction map and infinite landscape with our fine/coarse maps
			# makes sense
			if self.dispersal_map.file_name not in {"none", None}:
				if self.coarse_map.file_name not in {None, "none"}:
					raise TypeError("Cannot use a coarse map if using a dispersal map. "
									"This feature is currently unsupported.")
			if self.reproduction_map.file_name not in {None, "none", "null"}:
				if self.coarse_map.file_name not in {None, "none", "null"}:
					raise TypeError("Cannot use a coarse map if using a reproduction map. "
									"This feature is currently unsupported.")
			if self.infinite_landscape is "tiled_fine":
				if self.coarse_map.file_name not in {None, "none"}:
					raise TypeError("Cannot use a coarse map with a tiled fine landscape.")
			if self.infinite_landscape is "tiled_coarse":
				if self.coarse_map.file_name in {None, "none"}:
					raise TypeError("Cannot use a tiled_coarse landscape without a coarse map.")

	def run_checks(self, expected=False):
		"""
		Check that the simulation is correctly set up and that all the required files exist.

		:param expected: set to true if we expect the output file to already exist

		:raises RuntimeError: if previous set-up routines are not complete
		"""
		if self.is_setup_map and self.is_setup_param:
			self.check_maps()
		else:
			err = "Set up is incomplete."
			raise RuntimeError(err)
		self.check_sql_database(expected=expected)

	def _create_logger(self, file=None, logging_level=None):
		"""
		Creates the logger for use with NECSim simulation. Note you can supply your own logger by over-riding
		self.logger. This function should only be run during self.__init__()

		:param file: file to write output to. If None, outputs to terminal
		:param logging_level: the logging level to use (defaults to INFO)

		:return: None
		"""
		if logging_level is None:
			logging_level = self.logging_level
		self.logger = create_logger(self.logger, file, logging_level)

	def run_from_config(self, logger, config_file):
		"""
		Calls NECSim to run from config within a new thread

		:param logger:
		:param config_file:

		:return:
		"""
		# TODO correct or remove this function
		necsimmodule.set_log_function(write_to_log)
		necsimmodule.set_logger(logger)
		output = necsimmodule.run_from_config(config_file)

	def run_coalescence(self):
		"""Attempt to run the simulation with the given simulation set-up.
		This is the main routine performing the actual simulation which will take a considerable amount of time."""
		if self.is_setup_complete:
			# Make the output directory if it doesn't yet exist
			if not os.path.exists(self.output_directory):
				os.makedirs(self.output_directory)
			# Call the c++ code and run the simulation
			if not necsim_import_success:
				self.logger.error("NECSim import unsuccessful: cannot run simulations using c++ API. Attempting system call"
							  " instead")
			if self.full_config_file != '' and self.full_config_file is not None and necsim_import_success:
				# Run NECSim
				try:
					self.setup_necsim()
					if self.protracted and self.is_spatial:
						self.necsim.run_spatial_protracted(self.full_config_file)
					elif self.is_spatial:
						self.necsim.run_spatial(self.full_config_file)
					elif self.protracted:
						self.necsim.run_NSE_protracted(self.full_config_file)
					else:
						self.necsim.run_NSE(self.full_config_file)
				except Exception as e:
					raise self.necsim.NECSimError(str(e))
			else:
				# Deprecated method if cannot link to shared objects
				self.logger.warning("Using deprecated os call method.")
				if necsim_import_success:
					self.logger.warning("NECSim not successfully imported.")
				else:
					self.logger.warning("Config file was :" + self.full_config_file)
				try:
					execute_log_info(self.call_list)
				except:
					self.logger.critical("Error raised using deprecated os call method.")
					self.logger.critical("Call was " + str(self.call_list))
		else:
			err = "Set up is incomplete."
			raise RuntimeError(err)

	def _wipe_objects(self):
		"""
		Clears the arrays from memory
		:return:
		"""
		self.fine_map_array = None
		self.sample_map_array = None

	def _fine_map_check(self, max_x, max_y, size):
		"""
		Checks the total number of individuals in a subset from the fine map is less than the average density multiplied
		by the size of the square.

		:param max_x: the x value to start subsetting from
		:param max_y: the y value to start subsetting from
		:param size: the size of the square
		:return: bool true if it is smaller
		:rtype: bool
		"""
		self._fine_map_sum_res = self.grid_density_actual(max_x, max_y, size, size)
		return self._fine_map_sum_res > size * size * self.get_average_density()
