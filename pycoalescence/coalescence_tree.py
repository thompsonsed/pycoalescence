"""
Contains basic analyses for the output of a pycoalescence simulation.
"""
from __future__ import absolute_import
import os
import subprocess
import logging
import random
import math
import numpy as np
import sqlite3
from collections import defaultdict

try:
	from math import isclose
except ImportError:
	# Python 2 compatibility
	def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
		"""
		:param a: value 1
		:param b: value 2
		:param rel_tol: percentage relative to larger value
		:param abs_tol: absolute value for similarity
		:return: true for significantly different a and b, false otherwise
		"""
		return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
e_list = []
try:
	try:
		from .build import applyspecmodule
	except ImportError as ie:
		e_list.append(ie)
		from build import applyspecmodule
	ApplySpecError = applyspecmodule.ApplySpecError
	applyspec_import = True
except ImportError as ie:
	logging.warn("Could not import the apply speciation module. Using deprecated mode.")
	e_list.append(ie)
	for each in e_list:
		logging.warn(str(each))
	applyspecmodule = None
	applyspec_import = False


	# Empty class for exception handling
	class ApplySpecError(Exception):
		pass

import warnings
import sys
import json
# import pdb

from .system_operations import execute_log_info, mod_directory, create_logger, write_to_log
import pycoalescence

# Reads the parameter descriptions from the json file.
try:
	with open(os.path.join(mod_directory, "reference", "parameter_descriptions.json")) as f:
		_parameter_descriptions = json.load(f)
except FileNotFoundError:
	logging.error("Could not find parameter dictionary. Check install is complete.")


def get_parameter_description(key=None):
	"""
	Gets the parameter descriptions for the supplied key. If the key is None, returns all keys.

	:param key: the simulation parameter

	:return: string containing the parameter description or a dict containing all values if no key is supplied
	"""
	if key is None:
		return _parameter_descriptions
	try:
		return _parameter_descriptions[key]
	except ValueError:
		raise ValueError("Key {} was not found in parameter dictionary. Use key=None to show the whole dictionary")


