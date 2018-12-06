"""
Run spatially explicit neutral simulations on provided landscapes with support for a wide range of scenarios and
parameters. Detailed :ref:`here <performing_simulations>`.

The main class is :class:`.Simulation`, which contains routines for setting up and running simulations, plus basic tree
generation after simulations have been completed.

:input:
	- Simulation parameters (such as dispersal kernel, speciation rate)
	- Map files representing density over space
	- [optional] map files representing relative reproductive ability
	- [optional] map files representing dispersal potential
	- [optional] historical density map files

:output:
	- Database containing generated coalescence tree, simulation parameters and basic biodiversity metrics.
	- If the simulation does not complete, will instead dump data to a Dump_main_*_*.csv file for resuming simulations.
"""
from __future__ import absolute_import
from __future__ import print_function

import copy
import logging
import os
import types

import numpy as np

global sqlite_import

try:
	import configparser as ConfigParser
	from io import StringIO
except ImportError as ie:  # Python 2.x support
	import ConfigParser
	from cStringIO import StringIO

	ConfigParser.ConfigParser.read_file = ConfigParser.ConfigParser.read

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

from pycoalescence.necsim import libnecsim
from pycoalescence.future_except import FileNotFoundError, FileExistsError
from pycoalescence.landscape import Landscape
from pycoalescence.map import Map
from pycoalescence.system_operations import write_to_log, check_parent


