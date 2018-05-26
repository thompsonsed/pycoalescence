"""
Combine simulation outputs from separate guilds. Detailed :ref:`here <merging_simulations>`.

:py:class:`~Merger` will output a single database file, merging the various biodiversity tables into one.

Metrics are also calculated for the entire system, with a guild reference of 0.

All standard routines provided in :py:class:`~pycoalescence.coal_analyse.CoalescenceTree` can then be performed on the
combined database.
"""
from __future__ import absolute_import

import logging
import os

try:
	import sqlite3
except ImportError:
	# Python 3 compatibility
	import sqlite as sqlite3
try:
	from math import isclose
except ImportError:
	from .system_operations import isclose

from .coalescence_tree import CoalescenceTree
from .sqlite_connection import check_sql_table_exist, fetch_table_from_sql
from .system_operations import cantor_pairing, check_parent


class Merger(CoalescenceTree):
	"""
	Merges simulation outputs into a single database. Inherits from
	:py:class:`~pycoalescence.coal_analyse.CoalescenceTree` to provide all routines in the same object.
	"""
	def __init__(self, database=None, logging_level=logging.WARNING, log_output=None):
		super(Merger, self).__init__(database, logging_level, log_output)
		self.species_list_parent_counter = 0
		self.parameters_list = []
		self.guild = 0
		self.simulation_list = []
		self.species_list = []
		self.species_locations = []
		self.species_abundances = []
		self.fragment_abundances = []
		self.species_richness = []
		self.fragment_richness = []
		self.fragment_octaves = []
		self.community_parameters = []
		self.metacommunity_parameters = []
		self.max_species_id = 0
		self.max_locations_id = 0

	def __del__(self):
		"""
		Closes the connection to the database.
		"""
		if self.database:
			self.database.close()
			self.database = None

	def set_database(self, filename):
		"""
		Sets the output database for the merged simulations

		Assumes no database currently exists, and will create one.

		:raises IOError: if the output database already exists

		:param filename: the filename to output merged simulations into

		:rtype: None
		"""
		if os.path.exists(filename):
			raise IOError("Database already exists at {}".format(filename))
		self.file = filename
		check_parent(filename)
		try:
			self.database = sqlite3.connect(filename)
		except sqlite3.OperationalError as e:
			try:
				self.database.close()
			except AttributeError:
				pass
			self.database = None
			raise IOError("Error opening SQLite database: " + str(e))
		self._create_simulation_parameters()
		self._create_species_list()

	def _create_simulation_parameters(self):
		"""
		Creates the SIMULATION_PARAMETERS table in the database.

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a SIMULATION_PARAMETERS table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE SIMULATION_PARAMETERS (seed INT not null, job_type INT NOT NULL, " \
					 "output_dir TEXT NOT NULL, speciation_rate DOUBLE NOT NULL, sigma DOUBLE NOT NULL,tau DOUBLE NOT " \
					 "NULL, deme INT NOT NULL, sample_size DOUBLE NOT NULL, max_time INT NOT NULL, " \
					 "dispersal_relative_cost DOUBLE NOT NULL, min_num_species INT NOT NULL, " \
					 "habitat_change_rate DOUBLE NOT NULL, gen_since_historical DOUBLE NOT NULL, " \
					 "time_config_file TEXT NOT NULL, coarse_map_file TEXT NOT NULL, coarse_map_x INT NOT NULL, " \
					 "coarse_map_y INT NOT NULL, coarse_map_x_offset INT NOT NULL, coarse_map_y_offset INT NOT NULL, " \
					 "coarse_map_scale DOUBLE NOT NULL, fine_map_file TEXT NOT NULL, fine_map_x INT NOT NULL, " \
					 "fine_map_y INT NOT NULL, fine_map_x_offset INT NOT NULL, fine_map_y_offset INT NOT NULL, " \
					 "sample_file TEXT NOT NULL, grid_x INT NOT NULL, grid_y INT NOT NULL, sample_x INT NOT NULL, " \
					 "sample_y INT NOT NULL, sample_x_offset INT NOT NULL, sample_y_offset INT NOT NULL, " \
					 "historical_coarse_map TEXT NOT NULL, historical_fine_map TEXT NOT NULL, sim_complete INT NOT NULL, " \
					 "dispersal_method TEXT NOT NULL, m_probability DOUBLE NOT NULL, cutoff DOUBLE NOT NULL, " \
					 "restrict_self INT NOT NULL, landscape_type TEXT NOT NULL, protracted INT NOT NULL, " \
					 "min_speciation_gen DOUBLE NOT NULL, max_speciation_gen DOUBLE NOT NULL, " \
					 "dispersal_map TEXT NOT NULL, guild INT PRIMARY KEY NOT NULL, filename TEXT NOT NULL);"
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SIMULATION_PARAMETERS table in database {}: {}".format(self.file, soe))

	def _create_community_parameters(self):
		"""
		Creates the COMMUNITY_PARAMETERS table in the database.

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a COMMUNITY_PARAMETERS table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS COMMUNITY_PARAMETERS (reference INT PRIMARY KEY NOT NULL," \
					 " speciation_rate DOUBLE NOT NULL, time DOUBLE NOT NULL, fragments INT NOT NULL, " \
					 "metacommunity_reference INT);"
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create COMMUNITY_PARAMETERS table in database {}: {}".format(self.file, soe))

	def _create_metacommunity_parameters(self):
		"""
		Creates the METACOMMUNITY_PARAMETERS table in the database.

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a METACOMMUNITY_PARAMETERS table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS METACOMMUNITY_PARAMETERS (reference INT PRIMARY KEY NOT NULL," \
					 " speciation_rate DOUBLE NOT NULL, metacommunity_size DOUBLE NOT NULL);"
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create COMMUNITY_PARAMETERS table in database {}: {}".format(self.file, soe))

	def _create_species_list(self):
		"""
		Creates the SPECIES_LIST table in the database.

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a SPECIES_LIST table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS SPECIES_LIST (ID int PRIMARY KEY NOT NULL, unique_spec INT NOT NULL, " \
					 "xval INT NOT NULL, yval INT NOT NULL, xwrap INT NOT NULL, ywrap INT NOT NULL, tip INT NOT NULL, " \
					 "speciated INT NOT NULL, " \
					 "parent INT NOT NULL, existence INT NOT NULL, randnum DOUBLE NOT NULL, gen_alive INT NOT NULL, " \
					 "gen_added DOUBLE NOT NULL, guild INT NOT NULL);"
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SPECIES_LIST table in database {}: {}".format(self.file, soe))

	def _create_species_locations(self):
		"""
		Creates the SPECIES_LOCATIONS table in the database.

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a SPECIES_LOCATIONS table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS SPECIES_LOCATIONS (ID int PRIMARY KEY NOT NULL, species_id INT " \
					 "NOT NULL, x INT NOT NULL, y INT NOT NULL, community_reference INT NOT NULL, guild INT NOT NULL);"
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SPECIES_LOCATIONS table in database {}: {}".format(self.file, soe))

	def _create_species_abundances(self, guilds=False):
		"""
		Creates the SPECIES_ABUNDANCES table in the database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a SPECIES_ABUNDANCES table as the database has not been created.")
		if guilds:
			additional = "_GUILDS"
		else:
			additional = ""
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS SPECIES_ABUNDANCES{} (ID int PRIMARY KEY NOT NULL, " \
					 "species_id INT NOT NULL, no_individuals INT NOT NULL, community_reference INT NOT NULL, " \
					 "guild INT NOT NULL);".format(additional)
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SPECIES_ABUNDANCES table in database {}: {}".format(self.file, soe))

	def _create_fragment_abundances(self, guilds=False):
		"""
		Creates the FRAGMENT_ABUNDANCES table in the database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community
		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a FRAGMENT_ABUNDANCES table as the database has not been created.")
		self.cursor = self.database.cursor()
		if guilds:
			additional = "_GUILDS"
		else:
			additional = ""
		create_sql = "CREATE TABLE IF NOT EXISTS FRAGMENT_ABUNDANCES{} (ID int PRIMARY KEY NOT NULL," \
					 " fragment TEXT NOT NULL, area DOUBLE NOT NULL, size INT NOT NULL,  species_id INT NOT NULL, " \
					 "no_individuals INT NOT NULL, community_reference int NOT NULL," \
					 " guild INT NOT NULL);".format(additional)
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SPECIES_ABUNDANCES table in database {}: {}".format(self.file, soe))

	def _create_species_octaves(self, guilds=False):
		"""
		Creates the SPECIES_OCTAVES table in the database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a SPECIES_OCTAVES table as the database has not been created.")
		if guilds:
			additional = "_GUILDS"
		else:
			additional = ""
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS SPECIES_OCTAVES{} (ID int PRIMARY KEY NOT NULL," \
					 " fragment TEXT NOT NULL, area DOUBLE NOT NULL, size INT NOT NULL,  species_id INT NOT NULL, " \
					 "no_individuals INT NOT NULL, community_reference int NOT NULL," \
					 " guild INT NOT NULL);".format(additional)
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SPECIES_ABUNDANCES table in database {}: {}".format(self.file, soe))

	def _create_fragment_octaves(self, guilds=False):
		"""
		Creates the FRAGMENT_OCTAVES table in the database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a FRAGMENT_OCTAVES table as the database has not been created.")
		if guilds:
			additional1 = "_GUILDS"
			additional2 = ", guild INT NOT NULL"
		else:
			additional1 = ""
			additional2 = ""
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS FRAGMENT_OCTAVES{} (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL, " \
					 "octave INT NOT NULL, richness INT NOT NULL{});".format(additional1, additional2)
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SPECIES_ABUNDANCES table in database {}: {}".format(self.file, soe))

	def _create_species_richness(self, guilds=False):
		"""
		Creates the SPECIES_RICHNESS table in the database.

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a SPECIES_RICHNESS table as the database has not been created.")
		if guilds:
			additional1 = "_GUILDS"
			additional2 = ", guild INT NOT NULL"
		else:
			additional1 = ""
			additional2 = ""
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE IF NOT EXISTS SPECIES_RICHNESS{} (ref INT PRIMARY KEY NOT NULL," \
					 " community_reference INT NOT NULL, richness INT NOT NULL{})".format(additional1, additional2)

		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SPECIES_RICHNESS table in database {}: {}".format(self.file, soe))

	def _create_fragment_richness(self, guilds=False):
		"""
		Creates the FRAGMENT_RICHNESS table in the database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community

		:raises IOError: if the database has not been successfully created
		"""
		if self.database is None:
			raise IOError("Cannot create a FRAGMENT_RICHNESS table as the database has not been created.")
		if guilds:
			additional1 = "_GUILDS"
			additional2 = ", guild INT NOT NULL"
		else:
			additional1 = ""
			additional2 = ""
		self.cursor = self.database.cursor()
		create_sql = "CREATE TABLE FRAGMENT_RICHNESS{} (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL," \
					 " community_reference INT NOT NULL,  richness INT NOT NULL{})".format(additional1, additional2)
		try:
			self.cursor.execute(create_sql)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create FRAGMENT_RICHNESS table in database {}: {}".format(self.file, soe))


	def _read_simulation_parameters(self, input_simulation):
		"""
		Reads the simulation parameters from the input file and returns a list containing these parameters

		:param input_simulation: the simulation to read the simulation parameters from

		:return: list containing the simulation parameters from the input file
		"""
		output = fetch_table_from_sql(input_simulation, "SIMULATION_PARAMETERS")
		if len(output[0]) != 44:
			raise IOError("SIMULATION_PARAMETERS table does not contain 44 columns, contains {}."
						  " Check database.".format(len(output[0])))
		return output[0]

	def _add_simulation_parameters(self, parameters_list, guild, filename):
		"""
		Adds the provided parameters to the output statement for SIMULATION_PARAMETERS with the provided guild reference.
		:param list parameters_list: a list containing the SIMULATION_PARAMETERS outputs.
		:param int guild: the guild reference number for
		:param str filename: the simulation file associated with these parameters
		:return: None
		:rtype: None
		"""
		parameters_list.extend([guild, filename])
		self.parameters_list.append(tuple(parameters_list))

	def _write_simulation_parameters(self):
		"""
		Writes out the parameters_list object to the output database.

		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to SPECIES_PARAMETERS table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO SIMULATION_PARAMETERS VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?," \
					 "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
		try:
			self.cursor.executemany(create_sql, self.parameters_list)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not create SIMULATION_PARAMETERS table in database {}: {}".format(self.file, soe))

	def _read_species_list(self, input_simulation):
		"""
		Reads the SPECIES_LIST table from the input simulation
		:param input_simulation: the completed simulation to read the SPECIES_LIST object from.
		:return:
		"""
		return fetch_table_from_sql(input_simulation, "SPECIES_LIST")

	def _add_species_list(self, species_list, guild):
		"""
		Adds to the species_list object with the provided list of species and guild reference.
		:param species_list: the list of lists of species information to append
		:param guild: the guild to append to each species row.
		"""
		for i, row in enumerate(species_list):
			row[0] = cantor_pairing(row[0], guild)
			if i != 0 and row[8] != 0:
					row[8] = row[8] + self.species_list_parent_counter
			row.append(guild)
		self.species_list_parent_counter += len(species_list)
		self.species_list.extend([tuple(x) for x in species_list])

	def _write_species_list(self):
		"""
		Writes out the species_list object to the output database.

		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to SPECIES_LIST table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO SPECIES_LIST VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
		try:
			self.cursor.executemany(create_sql, self.species_list)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into SPECIES_LIST table in database {}: {}".format(self.file, soe))

	def _read_species_locations(self, input_simulation):
		"""
		Reads the SPECIES_LOCATIONS table from the input simulation
		:param input_simulation: the completed simulation to read the SPECIES_LIST object from.
		:return:
		"""
		return fetch_table_from_sql(input_simulation, "SPECIES_LOCATIONS")

	def _add_species_locations(self, species_locations, guild):
		"""
		Adds to the species_locations object with the provided list of species and guild reference.
		:param species_list: the list of lists of species information to append
		:param guild: the guild to append to each species row.
		"""
		tmp_max = self.max_locations_id
		for row in species_locations:
			row[0] = cantor_pairing(row[0], guild)
			row.append(guild)
			self.max_locations_id = max(row[1], self.max_locations_id)
			row[1] += tmp_max
		self.species_locations.extend([tuple(x) for x in species_locations])

	def _write_species_locations(self):
		"""
		Writes out the species_locations object to the output database.

		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to SPECIES_LIST table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO SPECIES_LOCATIONS VALUES (?,?,?,?,?,?);"
		try:
			self.cursor.executemany(create_sql, self.species_locations)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into SPECIES_LIST table in database {}: {}".format(self.file, soe))

	def _read_species_abundances(self, input_simulation):
		"""
		Reads the SPECIES_ABUNDANCES table from the input simulation.

		:param input_simulation: the completed simulation to read the SPECIES_ABUNDANCES object from.
		:return:
		"""
		return fetch_table_from_sql(input_simulation, "SPECIES_ABUNDANCES")


	def _add_species_abundances(self, species_abundances, guild):
		"""
		Adds to the species_abundances object with the provided list of species and guild reference.

		:param species_abundances: the list of lists of species information to append
		:param guild: the guild to append to each species row.
		"""
		tmp_max = self.max_species_id
		for row in species_abundances:
			row[0] = cantor_pairing(row[0], guild)
			row.append(guild)
			self.max_species_id = max(row[1], self.max_species_id)
			row[1] += tmp_max
		self.species_abundances.extend([tuple(x) for x in species_abundances])

	def _write_species_abundances(self):
		"""
		Writes out the species_list object to the output database.

		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to SPECIES_ABUNDANCES table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO SPECIES_ABUNDANCES VALUES (?,?,?,?,?);"
		try:
			self.cursor.executemany(create_sql, self.species_abundances)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into SPECIES_ABUNDANCES table in database {}: {}".format(self.file, soe))

	def _read_fragment_abundances(self, input_simulation):
		"""
		Reads the FRAGMENT_ABUNDANCES table from the input simulation
		:param input_simulation: the completed simulation to read the FRAGMENT_ABUNDANCES object from.
		:return:
		"""
		return fetch_table_from_sql(input_simulation, "FRAGMENT_ABUNDANCES")

	def _add_fragment_abundances(self, fragment_abundances, guild):
		"""
		Adds to the fragment_abundances object with the provided list of species and guild reference.
		:param fragment_abundances: the list of lists of species information to append
		:param guild: the guild to append to each species row.
		"""
		for row in fragment_abundances:
			row[0] = cantor_pairing(row[0], guild)
			row.append(guild)
		self.fragment_abundances.extend([tuple(x) for x in fragment_abundances])

	def _write_fragment_abundances(self):
		"""
		Writes out the fragment_abundances object to the output database.

		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to FRAGMENT_ABUNDANCES table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO FRAGMENT_ABUNDANCES VALUES (?,?,?,?,?);"
		try:
			self.cursor.executemany(create_sql, self.fragment_abundances)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into FRAGMENT_ABUNDANCES table in database {}: {}".format(self.file, soe))

	def _read_species_richness(self, input_simulation):
		"""
		Reads the SPECIES_RICHNESS table from the input simulation

		:param input_simulation: the completed simulation to read the SPECIES_RICHNESS object from.
		:return:
		"""
		return fetch_table_from_sql(input_simulation, "SPECIES_RICHNESS")

	def _add_species_richness(self, species_richness, guild):
		"""
		Adds to the species_richness object with the provided list of species and guild reference.
		:param species_richness: the list of lists of species information to append
		:param guild: the guild to append to each species row.
		"""
		for row in species_richness:
			row[0] = cantor_pairing(row[0], guild)
			row.append(guild)
		self.species_richness.extend([tuple(x) for x in species_richness])

	def _write_species_richness(self, guilds=False):
		"""
		Writes out the species_richness object to the output database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community

		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to SPECIES_RICHNESS table as the database has not been created.")
		if guilds:
			additional = "_GUILDS VALUES (?,?,"
		else:
			additional = " VALUES (?,"
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO SPECIES_RICHNESS{} ?,?);".format(additional)
		try:
			self.cursor.executemany(create_sql, self.species_richness)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into SPECIES_RICHNESS table in database {}: {}".format(self.file, soe))

	def _read_fragment_richness(self, input_simulation):
		"""
		Reads the FRAGMENT_RICHNESS table from the input simulation

		:param input_simulation: the completed simulation to read the FRAGMENT_RICHNESS object from.
		:return:
		"""
		return fetch_table_from_sql(input_simulation, "FRAGMENT_RICHNESS")

	def _add_fragment_richness(self, fragment_richness, guild):
		"""
		Adds to the species_richness object with the provided list of species and guild reference.
		:param fragment_richness: the list of lists of species information to append
		:param guild: the guild to append to each species row.
		"""
		for row in fragment_richness:
			row[0] = cantor_pairing(row[0], guild)
			row.append(guild)
		self.fragment_richness.extend([tuple(x) for x in fragment_richness])

	def _write_fragment_richness(self, guilds=False):
		"""
		Writes out the fragment_richness object to the output database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community


		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to FRAGMENT_RICHNESS table as the database has not been created.")
		if guilds:
			additional = "_GUILDS VALUES (?,"
		else:
			additional = " VALUES ("
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO FRAGMENT_RICHNESS{} ?,?,?,?);".format(additional)
		try:
			self.cursor.executemany(create_sql, self.fragment_richness)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into FRAGMENT_RICHNESS table in database {}: {}".format(self.file, soe))

	def _read_fragment_octaves(self, input_simulation):
		"""
		Reads the FRAGMENT_ABUNDANCES table from the input simulation

		:param input_simulation: the completed simulation to read the FRAGMENT_ABUNDANCES object from.
		:return:
		"""
		try:
			db = sqlite3.connect(input_simulation)
			c = db.cursor()
			c.execute("SELECT ref, fragment, octave, richness FROM FRAGMENT_OCTAVES")
			out = [list(x) for x in c.fetchall()]
			db.close()
			db = None
			return out
		except sqlite3.OperationalError as soe:
			raise IOError("Cannot fetch FRAGMENT_OCTAVES from database {}: {}".format(input_simulation, soe))


	def _add_fragment_octaves(self, fragment_octaves, guild):
		"""
		Adds to the fragment_octaves object with the provided list of species and guild reference.
		:param fragment_octaves: the list of lists of species information to append
		:param guild: the guild to append to each species row.
		"""
		for row in fragment_octaves:
			row[0] = cantor_pairing(row[0], guild)
			row.append(guild)
		self.fragment_octaves.extend([tuple(x) for x in fragment_octaves])

	def _write_fragment_octaves(self, guilds=False):
		"""
		Writes out the fragment_octaves object to the output database.

		:param guilds: if true, creates a separate table for individual guilds, rather than for the whole community

		:return: None
		:rtype: None
		"""
		if self.database is None:
			raise IOError("Cannot insert to FRAGMENT_ABUNDANCES table as the database has not been created.")
		if guilds:
			additional = "_GUILDS VALUES (?,"
		else:
			additional = " VALUES ("
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO FRAGMENT_OCTAVES{} ?,?,?,?);".format(additional)
		try:
			self.cursor.executemany(create_sql, self.fragment_octaves)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into FRAGMENT_ABUNDANCES table in database {}: {}".format(self.file, soe))

	def _add_community_parameters(self, input_simulation):
		"""
		Adds the community parameters to the internal object, checking to ensure that no repeat references exist with
		different parameters.

		:param input_simulation: completed simulation to obtain community references from

		:raises ValueError: if there is a parameter mismatch between the references
		"""
		community_parameters = fetch_table_from_sql(input_simulation, "COMMUNITY_PARAMETERS")
		if len(self.community_parameters) > 0:
			for reference, speciation_rate, time, fragments, metacommunity_reference in community_parameters:
				subsetted_params = [x for x in self.community_parameters if
									isclose(speciation_rate, x[1]) and isclose(time, x[2], abs_tol=0.00001) and
									metacommunity_reference == x[4]]
				if len(subsetted_params) > 0:
					if subsetted_params[0][0] != reference:
						raise ValueError("Parameter mismatch in references for speciation rate = {} and"
										 " time = {}".format(speciation_rate, time))
				else:
					self.logger.error("Parameter set for reference of {} "
										"does not exist in all simulations.".format(reference))
					self.community_parameters.extend(community_parameters)
			for reference, speciation_rate, time, fragments, metacommunity_reference in self.community_parameters:
				subsetted_params = [x for x in community_parameters if isclose(speciation_rate, x[1]) and
									isclose(time, x[2], abs_tol=0.00001) and metacommunity_reference == x[4]]
				if len(subsetted_params) == 0:
					self.logger.error("Parameter set for reference of {} "
									  "does not exist in all simulations.".format(reference))
					self.community_parameters.extend(community_parameters)
		else:
			self.community_parameters.extend(community_parameters)

	def _write_community_parameters(self):
		"""
		Outputs the community parameters into the database
		"""
		if self.database is None:
			raise IOError("Cannot insert to COMMUNITY_PARAMETERS table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO COMMUNITY_PARAMETERS VALUES (?,?,?,?,?);"
		try:
			self.cursor.executemany(create_sql, self.community_parameters)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into COMMUNITY_PARAMETERS table in database {}: {}".format(self.file, soe))

	def _add_metacommunity_parameters(self, input_simulation):
		"""
		Adds the metacommunity parameters to the internal object, checking to ensure that no repeat references exist
		with different parameters.

		:param input_simulation: completed simulation to obtain metacommunity references from

		:raises ValueError: if there is a parameter mismatch between the references
		"""
		metacommunity_parameters = fetch_table_from_sql(input_simulation, "METACOMMUNITY_PARAMETERS")
		if len(self.community_parameters) > 0:
			for reference, speciation_rate, metacommunity_size in metacommunity_parameters:
				subsetted_params = [x for x in self.metacommunity_parameters if
									isclose(speciation_rate, x[1]) and metacommunity_size == x[2]]
				if len(subsetted_params) > 0:
					if subsetted_params[1] != reference:
						raise ValueError("Parameter mismatch in metacommunity references for speciation rate = {} and"
										 " size = {}".format(speciation_rate, metacommunity_size))
				else:
					self.logger.error("Parameter set for metacommunity reference of {} "
									  "does not exist in all simulations.".format(reference))
					self.metacommunity_parameters.extend(metacommunity_parameters)
			for reference, speciation_rate, metacommunity_size in self.metacommunity_parameters:
				subsetted_params = [x for x in metacommunity_parameters if isclose(speciation_rate, x[1]) and
									metacommunity_size == x[2]]
				if len(subsetted_params) == 0:
					self.logger.error("Parameter set for metacommunity reference of {} "
									  "does not exist in all simulations.".format(reference))
					self.metacommunity_parameters.extend(metacommunity_parameters)
		else:
			self.metacommunity_parameters.extend(metacommunity_parameters)

	def _write_metacommunity_parameters(self):
		if self.database is None:
			raise IOError("Cannot insert to METACOMMUNITY_PARAMETERS table as the database has not been created.")
		self.cursor = self.database.cursor()
		create_sql = "INSERT INTO METACOMMUNITY_PARAMETERS VALUES (?,?,?);"
		try:
			self.cursor.executemany(create_sql, self.community_parameters)
			self.database.commit()
		except sqlite3.OperationalError as soe:
			raise IOError("Could not insert into METACOMMUNITY_PARAMETERS table in database {}: {}".format(self.file, soe))

	def add_simulation(self, input_simulation):
		"""
		Adds a simulation to the list of merged simulations.

		This also calls the relevant merges for the tables that exist in the provided database.

		:param input_simulation: either the path to the input simulation, a Coalescence class object, or a CoalescenceTree object
			which contains the completed simulation.
		:return: None
		:rtype: None
		"""
		if isinstance(input_simulation, CoalescenceTree):
			t = input_simulation
		else:
			t = CoalescenceTree(input_simulation)
		simulation_path = t.file
		# Ensure that any open sql connections are closed
		del t
		self.guild += 1
		# First add the parameters (which might throw some simple errors)
		self._add_simulation_parameters(self._read_simulation_parameters(simulation_path), self.guild, simulation_path)
		if check_sql_table_exist(simulation_path, "COMMUNITY_PARAMETERS"):
			self._create_community_parameters()
			self._add_community_parameters(simulation_path)
		if check_sql_table_exist(simulation_path, "METACOMMUNITY_PARAMETERS"):
			self._create_metacommunity_parameters()
			self._add_metacommunity_parameters(simulation_path)
		# Now the longer routines
		self._add_species_list(self._read_species_list(simulation_path), self.guild)
		if check_sql_table_exist(simulation_path, "SPECIES_ABUNDANCES"):
			self._create_species_abundances()
			self._add_species_abundances(self._read_species_abundances(simulation_path), self.guild)
		if check_sql_table_exist(simulation_path, "FRAGMENT_ABUNDANCES"):
			self._create_fragment_abundances()
			self._add_fragment_abundances(self._read_fragment_abundances(simulation_path), self.guild)
		if check_sql_table_exist(simulation_path, "SPECIES_RICHNESS"):
			self._create_species_richness(guilds=True)
			self._add_species_richness(self._read_species_richness(simulation_path), self.guild)
		if check_sql_table_exist(simulation_path, "FRAGMENT_RICHNESS"):
			self._create_fragment_richness(guilds=True)
			self._add_fragment_richness(self._read_fragment_richness(simulation_path), self.guild)
		if check_sql_table_exist(simulation_path, "FRAGMENT_OCTAVES"):
			self._create_fragment_octaves(guilds=True)
			self._add_fragment_octaves(self._read_fragment_octaves(simulation_path), self.guild)

	def add_simulations(self, simulation_list):
		"""
		A convenience function that adds each simulation from the list of simulations provided and then writes to the
		database.

		:param simulation_list: list of paths to completed simulations
		"""
		for each in simulation_list:
			self.add_simulation(each)
		self.write()

	def write(self):
		"""
		Writes out all stored simulation parameters to the output database and wipes the in-memory objects.

		This should be called after all simulation have been added, or when RAM usage gets too large for large
		simulations

		"""
		self._write_simulation_parameters()
		if len(self.community_parameters) > 0:
			self._write_community_parameters()
		if len(self.metacommunity_parameters) > 0:
			self._write_metacommunity_parameters()
		self._write_species_list()
		if len(self.species_abundances) > 0:
			self._write_species_abundances()
		if len(self.fragment_abundances) > 0:
			self._write_fragment_abundances()
		if len(self.species_richness) > 0:
			self._write_species_richness(guilds=True)
			self._create_combined_species_richness()
		if len(self.fragment_richness) > 0:
			self._write_fragment_richness(guilds=True)
		if len(self.fragment_octaves) > 0:
			self._write_fragment_octaves(guilds=True)

	def _create_combined_species_richness(self):
		"""
		Combines the species richness guilds so that richness values are for all guilds.
		"""
		if len(self.species_richness) == 0:
			raise ValueError("No species richnesses are detected. Add simulations before combining richness.")
		self._create_species_richness(guilds=False)
		out_richness = []
		references = set([x[1] for x in self.species_richness])
		i = 0
		for reference in references:
			total = sum([x[2] for x in self.species_richness if x[1] == reference])
			out_richness.append([i, reference, total])
			i += 1
		self.species_richness = out_richness
		self._write_species_richness(guilds=False)

	def _create_combined_fragment_richness(self):
		"""
		Combines the fragment richness guilds so that richness values are for all guilds in each fragment.
		"""
		if len(self.fragment_richness) == 0:
			raise ValueError("No fragment richnesses are detected. Add simulations before combining richness.")
		self._create_fragment_richness(guilds=False)
		out_richness = []
		fragments = set([x[1] for x in self.fragment_richness])
		references = set([x[2] for x in self.fragment_richness])
		i = 0
		for reference in references:
			for fragment in fragments:
				total = sum([x[3] for x in self.fragment_richness if x[1] == fragment and x[2] == reference])
				out_richness.append([i, fragment, reference, total])
				i += 1
		self.fragment_richness = out_richness
		self._write_fragment_richness(guild=False)

	def _create_combined_fragment_octaves(self):
		"""
		Combines the fragment octaves guilds so that octaves values are for all guilds in each fragment.
		"""
		if len(self.fragment_octaves) == 0:
			raise ValueError("No fragment octaves are detected. Add simulations before creating combined octaves")
		self._create_fragment_octaves(guilds=False)
		octaves = []
		fragments = set([x[1] for x in self.fragment_octaves])
		references = set([x[2] for x in self.fragment_octaves])
		i = 0
		for reference in references:
			for fragment in fragments:
				total = sum([x[3] for x in self.fragment_octaves if x[1] == fragment and x[2] == reference])
				octaves.append([i, fragment, reference, total])
				i += 1
		self.fragment_octaves = octaves
		self._write_fragment_octaves(guild=False)