def check_sql_table_exist(database, table_name):
	"""
	Checks that the supplied table exists in the supplied database.

	:param database: the database to check existence in
	:param table_name: the table name to check for

	:return: boolean of whether the table exists
	:rtype: bool
	"""
	opened_here = False
	if isinstance(database, str):
		opened_here = True
		database = sqlite3.connect(database)
	cursor = database.cursor()
	table_names = [x[0] for x in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
	if opened_here:
		database.close()
		database = None
	return table_name in table_names


def fetch_table_from_sql(database, table_name):
	"""
	Returns a list of the data contained by the provided table in the database.

	:raises sqlite3.OperationalError: if the table is not contained in the database (protects SQL injections).

	:param database: the database to obtain from
	:param table_name: the table name to fetch data from
	:return: a list of lists, containing all data within the provided table in the database
	"""
	try:
		db = sqlite3.connect(database)
		c = db.cursor()
		if not check_sql_table_exist(db, table_name):
			raise sqlite3.OperationalError("Table {} does not exist in database.".format(table_name))
		c.execute("SELECT * FROM {}".format(table_name))
		out = [list(x) for x in c.fetchall()]
		db.close()
		db = None
		return out
	except sqlite3.OperationalError as soe:
		raise IOError("Cannot fetch {} from database {}: {}".format(table_name, database, soe))


class CoalescenceTree(object):
	"""
	Contains the coalescence tree and performs various calculations of different biodiversity metrics, which are then
	stored in the SQLite database.

	The general process is

	* Import the database (:py:meth:`~set_database`) and import the comparison data,
	  if required (:py:meth:`~import_comparison_data`)

	* Apply additional speciation rates (if required) using :py:meth:`~set_speciation_params` and then
	  :py:meth:`~apply_speciation`

	* Calculate required metrics (such as :py:meth:`~calculate_fragment_richness`)
	* Optionally, calculate the goodness of fit (:py:meth:`~calculate_goodness_of_fit`)
	"""

	def __init__(self, database=None, logging_level=logging.WARNING, log_output=None):
		"""
		Initiates the CoalescenceTree object. By default, links to the SpeciationCounter program stored in
		build/default/SpeciationCounter, but optionally takes speciation_program as a path to an alternative program.

		:param database: optionally specify the path to call :py:meth:`~set_database` to
		:param logging_level: the level from the logging module for desired terminal outputs
		:param log_output: optionally provide a file to output information to instead
		:return: None
		"""
		# speciation objects
		self.equalised = False
		self.is_setup_speciation = False
		self.record_spatial = False
		self.time_config_file = "null"
		self.sample_file = "null"
		self.record_fragments = False
		self.speciation_simulator = None
		self.applied_speciation_rates_list = []
		# Other objects
		self.is_complete = False
		self.total_individuals = 0
		self.comparison_abundances_whole = None
		self.comparison_file = None
		self.file = None
		self.database = None
		self.cursor = None
		self.fragments = []
		self.fragment_abundances = []
		self.comparison_data = None
		self.comparison_abundances = None
		self.comparison_octaves = None
		# Protracted parameters
		self.protracted_speciation_min = None
		self.protracted_speciation_max = None
		# Metacommunity parameters
		self.metacommunity_size = None
		self.metacommunity_speciation_rate = None
		# Support for deprecated methods
		self.apply_spec_module = applyspecmodule
		self.logger = logging.Logger("applyspeclogger")
		self.logging_level = logging_level
		self._create_logger(file=log_output)
		if not applyspec_import:
			self.setup(os.path.join(mod_directory, "build/default/SpeciationCounter"))
		if database is not None:
			self.set_database(database)

	def __del__(self):
		"""
		Closes the database connection.
		"""
		if self.database is not None:
			self.cursor = None
			self.database.close()
			self.database = None
		for handler in self.logger.handlers:
			handler.close()
			self.logger.removeHandler(handler)

	def _create_logger(self, file=None, logging_level=None):
		"""
		Creates the logger for use with applying speciation rates to a simulation.
		This function should only be run during :py:meth:`~__init__`

		.. tip:: Supply your own logger by over-riding :attr:`~import_comparison_data`.

		:param file: file to write output to. If None, outputs to terminal
		:param logging_level: the logging level to use (defaults to INFO)

		:return: None
		"""
		if logging_level is None:
			logging_level = self.logging_level
		self.logger = create_logger(self.logger, file, logging_level)

	def _check_fragment_numbers_match(self):
		"""
		Checks that the numbers of individuals match between the comparison_abundances object and the simulation
		database for each fragment

		:return: boolean, true if the numbers match
		:rtype: bool
		"""
		if not self.fragment_abundances:
			self.calculate_fragment_abundances()
		if self.comparison_abundances is None:
			if self.comparison_file is not None:
				self.import_comparison_data(self.comparison_file)
			else:
				raise ValueError("Cannot check matched numbers before importing comparison database.")
		for fragment in set([x[0] for x in self.fragment_abundances]):
			for ref in set([x[3] for x in self.fragment_abundances]):
				sum_simulated = sum([x[2] for x in self.fragment_abundances if x[0] == fragment and
									 x[3] == ref])
				if sum_simulated != sum([x[2] for x in self.comparison_abundances if x[0] == fragment]):
					return False
		return True

	def _equalise_fragment_number(self, fragment, reference):
		"""
		Equalises the number of individuals in the provided fragment, altering comparison_abundances and fragments so
		that the numbers are equal between the two.

		:param fragment: the fragment to alter
		:param reference: the reference key for the calculated community parameters

		:rtype: None
		"""
		total_fragments = sum([x[2] for x in self.fragment_abundances if x[0] == fragment and x[3] == reference])
		if total_fragments == 0:
			self.logger.debug("No individuals found in simulated data for fragment {}\n".format(fragment))
		total_comparison = sum([x[2] for x in self.comparison_abundances if x[0] == fragment])
		if total_comparison == 0:
			self.logger.debug("No individuals found in comparison data for fragment {}\n".format(fragment))
		difference = total_fragments - total_comparison
		if difference > 0:
			# need to remove individuals from fragments
			while difference != 0:
				# pick a random individual
				rand_individual = random.randint(0, total_fragments - 1)
				tmp_total = 0
				for i, f in enumerate(self.fragment_abundances):
					if f[0] == fragment and f[3] == reference:
						tmp_total += f[2]
						if tmp_total > rand_individual:
							if f[2] > 0:
								self.fragment_abundances[i][2] -= 1
								difference -= 1
								total_fragments -= 1
								break
		elif difference < 0:
			# need to remove individuals from comparison_abundances
			while difference != 0:
				# pick a random individual
				rand_individual = random.randint(0, total_comparison - 1)
				tmp_total = 0
				for i, f in enumerate(self.comparison_abundances):
					if f[0] == fragment:
						tmp_total += f[2]
						if tmp_total > rand_individual:
							if f[2] > 0:
								self.comparison_abundances[i][2] -= 1
								difference += 1
								total_comparison -= 1
								break
		self.comparison_abundances = [x for x in self.comparison_abundances if x[2] != 0]
		self.fragment_abundances = [x for x in self.fragment_abundances if x[2] != 0]

	def _equalise_all_fragment_numbers(self):
		"""
		Equalises the numbers in the fragments, removing individuals randomly from either the comparison_abundances or
		fragments objects so that the numbers are preserved.

		This is called automatically during importing the data for calculating comparison octaves, and should be called
		after importing all data, and before performing and goodness-of-fits.

		.. note:: Does not override the FRAGMENT_ABUNDANCES table - use adjust_fragment_abundances for this

		:return: None
		:rtype: None
		"""
		if self.equalised:
			return
		if not self.fragment_abundances:
			self.calculate_fragment_abundances()
		if not self.fragment_abundances or self.comparison_abundances is None:
			raise ValueError("Cannot equalise fragment numbers if comparison or simulation data is missing.")
		random.seed(self.get_simulation_parameters()['seed'])
		for fragment in set([x[0] for x in self.fragment_abundances]):
			for reference in set([x[3] for x in self.fragment_abundances]):
				self._equalise_fragment_number(fragment, reference)
		# now double check numbers match
		if not self._check_fragment_numbers_match():
			raise SystemError("Failure attempting to equalise fragment numbers.")
		else:
			self.equalised = True

	def _adjust_species_abundances(self):
		"""
		Recalculates the species abundances from the equalised fragment abundances and writes over the
		SPECIES_ABUNDANCES table
		"""
		if not self.equalised:
			self._equalise_all_fragment_numbers()
		species_abundances = []
		id = 0
		for reference in set([x[3] for x in self.fragment_abundances]):
			reference_subset = [x for x in self.fragment_abundances if x[3] == reference]
			for species_id in set([x[1] for x in reference_subset]):
				id += 1
				total = sum([x[2] for x in reference_subset if x[1] == species_id])
				species_abundances.append([id, species_id, total, reference])
		self._check_database()
		self.cursor.execute("DROP TABLE IF EXISTS SPECIES_ABUNDANCES")
		self.cursor.execute("CREATE TABLE SPECIES_ABUNDANCES (ID INT NOT NULL PRIMARY KEY, species_id INT NOT NULL,"
							"no_individuals INT NOT NULL, community_reference INT NOT NULL)")
		self.cursor.executemany("INSERT INTO SPECIES_ABUNDANCES VALUES(?,?,?,?)", species_abundances)
		self.database.commit()

	def _adjust_fragment_abundances(self):
		"""
		Equalises fragment abundances with the comparison data, and overrides the FRAGMENT_ABUNDANCES table in the
		output database.
		"""
		self._check_database()
		if not self.equalised:
			self._equalise_all_fragment_numbers()
		self.cursor.execute("DROP TABLE IF EXISTS FRAGMENT_ABUNDANCES")
		self.cursor.execute("CREATE TABLE FRAGMENT_ABUNDANCES (fragment TEXT NOT NULL, species_id INT NOT NULL,"
							" no_individuals INT NOT NULL, community_reference INT NOT NULL)")
		self.cursor.executemany("INSERT INTO FRAGMENT_ABUNDANCES VALUES(?,?,?,?)", self.fragment_abundances)
		self.database.commit()

	def _adjust_species_richness(self):
		"""
		Recalculates the species richnesses equating numbers from the comparison data.
		"""
		self._check_database()
		if not self.equalised:
			self._adjust_fragment_abundances()
			self._adjust_species_abundances()
		self.cursor.execute("DROP TABLE IF EXISTS SPECIES_RICHNESS")
		self.calculate_richness()


	def _check_database(self):
		"""
		Checks that the database has been opened and raises an error if it has not.
		Otherwise, makes sure that self.cursor is linked to the database
		:raises RuntimeError: if the database is None (has not been successfully imported).
		"""
		if self.database is None:
			raise RuntimeError("Database has not yet been successfully imported. Can't perform calculations.")
		self.cursor = self.database.cursor()

	def _clear_goodness_of_fit(self):
		"""
		Clears the goodness of fit calculations from the database.
		"""
		self._check_database()
		if check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):
			self.cursor.execute("DELETE FROM BIODIVERSITY_METRICS WHERE metric LIKE 'goodness_%'")

	def _get_comparison_plot_data(self):
		"""
		Gets the plot data table containing fragment names and numbers of individuals in each fragment.
		"""
		if self.comparison_file is None or not os.path.exists(self.comparison_file):
			raise ValueError("Cannot get plot data from comparison file {}".format(self.comparison_file))
		db = sqlite3.connect(self.comparison_file)
		c = db.cursor()
		plot_data = c.execute("SELECT fragment, no_individuals FROM PLOT_DATA").fetchall()
		db.close()
		db = None
		return [x for x in plot_data]

	def _get_sim_parameters_guild(self, guild):
		"""
		Gets the simulation parameters associated with this particular guild.
		:param guild: the guild number to obtain reference numbers for
		:return: dictionary containing simulation parameters for the given guild
		"""
		self._check_database()
		try:
			self.cursor.execute("SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme, sample_size, "
								"max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, gen_since_pristine, "
								"time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
								"coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, "
								"fine_map_x_offset, fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, "
								"sample_x_offset, sample_y_offset, pristine_coarse_map, "
								" pristine_fine_map, sim_complete, dispersal_method, m_probability, cutoff,"
								" infinite_landscape,  protracted, min_speciation_gen, max_speciation_gen, dispersal_map"
								" FROM SIMULATION_PARAMETERS WHERE guild == ?", (guild,))
		except sqlite3.OperationalError as e:
			self.logger.error("Failure to get SIMULATION_PARAMETERS table from database with guild {}"
							  ". Check table exists.".format(guild))
			raise e
		out = self.cursor.fetchone()
		if len(out) == 0 :
			raise ValueError("No simulation parameters exist for guild {}".format(guild))
		column_names = [member[0] for member in self.cursor.description]
		values = [x for x in out]
		if sys.version_info[0] is not 3:
			for i, each in enumerate(values):
				if isinstance(each, unicode):
					values[i] = each.encode('ascii')
		# Now convert it into a dictionary
		return dict(zip(column_names, values))

	def setup(self, speciation_program=os.path.join(mod_directory, "build/default/SpeciationCounter")):
		"""
		Sets up the link to the SpeciationCounter program. Defaults to the build/default/SpeciationCounter
		:param speciation_program: optionally provide a path to an alternative SpeciationCounter program.

		.. deprecated:: 1.2.4
			Deprecated due to movement towards using python API for applying speciation rates.

		:return: None
		"""
		self.speciation_simulator = speciation_program
		if not os.path.exists(self.speciation_simulator):
			raise IOError("Speciation simulator " + self.speciation_simulator +
						  " not found. Check file path and access.")

	def set_database(self, filename):
		"""
		Sets the database to the specified file and opens the sqlite connection.

		This must be done before any other operations can be performed and the
		file must exist.

		:raises IOError: if the simulation is not complete, as analysis can only be performed on complete simulations.
		 However, the database WILL be set before the error is thrown, allowing for analysis of
		 incomplete simulations if the error is handled correctly.

		:param filename: the SQLite database file to import
		"""
		if isinstance(filename, pycoalescence.simulation.Simulation):
			filename = filename.output_database
			if filename is None:
				raise RuntimeError("Coalescence object does has not been set up properly and does not contain an output"
								   " database location.")
		if os.path.exists(filename):
			self.file = filename
			try:
				self.database = sqlite3.connect(filename)
			except sqlite3.OperationalError as e:
				try:
					self.database.close()
				except AttributeError:
					pass
				self.database = None
				raise IOError("Error opening SQLite database: " + str(e))
			# Now make sure that the simulation has been completed
			try:
				self.cursor = self.database.cursor()
				sql_fetch = \
					self.cursor.execute("SELECT sim_complete, time_config_file FROM SIMULATION_PARAMETERS").fetchall()[
						0]
				# print(sql_fetch)
				complete = bool(sql_fetch[0])
				if sql_fetch[1] != "null":
					self.time_config_file = str(os.path.abspath(sql_fetch[1]))
				if not complete:
					self.is_complete = False
					raise IOError(filename + " is not a complete simulation. Please finish " \
											 "simulation before performing analysis.")
				else:
					self.is_complete = True
			except sqlite3.OperationalError as soe:
				self.database.close()
				raise sqlite3.OperationalError("Error checking simulation was complete: " + str(soe))
			except IndexError:
				self.database.close()
				raise sqlite3.OperationalError("Could not fetch SIMULATION_PARAMETERS. Table contains no data.")
		else:
			raise IOError("File " + filename + " does not exist.")

	def set_speciation_params(self, record_spatial, record_fragments, speciation_rates, sample_file=None,
							  time_config_file=None, protracted_speciation_min = None, protracted_speciation_max = None,
							  metacommunity_size=None, metacommunity_speciation_rate=None):
		"""

		Set the parameters for the application of speciation rates. If no config files or time_config files are provided,
		they will be taken from the main coalescence simulation.

		:rtype: None
		:param bool, str record_spatial: a boolean of whether to record spatial data
		:param bool, str record_fragments: either a csv file containing fragment data, or T/F for whether fragments should be
			calculated from squares of continuous habitat.
		:param list speciation_rates: a list of speciation rates to apply
		:param str sample_file: a sample tif or csv specifying the sampling mask
		:param str time_config_file: a configuration file of temporal sampling points
		:param float protracted_speciation_min: the minimum number of generations required for speciation to occur
		:param float protracted speciation_max: the maximum number of generations before speciation occurs
		:param float metacommunity_size: the size of the metacommunity to apply
		:param float metacommunity_speciation_rate: speciation rate for the metacommunity
		"""
		if isinstance(record_fragments, bool):
			if record_fragments:
				record_fragments = "null"
			else:
				record_fragments = "F"
		if record_fragments is "T":
			record_fragments = "null"
		if speciation_rates is None:
			raise RuntimeError("No speciation rates supplied: requires at least 1 for analysis.")
		if record_spatial is "T":
			record_spatial = True
		elif record_spatial is "F":
			record_spatial = False
		elif not isinstance(record_spatial, bool):
			raise TypeError("record_spatial must be a boolean.")
		if metacommunity_size is not None and metacommunity_speciation_rate is not None:
			if metacommunity_size > 0 and metacommunity_speciation_rate > 0:
				self.metacommunity_size = metacommunity_size
				self.metacommunity_speciation_rate = metacommunity_speciation_rate
			else:
				raise ValueError("Must supply both metacommunity size >0 and speciation rate >0 and < 1 for applying"
								 "a metacommunity.")
		else:
			self.metacommunity_size = 0
			self.metacommunity_speciation_rate = 0.0
		if protracted_speciation_max is not None and protracted_speciation_min is not None:
			if not self.is_protracted():
				raise ValueError("Supplied protracted parameters for a non-protracted simulation.");
			else:
				self.protracted_speciation_min = protracted_speciation_min
				self.protracted_speciation_max = protracted_speciation_max
		else:
			self.protracted_speciation_min = 0.0
			self.protracted_speciation_max = 0.0
		if not self.is_setup_speciation:
			self.record_spatial = record_spatial
			self.record_fragments = record_fragments
			if sample_file is None:
				warnings.warn("No sample file provided, defaulting to null.", RuntimeWarning)
				self.sample_file = "null"
			else:
				self.sample_file = sample_file
			if self.time_config_file is None:
				if time_config_file is None:
					warnings.warn("No time config file provided, defaulting to null.", RuntimeWarning)
					self.time_config_file = "null"
				else:
					self.time_config_file = time_config_file
			self.applied_speciation_rates_list = speciation_rates
		else:
			warnings.warn("Speciation parameters already set.", RuntimeWarning)
		if self.sample_file == "null" and self.record_fragments == "null":
			raise ValueError("Cannot specify a null samplemask and expect automatic fragment detection; "
							 "provide a samplemask or set record_fragments=False.")

	def apply_speciation(self):
		"""
		Creates the list of speciation options and performs the speciation analysis by calling SpeciationCounter.
		This must be run after the main coalescence simulations are complete.
		It will create additional fields and tables in the SQLite database which contains the requested data.
		"""
		# Check file exists
		if self.time_config_file is None:
			self.time_config_file = "null"
		if not os.path.exists(self.file):
			warnings.warn(str("Check file existance for " + self.file +
							  ". Potential lack of access (verify that definition is a relative path)."),
						  RuntimeWarning)
		# Convert fragment file to null if it is true
		# Log warning if sample file is null and record fragments is true
		if applyspec_import:
			try:
				self.apply_spec_module.set_logger(self.logger)
				self.apply_spec_module.set_log_function(write_to_log)
				self.apply_spec_module.apply(self.file, self.record_spatial, self.sample_file,
											 self.time_config_file, self.record_fragments,
											 self.applied_speciation_rates_list, self.protracted_speciation_min,
											 self.protracted_speciation_max, self.metacommunity_size,
											 self.metacommunity_speciation_rate)
			except TypeError as te:
				raise te
			except Exception as e:
				raise ApplySpecError(str(e))
		else:
			logging.warning("Using deprecated speciation application method.")
			sim_list = [self.speciation_simulator, self.file, self.record_spatial, self.sample_file,
						self.time_config_file, self.record_fragments]
			sim_list.extend([str(x) for x in self.applied_speciation_rates_list])
			sim_list_str = [str(x) for x in sim_list]
			try:
				execute_log_info(sim_list_str)
			except subprocess.CalledProcessError as cpe:
				warnings.warn("CalledProcessError while applying speciation rates: " +
							  ",".join([str(x) for x in sim_list_str]))
				raise cpe

	def get_richness(self, reference=1):
		"""
		Get the system richness for the parameters associated with the supplied community reference.

		.. note::

			Richness of 0 is returned if there has been some problem; it is assumed that species richness
			will be above 0 for any simulation.

		.. note:: Values generated by this method should be identical to those produced by self.get_landscape_richness()

		:param reference: community reference which contains the parameters of interest
		:return: the system species richness
		"""
		self._check_database()
		try:
			c = self.cursor.execute("SELECT species_id FROM SPECIES_ABUNDANCES WHERE no_individuals > 0 AND "
									"community_reference == ?", (reference,)).fetchall()
			return len(set([x[0] for x in c]))
		except sqlite3.OperationalError as oe:
			self.logger.warning(str(oe) + "\n")
			self.logger.warning("Could not find SPECIES_ABUNDANCES table in database " + self.file + "\n")
			return 0

	def get_octaves(self, reference):
		"""
		Get the pre-calculated octave data for the parameters associated with the supplied reference.
		This will call self.calculate_octaves() if it hasn't been called previously.

		Returns are of form [id, 'whole', time, speciation rate, octave class, number of species]

		:param reference: community reference which contains the parameters of interest
		:return: output from FRAGMENT_OCTAVES on the whole landscape for the selected variables
		"""
		self._check_database()
		if check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
			self.calculate_octaves()
		return self.get_fragment_octaves(fragment="whole", reference=reference)

	def get_number_individuals(self, fragment=None, community_reference=None):
		"""
		Gets the number of individuals that exist, either in the provided fragment, or on the whole landscape.
		Counts individuals from FRAGMENT_ABUNDANCES or SPECIES_ABUNDANCES, respectively.

		If a community reference is provided, only individuals for that time slice will be counted, otherwise a mean is
		taken across time slices.

		:param fragment: the name of the fragment to get a count of individuals from
		:return: the number of individuals that exists in the desired location
		"""
		self._check_database()
		if fragment:
			if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
				raise RuntimeError("Cannot get a count from a fragment without calculating fragment abundances.")
			if not community_reference:
				return self.cursor.execute("SELECT SUM(no_individuals)/COUNT(DISTINCT(community_reference))"
										   " FROM FRAGMENT_ABUNDANCES WHERE fragment == ?", (fragment, )).fetchone()[0]
			else:
				return self.cursor.execute("SELECT SUM(no_individuals) FROM FRAGMENT_ABUNDANCES "
										   "WHERE community_reference==?", (community_reference,)).fetchone()[0]
		else:
			if not check_sql_table_exist(self.database, "SPECIES_ABUNDANCES"):
				raise RuntimeError("No species abundances table to fetch data from. Ensure your simulation is complete.")
			if not community_reference:
				return self.cursor.execute("SELECT SUM(no_individuals)/COUNT(DISTINCT(community_reference)) "
										   "FROM SPECIES_ABUNDANCES").fetchone()[0]
			else:
				return self.cursor.execute("SELECT SUM(no_individuals) FROM SPECIES_ABUNDANCES "
										   "WHERE community_reference==?", (community_reference,)).fetchone()[0]

	def check_biodiversity_table_exists(self):
		"""
		Checks whether the biodiversity table exists and creates the table if required.
		
		:return: the max reference value currently existing
		"""
		self._check_database()
		tmp_create = "CREATE TABLE BIODIVERSITY_METRICS (ref INT PRIMARY KEY NOT NULL, metric TEXT NOT NULL," \
					 " fragment TEXT NOT NULL, community_reference INT NOT NULL," \
					 " value FLOAT NOT NULL, simulated FLOAT, actual FLOAT)"
		if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):
			try:
				self.cursor.execute(tmp_create)
				self.database.commit()
			except sqlite3.OperationalError as e:
				raise sqlite3.OperationalError("Error creating biodiversity metric table: " + str(e))
			return 0
		else:
			maxval = self.database.cursor().execute("SELECT MAX(ref) FROM BIODIVERSITY_METRICS").fetchone()[0]
			if maxval is None:
				return 0
			return maxval

	def calculate_richness(self):
		"""
		Calculates the landscape richness from across all fragments and stores result in a new table in
		SPECIES_RICHNESS
		Stores a separate result for each speciation rate and time.
		"""
		self._check_database()
		spec_abundances = self.cursor.execute("SELECT species_id, community_reference, no_individuals FROM "
											  "SPECIES_ABUNDANCES WHERE no_individuals>0").fetchall()
		tmp_create = "CREATE TABLE SPECIES_RICHNESS (ref INT PRIMARY KEY NOT NULL, community_reference INT NOT NULL," \
					 " richness INT NOT NULL)"
		if not check_sql_table_exist(self.database, "SPECIES_RICHNESS"):
			ref = 0
			try:
				self.cursor.execute(tmp_create)
				self.database.commit()
			except Exception as e:
				e.message = "Error creating SPECIES_RICHNESS table: " + str(e)
				raise e
		else:
			ref = self.cursor.execute("SELECT COUNT(ref) FROM SPECIES_RICHNESS").fetchone()[0]
		references = set([x[1] for x in spec_abundances])
		output = []
		for reference in references:
			select = [x[0] for x in spec_abundances if x[1] == reference]
			output.append([ref, reference, len(select)])
			ref += 1
		ref = self.check_biodiversity_table_exists()
		bio_output = []
		for x in output:
			ref += 1
			tmp = [ref, "fragment_richness", "whole"]
			tmp.extend([x[1], x[2]])
			bio_output.append(tmp)
		self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES (?, ?, ?, ?, ?, NULL, NULL)", bio_output)
		self.cursor.executemany("INSERT INTO SPECIES_RICHNESS VALUES(?,?,?)", output)
		self.database.commit()

	def get_landscape_richness(self, reference=1):
		"""
		Reads the landscape richness from the SPECIES_RICHNESS table in the database. Returns the richness for
		each speciation rate and time.

		.. note:: This should produce the same result as get_richness(sr, t) with the corresponding sr and t.

		.. note::

			Return type of this function changes based on whether speciation rates and times were supplied.
			If they were, returns a single integer. Otherwise, returns a list of all species richnesses.

		:param speciation_rate: the required speciation rate (optional)
		:param reference: the reference key for the calculated community parameters

		:return: either a list containing the speciation_rate, time, richness OR (if specific speciation rate and time
		 provided), the species richness at that time and speciation rate.

		:rtype: int, list
		"""
		self._check_database()
		try:
			return self.cursor.execute("SELECT richness FROM SPECIES_RICHNESS "
									   "WHERE community_reference==?", (reference,)).fetchone()[0]
		except sqlite3.OperationalError as oe:
			oe = sqlite3.OperationalError("Could not get SPECIES_RICHNESS table: " + str(oe))
			raise oe
		except TypeError:
			return 0

	def calculate_fragment_abundances(self):
		"""
		Calculates the fragment abundances, including equalising with the comparison database, if it has already been
		set.

		Sets fragment_abundances object.
		"""
		if not self.fragment_abundances:
			self._check_database()
			if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
				raise RuntimeError("Database does not contain FRAGMENT_ABUNDANCES table.")
			self.fragment_abundances = [list(x) for x in
										self.cursor.execute("SELECT fragment, species_id,"
															" no_individuals, community_reference "
															"FROM FRAGMENT_ABUNDANCES").fetchall() if x[2] > 0]
			if not self.fragment_abundances:
				raise ValueError("Fragment abundances table may be empty, or not properly stored.")
			if self.comparison_abundances:
				self._equalise_all_fragment_numbers()
		else:
			self.logger.warning("Fragment abundances already imported.")

	def calculate_fragment_richness(self):
		"""
		Calculates the fragment richness and stores it in a new table called FRAGMENT_RICHNESS. Also adds the record to
		BIODIVERSITY METRICS for
		If the table already exists, it will simply be returned. Each time point and speciation rate combination will be
		recorded as a new variable.
		"""
		self._check_database()
		tmp_create = "CREATE TABLE FRAGMENT_RICHNESS (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL," \
					 " community_reference INT NOT NULL,  richness INT NOT NULL)"
		# First check the FRAGMENT_ABUNDANCES TABLE EXISTS
		if not self.fragment_abundances:
			self.calculate_fragment_abundances()
		# Now try and create FRAGMENT_RICHNESS
		if not check_sql_table_exist(self.database, "FRAGMENT_RICHNESS"):
			try:
				self.cursor.execute(tmp_create)
				self.database.commit()
			except sqlite3.OperationalError:
				raise sqlite3.OperationalError("Could not create FRAGMENT_RICHNESS table")
			fragment_names = set([fa[0] for fa in self.fragment_abundances])
			references = set([fa[3] for fa in self.fragment_abundances])
			# self.fragments.extend(([]*len(times)-1))
			ref = 0
			self.fragments = []
			for each in fragment_names:
				for reference in references:
					selection = [row for row in self.fragment_abundances if row[0] == each and row[3] == reference]
					self.fragments.append([ref, each, reference, len(selection)])
					ref += 1
			self.cursor.executemany("INSERT INTO FRAGMENT_RICHNESS VALUES(?, ?, ?, ?)", self.fragments)
			self.database.commit()
		self.fragments = [list(x) for x in self.cursor.execute("SELECT fragment, community_reference, richness"
															   " FROM FRAGMENT_RICHNESS").fetchall()]
		# Move fragment richnesses into BIODIVERSITY METRICS
		ref = self.check_biodiversity_table_exists()
		tmp_fragments = []
		for x in self.fragments:
			ref += 1
			tmp = [ref, "fragment_richness"]
			tmp.extend(x)
			tmp_fragments.append(tmp)
		self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES(?,?,?,?,?, NULL, NULL)", tmp_fragments)
		self.database.commit()
		self.calculate_richness()

	def calculate_alpha_diversity(self):
		"""
		Calculates the system alpha diversity for each set of parameters stored in COMMUNITY_PARAMETERS.
		Stores the output in ALPHA_DIVERSITY table.
		"""
		self._check_database()
		if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
			raise RuntimeError("Fragment abundances must be calculated before alpha diversity.")
		if not check_sql_table_exist(self.database, "ALPHA_DIVERSITY"):
			tmp_create = "CREATE TABLE ALPHA_DIVERSITY (reference INT PRIMARY KEY NOT NULL, " \
						 "alpha_diversity INT NOT NULL)"
			try:
				self.cursor.execute(tmp_create)
				self.database.commit()
			except sqlite3.OperationalError:
				raise sqlite3.OperationalError("Could not create ALPHA_DIVERSITY table")
			all_community_references = self.get_community_references()
			all_fragments = self.get_fragment_list()
			output = []
			for reference in all_community_references:
				total = 0
				for fragment in all_fragments:
					total += self.get_fragment_richness(fragment=fragment, reference=reference)
				alpha = total/len(all_fragments)
				output.append([reference, alpha])
			self.cursor.executemany("INSERT INTO ALPHA_DIVERSITY VALUES(?,?)", output)
			# Now also insert into BIODIVERSITY metrics
			ref = self.check_biodiversity_table_exists() + 1
			output = [[i + ref, "alpha_diversity", "whole", x[0], x[1]] for i, x in enumerate(output)]
			self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES(?,?,?,?,?, NULL, NULL)", output)
			self.database.commit()
		else:
			logging.warning("Alpha diversity already calculated.")

	def calculate_beta_diversity(self):
		"""
		Calculates the beta diversity for the system for each speciation parameter set and stores the output in
		BETA_DIVERSITY.
		Will calculate alpha diversity and species richness tables if they have not already been performed.
		"""
		self._check_database()
		tmp_create = "CREATE TABLE BETA_DIVERSITY (reference INT PRIMARY KEY NOT NULL, " \
					 "beta_diversity INT NOT NULL)"
		if not check_sql_table_exist(self.database, "ALPHA_DIVERSITY"):
			self.calculate_alpha_diversity()
		if not check_sql_table_exist(self.database, "SPECIES_RICHNESS"):
			self.calculate_richness()
		if not check_sql_table_exist(self.database, "BETA_DIVERSITY"):
			try:
				self.cursor.execute(tmp_create)
				self.database.commit()
			except sqlite3.OperationalError:
				raise sqlite3.OperationalError("Could not create BETA_DIVERSITY table")
			all_community_references = self.get_community_references()
			output = []
			for reference in all_community_references:
				beta = float(self.get_landscape_richness(reference))/float(self.get_alpha_diversity(reference))
				output.append([reference, beta])
			self.cursor.executemany("INSERT INTO BETA_DIVERSITY VALUES(?,?)", output)
			# Now also insert into BIODIVERSITY metrics
			ref = self.check_biodiversity_table_exists() + 1
			output = [[i + ref, "beta_diversity", "whole", x[0], x[1]] for i, x in enumerate(output)]
			self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES(?,?,?,?,?, NULL, NULL)", output)
			self.database.commit()
			self.database.commit()
		else:
			logging.warning("Beta diversity already calculated.")

	def get_alpha_diversity(self, reference=1):
		"""
		Gets the system alpha diversity for the provided community reference parameters.
		Alpha diversity is the mean number of species per fragment.
		:param reference: the community reference for speciation parameters
		:return: the alpha diversity of the system
		"""
		self._check_database()
		if not check_sql_table_exist(self.database, "ALPHA_DIVERSITY"):
			self.calculate_alpha_diversity()
		self.cursor.execute("SELECT alpha_diversity FROM ALPHA_DIVERSITY WHERE reference == ?", (reference,))
		res = self.cursor.fetchone()
		if res is None:
			raise ValueError("No alpha diversity value for reference = {}".format(reference))
		return res[0]

	def get_beta_diversity(self, reference=1):
		"""
		Gets the system beta diversity for the provided community reference parameters.
		Beta diversity is the true beta diversity (gamma / alpha).
		:param reference: the community reference for speciation parameters
		:return: the beta diversity of the system
		"""
		self._check_database()
		if not check_sql_table_exist(self.database, "BETA_DIVERSITY"):
			self.calculate_beta_diversity()
		self.cursor.execute("SELECT beta_diversity FROM BETA_DIVERSITY WHERE reference == ?", (reference,))
		res = self.cursor.fetchone()
		if res is None:
			raise ValueError("No beta diversity value for reference = {}.".format(reference))
		return res[0]

	def import_comparison_data(self, filename, ignore_mismatch=False):
		"""
		Imports the SQL database that contains the biodiversity metrics that we want to compare against.

		This can either be real data (for comparing simulated data) or other simulated data (for comparing between models).

		If the SQL database does not contain the relevant biodiversity metrics, they will be calculated (if possible) or skipped.

		The expected form of the database is the same as the BIODIVERSITY_METRICS table, except without any speciation
		rates or time references, and a new column containing the number of individuals involved in each metric.

		.. note::

			This also equalises the comparison data if ignore_mismatch is not True, so that the number of individuals
			is equal between the simulated and comparison datasets.

		:param str filename: the file containing the comparison biodiversity metrics.
		:param bool ignore_mismatch: set to true to ignore abundance mismatches between the comparison and simulated data.
		"""
		conn = sqlite3.connect(filename)
		tmp_cursor = conn.cursor()
		if self.comparison_file is not None:
			warnings.warn("Comparison data has already been imported.")
		try:
			if check_sql_table_exist(conn, "BIODIVERSITY_METRICS"):
				self.comparison_data = tmp_cursor.execute("SELECT metric, fragment, value, no_individuals"
														  " FROM BIODIVERSITY_METRICS").fetchall()
			try:
				self.comparison_abundances = [list(x) for x in tmp_cursor.execute(
					"SELECT fragment, species_id, no_individuals FROM FRAGMENT_ABUNDANCES").fetchall()]
				self.comparison_abundances_whole = [list(x) for x in tmp_cursor.execute(
					"SELECT species_id, no_individuals FROM SPECIES_ABUNDANCES").fetchall()]
			except sqlite3.OperationalError as oe:
				raise sqlite3.OperationalError("Problem executing fetches from comparison data: " + str(oe))
			self.comparison_file = filename
		except sqlite3.OperationalError as oe:
			conn = None
			raise RuntimeError("Could not import from comparison data: " + str(oe))
		conn = None
		if self.fragment_abundances:
			if not self._check_fragment_numbers_match() and not ignore_mismatch:
				self._equalise_all_fragment_numbers()

	def adjust_data(self):
		"""
		Ensures that the numbers of individuals are equalised between the comparison and simulated datasets, and
		modifies the relevant tables with the new data
		"""
		self._equalise_all_fragment_numbers()
		self._adjust_fragment_abundances()
		self._adjust_species_abundances()
		self._adjust_species_richness()

	def calculate_comparison_octaves(self, store=False):
		"""
		Calculates the octave classes for the comparison data and for fragments (if required).
		If the octaves exist in the FRAGMENT_OCTAVES table in the comparison database, the data will be imported
		instead of being re-calculated.

		Stores the new octave classes in self.comparison_octaves.

		.. note::

		 	If store is True, will store an EDITED version of the comparison octaves, such that the number of
			individuals is equal between the comparison and simulated data.

		:param store: if True, stores within the comparison database.
		"""
		if self.comparison_octaves is None:
			# If comparison_octaves has not been calculated, then do that now.
			if self.comparison_abundances is None:
				warnings.warn(
					"Comparison abundances not yet imported, or FRAGMENT_ABUNDANCES does not exist in comparison file.")
			# Check whether the FRAGMENT_OCTAVES table exists, if it is, just stored that in self.comparison_octaves
			if self.comparison_file is not None:
				# read the data from the database
				db = sqlite3.connect(self.comparison_file)
				c = db.cursor()
				if check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
					tmp_list = c.execute("SELECT fragment, octave, richness FROM FRAGMENT_OCTAVES").fetchall()
					if len(tmp_list) > 0:
						self.comparison_octaves = tmp_list
						store = False
			# Need to calculate again if the fragment numbers don't match
			if not self._check_fragment_numbers_match():
				self.comparison_octaves = None
			# Otherwise, if comparison abundances exists, we can calculate the comparison octaves manually
			if self.comparison_abundances is not None and self.comparison_octaves is None:
				if not self._check_fragment_numbers_match():
					self._equalise_all_fragment_numbers()
				# now calculate octaves
				self.comparison_octaves = []
				ref = 0
				fragments = set([x[0] for x in self.comparison_abundances])
				for f in fragments:
					octaves = [[], []]
					octaves[0] = []
					octaves[1] = []
					abundances = [x for x in self.comparison_abundances if str(x[0]) == f]
					# print(abundances)
					# exit(0)
					for each in abundances:
						this_octave = int(math.floor(math.log(each[2], 2)))
						if this_octave in octaves[0]:
							pos = [i for i, x in enumerate(octaves[0]) if x == this_octave]
							# print(octaves)
							self.comparison_octaves[octaves[1][pos[0]]][2] += 1
						else:
							self.comparison_octaves.append([str(f), this_octave, 1])
							# print(self.comparison_octaves)
							octaves[0].append(this_octave)
							octaves[1].append(ref)
							ref += 1
					# print(len(self.comparison_octaves)-1)
				octaves = [[], []]
				octaves[0] = []
				octaves[1] = []
				abundances = self.comparison_abundances_whole
				# print(abundances)
				# exit(0)
				for each in abundances:
					this_octave = int(math.floor(math.log(each[1], 2)))
					if this_octave in octaves[0]:
						pos = [i for i, x in enumerate(octaves[0]) if x == this_octave]
						# print(octaves)
						self.comparison_octaves[octaves[1][pos[0]]][2] += 1
					else:
						self.comparison_octaves.append(["whole", this_octave, 1])
						# print(self.comparison_octaves)
						octaves[0].append(this_octave)
						octaves[1].append(ref)
						ref += 1
				# now sort the list
			# If we want to store the comparison octaves, overwrite the original FRAGMENT_OCTAVES table (if it exists
			# with the new calculated data
			if store:
				if self.comparison_file is None:
					raise ValueError("Comparison file has not been imported yet, and therefore cannot be written to.")
				conn = sqlite3.connect(self.comparison_file)
				cursor = conn.cursor()
				cursor.execute("DROP TABLE IF EXISTS FRAGMENT_OCTAVES")
				cursor.execute(
					"CREATE TABLE FRAGMENT_OCTAVES (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL, "
					"octave INT NOT NULL, richness INT NOT NULL)")
				cursor.executemany("INSERT INTO FRAGMENT_OCTAVES VALUES(?,?,?,?)",
								   [[i, x[0], x[1], x[2]] for i, x in enumerate(self.comparison_octaves)])
				conn.commit()
			conn = None

	def calculate_octaves(self):
		"""
		Calculates the octave classes for the landscape. Outputs the calculated richness into the SQL database within a
		FRAGMENT_OCTAVES table.

		"""
		self._check_database()
		self.cursor.execute(
			"CREATE TABLE IF NOT EXISTS FRAGMENT_OCTAVES (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL, "
			"community_reference INT NOT NULL, octave INT NOT NULL, richness INT NOT NULL)")
		abundances = self.cursor.execute(
			"SELECT species_id, no_individuals, community_reference FROM SPECIES_ABUNDANCES"
			" WHERE no_individuals>0").fetchall()
		references = set([x[2] for x in abundances])
		# Check what the maximum reference is in FRAGMENT_OCTAVES
		try:
			c = self.cursor.execute("SELECT max(ref) FROM FRAGMENT_OCTAVES").fetchone()[0] + 1
		except (sqlite3.OperationalError, TypeError):
			c = 0
		for ref in references:
			select_abundances = [x[1] for x in abundances if x[2] == ref]
			log_select = [math.floor(math.log(x, 2)) for x in select_abundances]
			out = []
			try:
				for i in range(0, int(max(log_select)), 1):
					tot = log_select.count(i)
					out.append([c, "whole", ref, i, tot])
					c += 1
			except ValueError as ve:
				raise ve
			try:
				self.cursor.executemany("INSERT INTO FRAGMENT_OCTAVES VALUES (?,?,?,?,?)", out)
				self.database.commit()
			except sqlite3.OperationalError as oe:
				raise sqlite3.OperationalError("Could not insert into FRAGMENT_OCTAVES." + str(oe))

	def calculate_fragment_octaves(self):
		"""
		Calculates the octave classes for each fragment. Outputs the calculated richness into the SQL database within a
		FRAGMENT_OCTAVES table
		"""
		self._check_database()
		if check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
			raise RuntimeError("FRAGMENT_OCTAVES already exists")
		if self.fragment_abundances is None:
			self.calculate_fragment_abundances()
		if len(self.fragments) == 0:
			raise RuntimeError("Fragments not imported correctly")
		self.cursor.execute(
			"CREATE TABLE IF NOT EXISTS FRAGMENT_OCTAVES (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL, "
			"community_reference INT NOT NULL, octave INT NOT NULL, richness INT NOT NULL)")
		fragments = set([x[0] for x in self.fragment_abundances])
		references = set([x[3] for x in self.fragment_abundances])
		c = 0
		for f in fragments:
			for ref in references:
				select_abundances = [int(x[2]) for x in self.fragment_abundances if x[0] == f and x[3] == ref]
				if len(select_abundances) == 0:
					raise ValueError("Could not calculate fragment octaves for {}, with reference = {}".format(f, ref))
				log_select = [math.floor(math.log(x, 2)) for x in select_abundances]
				out = []
				for i in range(0, int(max(log_select)), 1):
					tot = log_select.count(i)
					out.append([c, f, ref, i, tot])
					c += 1
				try:
					self.cursor.executemany("INSERT INTO FRAGMENT_OCTAVES VALUES (?,?,?,?,?)", out)
				except sqlite3.OperationalError as oe:
					raise sqlite3.OperationalError("Could not insert into FRAGMENT_OCTAVES." + str(oe))
		self.database.commit()
		self.calculate_octaves()

	def get_fragment_richness(self, fragment=None, reference=None):
		"""
		Gets the fragment richness for each speciation rate and time for the specified simulation. If the fragment
		richness has not yet been calculated, it tries to calculate the fragment richness,

		:param fragment: the desired fragment (defaults to None)
		:param reference: the reference key for the calculated community parameters

		:raises: sqlite3.OperationalError if no table FRAGMENT_ABUNDANCES exists
		:raises: RuntimeError if no data for the specified fragment, speciation rate and time exists.

		:return: A list containing the fragment richness, or a value of the fragment richness
		"""
		self._check_database()
		if reference is None:
			if fragment is not None:
				raise SyntaxError("Must supply a reference when supplying a fragment.")
			if len(self.fragments) is 0:
				self.calculate_fragment_richness()
			return self.fragments
		elif fragment is None:
			raise SyntaxError("Must supply a fragment name when supplying a reference.")
		output = self.cursor.execute("SELECT richness FROM FRAGMENT_RICHNESS WHERE community_reference == ? AND "
									 "fragment ==  ?", (reference, fragment)).fetchall()
		if len(output) == 0:
			raise RuntimeError("No output while fetching fragment data.")
		else:
			return output[0][0]

	def get_fragment_abundances(self, fragment, reference):
		"""
		Gets the species abundances for the supplied fragment and community reference.
		:param fragment: the name of the fragment to obtain
		:param reference: the reference for speciation parameters to obtain for
		:return: a list of species ids and abundances
		"""
		self._check_database()
		if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
			raise RuntimeError("Fragments abundances must be calculated before attempting to get fragment abundances.")
		output = self.cursor.execute("SELECT species_id, no_individuals FROM FRAGMENT_ABUNDANCES WHERE "
									 "community_reference == ? AND fragment ==  ?", (reference, fragment)).fetchall()
		if len(output) == 0:
			raise RuntimeError("No output while fetching fragment data")
		return [list(x) for x in output]


	def get_fragment_list(self):
		"""
		Returns a list of all fragments that exist in FRAGMENT_ABUNDANCES.
		:return: list all all fragment names
		"""
		self._check_database()
		if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
			raise RuntimeError("Fragment abundances have not been calculated; cannot obtain fragment list.")
		fetch = self.cursor.execute("SELECT DISTINCT(fragment) FROM FRAGMENT_ABUNDANCES").fetchall()
		if len(fetch) == 0:
			raise sqlite3.OperationalError("No fragments exist in FRAGMENT_ABUNDANCES.")
		return [x[0] for x in fetch]

	def get_fragment_octaves(self, fragment=None, reference=None):
		"""
		Get the pre-calculated octave data for the specified fragment, speciation rate and time. If fragment and
		speciation_rate are None, returns the entire FRAGMENT_OCTAVES object
		This requires self.calculate_fragment_octaves() to have been run successfully at some point previously.

		Returns are of form [id, fragment, community_reference, octave class, number of species]

		:param fragment: the desired fragment (defaults to None)
		:param reference: the reference key for the calculated community parameters

		:return: output from FRAGMENT_OCTAVES for the selected variables
		"""
		self._check_database()
		if fragment is None and reference is None:
			return [list(x) for x in self.cursor.execute("SELECT fragment, community_reference, octave, richness"
														 " FROM FRAGMENT_OCTAVES")]
		elif fragment is None or reference is None:
			raise SyntaxError("Only one of fragment or reference supplied: must supply both, or neither.")
		try:
			output = [list(x) for x in self.cursor.execute("SELECT octave, richness FROM FRAGMENT_OCTAVES WHERE "
														   "community_reference == ? AND fragment == ?",
														   (reference, fragment)).fetchall()]
			if len(output) == 0:
				raise RuntimeError(
					"No output while fetching fragment data for {} with ref: {}".format(fragment, reference))
		except sqlite3.OperationalError as oe:
			raise sqlite3.OperationalError("Failure whilst fetching fragment octave data." + str(oe))
		output.sort(key=lambda x: x[0])
		return output

	def get_species_abundances(self, fragment=None, reference=None):
		"""
		Gets the species abundance for a particular fragment, speciation rate and time. If fragment is None, returns the
		whole landscape species abundances.

		:param fragment: the fragment to obtain the species abundance of. If None, returns landscape abundances.
		:param speciation_rate: speciation rate to obtain abundances for
		:param time: the time to obtain abundances for

		:return: list of species abundances [reference, species ID, speciation rate, number of individuals, generation]
		"""
		self._check_database()
		if fragment is None:
			return [list(x) for x in
					self.cursor.execute("SELECT species_id, no_individuals FROM SPECIES_ABUNDANCES WHERE "
										"community_reference==?", (reference,)).fetchall()]
		elif reference is None:
			raise RuntimeError("Must specify a community reference to get a fragment species abundance")
		else:
			return [list(x) for x in
					self.cursor.execute("SELECT species_id, no_individuals FROM FRAGMENT_ABUNDANCES WHERE"
										" fragment == ? AND "
										"community_reference == ?", (fragment, reference))]

	def calculate_octaves_error(self):
		"""
		Calculates the error in octaves classes between the simulated data and the comparison data.
		Stores each error value as a new entry in BIODIVERSITY_METRICS under fragment_octaves.
		Calculates the error by comparing each octave class and summing the relative difference.
		Octaves are then averaged for each fragment.
		"""
		if self.comparison_octaves is None:
			self.calculate_comparison_octaves()
		self._check_database()
		if not check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
			self.calculate_fragment_octaves()

		data = self.cursor.execute("SELECT fragment, community_reference FROM FRAGMENT_OCTAVES").fetchall()
		if len(data) == 0:
			self.calculate_fragment_octaves()
		try:
			self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN comparison FLOAT")
			self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN error FLOAT")
			col_add = True
		except sqlite3.OperationalError as soe:
			raise sqlite3.OperationalError("Could not alter FRAGMENT_OCTAVES table: " + str(soe))
		fragments = set([x[0] for x in data])
		references = set([x[1] for x in data])
		fragment_errors = []
		ref = self.check_biodiversity_table_exists()
		for f in fragments:
			comparison_octaves = [x for x in self.comparison_octaves if x[0] == f]
			for reference in references:
				octaves = self.get_fragment_octaves(f, reference)
				try:
					maxval = max(max([x[0] for x in octaves]), max([x[1] for x in comparison_octaves]))
				except ValueError:
					try:
						maxval = max([x[1] for x in comparison_octaves])
					except ValueError:
						try:
							maxval = max([x[0] for x in octaves])
						except ValueError:
							maxval = 0
				difference = []
				for i in range(0, maxval, 1):
					try:
						richness_val = [x[1] for x in octaves if x[0] == i][0]
					except (ValueError, IndexError):
						difference.append(1.0)
						continue
					try:
						comp_val = [x[2] for x in comparison_octaves if x[1] == i][0]
					except (ValueError, IndexError):
						difference.append(1.0)
						comp_val = 1.0
					else:
						## The error is calculated
						difference.append(
							float(max(richness_val, comp_val) - min(richness_val, comp_val)) / max(comp_val,
																								   richness_val))
					if col_add:
						self.cursor.execute("UPDATE FRAGMENT_OCTAVES SET comparison = ?, error = ? WHERE ref == ?",
											(comp_val, difference[-1], reference))
				# now average the errors
				ref += 1
				fragment_errors.append(
					[ref, "fragment_octaves", f, reference, float(sum(difference) / float(len(difference)))])

		self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES(?,?,?,?,?, NULL, NULL)", fragment_errors)
		self.database.commit()

	def calculate_goodness_of_fit(self):
		"""
		Calculates the goodness-of-fit measure based on the calculated biodiversity metrics, scaling each metric by the
		number of individuals involved in the metric.

		This requires that import_comparison_data() has already been successfully run.

		.. note::

			This doesn't calculate anything for values which have not yet been written to the
			BIODIVERSITY_METRICS table. All in-built functions (e.g. calculate_alpha_diversity,
			calculate_fragment_richness) write to the BIODIVERSITY_METRICS table automatically, so this is only relevant
			for custom functions.

		The resulting value will then be written to the BIODIVERSITY_METRICS table in the SQL database.
		"""
		# TODO fix this as it no longer works
		## check that the comparison data has already been imported.
		if self.comparison_data is None:
			raise RuntimeError("Comparison data not yet imported.")
		self._check_database()
		if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):
			raise ValueError("BIODIVERSITY_METRICS table does not exist in database: cannot calculate goodness of fit.")
		bio_metrics = self.cursor.execute(
			"SELECT metric, fragment, community_reference, value FROM BIODIVERSITY_METRICS"
			" WHERE metric != 'goodness_of_fit'").fetchall()
		if check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
			self.total_individuals = self.cursor.execute("SELECT COUNT(tip) FROM SPECIES_LIST"
														 " WHERE tip==1 AND gen_added==0.0").fetchone()[0]
			try:
				self.cursor.execute("SELECT comparison, error from FRAGMENT_OCTAVES")
			except sqlite3.OperationalError:
				self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN comparison FLOAT")
				self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN error FLOAT")
		# Remove the extra goodness of fit values
		bio_metrics = [b for b in bio_metrics if 'goodness_of_fit' not in b[0]]
		references = set([x[2] for x in bio_metrics])
		categories = set([f[0] for f in bio_metrics])
		# this will contain: metric, fragment, community_reference, relative_goodness_of_fit, num_individuals, simulated, actual
		# Get the plot data containing fragment names and total abundances [fragment, abundance]
		plot_data = self._get_comparison_plot_data()
		abundance_total = sum([p[1] for p in plot_data])
		# Calculate the error values for each metric and reference
		ref_bio = self.check_biodiversity_table_exists()
		output_SQL = []
		for category in categories:
			fragments = set([f[1] for f in bio_metrics if f[0] == category])
			select_comparison = [f for f in self.comparison_data if f[0] == category if f[1] in fragments]
			# Calculate the total number of individuals in this category
			if category != "fragment_octaves":
				try:
					total_ind = sum([f[3] for f in select_comparison])
				except IndexError:
					self.logger.warning("Could not find comparable metric for {} and {}".format(each[0], each[1]))
					continue
			else:
				total_ind = abundance_total
			# Now calculate the biodiversity metrics for each fragment
			ref_dict = defaultdict(list)

			for fragment in fragments:
				# TODO move this into a self-contained function (after unittesting)
				if category != "fragment_octaves":
					try:
						fragment_comparison = [f for f in select_comparison if f[1] == fragment][0]
					except IndexError:
						raise ValueError("Could not find comparable metric for"
										 " {}, in {}".format(category, fragment))
					actual_val = fragment_comparison[2]
					no_ind = fragment_comparison[3]
				else:
					actual_val = 0.0
					no_ind = [p[1] for p in plot_data if p[0] == fragment][0]
				for ref in references:
					select_metrics = [b for b in bio_metrics if b[0] == category and b[1] == fragment and b[2] == ref]
					if len(select_metrics) != 1:
						if len(select_metrics) == 0:
							raise ValueError("Could not find metric for metric, {}, fragment = {}"
											 " and community_reference = {}".format(category, fragment, ref))
						raise ValueError("Achieved multiple matches for biodiversity metrics"
										 " for fragment {} and community reference = {}.".format(fragment, ref))
					if category != "fragment_octaves":
						sim_val = select_metrics[0][3]
						scaled_fit = scale_simulation_fit(sim_val, actual_val, no_ind, total_ind)
						self.cursor.execute("UPDATE BIODIVERSITY_METRICS SET simulated = ?, actual = ?, value=?"
											" WHERE metric == ? AND fragment == ? AND community_reference == ?",
											(sim_val, actual_val, scaled_fit, category, fragment, ref))
					else:
						scaled_fit = (1 - select_metrics[0][3])*float(no_ind)/float(total_ind)
					ref_dict[ref].append(scaled_fit)
			name = "goodness_of_fit_{}".format(category)
			for ref in ref_dict.keys():
				value = sum(ref_dict[ref])
				ref_bio += 1
				output_SQL.append([ref_bio, name, "whole", ref, value, None, None])
		# Now generate out metrics for the whole system for each community reference
		for reference in references:
			value = sum([g[4] for g in output_SQL if g[3] == reference]) / len(categories)
			ref_bio += 1
			output_SQL.append([ref_bio, "goodness_of_fit", "whole", reference, value, None, None])
		self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES(?, ?, ?, ?, ?, ?, ?)", output_SQL)
		self.database.commit()

	def get_species_list(self):
		"""
		Gets the entirety of the SPECIES_LIST table, returning a tuple with an entry for each row. This can be used to
		construct custom analyses of the coalescence tree.

		.. note:: The species list will be produced in an unprocessed format

		:return: a list of each coalescence and speciation event, with locations, performed in the simulation

		:rtype: tuple
		"""
		self._check_database()
		return self.cursor.execute("SELECT * FROM SPECIES_LIST").fetchall()

	def get_species_locations(self, community_reference=None):
		"""
		Gets the list of species locations after coalescence.

		If a community reference is provided, will return just the species for that community reference, otherwise
		returns the whole table

		:param int community_reference: community reference number
		:return: a list of lists containing each row of the SPECIES_LOCATIONS table
		"""
		self._check_database()
		if community_reference:
			return [list(x) for x in self.cursor.execute("SELECT species_id, x, y"
													 " FROM SPECIES_LOCATIONS WHERE community_reference==?",
														 (community_reference,))]
		return [list(x) for x in self.cursor.execute("SELECT species_id, x, y, community_reference"
													 " FROM SPECIES_LOCATIONS")]

	def get_goodness_of_fit(self, reference=1):
		"""
		Returns the goodness of fit from the file.

		:param reference: the community reference to get from
		:return: the full output from the SQL query

		:rtype: list
		"""
		self._check_database()
		if self.check_biodiversity_table_exists() == 0:
			raise RuntimeError("Biodiversity table does not contain any values.")
		ret = self.cursor.execute(
			"SELECT value FROM BIODIVERSITY_METRICS WHERE fragment=='whole' AND metric=='goodness_of_fit' AND "
			"community_reference == ?", (reference, )).fetchall()
		if len(ret) is 0:
			raise RuntimeError("Biodiversity table does not contain goodness-of-fit values.")
		else:
			return ret[0][0]

	def get_goodness_of_fit_metric(self, metric, reference=1):
		"""
		Gets the goodness-of-fit measure for the specified metric and community reference.

		:param metric: the metric goodness of fit has been calculated for to obtain
		:param reference: the community reference to fetch fits for
		:return: the goodness of fit value
		:rtype: float
		"""
		self._check_database()
		if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):
			raise ValueError("Biodiversity table does not contain any values.")
		metric_sql = "goodness_of_fit_{}".format(metric)
		ret = self.cursor.execute("SELECT value FROM BIODIVERSITY_METRICS WHERE fragment=='whole' AND "
								  "metric==? and "
								  "community_reference == ?", (metric_sql, reference,)).fetchone()
		if len(ret) == 0:
			raise ValueError("No goodness-of-fit for {} with"
							 " community reference = {}".format(metric, reference))
		return ret[0]

	def get_goodness_of_fit_fragment_richness(self, reference=1):
		"""
		Returns the goodness of fit for fragment richness from the file.

		:raises ValueError: if BIODIVERSITY_METRICS table does not exist.

		:param reference: the community reference number
		:return: the full output from the SQL query

		:rtype: float
		"""
		return self.get_goodness_of_fit_metric("fragment_richness", reference=reference)


	def get_goodness_of_fit_fragment_octaves(self, reference=1):
		"""
		Returns the goodness of fit for fragment octaves from the file.

		:raises ValueError: if BIODIVERSITY_METRICS table does not exist.

		:param reference: the community reference number
		:return: the full output from the SQL query

		:rtype: list
		"""
		# TODO This needs to be fixed
		self._check_database()
		if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):
			raise ValueError("Biodiversity table does not contain any values.")
		ret = self.cursor.execute("SELECT value FROM BIODIVERSITY_METRICS WHERE fragment=='whole' AND "
								  "metric=='goodness_of_fit_fragment_octaves' and "
								  "community_reference == ?", (reference,)).fetchone()
		if len(ret) == 0:
			raise ValueError("No goodness-of-fit for fragment octaves with"
							 " community reference = {}".format(reference))
		return ret[0]

	def dispersal_parameters(self):
		"""
		Reads the dispersal parameters from the database and returns them.

		:return: a list of the dispersal parameters [sigma, tau, m_probability, cutoff]
		"""
		ret = self.get_simulation_parameters()
		return [ret["sigma"], ret["tau"], ret["m_probability"], ret["cutoff"]]

	def get_job(self):
		"""
		Gets the job number (the seed) and the job type (the task identifier).

		:return: list containing [seed, job_type (the task identifier)]
		"""
		ret = self.get_simulation_parameters()
		return [ret["seed"], ret["job_type"]]

	def get_simulation_parameters(self, guild=None):
		"""
		Reads the simulation parameters from the database and returns them.

		:return: a dictionary mapping names to values for seed, job_type, output_dir, speciation_rate, sigma, L_value, deme,
		sample_size, maxtime, dispersal_relative_cost, min_spec, habitat_change_rate, gen_since_pristine, time_config,
		coarse_map vars, fine map vars, sample_file, gridx, gridy, pristine coarse map, pristine fine map, sim_complete,
		dispersal_method, m_probability, cutoff, infinite_landscape, protracted, min_speciation_gen, max_speciation_gen,
		dispersal_map
		"""
		self._check_database()
		if not guild:
			try:
				self.cursor.execute("SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme, sample_size, "
									"max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, gen_since_pristine, "
									"time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
									"coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, "
									"fine_map_x_offset, fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, "
									"sample_x_offset, sample_y_offset, pristine_coarse_map, "
									" pristine_fine_map, sim_complete, dispersal_method, m_probability, cutoff,"
									" infinite_landscape,  protracted, min_speciation_gen, max_speciation_gen, dispersal_map"
									" FROM SIMULATION_PARAMETERS")
			except sqlite3.OperationalError as e:
				self.logger.error("Failure to get SIMULATION_PARAMETERS table from database. Check table exists.")
				raise e
			column_names = [member[0] for member in self.cursor.description]
			values = [x for x in self.cursor.fetchone()]
			if sys.version_info[0] is not 3:
				for i, each in enumerate(values):
					if isinstance(each, unicode):
						values[i] = each.encode('ascii')
			# Now convert it into a dictionary
			return dict(zip(column_names, values))
		else:
			return self._get_sim_parameters_guild(guild=guild)



	def get_community_references(self):
		"""
		Gets a list of all the commuity references already calculated for the simulation.

		:return: list of all calculated community references

		:rtype: list
		"""
		self._check_database()
		try:
			self.cursor.execute("SELECT reference FROM COMMUNITY_PARAMETERS")
		except sqlite3.OperationalError as e:
			self.logger.error("Failure to fetch references from COMMUNITY_PARAMETERS table in database."
							  " Check table exists.")
			raise e
		references = [x[0] for x in self.cursor.fetchall()]
		return references

	def get_community_parameters(self, reference=1):
		"""
		Returns a dictionary containing the parameters for the calculated community.

		:param reference: the reference key for the calculated parameters. (default is 1)
		:return: dictionary containing the speciation_rate, time, fragments and metacommunity_reference
		:rtype: dict
		"""
		self._check_database()
		try:
			self.cursor.execute("SELECT speciation_rate, time, fragments, metacommunity_reference "
								"FROM COMMUNITY_PARAMETERS WHERE reference==?", (reference,))
		except sqlite3.OperationalError as e:
			self.logger.error("Failure to fetch COMMUNITY_PARAMETERS table from database. Check table exists.")
			raise e
		fetch = self.cursor.fetchone()
		if fetch is None:
			raise KeyError("No community parameters found for reference of {}".format(reference))
		values = [x for x in fetch]
		column_names = [member[0] for member in self.cursor.description]
		if sys.version_info[0] is not 3:
			for i, each in enumerate(values):
				if isinstance(each, unicode):
					values[i] = each.encode('ascii')
		# Now convert it into a dictionary
		return dict(zip(column_names, values))

	def get_community_reference(self, speciation_rate, time, fragments, metacommunity_size=0,
								metacommunity_speciation_rate=0.0):
		"""
		Gets the community reference associated with the supplied community parameters

		:raises KeyError: if COMMUNITY_PARAMETERS (or METACOMMUNITY_PARAMETERS) does not exist in database or no
			reference exists for the supplied parameters

		:param speciation_rate: the speciation rate of the community
		:param time: the time in generations of the community
		:param fragments: whether fragments were determined for the community
		:param metacommunity_size: the metacommunity size
		:param metacommunity_speciation_rate: the metacommunity speciation rate
		:return: the reference associated with this set of simulation parameters
		"""
		if metacommunity_size == 0:
			metacommunity_reference = 0
		else:
			self._check_database()
			if not check_sql_table_exist(self.database, "METACOMMUNITY_PARAMETERS"):
				raise KeyError("No table METACOMMUNITY_PARAMETERS exists in database {}".format(self.file))
			self.cursor.execute("SELECT reference FROM METACOMMUNITY_PARAMETERS WHERE metacommunity_size == ? AND "
								"speciation_rate == ? AND fragments == ?",
								(metacommunity_size, metacommunity_speciation_rate, int(fragments)))
			try:
				metacommunity_reference = self.cursor.fetchone()[0]
			except IndexError:
				raise KeyError("Cannot obtain metacommunity reference from database with size={}, "
							   "speciation rate={} and fragments={}".format(metacommunity_size,
																			metacommunity_speciation_rate, fragments))
		if check_sql_table_exist(self.database, "COMMUNITY_PARAMETERS"):
			self.cursor.execute("SELECT reference FROM COMMUNITY_PARAMETERS WHERE speciation_rate == ? AND "
								"time == ? AND fragments == ? AND metacommunity_reference == ?",
								(speciation_rate, time, int(fragments), metacommunity_reference))
			try:
				return self.cursor.fetchone()[0]
			except IndexError:
				pass
		raise KeyError("Cannot obtain community reference from database with provided parameters")

	def get_metacommunity_references(self):
		"""
		Gets a list of all the metacommuity references already calculated for the simulation.

		.. note:: Returns an empty list and logs an error message if the METACOMMUNITY_PARAMETERS table does not exist.

		:return: list of all calculated metacommunity references

		:rtype: list
		"""
		self._check_database()
		if not check_sql_table_exist(self.database, "METACOMMUNITY_PARAMETERS"):
			self.logger.error("No table METACOMMUNITY_PARAMETERS exists in database {}".format(self.file))
			return []
		try:
			self.cursor.execute("SELECT reference FROM METACOMMUNITY_PARAMETERS")
		except sqlite3.OperationalError as e:
			self.logger.error("Failure to fetch references from METACOMMUNITY_PARAMETERS table in database."
							  " Check table exists.")
			raise e
		references = [x[0] for x in self.cursor.fetchall()]
		return references

	def get_metacommunity_parameters(self, reference=1):
		"""
		Returns a dictionary containing the parameters for the calculated community.

		:param reference: the reference key for the calculated parameters. (default is 1)

		:raises sqlite3.OperationalError: if the METACOMMUNITY_PARAMETERS table does not exist, or some other sqlite
			error occurs

		:raises KeyError: if the supplied reference does not exist in the METACOMMUNITY_PARAMETERS table

		:return: dictionary containing the speciation_rate, time, fragments and metacommunity_reference
		:rtype: dict
		"""
		self._check_database()
		try:
			self.cursor.execute("SELECT speciation_rate, metacommunity_size FROM"
								" METACOMMUNITY_PARAMETERS  WHERE reference== ?", (reference,))
		except sqlite3.OperationalError as e:
			self.logger.error("Failure to fetch METACOMMUNITY_PARAMETERS table from database. Check table exists. \n")
			raise e
		values = [x for x in self.cursor.fetchone()]
		if len(values) == 0:
			raise KeyError("No metacommunity parameters found for reference of {}".format(reference))
		column_names = [member[0] for member in self.cursor.description]
		if sys.version_info[0] is not 3:
			for i, each in enumerate(values):
				if isinstance(each, unicode):
					values[i] = each.encode('ascii')
		# Now convert it into a dictionary
		return dict(zip(column_names, values))

	def get_parameter_description(self, key=None):
		"""
		Gets the description of the parameter matching the key from those contained in SIMULATION_PARAMETERS

		Simply accesses the _parameter_descriptions data stored in parameter_descriptions.json

		:return: string containing the parameter description or a dict containing all values if no key is supplied

		:rtype: str
		"""
		return get_parameter_description(key)

	def is_completed(self):
		"""
		Indicates whether the simulation has been performed to completion, or if the simulation has been paused and
		needs to be completed before analysis can be performed.

		:return: bool: true if simulation is complete
		"""
		return self.is_complete

	def is_protracted(self):
		"""
		Indicates whether the simulation is a protracted simulation or not. This is read from the completed database file.

		:return: boolean, true if the simulation was performed with protracted speciation.
		"""
		return bool(self.get_simulation_parameters().get("protracted", False))

	def clear_calculations(self):
		"""
		Removes the BIODIVERSITY_METRICS and FRAGMENT_OCTAVES tables completely.

		.. note:: that this cannot be undone (other than re-running the calculations).
		"""
		self._check_database()
		self.cursor.execute('DROP TABLE IF EXISTS BIODIVERSITY_METRICS')
		self.cursor.execute('DROP TABLE IF EXISTS FRAGMENT_OCTAVES')
		self.cursor.execute('DROP TABLE IF EXISTS FRAGMENT_RICHNESS')
		self.cursor.execute('DROP TABLE IF EXISTS PLOT_DATA')
		self.cursor.execute('DROP TABLE IF EXISTS SPECIES_RICHNESS')
		self.cursor.execute("DROP TABLE IF EXISTS ALPHA_DIVERSITY")
		self.cursor.execute("DROP TABLE IF EXISTS BETA_DIVERSITY")
		self.database.commit()

	def wipe_data(self):
		"""
		Wipes all calculated data apart from the original, unformatted coalescence tree.
		The Speciation_Counter program will have to be re-run to perform any analyses.
		"""
		self._check_database()
		self.cursor.execute("DROP TABLE IF EXISTS FRAGMENT_ABUNDANCES")
		self.cursor.execute("DROP TABLE IF EXISTS SPECIES_ABUNDANCES")
		self.cursor.execute("DROP TABLE IF EXISTS SPECIES_RICHNESS")
		self.cursor.execute("DROP TABLE IF EXISTS COMMUNITY_PARAMETERS")
		self.cursor.execute("DROP TABLE IF EXISTS SPECIES_LOCATIONS")
		self.cursor.execute("DROP TABLE IF EXISTS BIODIVERSITY_METRICS")
		self.cursor.execute("DROP TABLE IF EXISTS FRAGMENT_OCTAVES")
		self.cursor.execute('DROP TABLE IF EXISTS FRAGMENT_RICHNESS')
		self.cursor.execute("DROP TABLE IF EXISTS ALPHA_DIVERSITY")
		self.cursor.execute("DROP TABLE IF EXISTS BETA_DIVERSITY")
		self.database.commit()

	def sample_fragment_richness(self, fragment, number_of_individuals, community_reference=1, n=1):
		"""
		Samples from the database from FRAGMENT_ABUNDANCES, the desired number of individuals.

		Randomly selects the desired number of individuals from the database n times and returns the mean richness for
		the random samples.

		:raises IOError: if the FRAGMENT_ABUNDANCES table does not exist in the database.

		:param fragment: the reference of the fragment to aquire the richness for
		:param number_of_individuals: the number of individuals to sample
		:param community_reference: the reference for the community parameters
		:param n: number of times to repeatedly sample

		:return: the mean of the richness from the repeats
		:rtype: float
		"""
		if not self.fragment_abundances:
			self.calculate_fragment_abundances()
		try:
			chosen, richness = zip(*[[x[1], x[2]] for x in self.fragment_abundances if x[0] == fragment and
									 x[3] == community_reference])
		except ValueError as ve:
			raise ValueError("Fragment abundances do not contain data"
							 " for {} with reference={}: {}".format(fragment,
																	number_of_individuals,
																	ve))
		species_ids = np.repeat(chosen, richness)
		richness_out = []
		for i in range(n):
			# Randomly select number_of_individuals
			richness_out.append(len(set(np.random.choice(species_ids, size=number_of_individuals, replace=False))))
		return np.mean(richness_out)

	def sample_landscape_richness(self, number_of_individuals, n=1, community_reference=1):
		"""
		Samples from the landscape the required number of individuals, returning the mean of the species richnesses
		produced.

		If number_of_individuals is a dictionary mapping fragment names to numbers sampled, will sample the respective
		number from each fragment and return the whole landscape richness.

		:raises KeyError: if the dictionary supplied contains more sampled individuals than exist in a fragment, or
			if the fragment is not contained within the dictionary.

		:param int/dict number_of_individuals: either an int containing the number of individuals to be sampled, or a
			dictionary mapping fragment names to numbers of individuals to be sampled
		:param n: the number of repeats to average over
		:param community_reference: the community reference to fetch abundances for

		:return: the mean of the richness from the repeats for the whole landscape
		:rtype: float
		"""
		richness_out = []
		if isinstance(number_of_individuals, dict):
			if not self.fragment_abundances:
				self.calculate_fragment_abundances()
			select_abundances = [[x[0], x[1], x[2]] for x in self.fragment_abundances if x[3] == community_reference]
			fragments = set([x[0] for x in select_abundances])
			for f in fragments:
				try:
					_ = number_of_individuals[f]
				except KeyError as ke:
					raise KeyError("Fragment not found in number_of_individuals dictionary: {}".format(ke))
				sum_total = sum([x[2] for x in select_abundances if x[0] == f])
				if sum_total < number_of_individuals[f]:
					raise KeyError("Sampled number of individuals is greater"
								   " than exists for fragment {}: {} < {}".format(f, sum_total,
																				  number_of_individuals[f]))
			for n in range(n):
				ids = []
				for f in fragments:
					chosen, richness = zip(*[[x[1], x[2]] for x in select_abundances if x[0] == f])
					species_ids = np.repeat(chosen, richness)
					ids.extend(np.random.choice(species_ids, size=number_of_individuals[f], replace=False).tolist())
				richness_out.append(len(set(ids)))
			return np.mean(richness_out)
		else:
			# straightforward case
			chosen, richness = zip(*[[x[0], x[1]] for x in self.get_species_abundances(reference=community_reference)])
			species_ids = np.repeat(chosen, richness)
			for i in range(n):
				# Randomly select number_of_individuals
				richness_out.append(len(set(np.random.choice(species_ids, size=number_of_individuals, replace=False))))
			return np.mean(richness_out)

