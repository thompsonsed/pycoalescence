"""
Simulate dispersal kernels on landscapes. Detailed :ref:`here <Simulate_landscapes>`.

:input:
	- Map file to simulate on
	- Set of dispersal pararameters, including the dispersal kernel, number of repetitions and landscape properties

:output:
	- Database containing each distance travelled so that metrics can be calculated.
	- A table is created for mean dispersal distance over a single step or for mean distance travelled.
"""
import logging
import os
import sys
from numpy import std

from .landscape import Landscape

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
	logging.warning("Problem importing sqlite module " + str(ie))

from .system_operations import check_parent, write_to_log
from .map import Map

class DispersalSimulation(Landscape):
	"""
	Simulates a dispersal kernel upon a tif file to calculate landscape-level dispersal metrics.
	"""

	def __init__(self, file=None, logging_level=logging.WARNING, dispersal_db=None):
		"""
		Default initialiser for members of DispersalSimulation. Ensures that the database is

		:param file: sets the filename for reading tif files.
		:param is_sample: sets the sample mask to true, if it is a sampled file
		:param logging_level: the level of logging to output during dispersal simulations
		:param dispersal_db: path to a complete dispersal simulation database. Can also be a Map object containing the
							 completed simulation
		"""
		Landscape.__init__(self)
		self.logger = logging.Logger("dipersallogger")
		self._create_logger(logging_level=logging_level)
		self._db_conn = None
		# The dispersal simulation data
		self.dispersal_database = None
		self.deme = 1
		self.number_repeats = None
		self.number_steps = None
		self.seed = 1
		self.dispersal_method = None
		self.landscape_type = None
		self.sigma = None
		self.tau = None
		self.m_prob = None
		self.cutoff = None
		self.sequential = None
		self.dispersal_relative_cost = None
		self.restrict_self = None
		self.dispersal_file = None
		if file:
			self.set_map(file)
		if isinstance(dispersal_db, DispersalSimulation):
			self.dispersal_database = dispersal_db.dispersal_database
		elif isinstance(dispersal_db, Map):
			self.file_name = dispersal_db.file_name
		else:
			self.dispersal_database = dispersal_db

	def __del__(self):
		"""
		Safely destroys the connection to the database, if it exists.
		"""
		self._close_database_connection()

	def _open_database_connection(self, database=None):
		"""
		Opens the connection to the database, raising the appropriate errors if the database does not exist
		Should have a matching call to _close_database_connection() for safely destroying the connection to the database
		file.
		"""
		if database is not None:
			if self.dispersal_database is not None:
				return
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

	def _check_table_exists(self, database=None, table_name="DISPERSAL_DISTANCES"):
		"""
		Checks that the dispersal distances table exits, and returns true/false.

		:param database: the database to open

		:return: true if the DISPERSAL_DISTANCES table exists in the output database
		:rtype bool
		"""
		self._open_database_connection(database)
		existence = self._db_conn.cursor().execute("SELECT name FROM sqlite_master WHERE type='table' AND"
												   " name='{}';".format(table_name)).fetchone() is not None
		return existence

	def set_simulation_parameters(self, number_repeats, output_database="output.db", seed=1, dispersal_method="normal",
								  landscape_type="closed", sigma=1, tau=1, m_prob=1, cutoff=100, sequential=False,
								  dispersal_relative_cost=1, restrict_self=False, number_steps=1,
								  dispersal_file="none"):
		"""
		Sets the simulation parameters for the dispersal simulations.

		:param int number_repeats: the number of times to iterate on the map
		:param str output_database: the path to the output database
		:param int seed: the random seed
		:param str dispersal_method: the dispersal method to use ("normal", "fat-tailed" or "norm-uniform")
		:param str landscape_type: the landscape type to use ("infinite", "tiled" or "closed")
		:param float sigma: the sigma value to use for normal and norm-uniform dispersal
		:param float tau: the tau value to use for fat-tailed dispersal
		:param float m_prob: the m_prob to use for norm-uniform dispersal
		:param float cutoff: the cutoff value to use for norm-uniform dispersal
		:param bool sequential: if true, end locations of one dispersal event are used as the start for the next. Otherwise,
		a new random cell is chosen
		:param float dispersal_relative_cost: relative dispersal ability through non-habitat
		:param bool restrict_self: if true, self-dispersal is not allowed
		:param str dispersal_file: path to the dispersal map file, or none.
		"""
		self.number_repeats = number_repeats
		if output_database != "output.db" or self.dispersal_database is None:
			self.dispersal_database = output_database
		self.seed = seed
		self.dispersal_method = dispersal_method
		self.landscape_type = landscape_type
		self.sigma = sigma
		self.tau = tau
		self.m_prob = m_prob
		self.cutoff = cutoff
		self.sequential = sequential
		self.dispersal_relative_cost = dispersal_relative_cost
		self.restrict_self = restrict_self
		self.number_steps = number_steps
		self.dispersal_file = dispersal_file



	def complete_setup(self):
		"""
		Completes the setup for the dispersal simulation.
		"""
		if not self.is_setup_map:
			raise RuntimeError("Maps have not been set up yet.")
		Dispersal.set_logger(self.logger)
		Dispersal.set_log_function(write_to_log)
		Dispersal.set_dispersal_parameters(self.dispersal_method, self.dispersal_file, self.sigma, self.tau,
										   self.m_prob, self.cutoff, self.dispersal_relative_cost, self.restrict_self)
		Dispersal.set_map_parameters(self.deme, self.fine_map.file_name, self.fine_map.x_size, self.fine_map.y_size,
									 self.fine_map.x_offset, self.fine_map.y_offset, self.sample_map.x_size,
									 self.sample_map.y_size, self.coarse_map.file_name, self.coarse_map.x_size,
									 self.coarse_map.y_size, self.coarse_map.x_offset, self.coarse_map.y_offset,
									 self.landscape_type)
		Dispersal.set_historical_map_parameters(self.historical_fine_list,
											  [x for x in range(len(self.historical_fine_list))],
											  self.rates_list, self.times_list, self.historical_coarse_list,
											  [x for x in range(len(self.historical_fine_list))],
											  self.rates_list, self.times_list)

	def test_mean_distance_travelled(self):
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
		self._close_database_connection()
		# Delete the file if it exists, and recursively create the folder if it doesn't
		check_parent(self.dispersal_database)
		if necsim_import_success:
			try:
				self.complete_setup()
				Dispersal.test_mean_distance_travelled(self.dispersal_database, self.number_repeats, self.number_steps,
													   self.seed)
			except Exception as e:
				raise Dispersal.DispersalError(str(e))
		else:
			raise ImportError("Successful c++ module import required for testing dispersal functions.")


	def test_mean_dispersal(self):
		"""
		Tests the dispersal kernel on the provided map, producing a database containing each dispersal distance for
		analysis purposes.

		.. note:: should be equivalent to :func:`~test_mean_distance_travelled` with number_steps = 1

		"""
		self._close_database_connection()
		# Delete the file if it exists, and recursively create the folder if it doesn't
		check_parent(self.dispersal_database)
		if necsim_import_success:
			try:
				self.complete_setup()
				Dispersal.test_mean_dispersal(self.dispersal_database, self.number_repeats, self.seed, self.sequential)
			except Exception as e:
				raise DispersalError(str(e))
		else:
			raise ImportError("Successful c++ module import required for testing dispersal functions.")

	def get_mean_dispersal(self, database=None, parameter_reference=1):
		"""
		Gets the mean dispersal for the map if test_mean_dispersal has already been run.

		:raises: ValueError if dispersal_database is None and so test_mean_dispersal() has not been run
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
									   (parameter_reference,)).fetchall()[0][0]
			if not sql_fetch:
				raise ValueError("Could not get mean distance for "
								 "parameter reference of {} from {}.".format(parameter_reference,
																			 self.dispersal_database))
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
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
									   (parameter_reference,)).fetchall()[0][0]
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
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
													  (parameter_reference,)).fetchall()]
			if len(sql_fetch) == 0:
				raise ValueError("No distances in DISPERSAL_DISTANCES, cannot find standard deviation.")
			stdev_distance = std(sql_fetch)
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
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
		:rtype: float
		"""
		if not self._check_table_exists(database=database, table_name="DISTANCES_TRAVELLED"):
			raise IOError("Database {} does not have a DISTANCES_TRAVELLED table".format(self.dispersal_database))
		try:
			self._open_database_connection(database=database)
			cursor = self._db_conn.cursor()
			sql_fetch = [x[0] for x in cursor.execute("SELECT distance FROM DISTANCES_TRAVELLED"
													  " WHERE parameter_reference = ?",
													  (parameter_reference,)).fetchall()]
			if len(sql_fetch) == 0:
				raise ValueError("No distances in DISTANCES_TRAVELLED, cannot find standard deviation.")
			stdev_distance = std(sql_fetch)
		except sqlite3.OperationalError as e:
			raise IOError("Could not get average distance from database: " + str(e))
		return stdev_distance

	def get_database_parameters(self):
		"""
		Gets the dispersal simulation parameters from the dispersal_db
		:return: the dispersal simulation parameters
		:rtype: dict
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
			# python 2.x support
			if sys.version_info[0] != 3:
				for i, each in enumerate(values):
					if isinstance(each, unicode):
						values[i] = each.encode('ascii')
			main_dict[values[0]] = dict(zip(column_names[1:], values[1:]))
		# Now convert it into a dictionary
		return main_dict

	def get_database_references(self):
		"""
		Gets the references from the database.
		:return: a list of references from the database
		:rtype: list
		"""
		self._open_database_connection()
		try:
			cursor = self._db_conn.cursor()
			cursor.execute("SELECT DISTINCT(ref) FROM PARAMETERS")
		except sqlite3.OperationalError as e:
			raise IOError("Could not get dispersal simulation parameters from database: {}".format(e))
		return [x[0] for x in cursor.fetchall()]