class Simulation(Landscape):
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
		Landscape.__init__(self)
		# Contains the C object for performing simulations
		# This will be set depending on the simulation type
		self.c_simulation = None
		self._fine_map_sum_res = None
		self.count_total = None
		# Create the logging object and pass on the required arguments for its creation
		passedKwards = {k: v for k, v in kwargs.items() if "stream" not in k}
		self.logger = logging.Logger("pycoalescence.simulation", **passedKwards)
		self._create_logger(file=log_output, logging_level=logging_level, **kwargs)
		self.output_directory = ""
		self.pause_directory = ""
		self.config = ConfigParser.ConfigParser()
		self.config_string = StringIO()
		self.full_config_file = None
		self.is_setup = False
		self.is_setup_param = False
		self.is_setup_complete = False
		self.seed = 0
		self.min_speciation_rate = 0
		self.sigma = 2
		self.deme = 1
		self.sample_size = 1
		self.max_time = 100
		self.dispersal_relative_cost = 1  # the relative cost of moving through non-matrix
		self.job_type = 0
		self.min_num_species = 1
		self.tau = 0
		self.times = None
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
		# The output database location
		self.output_database = None
		self.dispersal_method = None
		self.m_prob = 0
		self.cutoff = 0
		self.restrict_self = False
		# The protracted variables
		self.protracted = False
		self.min_speciation_gen = 0.0
		self.max_speciation_gen = 0.0
		# This variable stores whether a new config file has been opened or not
		self.config_open = False
		# Grid dimensions sizing
		self.grid = Map()
		# Dispersal map data
		self.dispersal_map = Map()
		self.death_map = Map()
		self.reproduction_map = Map()
		self.fine_map_array = None
		self.sample_map_array = None
		self.fine_map_average = None
		self.is_spatial = True;
		self.uses_spatial_sampling = False

	def __del__(self):
		"""Safely destroys the logger and the C++ objects."""
		handlers = copy.copy(self.logger.handlers)
		for handler in handlers:
			handler.close()
			self.logger.removeHandler(handler)
		self.logger = None
		self.c_simulation = None

	def add_sample_time(self, time):
		"""
		Adds an extra sample time to the list of times.

		This allows for multiple temporal sample points from within the same simulation.

		:param time: the sample time to add
		"""
		if isinstance(time, list):
			[self.add_sample_time(x) for x in time]
		else:
			if not self.times or len(self.times) == 0:
				self.times = [0.0]
			self.times.append(time)

	def set_config_file(self, output_file=None):
		"""
		Sets the config file to the output, over-writing any existing config file that has been stored.

		:param output_file: path to config file to output to
		"""
		if self.full_config_file and output_file != self.full_config_file and output_file:
			self.logger.warning("Config file has already been set to {}, changing to {}.".format(self.full_config_file,
																								 output_file))
		if output_file is not None:
			self.full_config_file = output_file

	def load_config(self, config_file):
		"""
		Loads the config file by reading the lines in order.

		:param str config_file: the config file to read in.
		"""
		# New method using ConfigParser
		with open(config_file, "wa") as f:
			self.config.read_file(f)
		self.seed = self.config.getint("main", "seed")
		self.job_type = self.config.getint("main", "job_type")
		self.output_directory = self.config.get("main", "result_directory")
		self.min_speciation_rate = self.config.getfloat("main", "min_spec_rate")
		self.sigma = self.config.getfloat("main", "sigma")
		self.tau = self.config.getfloat("main", "tau")
		self.deme = self.config.getint("main", "deme")
		self.sample_size = self.config.getfloat("main", "sample_size")
		self.max_time = self.config.getint("main", "max_time")
		self.dispersal_relative_cost = self.config.getfloat("main", "lambda")
		self.min_num_species = self.config.getint("main", "min_species")
		self.full_config_file = config_file
		if self.config.has_section("spec_rate"):
			opts = self.config.options("spec_rate")
			for each in opts:
				self.speciation_rates.append(self.config.getfloat("spec_rate", each))

	def write_config(self, config_file):
		"""
		Writes the config to the config file provided, overwriting any existing config files.

		:param config_file: the config file to write out to

		:rtype: None
		"""
		if not self.config.has_section("main"):
			self.create_config()
			self.create_map_config()
		if config_file is not None:
			check_parent(config_file)
			if os.path.exists(config_file) and not self.config_open:
				os.remove(config_file)
		with open(config_file, "w") as f:
			self.config.write(f)
		self.config_open = True
		self.full_config_file = config_file

	def create_temporal_sampling_config(self):
		"""
		Creates the time-sampling config file.

		Function is called automatically when creating a config file, and should not be manually called.
		"""
		if self.times and len(self.times) != 0:
			self.config.add_section("times")
			for i, j in enumerate(sorted(set(self.times))):
				self.config.set("times", "time" + str(i), str(j))
			if self.full_config_file is not None:
				self.write_config(self.full_config_file)

	def create_map_config(self, output_file=None):
		"""
		Generates the map config file from reading the spatial structure of each of the provided files.

		:param str output_file: the file to output configuration data to (the map config file)
		"""
		self.set_config_file(output_file)
		if self.is_setup_map:
			if self.is_spatial:
				self.config.add_section("sample_grid")
				self.config.set("sample_grid", "path", self.sample_map.file_name)
				x, y = map(str, self.sample_map.get_x_y())
				self.config.set("sample_grid", "x", str(x))
				self.config.set("sample_grid", "y", str(y))
				if self.sample_map.file_name is None:
					self.config.set("sample_grid", "mask", "null")
				else:
					self.config.set("sample_grid", "mask", self.sample_map.file_name)
					self.config.set("sample_grid", "uses_spatial_sampling", str(int(self.uses_spatial_sampling)))
				self.config.add_section("fine_map")
				self.config.set("fine_map", "path", self.fine_map.file_name)
				x, y = map(str, self.fine_map.get_x_y())
				self.config.set("fine_map", "x", str(x))
				self.config.set("fine_map", "y", str(y))
				self.config.set("fine_map", "x_off", str(self.fine_map.x_offset))
				self.config.set("fine_map", "y_off", str(self.fine_map.y_offset))
				self.config.add_section("coarse_map")
				if self.coarse_map.file_name is not None:
					self.config.set("coarse_map", "path", self.coarse_map.file_name)
					x, y = map(str, self.coarse_map.get_x_y())
					self.config.set("coarse_map", "x", str(x))
					self.config.set("coarse_map", "y", str(y))
					self.config.set("coarse_map", "x_off", str(self.coarse_map.x_offset))
					self.config.set("coarse_map", "y_off", str(self.coarse_map.y_offset))
					self.config.set("coarse_map", "scale", str(self.coarse_scale))
				else:
					self.config.set("coarse_map", "path", "none")
					self.config.set("coarse_map", "x", 0)
					self.config.set("coarse_map", "y", 0)
					self.config.set("coarse_map", "x_off", 0)
					self.config.set("coarse_map", "y_off", 0)
					self.config.set("coarse_map", "scale", 1)
				self.sort_historical_maps()
				if len(self.historical_coarse_list) != 0 and len(self.historical_fine_list) != 0:
					for i, t in enumerate(self.times_list):
						try:
							tmp_fine = "historical_fine{}".format(i)
							self.config.add_section(tmp_fine)
							self.config.set(tmp_fine, "path", self.historical_fine_list[i])
							self.config.set(tmp_fine, "number", str(i))
							self.config.set(tmp_fine, "time", str(t))
							self.config.set(tmp_fine, "rate", str(self.rates_list[i]))
							tmp_coarse = "historical_coarse{}".format(i)
							self.config.add_section(tmp_coarse)
							self.config.set(tmp_coarse, "path", self.historical_coarse_list[i])
							self.config.set(tmp_coarse, "number", str(i))
							self.config.set(tmp_coarse, "time", str(t))
							self.config.set(tmp_coarse, "rate", str(self.rates_list[i]))
						except IndexError as ie:
							self.logger.warning(
								'Discrepancy between historical file list, time list or rate list. Check inputs: {}'.format(
									ie))
							break
				if self.grid.file_name == "set":
					self.config.add_section("grid_map")
					self.config.set("grid_map", "x", str(self.grid.x_size))
					self.config.set("grid_map", "y", str(self.grid.y_size))
					self.config.set("sample_grid", "x_off", str(self.sample_map.x_offset))
					self.config.set("sample_grid", "y_off", str(self.sample_map.y_offset))
				if self.death_map.file_name not in [None, "none", "null"]:
					self.config.add_section("death")
					self.config.set("death", "map", self.death_map.file_name)
				if self.reproduction_map.file_name not in [None, "none", "null"]:
					self.config.add_section("reproduction")
					self.config.set("reproduction", "map", self.reproduction_map.file_name)
				if self.dispersal_method is not None:
					self.config.add_section("dispersal")
					self.config.set("dispersal", "method", self.dispersal_method)
					self.config.set("dispersal", "m_probability", str(self.m_prob))
					self.config.set("dispersal", "cutoff", str(self.cutoff))
				if self.restrict_self:
					if not self.config.has_section("dispersal"):
						self.config.add_section("dispersal")
					self.config.set("dispersal", "restrict_self", str(int(self.restrict_self)))
				if self.landscape_type != "closed":
					if not self.config.has_section("dispersal"):
						self.config.add_section("dispersal")
					self.config.set("dispersal", "landscape_type", self.landscape_type)
				if self.dispersal_map.file_name not in ["none", None]:
					if not self.config.has_section("dispersal"):
						self.config.add_section("dispersal")
					self.config.set("dispersal", "dispersal_file", self.dispersal_map.file_name)
				if self.full_config_file is not None:
					self.write_config(self.full_config_file)
		else:
			raise RuntimeError("Cannot generate map config file without setting up map variables")

	def create_config(self, output_file=None):
		"""
		Generates the configuration. This will be written out either by providing an output file here, or by calling
		write_config();

		:param str output_file: the file to generate the config option. Must be a path to a .txt file.
		"""
		self.set_config_file(output_file)
		if self.full_config_file is not None:
			if not os.path.exists(os.path.dirname(self.full_config_file)) and \
					os.path.dirname(self.full_config_file) != "":
				self.logger.info('Path {} does not exist for writing '
								 'output to, creating.'.format(os.path.dirname(self.full_config_file)))
				os.makedirs(os.path.dirname(self.full_config_file))
			if os.path.exists(self.full_config_file) and not self.config_open:
				os.remove(self.full_config_file)
		if self.is_setup_map and self.is_setup_param:
			# New method using ConfigParser
			self.config.add_section("main")
			self.config.set("main", "seed", str(self.seed))
			self.config.set("main", "job_type", str(self.job_type))
			self.config.set("main", "output_directory", self.output_directory)
			self.config.set("main", "min_spec_rate", str(self.min_speciation_rate))
			if self.is_spatial:
				self.config.set("main", "sigma", str(self.sigma))
				self.config.set("main", "tau", str(self.tau))
				self.config.set("main", "dispersal_relative_cost", str(self.dispersal_relative_cost))
			self.config.set("main", "deme", str(self.deme))
			self.config.set("main", "sample_size", str(self.sample_size))
			self.config.set("main", "max_time", str(self.max_time))
			self.config.set("main", "min_species", str(self.min_num_species))
			if self.protracted:
				self.config.add_section("protracted")
				self.config.set("protracted", "has_protracted", str(int(self.protracted)))
				self.config.set("protracted", "min_speciation_gen", str(float(self.min_speciation_gen)))
				self.config.set("protracted", "max_speciation_gen", str(float(self.max_speciation_gen)))
			if len(self.speciation_rates) != 0:
				self.config.add_section("spec_rates")
				for i, j in enumerate(set([x for x in self.speciation_rates])):
					spec_rate = "spec_{}".format(i)
					self.config.set("spec_rates", spec_rate, str(j))
			if self.full_config_file is not None:
				self.write_config(self.full_config_file)
		else:
			raise RuntimeError("Setup has not been completed, cannot create config file")
		self.create_temporal_sampling_config()

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
		self.set_simulation_parameters(seed=seed, job_type=task, output_directory=output, min_speciation_rate=alpha,
									   sigma=sigma, tau=1, deme=1, sample_size=1.0, max_time=36000,
									   dispersal_relative_cost=1,
									   min_num_species=1, habitat_change_rate=0.0, gen_since_historical=1)
		self.set_map_parameters("null", size, size, "null", size, size, 0, 0, "null", size, size, 0, 0, 1, "null",
								"null")
		self.set_speciation_rates([alpha])
		self.run()
		# Now read the species richness from the database
		try:
			richness = self.get_species_richness()
			if richness == 0:
				raise AssertionError("Richness is 0, error in program. This should never be the case for a complete "
									 "sim.")
			return richness
		except IOError:
			raise RuntimeError("Simulation didn't complete in 10 hours (maximum time for run_simple). Try running a "
							   "custom simulation instead.")

	def get_species_richness(self, reference=1):
		"""
		Calls coal_analyse.get_species_richness() with the supplied variables.

		Requires successful import of coal_analyse and sqlite3.

		:param speciation_rate: the speciation rate to extract system richness from.
		:param time: the time to extract system richness from

		:return: the species richness.
		"""
		if not sqlite_import:
			raise ImportError("sqlite3 module required for obtaining richness from database files.")
		else:
			self.calculate_sql_database()
			db = self.output_database
			t = CoalescenceTree()
			t.set_database(db)
			return t.get_species_richness(reference)

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

	def set_map_files(self, sample_file, fine_file=None, coarse_file=None, historical_fine_file=None,
					  historical_coarse_file=None, dispersal_map=None, death_map=None, reproduction_map=None):
		"""
		Sets the map files (or to null, if none specified). It then calls detect_map_dimensions() to correctly read in
		the specified dimensions.

		If sample_file is "null", dimension values will remain at 0.
		If coarse_file is "null", it will default to the size of fine_file with zero offset.
		If the coarse file is "none", it will not be used.
		If the historical fine or coarse files are "none", they will not be used.

		.. note:: the dispersal map should be of dimensions xy by xy where x, y are the fine map dimensions. Dispersal
				  rates from each row/column index represents dispersal from the
				  row index to the column index according to index = x+(y*xdim), where x,y are the coordinates of the
				  cell and xdim is the x dimension of the fine map. See the
				  :class:`PatchedLandscape class <pycoalescence.patched_landscape.PatchedLandscape>` for routines for
				  generating these landscapes.

		:param str sample_file: the sample map file. Provide "null" if on samplemask is required
		:param str fine_file: the fine map file. Defaults to "null" if none provided
		:param str coarse_file: the coarse map file. Defaults to "none" if none provided
		:param str historical_fine_file: the historical fine map file. Defaults to "none" if none provided
		:param str historical_coarse_file: the historical coarse map file. Defaults to "none" if none provided
		:param str dispersal_map: the dispersal map for reading dispersal values. Default to "none" if none provided
		:param str death_map: a map of relative death probabilities, at the scale of the fine map
		:param str reproduction_map: a map of relative reproduction probabilities, at the scale of the fine map

		:rtype: None

		:return: None
		"""
		if dispersal_map is None:
			self.dispersal_map.file_name = "none"
		else:
			self.dispersal_map.file_name = dispersal_map
		if death_map is None:
			self.death_map.file_name = "none"
		else:
			self.death_map.file_name = death_map
		if reproduction_map is None:
			self.reproduction_map.file_name = "none"
		else:
			self.reproduction_map.file_name = reproduction_map
		Landscape.set_map_files(self, sample_file, fine_file, coarse_file, historical_fine_file, historical_coarse_file)

	def detect_map_dimensions(self):
		"""
		Detects all the map dimensions for the provided files (where possible) and sets the respective values.
		This is intended to be run after set_map_files()

		:raises TypeError: if a dispersal map or death map is specified, we must have a fine map specified, but
						   not a coarse map.

		:raises IOError: if one of the required maps does not exist
		
		:raises ValueError: if the dimensions of the dispersal map do not make sense when used with the fine map
							provided

		:return: None
		"""
		Landscape.detect_map_dimensions(self)
		# Now do detection for dispersal map
		if self.dispersal_map.file_name not in {"none", "null", None}:
			self.dispersal_map.set_dimensions()
			if self.dispersal_map.x_size != self.fine_map.x_size * self.fine_map.y_size or \
					self.dispersal_map.y_size != self.fine_map.x_size * self.fine_map.y_size:
				raise ValueError("Dimensions of dispersal map do not match dimensions of fine map. This is currently"
								 " unsupported.")
		self.check_dimensions_match_fine(self.death_map, "death")
		self.check_dimensions_match_fine(self.reproduction_map, "reproduction")
		self.check_maps()

	def check_dimensions_match_fine(self, map_to_check, name=""):
		"""
		Checks that the dimensions of the provided map matches the fine map.

		:param Map map_to_check: map to check the dimensions of against the fine map
		:param str name: name to write out in error message

		:return: true if the dimensions match
		"""
		if map_to_check.file_name not in {"none", "null", None}:
			map_to_check.set_dimensions()
			if not map_to_check.has_equal_dimensions(self.fine_map):
				# if the sizes match, then proceed with a warning
				if map_to_check.x_size == self.fine_map.x_size and \
						map_to_check.y_size == self.fine_map.y_size:
					self.logger.warning("Coordinates of {} map did not match fine map.".format(name))
					map_to_check.x_offset = self.fine_map.x_offset
					map_to_check.y_offset = self.fine_map.y_offset
					map_to_check.x_res = self.fine_map.x_res
					map_to_check.y_res = self.fine_map.y_res
				else:
					raise ValueError("Dimensions of the {} map do not match the fine map. This is currently "
									 "unsupported.".format(name))

	def set_simulation_parameters(self, seed, job_type, output_directory, min_speciation_rate, sigma=1.0, tau=1.0,
								  deme=1, sample_size=1.0, max_time=3600, dispersal_method=None, m_prob=0.0, cutoff=0,
								  dispersal_relative_cost=1, min_num_species=1, habitat_change_rate=0.0,
								  gen_since_historical=1, restrict_self=False, landscape_type=False,
								  protracted=False, min_speciation_gen=None, max_speciation_gen=None,
								  spatial=True, uses_spatial_sampling=False, times=None):
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
		:param float gen_since_historical: the time in generations since a historical state was achieved
		:param bool restrict_self: if true, restricts dispersal from own cell
		:param bool/str landscape_type: if false or "closed", restricts dispersal to the provided maps, otherwise
										can be "infinite", or a tiled landscape using "tiled_coarse" or "tiled_fine".
		:param bool protracted: if true, uses protracted speciation application
		:param float min_speciation_gen: the minimum amount of time a lineage must exist before speciation occurs.
		:param float max_speciation_gen: the maximum amount of time a lineage can exist before speciating.
		:param bool spatial: if true, means that the simulation is spatial
		:param bool uses_spatial_sampling: if true, the sample mask is interpreted as a proportional sampling mask,
										   where the number of individuals sampled in the cell is equal to the
										   density * deme_sample * cell sampling proportion
		:param list times: list of temporal sampling points to apply (in generations)
		"""
		if not self.is_setup_param:
			self.set_seed(seed)
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
			self.gen_since_historical = gen_since_historical
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
			if landscape_type in {False, "closed"}:
				self.landscape_type = "closed"
			elif landscape_type in {True, "infinite"}:
				self.landscape_type = "infinite"
			elif landscape_type in {"tiled_coarse", "tiled_fine"}:
				self.landscape_type = landscape_type
			else:
				raise ValueError("Supplied landscape type is not recognised: {}".format(landscape_type))
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
			if times:
				self.times = times
		else:
			self.logger.warning("Parameters already set up.")

	def set_seed(self, seed):
		"""
		Sets the seed for the simulation.

		A seed < 1 should not be set for the necsim, as equivalent behaviour is produce for seed and abs(seed), plus for
		seed = 1 and seed = 0. Consequently, for any values less than 1, we take a very large number plus the seed,
		instead. Therefore a error is raised if the seed exceeds this very large number (this is an acceptable
		decrease in userability as a seed that large is unlikely to ever be used).

		:param int seed: the random number seed
		"""
		limit_val = int(2147483647 / 2)
		if seed > limit_val:
			raise ValueError("Seed cannot be larger than 2,147,483,647")
		if seed < 1:
			new_seed = abs(seed) + limit_val
			self.logger.critical("Seed of {} is < 1, so will be changed to {}\n".format(seed, new_seed))
			self.seed = new_seed
		else:
			self.seed = seed

	def check_simulation_parameters(self):
		"""
		Checks that simulation parameters have been correctly set and the program is ready for running.
		Note that these checks have not been fully tested and are probably unnecessary in a large number of cases.
		"""
		if not self.is_setup_param:
			raise RuntimeError("Simulation parameters have not been set.")
		if self.output_directory in {"", None, 'null'}:
			raise RuntimeError('Output directory not set.')
		check_parent(self.output_directory)
		if self.full_config_file is not None:
			check_parent(self.full_config_file)

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
		file_path = os.path.join(pause_directory, "Pause", str("Dump_main_" + str(job_type) + "_" + str(seed) + ".csv"))
		if not os.path.exists(file_path):
			raise IOError(
				"Paused file " + file_path + " not found. Ensure pause directory is correct and is accessible.")
		self.setup_necsim()
		self.c_simulation.setup_resume(pause_directory, out_directory, seed, job_type, max_time)
		self.is_setup_complete = True
		self._run_and_output()

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
		if self.historical_fine_map_file not in [None, "none"] or len(self.historical_fine_list) != 0:
			total_ram += self.fine_map.x_size * self.fine_map.y_size * 4
		if self.historical_coarse_map_file not in [None, "none"] or len(self.historical_coarse_list) != 0:
			total_ram += self.coarse_map.x_size * self.coarse_map.y_size * 4
		if self.death_map.file_name not in [None, "none"]:
			total_ram += self.death_map.x_size * self.death_map.y_size * 8
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
			if self.fine_map.file_name == "null":
				self.fine_map_array = np.ones((self.fine_map.x_size, self.fine_map.y_size))
			else:
				self.fine_map_array = self.fine_map.get_subset(self.fine_map.x_offset, self.fine_map.y_offset,
															   self.sample_map.x_size, self.sample_map.y_size)

	def import_sample_map_array(self):
		"""
		Imports the sample map array to the in-memory object.

		:rtype: None
		"""
		if self.sample_map_array is None:
			if self.sample_map.file_name == "null":
				self.sample_map_array = np.ones((self.sample_map.x_size, self.sample_map.y_size))
			else:
				self.sample_map.open()
				if not self.uses_spatial_sampling:
					self.sample_map_array = np.ma.masked_where(self.sample_map.data >= 0.5, self.sample_map.data).mask
				else:
					self.sample_map_array = self.sample_map.data
				self.sample_map.data = None

	def grid_density_estimate(self, x_off, y_off, x_dim, y_dim):
		"""
		Counts the density total for a subset of the grid by sampling from the fine map

		:note: This is an approximation (based on the average density of the fine map) and does not produce
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
			arr_subset = self.sample_map_array[y_off:y_off + y_dim, x_off:x_off + x_dim]
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
			return int(np.sum(np.floor(np.multiply(self.fine_map_array[y_off:y_off + y_dim, x_off:x_off + x_dim],
												   self.sample_map_array[y_off:y_off + y_dim, x_off:x_off + x_dim]) *
									   self.deme * self.sample_size)))
		else:
			return int(np.sum(np.floor(self.fine_map_array[y_off:y_off + y_dim, x_off:x_off + x_dim] *
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

	def optimise_ram(self, ram_limit):
		"""
		Optimises the maps for a specific RAM usage.

		If ram_limit is None, this function does nothing.

		:note: Assumes that the C++ compiler has sizeof(long) = 8 bytes for calculating space usage.

		:note: Only optimises RAM for a square area of the map. For rectangular shapes, will use the shortest length as
			   a maximum size.

		:param ram_limit: the desired amount of RAM to limit to, in GB

		:raises MemoryError: if the desired simulation cannot be compressed into available RAM
		"""
		if self.sample_size <= 0 or self.deme <= 0:
			raise ValueError("Sample size is 0, or deme is 0. set_simulation_parameters() before optimising RAM.")
		self.grid = copy.deepcopy(self.sample_map)
		# Over-estimate static usage slightly
		static_usage = 1.1 * self.persistent_ram_usage() / 1024 ** 3
		if static_usage > ram_limit:
			raise MemoryError(
				"Cannot achieve RAM limit: minimum requirements are {}GB.".format(round(static_usage, 2)))
		remaining_space = (ram_limit - static_usage) * 1024 ** 3
		self.logger.info("Remaining space is {}GB.\n".format(round(remaining_space / 1024 ** 3, 2)))
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
					size = max(1, int(size / 2))
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

	def finalise_setup(self, expected=False, ignore_errors=False):
		"""
		Runs all setup routines to provide a complete simulation. Should be called immediately before run_coalescence()
		to ensure the simulation setup is complete.

		:param ignore_errors: if true, any FileNotFoundError and FileExistsError raised by checking the output database
							  are ignored
		:param expected: set to true if we expect the output file to exist

		"""
		self.check_simulation_parameters()
		try:
			self.run_checks(expected=expected)
		except (FileExistsError, FileNotFoundError) as err:
			if not ignore_errors:
				raise err
			else:
				self.logger.info(str(err))
		# Now check if config files need to be written.
		if self.historical_fine_map_file not in self.historical_fine_list and \
				self.historical_fine_map_file not in [None, "", "none"]:
			self.add_historical_map(self.historical_fine_map_file, self.historical_coarse_map_file,
									self.gen_since_historical, self.habitat_change_rate)
		self.create_config()
		self.create_map_config()
		self.calculate_sql_database()
		self.setup_necsim()
		if self.full_config_file is not None:
			self.c_simulation.import_from_config(self.full_config_file)
		else:
			self.config.write(self.config_string)
			self.c_simulation.import_from_config_string(self.config_string.getvalue())
		self.c_simulation.setup()
		self.is_setup_complete = True

	def setup_necsim(self):
		"""
		Calculates the type of the simulation (spatial/non-spatial, protracted/non-protracted) and sets the c object
		appropriately.

		:rtype: None
		"""
		if self.protracted:
			if self.is_spatial:
				self.c_simulation = libnecsim.CPSpatialSimulation(self.logger, write_to_log)
			else:
				self.c_simulation = libnecsim.CPNSESimulation(self.logger, write_to_log)
		elif self.is_spatial:
			self.c_simulation = libnecsim.CSpatialSimulation(self.logger, write_to_log)
		else:
			self.c_simulation = libnecsim.CNSESimulation(self.logger, write_to_log)

	def set_speciation_rates(self, speciation_rates):
		"""Add speciation rates for analysis at the end of the simulation. This is optional

		:param list speciation_rates: a list of speciation rates to apply at the end of the simulation
		"""
		self.speciation_rates.extend(speciation_rates)

	def calculate_sql_database(self):
		"""
		Saves the output database location to self.output_database.
		"""
		self.output_database = os.path.join(self.output_directory, "data_{}_{}.db".format(str(self.job_type),
																						  str(self.seed)))

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

		:raises TypeError: if a dispersal map or death map is specified, we must have a fine map specified, but
			not a coarse map.

		:raises IOError: if one of the required maps does not exist

		:return: None
		"""
		if self.is_spatial:
			Landscape.check_maps(self)
			if self.grid.file_name == "set" and \
					self.sample_map.x_offset + self.grid.x_size > self.sample_map.x_size or \
					self.sample_map.y_offset + self.grid.y_size > self.sample_map.y_size:
				raise ValueError("Grid is not within the sample map - please check offsets of sample map.")
			# Now check our combination of dispersal map, death map and infinite landscape with our fine/coarse maps
			# makes sense
			if self.dispersal_map.file_name not in {"none", None}:
				if self.coarse_map.file_name not in {None, "none"}:
					raise TypeError("Cannot use a coarse map if using a dispersal map. "
									"This feature is currently unsupported.")
			if self.death_map.file_name not in {None, "none", "null"}:
				if self.coarse_map.file_name not in {None, "none", "null"}:
					raise TypeError("Cannot use a coarse map if using a death map. "
									"This feature is currently unsupported.")

	def run_checks(self, expected=False):
		"""
		Check that the simulation is correctly set up and that all the required files exist.

		:param expected: set to true if we expect the output file to already exist

		:raises RuntimeError: if previous set-up routines are not complete
		"""
		if self.is_setup_map and self.is_setup_param:
			self.check_maps()
		else:
			err = "Set up of maps or parameters is incomplete."
			raise RuntimeError(err)
		self.check_sql_database(expected=expected)

	def run(self):
		"""
		Convenience function which completes setp, runs the simulation and calculates the coalescence tree for the set
		speciation rates in one step.

		:rtype: None
		"""
		self.finalise_setup()
		self._run_and_output()

	def _run_and_output(self):
		"""
		Runs the simulation and outputs to the database. Should only be called internally.

		:return:
		"""
		if self.run_coalescence():
			self.apply_speciation_rates()
		else:
			self.logger.warning("Simulation did not complete in time specified.\n")
			self.logger.warning("Resume with extra time to continue.\n")

	def run_coalescence(self):
		"""
		Attempt to run the simulation with the given simulation set-up.
		This is the main routine performing the actual simulation which will take a considerable amount of time.

		:return: True if the simulation completes successfully, False if the simulation pauses.

		:rtype: bool
		"""
		if self.is_setup_complete:
			# Make the output directory if it doesn't yet exist
			if not os.path.exists(self.output_directory):
				os.makedirs(self.output_directory)
			# Call the C++ object and run the simulation
			return self.c_simulation.run()
		else:
			raise RuntimeError("Set up is incomplete.")

	def apply_speciation_rates(self, speciation_rates=None):
		"""
		Applies the speciation rates to the coalescence tree and outputs to the database.

		:param speciation_rates: a list of speciation rates to apply

		:rtype: None
		"""
		if speciation_rates:
			for each in speciation_rates:
				self.speciation_rates.append(each)
			self.speciation_rates = [x for x in set(self.speciation_rates)]
		self.c_simulation.apply_speciation_rates(self.speciation_rates)

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