def collate_fits(file_dir, filename="Collated_fits.db"):
	"""
	Collates the goodness of fit values from every file in the specified directory and places them in one new file.

	.. note:: Files with 'collated' in the name will be ignored.

	.. note:: If the output file exists, it will be deleted.

	Creates three separate tables in the output file, one for overall goodness of fit, one for fragment richness fits,
	and one for fragment octaves fits.

	:param file_dir: the file directory to examine
	:param filename: [optional] the output file name.
	"""
	if filename == "Collated_fits.db":
		filename = os.path.join(file_dir, filename)
	if os.path.exists(filename):
		os.remove(filename)

	try:
		database = sqlite3.connect(filename)
	except Exception as e:
		raise IOError("Error opening SQLite database: " + e.message)
	database.execute("CREATE TABLE GOODNESS_FIT (ref INT PRIMARY KEY NOT NULL, task INT NOT NULL, seed INT NOT NULL, "
					 "sigma FLOAT NOT NULL, tau FLOAT NOT NULL, m_probability FLOAT NOT NULL, cutoff FLOAT NOT NULL," \
					 "time FLOAT NOT NULL, speciation_rate FLOAT NOT NULL, value FLOAT NOT NULL)")
	database.execute(
		"CREATE TABLE GOODNESS_FIT_FRAGMENT_RICHNESS (ref INT PRIMARY KEY NOT NULL, task INT NOT NULL, seed INT NOT NULL, "
		"sigma FLOAT NOT NULL, tau FLOAT NOT NULL, m_probability FLOAT NOT NULL, cutoff FLOAT NOT NULL," \
		"time FLOAT NOT NULL, speciation_rate FLOAT NOT NULL, value FLOAT NOT NULL)")
	database.execute(
		"CREATE TABLE GOODNESS_FIT_FRAGMENT_OCTAVES (ref INT PRIMARY KEY NOT NULL, task INT NOT NULL, seed INT NOT NULL, "
		"sigma FLOAT NOT NULL, tau FLOAT NOT NULL, m_probability FLOAT NOT NULL, cutoff FLOAT NOT NULL," \
		"time FLOAT NOT NULL, speciation_rate FLOAT NOT NULL, value FLOAT NOT NULL)")
	ref = 0
	ref_richness = 0
	ref_octaves = 0
	out = []
	out_richness = []
	out_octaves = []
	if os.path.exists(file_dir):
		for file in os.listdir(file_dir):
			if os.path.join(file_dir, file) == filename or "Collated" in file:
				continue
			elif ".db" in file and os.path.isfile(os.path.join(file_dir, file)):
				temp = CoalescenceTree()
				try:
					temp.set_database(os.path.join(file_dir, file))
				except IOError:
					temp.logger.warning("Database {} is not complete or does not exist.\n".format(file))
					continue
				try:
					gof = temp.get_goodness_of_fit()
				except:
					raise RuntimeError("File: " + file)
				gof_octaves = temp.get_goodness_of_fit_fragment_octaves()
				gof_richness = temp.get_goodness_of_fit_fragment_richness()
				disp = temp.dispersal_parameters()
				j = temp.get_job()
				for each in gof:
					out.append([ref, j[0], j[1], disp[0], disp[1], disp[2], disp[3], each[3], each[4], each[5]])
					ref += 1
				for each in gof_richness:
					out_richness.append(
						[ref_richness, j[0], j[1], disp[0], disp[1], disp[2], disp[3], each[3], each[4], each[5]])
					ref_richness += 1
				for each in gof_octaves:
					out_octaves.append(
						[ref_octaves, j[0], j[1], disp[0], disp[1], disp[2], disp[3], each[3], each[4], each[5]])
					ref_octaves += 1
		database.executemany("INSERT INTO GOODNESS_FIT VALUES(?,?,?,?,?,?,?,?,?,?)", out)
		database.executemany("INSERT INTO GOODNESS_FIT_FRAGMENT_RICHNESS VALUES(?,?,?,?,?,?,?,?,?,?)", out_richness)
		database.executemany("INSERT INTO GOODNESS_FIT_FRAGMENT_OCTAVES VALUES(?,?,?,?,?,?,?,?,?,?)", out_octaves)
		database.commit()
	else:
		raise RuntimeError("Specified file directory " + file_dir + " does not exist")

def scale_simulation_fit(simulated_value, actual_value, number_individuals, total_individuals):
	"""
	Calculates goodness of fit for the provided values, and scales based on the total number of individuals that exist.
	The calculation is 1 - (|x - y|/max(x, y)) * n/n_tot for x, y simulated and actual values, n, n_tot for metric and total
	number of individuals.

	:param simulated_value: the simulated value of the metric
	:param actual_value: the actual value of the metric
	:param number_individuals: the number of individuals this metric relates to
	:param total_individuals: the total number of individuals across all sites for this metric
	:return: the scaled fit value
	"""
	return (1 -(abs(simulated_value -actual_value))/max(simulated_value, actual_value)) *\
		   number_individuals/total_individuals