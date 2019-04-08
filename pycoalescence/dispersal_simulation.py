"""
Simulate dispersal kernels on landscapes. Detailed :ref:`here <Simulate_landscapes>`.

:input:
    - Map file to simulate on
    - Set of dispersal pararameters, including the dispersal kernel, number of repetitions and landscape properties

:output:
    - Database containing each distance travelled so that metrics can be calculated.
    - A table is created for mean dispersal distance over a single step or for mean distance travelled.
"""
from __future__ import absolute_import

import logging
import os
import sys

from numpy import std

# Python 2
try:
    from .necsim import libnecsim
except ImportError as ime:  # pragma: no cover
    from pycoalescence.necsim import libnecsim

try:
    try:
        import sqlite3
    except ImportError:  # pragma: no cover
        # Python 3 compatibility
        import sqlite as sqlite3
except ImportError as ie:  # pragma: no cover
    sqlite3 = None
    logging.warning("Problem importing sqlite module " + str(ie))

from pycoalescence.system_operations import check_parent, write_to_log
from pycoalescence.landscape import Landscape


class DispersalSimulation(Landscape):
    """
    Simulates a dispersal kernel upon a tif file to calculate landscape-level dispersal metrics.
    """

    def __init__(self, dispersal_db=None, file=None, logging_level=logging.WARNING):
        """
        Default initialiser for members of DispersalSimulation. Ensures that the database is

        :param str/pycoalescence.DispersalSimulation dispersal_db: path to a dispersal simulation database. Can also be
                                                                   a DispersalSimulation object containing the completed
                                                                   simulation.
        :param str file: sets the filename for reading tif files.
        :param bool is_sample: sets the sample mask to true, if it is a sampled file
        :param int logging_level: the level of logging to output during dispersal simulations
        """
        Landscape.__init__(self)
        self.logger = logging.Logger("pycoalescence.dispersal_simulation")
        self._create_logger(logging_level=logging_level)
        self._db_conn = None
        self.c_dispersal_simulation = None
        self._create_c_dispersal_simulation()
        self.deme = 1
        self.number_repeats = None
        self.number_steps = None
        self.seed = None
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
        if file is not None:
            self.set_map(file)
        if isinstance(dispersal_db, DispersalSimulation):
            self.dispersal_database = dispersal_db.dispersal_database
        else:
            self.dispersal_database = dispersal_db

    def __del__(self):
        """
        Safely destroys the connection to the database, if it exists, and destroys the C++ objects.
        """
        self._close_database_connection()
        self.c_dispersal_simulation = None

    def _create_c_dispersal_simulation(self):
        """Creates the CDispersalSimulation object, if it has not already been created."""
        if self.c_dispersal_simulation is None:
            self.c_dispersal_simulation = libnecsim.CDispersalSimulation(self.logger, write_to_log)

    def _open_database_connection(self, database=None):
        """
        Opens the connection to the database, raising the appropriate errors if the database does not exist
        Should have a matching call to _close_database_connection() for safely destroying the connection to the database
        file.
        """
        if database is not None:
            if self._db_conn is not None:  # pragma: no cover
                return
            self.dispersal_database = database
        if self.dispersal_database is None:  # pragma: no cover
            raise ValueError("Dispersal database is not set, run test_average_dispersal() first or set dispersal_db.")
        if not os.path.exists(self.dispersal_database):
            raise IOError("Dispersal database does not exist: {}".format(self.dispersal_database))
        # Open the SQLite connection
        try:
            self._db_conn = sqlite3.connect(self.dispersal_database)
        except sqlite3.Error as e:  # pragma: no cover
            self._db_conn = None
            raise IOError("Error opening SQLite database: {}".format(e))

    def _close_database_connection(self):
        """Safely closes the database connection."""
        if self._db_conn is not None:
            try:
                self._db_conn.close()
                self._db_conn = None
            except sqlite3.Error as e:  # pragma: no cover
                self._db_conn = None
                raise IOError("Could not close database: " + str(e))

    def _check_table_exists(self, database=None, table_name="DISPERSAL_DISTANCES"):
        """
        Checks that the dispersal distances table exits, and returns true/false.

        :param database: the database to open

        :return: true if the DISPERSAL_DISTANCES table exists in the output database
        :rtype: bool
        """
        self._open_database_connection(database)
        existence = (
            self._db_conn.cursor()
            .execute("SELECT name FROM sqlite_master WHERE type='table' AND" " name='{}';".format(table_name))
            .fetchone()
            is not None
        )
        return existence

    def _check_output_database(self):
        """Sets the setup to false if the output database has not been generated already."""
        self._create_c_dispersal_simulation()
        if not os.path.exists(self.dispersal_database):
            self.setup_complete = False
            self.c_dispersal_simulation.set_output_database(self.dispersal_database)

    def _remove_existing_db(self):
        """Removes an existing database correctly."""
        self._close_database_connection()
        self.c_dispersal_simulation = None
        self.setup_complete = False
        os.remove(self.dispersal_database)

    def set_map_files(
        self,
        fine_file,
        sample_file="null",
        coarse_file=None,
        historical_fine_file=None,
        historical_coarse_file=None,
        deme=1,
    ):
        """
        Sets the map files.

        Uses a null sampling regime, as the sample file should have no effect.

        :param str fine_file: the fine map file. Defaults to "null" if none provided
        :param str coarse_file: the coarse map file. Defaults to "none" if none provided
        :param str historical_fine_file: the historical fine map file. Defaults to "none" if none provided
        :param str historical_coarse_file: the historical coarse map file. Defaults to "none" if none provided
        :param int deme: the number of individuals per cell

        :rtype: None
        """
        Landscape.set_map_files(
            self,
            sample_file=sample_file,
            fine_file=fine_file,
            coarse_file=coarse_file,
            historical_fine_file=historical_fine_file,
            historical_coarse_file=historical_coarse_file,
        )
        self.deme = deme

    def set_dispersal_parameters(
        self,
        dispersal_method="normal",
        dispersal_file="none",
        sigma=1,
        tau=1,
        m_prob=1,
        cutoff=100,
        dispersal_relative_cost=1,
        restrict_self=False,
    ):
        """
        Sets the dispersal parameters.

        :param str dispersal_method: the dispersal method to use ("normal", "fat-tailed" or "norm-uniform")
        :param str dispersal_file: path to the dispersal map file, or none.
        :param float sigma: the sigma value to use for normal and norm-uniform dispersal
        :param float tau: the tau value to use for fat-tailed dispersal
        :param float m_prob: the m_prob to use for norm-uniform dispersal
        :param float cutoff: the cutoff value to use for norm-uniform dispersal
        :param float dispersal_relative_cost:relative dispersal ability through non-habitat
        :param bol restrict_self: if true, self-dispersal is prohibited
        """
        self.dispersal_method = dispersal_method
        self.sigma = sigma
        self.tau = tau
        self.m_prob = m_prob
        self.cutoff = cutoff
        self.dispersal_relative_cost = dispersal_relative_cost
        self.restrict_self = restrict_self
        self.dispersal_file = dispersal_file
        self.c_dispersal_simulation.set_dispersal_parameters(
            self.dispersal_method,
            self.dispersal_file,
            self.sigma,
            self.tau,
            self.m_prob,
            self.cutoff,
            self.dispersal_relative_cost,
            self.restrict_self,
        )

    def update_parameters(
        self,
        number_repeats=None,
        number_steps=None,
        seed=None,
        dispersal_method=None,
        dispersal_file=None,
        sigma=None,
        tau=None,
        m_prob=None,
        cutoff=None,
        dispersal_relative_cost=None,
        restrict_self=None,
    ):
        """
        Provides a convenience function for updating all parameters which can be updated.

        :param int number_repeats: the number of repeats to perform the dispersal simulation for
        :param list/int number_steps: the number of steps to iterate for in calculating the mean distance travelled
        :param int seed: the random number seed
        :param str dispersal_method: the method of dispersal
        :param str dispersal_file: the dispersal file (alternative to dispersal_method)
        :param float sigma: the sigma dispersal value
        :param float tau: the tau dispersal value
        :param float m_prob: the probability of drawing from a uniform distribution
        :param float cutoff: the maximum value for the uniform distribution
        :param float dispersal_relative_cost: the relative cost of moving through non-habitat
        :param bool restrict_self: if true, prohibits dispersal from the same cell

        :rtype: None
        """
        vars = locals().copy()
        for k, v in vars.items():
            if v is not None:
                setattr(self, k, v)
            if k == "number_steps" and v is not None:
                if isinstance(v, list):
                    self.number_steps = v
                else:
                    self.number_steps = [v]
        self.set_dispersal_parameters(
            self.dispersal_method,
            self.dispersal_file,
            self.sigma,
            self.tau,
            self.m_prob,
            self.cutoff,
            self.dispersal_relative_cost,
            self.restrict_self,
        )

    def set_simulation_parameters(
        self,
        number_repeats=None,
        output_database="output.db",
        seed=1,
        dispersal_method="normal",
        landscape_type="closed",
        sigma=1,
        tau=1,
        m_prob=1,
        cutoff=100,
        sequential=False,
        dispersal_relative_cost=1,
        restrict_self=False,
        number_steps=1,
        dispersal_file="none",
    ):
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
        :param bool restrict_self: if true, self-dispersal is prohibited
        :param list/int number_steps: the number to calculate for mean distance travelled, provided as an int or a list
                                       of ints
        :param str dispersal_file: path to the dispersal map file, or none.
        """
        self.number_repeats = number_repeats
        if output_database != "output.db" or self.dispersal_database is None:
            self.dispersal_database = output_database
        self.dispersal_database = os.path.abspath(self.dispersal_database)
        self.seed = seed
        self.landscape_type = landscape_type
        self.sequential = sequential
        self.restrict_self = restrict_self
        if isinstance(number_steps, list):  # pragma: no cover
            self.number_steps = [int(x) for x in number_steps]
        else:
            self.number_steps = [int(number_steps)]
        if not os.path.exists(os.path.dirname(self.dispersal_database)):  # pragma: no cover
            os.makedirs(os.path.dirname(self.dispersal_database))
        self.c_dispersal_simulation.set_output_database(self.dispersal_database)
        self.set_dispersal_parameters(
            dispersal_method, dispersal_file, sigma, tau, m_prob, cutoff, dispersal_relative_cost, restrict_self
        )

    def complete_setup(self):
        """
        Completes the setup for the dispersal simulation, including importing the map files and setting the historical
        maps.
        """
        if not self.is_setup_map:  # pragma: no cover
            raise RuntimeError("Maps have not been set up yet.")
        self._check_output_database()
        self.c_dispersal_simulation.set_dispersal_parameters(
            self.dispersal_method,
            self.dispersal_file,
            self.sigma,
            self.tau,
            self.m_prob,
            self.cutoff,
            self.dispersal_relative_cost,
            self.restrict_self,
        )
        if self.setup_complete:  # pragma: no cover
            self.logger.info("Set up has already been completed.")
        else:
            if len(self.historical_fine_list) != 0:
                self.c_dispersal_simulation.import_all_maps(
                    self.deme,
                    self.fine_map.file_name,
                    self.fine_map.x_size,
                    self.fine_map.y_size,
                    self.fine_map.x_offset,
                    self.fine_map.y_offset,
                    self.sample_map.x_size,
                    self.sample_map.y_size,
                    self.coarse_map.file_name,
                    self.coarse_map.x_size,
                    self.coarse_map.y_size,
                    self.coarse_map.x_offset,
                    self.coarse_map.y_offset,
                    int(self.coarse_scale),
                    self.landscape_type,
                    self.historical_fine_list,
                    [x for x in range(len(self.historical_fine_list))],
                    [float(x) for x in self.rates_list],
                    [float(x) for x in self.times_list],
                    self.historical_coarse_list,
                    [x for x in range(len(self.historical_fine_list))],
                    [float(x) for x in self.rates_list],
                    [float(x) for x in self.times_list],
                )
            else:
                self.c_dispersal_simulation.import_maps(
                    self.deme,
                    self.fine_map.file_name,
                    self.fine_map.x_size,
                    self.fine_map.y_size,
                    self.fine_map.x_offset,
                    self.fine_map.y_offset,
                    self.sample_map.x_size,
                    self.sample_map.y_size,
                    self.coarse_map.file_name,
                    self.coarse_map.x_size,
                    self.coarse_map.y_size,
                    self.coarse_map.x_offset,
                    self.coarse_map.y_offset,
                    int(self.coarse_scale),
                    self.landscape_type,
                )
            self.setup_complete = True

    def check_base_parameters(self, number_repeats=None, seed=None, sequential=None):
        """
        Checks that the parameters have been set properly.

        :param int number_repeats: the number of times to iterate on the map
        :param int seed: the random seed
        :param bool sequential: if true, runs repeats sequentially

        :rtype: None
        """
        if number_repeats is None and self.number_repeats is None:
            raise ValueError("number_repeats has not been set.")
        if seed is None and self.seed is None:
            raise ValueError("Seed has not been set.")
        if sequential is None and self.sequential is None:
            raise ValueError("sequential flag has not been set.")
        if number_repeats is not None:
            self.number_repeats = number_repeats
        if seed is not None:
            self.seed = seed
        if sequential is not None:
            self.sequential = sequential
        self._check_output_database()

    def run_mean_distance_travelled(self, number_repeats=None, number_steps=None, seed=None, sequential=None):
        """
        Tests the dispersal kernel on the provided map, producing a database containing the average distance travelled
        after number_steps have been moved.

        .. note::

                mean distance travelled with number_steps=1 should be equivalent to running
                :func:`~run_mean_dispersal`

        :param int number_repeats: the number of times to iterate on the map
        :param int/list number_steps: the number of steps to take each time before recording the distance travelled
        :param int seed: the random seed
        :param bool sequential: if true, runs repeats sequentially

        :rtype: None
        """
        self._close_database_connection()
        # Delete the file if it exists, and recursively create the folder if it doesn't
        check_parent(self.dispersal_database)
        if number_steps is None and self.number_steps in [None, [None], []]:
            raise ValueError("number_steps has not been set.")
        self.check_base_parameters(number_repeats=number_repeats, seed=seed, sequential=sequential)
        if number_steps is not None:
            self.number_steps = number_steps
        if not self.setup_complete:
            self.complete_setup()
        self.c_dispersal_simulation.run_mean_distance_travelled(
            self.number_repeats, self.number_steps, self.seed, self.sequential
        )

    def run_mean_dispersal(self, number_repeats=None, seed=None, sequential=None):
        """
        Tests the dispersal kernel on the provided map, producing a database containing each dispersal distance for
        analysis purposes.

        .. note:: should be equivalent to :func:`~run_mean_distance_travelled` with number_steps = 1

        :param int number_repeats: the number of times to iterate on the map
        :param int seed: the random seed
        :param bool sequential: if true, runs repeats sequentially
        """
        self._close_database_connection()
        # Delete the file if it exists, and recursively create the folder if it doesn't
        check_parent(self.dispersal_database)
        self.check_base_parameters(number_repeats=number_repeats, seed=seed, sequential=sequential)
        if not self.setup_complete:
            self.complete_setup()
        self.c_dispersal_simulation.run_mean_dispersal_distance(self.number_repeats, self.seed, self.sequential)

    def get_all_dispersal(self, database=None, parameter_reference=1):
        """
        Gets all mean dispersal values from the database if run_mean_dispersal has already been run.

        :raises: ValueError if dispersal_database is None and so run_mean_dispersal() has not been run
        :raises: IOError if the output database does not exist

        :param str database: the database to open
        :param int parameter_reference: the parameter reference to use (default 1)
        :return: the dispersal values from the database
        """
        if not self._check_table_exists(database=database, table_name="DISPERSAL_DISTANCES"):
            raise IOError("Database {} does not have a DISPERSAL_DISTANCES table".format(self.dispersal_database))
        try:
            self._open_database_connection(database=database)
            cursor = self._db_conn.cursor()
            sql_fetch = cursor.execute(
                "SELECT distance FROM DISPERSAL_DISTANCES WHERE parameter_reference = ?", (parameter_reference,)
            ).fetchall()
            if not sql_fetch:
                raise ValueError(
                    "Could not get dispersal distances for "
                    "parameter reference of {} from {}.".format(parameter_reference, self.dispersal_database)
                )
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get all dispersals from database: {}.".format(e))
        return [x[0] for x in sql_fetch]

    def get_mean_dispersal(self, database=None, parameter_reference=1):
        """
        Gets the mean dispersal for the map if run_mean_dispersal has already been run.

        :raises: ValueError if dispersal_database is None and so run_mean_dispersal() has not been run
        :raises: IOError if the output database does not exist

        :param str database: the database to open
        :param int parameter_reference: the parameter reference to use (default 1)).
        :return: mean dispersal from the database
        """
        if not self._check_table_exists(database=database, table_name="DISPERSAL_DISTANCES"):
            raise IOError("Database {} does not have a DISPERSAL_DISTANCES table".format(self.dispersal_database))
        try:
            self._open_database_connection(database=database)
            cursor = self._db_conn.cursor()
            sql_fetch = cursor.execute(
                "SELECT AVG(distance) FROM DISPERSAL_DISTANCES WHERE parameter_reference = ?", (parameter_reference,)
            ).fetchall()[0][0]
            if not sql_fetch:
                raise ValueError(
                    "Could not get mean dispersal for "
                    "parameter reference of {} from {}.".format(parameter_reference, self.dispersal_database)
                )
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get mean dispersal from database: {}.".format(e))
        return sql_fetch

    def get_all_distances(self, database=None, parameter_reference=1):
        """
        Gets all total distances travelled from the database if run_distance_travelled has already been run.

        :raises: ValueError if dispersal_database is None and so run_mean_dispersal() has not been run
        :raises: IOError if the output database does not exist

        :param str database: the database to open
        :param int parameter_reference: the parameter reference to use (default 1)
        :return: the dispersal values from the database
        """
        if not self._check_table_exists(database=database, table_name="DISTANCES_TRAVELLED"):
            raise IOError("Database {} does not have a DISTANCES_TRAVELLED table".format(self.dispersal_database))
        try:
            self._open_database_connection(database=database)
            cursor = self._db_conn.cursor()
            sql_fetch = cursor.execute(
                "SELECT distance FROM DISTANCES_TRAVELLED WHERE parameter_reference = ?", (parameter_reference,)
            ).fetchall()
            if not sql_fetch:
                raise ValueError(
                    "Could not get distances travelled for "
                    "parameter reference of {} from {}.".format(parameter_reference, self.dispersal_database)
                )
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get all distances travelled from database: {}.".format(e))
        return [x[0] for x in sql_fetch]

    def get_mean_distance_travelled(self, database=None, parameter_reference=1):
        """
        Gets the mean dispersal for the map if run_mean_dispersal has already been run.

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
            sql_fetch = cursor.execute(
                "SELECT AVG(distance) FROM DISTANCES_TRAVELLED WHERE parameter_reference = ?", (parameter_reference,)
            ).fetchall()[0][0]
            if not sql_fetch:
                raise ValueError(
                    "Could not get mean distance travelled for "
                    "parameter reference of {} from {}.".format(parameter_reference, self.dispersal_database)
                )
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get average distance from database: {}.".format(e))
        return sql_fetch

    def get_stdev_dispersal(self, database=None, parameter_reference=1):
        """
        Gets the standard deviation of dispersal for the map if run_mean_dispersal has already been run.

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
            sql_fetch = [
                x[0]
                for x in cursor.execute(
                    "SELECT distance FROM DISPERSAL_DISTANCES " "WHERE parameter_reference = ?", (parameter_reference,)
                ).fetchall()
            ]
            if len(sql_fetch) == 0:  # pragma: no cover
                raise ValueError("No distances in DISPERSAL_DISTANCES, cannot find standard deviation.")
            stdev_distance = std(sql_fetch)
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get average distance from database: {}".format(e))
        return stdev_distance

    def get_stdev_distance_travelled(self, database=None, parameter_reference=1):
        """
        Gets the standard deviation of the  distance travelled for the map if run_mean_distance_travelled has already
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
            sql_fetch = [
                x[0]
                for x in cursor.execute(
                    "SELECT distance FROM DISTANCES_TRAVELLED" " WHERE parameter_reference = ?", (parameter_reference,)
                ).fetchall()
            ]
            if len(sql_fetch) == 0:  # pragma: no cover
                raise ValueError("No distances in DISTANCES_TRAVELLED, cannot find standard deviation.")
            stdev_distance = std(sql_fetch)
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get average distance from database: {}.".format(e))
        return stdev_distance

    def get_database_parameters(self, reference=None):
        """
        Gets the dispersal simulation parameters from the dispersal_db

        :param reference: the reference to obtain parameters for

        :return: the dispersal simulation parameters

        :rtype: dict
        """
        self._open_database_connection()
        try:
            cursor = self._db_conn.cursor()
            cursor.execute(
                "SELECT ref, simulation_type, sigma, tau, m_prob, cutoff, dispersal_method, map_file, seed,"
                " number_steps, number_repeats FROM PARAMETERS"
            )
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get dispersal simulation parameters from database: {}".format(e))
        column_names = [member[0] for member in cursor.description]
        main_dict = {}
        for row in cursor.fetchall():
            values = [x for x in row]
            # Python 2.x support
            if sys.version_info[0] != 3:  # pragma: no cover
                for i, each in enumerate(values):
                    if isinstance(each, unicode):
                        values[i] = each.encode("ascii")
            # Now convert it into a dictionary
            main_dict[values[0]] = dict(zip(column_names[1:], values[1:]))
        if reference is None:
            return main_dict
        else:
            try:
                return main_dict[reference]
            except KeyError:
                raise KeyError("No reference exists in the database with a value of {}".format(reference))

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
        except sqlite3.Error as e:  # pragma: no cover
            raise IOError("Could not get dispersal simulation parameters from database: {}".format(e))
        return [x[0] for x in cursor.fetchall()]
