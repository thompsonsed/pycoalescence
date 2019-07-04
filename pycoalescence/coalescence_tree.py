"""
Generate the coalescence tree and acquire a number of biodiversity metrics for different parameter sets. Can also be
used to compare against a comparison simulation object.

:input:
	- Completed simulation database from :class:`.Simulation`
	- Parameters and operations to apply

:output:
	- A variety of biodiversity metrics, including species richness and abundance distributions, locations of each
	  species, alpha and beta diversity, plus equivalent fragment biodiversity metrics.
	- Modifies the simulation database in place.
"""
from __future__ import absolute_import, division

import csv
import json
import logging
import math
import os
import random
import sqlite3
import sys
from collections import defaultdict, Iterable
from operator import itemgetter

import numpy as np
import pandas as pd

try:
    from .necsim import libnecsim
except ImportError as ie:  # pragma: no cover
    logging.info(str(ie))
    from necsim import libnecsim, necsimError

from .future_except import FileNotFoundError, FileExistsError
from .system_operations import mod_directory, create_logger, write_to_log
from .spatial_algorithms import calculate_distance_between
from .sqlite_connection import check_sql_table_exist, fetch_table_from_sql, get_table_names, SQLiteConnection
import pycoalescence

# Reads the parameter descriptions from the json file.
try:
    with open(os.path.join(mod_directory, "reference", "parameter_descriptions.json")) as f:
        _parameter_descriptions = json.load(f)
except (FileNotFoundError, IOError):  # pragma: no cover
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
    except KeyError:
        raise KeyError("Key {} was not found in parameter dictionary. Use key=None to show the whole dictionary")


class CoalescenceTree(object):
    """
    Contains the coalescence tree and performs various calculations of different biodiversity metrics, which are then
    stored in the SQLite database.

    The general process is

    * Import the database (:py:meth:`~set_database`) and import the comparison data,
      if required (:py:meth:`~import_comparison_data`)

    * Apply additional speciation rates (if required) using :py:meth:`~set_speciation_parameters` and then
      :py:meth:`~apply`

    * Calculate required metrics (such as :py:meth:`~calculate_fragment_richness`)
    * Optionally, calculate the goodness of fit (:py:meth:`~calculate_goodness_of_fit`)
    """

    def __init__(self, database=None, logging_level=logging.WARNING, log_output=None):
        """
        Initiates the CoalescenceTree object. By default, links to the SpeciationCounter program stored in
        build/default/SpeciationCounter, but optionally takes speciation_program as a path to an alternative program.

        :param str/pycoalescence.Simulation database: optionally specify the path to call :py:meth:`~set_database` to
        :param int logging_level: the level from the logging module for desired terminal outputs
        :param str log_output: optionally provide a file to output information to instead
        :return: None
        """
        # C object for calculating the coalescence tree
        self.c_community = None
        # speciation objects
        self.equalised = False
        self.is_setup_speciation = False
        self.record_spatial = False
        self.times = None
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
        self.protracted_parameters = []
        # Metacommunity parameters
        self.metacommunity_size = None
        self.metacommunity_speciation_rate = None
        self.metacommunity_option = None
        self.metacommunity_reference = None
        self.logger = logging.Logger("pycoalescence.coalescence")
        self.logging_level = logging_level
        self._create_logger(file=log_output)
        if database is not None:
            self.set_database(database)
        # Set to true once speciation rates have been written to the output database.
        self.has_outputted = False
        self.has_applied = False

    def __del__(self):
        """
        Closes the database connection.
        """
        if self.database is not None:
            self.cursor = None
            self.database.close()
            self.database = None
        self.c_community = None
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def _create_logger(self, file=None, logging_level=None):
        """
        Creates the logger for use with applying speciation rates to a simulation.
        This function should only be run during :py:meth:`~__init__`

        .. tip:: Supply your own logger by over-riding :attr:`~import_comparison_data`.

        :param str file: file to write output to. If None, outputs to terminal
        :param int logging_level: the logging level to use (defaults to INFO=20)

        :return: None
        """
        if logging_level is None:
            logging_level = self.logging_level
        self.logger = create_logger(self.logger, file, logging_level)

    def _check_fragment_numbers_match(self):
        """
        Checks that the numbers of individuals match between the comparison_abundances object and the simulation
        database for each fragment

        :return: true if the numbers match
        :rtype: bool
        """
        if not self.fragment_abundances:
            raise RuntimeError("No fragment abundances imported.")
        if self.comparison_abundances is None:
            if self.comparison_file is not None:
                self.import_comparison_data(self.comparison_file)
            else:
                raise ValueError("Cannot check matched numbers before importing comparison database.")
        for fragment in set([x[0] for x in self.fragment_abundances]):
            for ref in set([x[3] for x in self.fragment_abundances]):
                sum_simulated = sum([x[2] for x in self.fragment_abundances if x[0] == fragment and x[3] == ref])
                if sum_simulated != sum([x[2] for x in self.comparison_abundances if x[0] == fragment]):
                    return False
        return True

    def _set_record_fragments(self, record_fragments):
        """
        Checks if the fragment record flag is correctly set and sets the relevant parameter.

        :param bool/str record_fragments: the fragments record flag to check

        :rtype: None
        """
        if isinstance(record_fragments, bool):
            if record_fragments:
                record_fragments = "null"
            else:
                record_fragments = "F"
        if record_fragments is "T":
            record_fragments = "null"
        if record_fragments not in ["F", "null"]:
            if not os.path.exists(record_fragments):
                raise FileNotFoundError("Fragment config does not exist at {}.".format(record_fragments))
            if not (record_fragments.endswith(".csv") or record_fragments.endswith(".txt")):
                raise IOError("Supplied fragment config file is not a csv or txt file: {}.".format(record_fragments))
        self.record_fragments = record_fragments

    def _set_record_spatial(self, record_spatial):
        """
        Checks that the spatial record flag has been correctly set and sets the relevant parameter.

        :param bool/str record_spatial: the object to check correctly identifies a spatial option

        :rtype: None
        """
        if record_spatial is "T":
            record_spatial = True
        elif record_spatial is "F":
            record_spatial = False
        elif not isinstance(record_spatial, bool):
            raise TypeError("record_spatial must be a boolean.")
        self.record_spatial = record_spatial

    def _set_speciation_rates(self, speciation_rates):
        """
        Checks that the speciation rates are correctly set for applying to the community and sets the applied
        speciation rates parameter.

        :param list/float speciation_rates: the speciation rates object to check is the correct format

        :rtype: None
        """
        if speciation_rates is None:
            raise RuntimeError("No speciation rates supplied: requires at least 1 for analysis.")
        elif not isinstance(speciation_rates, Iterable):
            speciation_rates = [speciation_rates]
        try:
            speciation_rates = [float(x) for x in speciation_rates]
        except ValueError as ve:
            raise TypeError("Speciation rates are not floats: {}".format(ve))
        for spec_rate in speciation_rates:
            if spec_rate > 1.0 or spec_rate < 0.0:
                raise ValueError("Speciation rates must be between 0.0 and 1.0.")
        self.applied_speciation_rates_list = speciation_rates

    def _set_metacommunity_parameters(
        self,
        metacommunity_size=None,
        metacommunity_speciation_rate=None,
        metacommunity_option=None,
        metacommunity_reference=None,
    ):
        """
        Checks that the metacommunity parameters make sense and assigns them within the object.

        :param float metacommunity_size: the number of individuals in the metacommunity
        :param float metacommunity_speciation_rate: the speciation rate within the metacommunity
        :param str metacommunity_option: either "simulated", "analytical", or a path to a database to read SADs from
        :param int metacommunity_reference: the metacommunity reference if using a database to provide the metacommunity

        :rtype: None
        """
        if (
            not metacommunity_size
            and not metacommunity_speciation_rate
            and not metacommunity_option
            and not metacommunity_reference
        ):
            self.metacommunity_size = 0
            self.metacommunity_speciation_rate = 0.0
            self.metacommunity_option = "none"
            self.metacommunity_reference = 0
        else:
            if metacommunity_option is None:
                metacommunity_option = "none"
            if metacommunity_size is not None and metacommunity_speciation_rate is not None:
                if metacommunity_size > 0 and 0.0 < metacommunity_speciation_rate <= 1.0:
                    self.metacommunity_size = metacommunity_size
                    self.metacommunity_speciation_rate = metacommunity_speciation_rate
                else:
                    raise ValueError(
                        "Must supply both metacommunity size >0 and speciation rate between 0 and 1 for "
                        "generating a metacommunity."
                    )
                if metacommunity_option not in ["simulated", "analytical", "none"]:
                    raise ValueError(
                        "Must use 'simulated' or 'analytical' for metacommunity option when supplying "
                        "a metacommunity size and speciation rate."
                    )
                if metacommunity_option == "none":
                    if metacommunity_size > 100000:
                        self.logger.info("Using analytical method for generating metacommunity.\n")
                        self.metacommunity_option = "analytical"
                    else:
                        self.logger.info("Using simulated method of generating metacommunity.\n")
                        self.metacommunity_option = "simulated"
                else:
                    self.metacommunity_option = metacommunity_option
                self.metacommunity_reference = 0
            else:
                if metacommunity_option in ["simulated", "analytical", "none"]:
                    raise ValueError(
                        "Must supply both metacommunity size >0 and speciation rate between 0 and 1 for "
                        "generating a metacommunity."
                    )
                if metacommunity_size not in [0, None] or metacommunity_speciation_rate not in [
                    0.0,
                    None,
                ]:  # pragma: no cover
                    raise ValueError(
                        "No metacommunity size or speciation rate should be supplied when using an "
                        "external database for the metacommunity."
                    )
                if not os.path.exists(metacommunity_option):
                    raise FileNotFoundError("No file exists to supply metacommunity at {}.".format(metacommunity_option))
                if metacommunity_reference is None:
                    self.metacommunity_reference = 1
                else:
                    self.metacommunity_reference = metacommunity_reference
                self.metacommunity_size = 0
                self.metacommunity_speciation_rate = 0.0
                self.metacommunity_option = metacommunity_option
            if not isinstance(self.c_community, libnecsim.CMetacommunity):
                self._reset_parameters()
            self.c_community.add_metacommunity_parameters(
                self.metacommunity_size,
                self.metacommunity_speciation_rate,
                self.metacommunity_option,
                self.metacommunity_reference,
            )

    def _set_protracted_parameters(self, protracted_speciation_min=None, protracted_speciation_max=None):
        """
        Checks that the protracted parameters are valid and adds them to the simulation object.

        :param float protracted_speciation_min: the minimum generation for protracted speciation
        :param float protracted_speciation_max: the maximum generation for protracted speciation

        :return: list containing the set of protracted speciation minimums and maximums
        """
        if protracted_speciation_max is not None and protracted_speciation_min is not None:
            if not self.is_protracted():
                raise ValueError("Supplied protracted parameters for a non-protracted simulation.")
            else:
                self.add_protracted_parameters(float(protracted_speciation_min), float(protracted_speciation_max))
        else:
            self.add_protracted_parameters(0.0, 0.0)

    def _check_protracted_parameters(self, min_speciation_gen, max_speciation_gen):
        """
        Checks that the protracted parameters make sense compared to the original protracted parameters.

        :param float min_speciation_gen: minimum number of generations for protracted speciation
        :param float max_speciation_gen: maximum number of generations for protracted speciation

        :rtype: None
        """
        db_min = self.get_simulation_parameters()["min_speciation_gen"]
        db_max = self.get_simulation_parameters()["max_speciation_gen"]
        if min_speciation_gen < 0.0 or min_speciation_gen > db_min:
            raise ValueError(
                "Minimum generation for protracted speciation cannot be less than 0.0, or greater than "
                "the initial value used during simulation ({}).".format(db_min)
            )
        if max_speciation_gen < min_speciation_gen or max_speciation_gen > db_max:
            raise ValueError(
                "Maximum generation for protracted speciation cannot be less than the minimum, or greater"
                " than the initial value used during simulation ({}).".format(db_max)
            )

    def _set_sample_file(self, sample_file=None):
        """
        Checks that the sample file has been correctly set and sets it within the object.

        :param str sample_file: the file to use to determine spatial sampling

        :rtype: None
        """
        if sample_file is None:
            self.logger.info("No sample file provided, defaulting to null.\n")
            self.sample_file = "null"
        else:
            if sample_file != "null":
                if not os.path.exists(sample_file):
                    raise FileNotFoundError("Sample file does not exist at {}.".format(sample_file))
                ext = os.path.splitext(sample_file)[1]
                if ext not in [".tif", ".csv"]:
                    raise IOError("Extension is not .tif or .csv: {}.".format(ext))
            self.sample_file = sample_file

    def _set_times(self, times):
        """
        Checks that the times are valid and adds them to the object.

        :param list/float times: times to generate communities for

        :rtype: None
        """
        if times in (None, [], [None]):
            self.logger.info("No times provided, defaulting to 0.0.\n")
            self.add_time(0.0)
        else:
            if isinstance(times, Iterable):
                self.add_times(times)
            else:
                self.add_time(times)

    def _reset_parameters(self):
        """
        Resets the object and adds all the required parameters to the object again.

        Used when a standard CCommunity object is converted to a CMetacommunity object.
        """
        self.c_community = None
        self._setup_c_community()
        # The times have already been added in the above function call, so just need to add the protracted parameters
        tmp_protracted_params = self.protracted_parameters
        if len(tmp_protracted_params) > 0:
            self.protracted_parameters = []
            for min_proc, max_proc in tmp_protracted_params:
                self.add_protracted_parameters(min_proc, max_proc)

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
                for i, frag_abundance in enumerate(self.fragment_abundances):
                    if frag_abundance[0] == fragment and frag_abundance[3] == reference:
                        tmp_total += frag_abundance[2]
                        if tmp_total > rand_individual:
                            if frag_abundance[2] > 0:
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
                for i, frag_abundance in enumerate(self.comparison_abundances):
                    if frag_abundance[0] == fragment:
                        tmp_total += frag_abundance[2]
                        if tmp_total > rand_individual:
                            if frag_abundance[2] > 0:
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
        if not self.equalised:
            if not self.fragment_abundances:  # pragma: no cover
                self.calculate_fragment_abundances()
            if not self.fragment_abundances or not self.comparison_abundances:
                raise ValueError("Cannot equalise fragment numbers if comparison or simulation data is missing.")
            random.seed(self.get_simulation_parameters()["seed"])
            for fragment in set([x[0] for x in self.fragment_abundances]):
                for reference in set([x[3] for x in self.fragment_abundances]):
                    self._equalise_fragment_number(fragment, reference)
            # now double check numbers match
            if not self._check_fragment_numbers_match():  # pragma: no cover
                raise SystemError("Failure attempting to equalise fragment numbers.")
            else:
                self.equalised = True

    def _adjust_species_abundances(self):
        """
        Recalculates the species abundances from the equalised fragment abundances and writes over the
        SPECIES_ABUNDANCES table
        """
        if not self.equalised:  # pragma: no cover
            self._equalise_all_fragment_numbers()
        species_abundances = []
        id_counter = 0
        for reference in set([x[3] for x in self.fragment_abundances]):
            reference_subset = [x for x in self.fragment_abundances if x[3] == reference]
            for species_id in set([x[1] for x in reference_subset]):
                id_counter += 1
                total = sum([x[2] for x in reference_subset if x[1] == species_id])
                species_abundances.append([id_counter, species_id, total, reference])
        self._check_database()
        self.cursor.execute("DROP TABLE IF EXISTS SPECIES_ABUNDANCES")
        self.cursor.execute(
            "CREATE TABLE SPECIES_ABUNDANCES (ID INT NOT NULL PRIMARY KEY, species_id INT NOT NULL,"
            "no_individuals INT NOT NULL, community_reference INT NOT NULL)"
        )
        self.cursor.executemany("INSERT INTO SPECIES_ABUNDANCES VALUES(?,?,?,?)", species_abundances)
        self.database.commit()

    def _adjust_fragment_abundances(self):
        """
        Equalises fragment abundances with the comparison data, and overrides the FRAGMENT_ABUNDANCES table in the
        output database.
        """
        self._check_database()
        if not self.equalised:  # pragma: no cover
            self._equalise_all_fragment_numbers()
        self.cursor.execute("DROP TABLE IF EXISTS FRAGMENT_ABUNDANCES")
        self.cursor.execute(
            "CREATE TABLE FRAGMENT_ABUNDANCES (fragment TEXT NOT NULL, species_id INT NOT NULL,"
            " no_individuals INT NOT NULL, community_reference INT NOT NULL)"
        )
        self.cursor.executemany("INSERT INTO FRAGMENT_ABUNDANCES VALUES(?,?,?,?)", self.fragment_abundances)
        self.database.commit()

    def _adjust_species_richness(self):
        """
        Recalculates the species richnesses equating numbers from the comparison data.
        """
        self._check_database()
        if not self.equalised:  # pragma: no cover
            self._adjust_fragment_abundances()
            self._adjust_species_abundances()
        self.cursor.execute("DROP TABLE IF EXISTS SPECIES_RICHNESS")
        self.calculate_richness(output_metrics=False)

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
        if self.comparison_file is None or not os.path.exists(self.comparison_file):  # pragma: no cover
            raise ValueError("Cannot get plot data from comparison file {}".format(self.comparison_file))
        with SQLiteConnection(self.comparison_file) as cursor:
            plot_data = cursor.execute("SELECT fragment, no_individuals FROM PLOT_DATA").fetchall()
        return [x for x in plot_data]

    def _get_sim_parameters_guild(self, guild):
        """
        Gets the simulation parameters associated with this particular guild.

        :param guild: the guild number to obtain reference numbers for

        :return: dictionary containing simulation parameters for the given guild
        """
        self._check_database()
        try:
            self.cursor.execute(
                "SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme, sample_size, "
                "max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, "
                "gen_since_historical, "
                "time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, "
                "fine_map_x_offset, fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, "
                "sample_y, "
                "sample_x_offset, sample_y_offset, historical_coarse_map, "
                " historical_fine_map, sim_complete, dispersal_method, m_probability, cutoff,"
                " landscape_type,  protracted, min_speciation_gen, max_speciation_gen, dispersal_map"
                " FROM SIMULATION_PARAMETERS WHERE guild == ?",
                (guild,),
            )
        except sqlite3.Error as e:  # pragma: no cover
            self.logger.error(
                "Failure to get SIMULATION_PARAMETERS table from database with guild {}"
                ". Check table exists.".format(guild)
            )
            raise e
        out = self.cursor.fetchone()
        if len(out) == 0:  # pragma: no cover
            raise ValueError("No simulation parameters exist for guild {}".format(guild))
        column_names = [member[0] for member in self.cursor.description]
        values = [x for x in out]
        if sys.version_info[0] is not 3:  # pragma: no cover
            for i, each in enumerate(values):
                if isinstance(each, unicode):
                    values[i] = each.encode("ascii")
        # Now convert it into a dictionary
        return dict(zip(column_names, values))

    def set_database(self, filename):
        """
        Sets the database to the specified file and opens the sqlite connection.

        This must be done before any other operations can be performed and the
        file must exist.

        :raises IOError: if the simulation is not complete, as analysis can only be performed on complete simulations.
         However, the database WILL be set before the error is thrown, allowing for analysis of
         incomplete simulations if the error is handled correctly.

        :param pycoalescence.simulation.Simulation/str filename: the SQLite database file to import
        """
        if isinstance(filename, pycoalescence.simulation.Simulation):
            filename = filename.output_database
            if filename is None:  # pragma: no cover
                raise RuntimeError(
                    "Coalescence object does has not been set up properly and does not contain an output"
                    " database location."
                )
        if os.path.exists(filename):
            self.file = filename
            try:
                self.database = sqlite3.connect(filename)
            except sqlite3.Error as e:  # pragma: no cover
                try:
                    self.database.close()
                except AttributeError:
                    pass
                self.database = None
                raise IOError("Error opening SQLite database: {}".format(e))
            # Now make sure that the simulation has been completed
            try:
                self.cursor = self.database.cursor()
                sql_fetch = self.cursor.execute(
                    "SELECT sim_complete, time_config_file FROM SIMULATION_PARAMETERS"
                ).fetchall()[0]
                # print(sql_fetch)
                complete = bool(sql_fetch[0])
                if sql_fetch[1] != "null":
                    self.times = [0.0]
                if not complete:
                    self.is_complete = False
                    raise IOError(
                        "{} is not a complete simulation. "
                        "Please finish simulation before performing analysis.".format(filename)
                    )
                else:
                    self.is_complete = True
            except sqlite3.Error as soe:  # pragma: no cover
                self.database.close()
                raise sqlite3.Error("Error checking simulation was complete: " + str(soe))
            except IndexError:  # pragma: no cover
                self.database.close()
                raise sqlite3.Error("Could not fetch SIMULATION_PARAMETERS. Table contains no data.")
        else:
            raise FileNotFoundError("File {} does not exist.".format(filename))

    def set_speciation_parameters(
        self,
        speciation_rates,
        record_spatial=False,
        record_fragments=False,
        sample_file=None,
        times=None,
        protracted_speciation_min=None,
        protracted_speciation_max=None,
        metacommunity_size=None,
        metacommunity_speciation_rate=None,
        metacommunity_option=None,
        metacommunity_reference=None,
    ):
        """

        Set the parameters for the application of speciation rates. If no config files or time_config files are
        provided, they will be taken from the main coalescence simulation.

        :param float/list speciation_rates: a single float, or list of speciation rates to apply
        :param bool, str record_spatial: a boolean of whether to record spatial data (default=False)
        :param bool, str record_fragments: either a csv file containing fragment data, or T/F for whether fragments
                                           should be calculated from squares of continuous habitat (default=False)
        :param str sample_file: a sample tif or csv specifying the sampling mask
        :param list times: a list of times to apply (should have been run with the original simulation)
        :param float protracted_speciation_min: the minimum number of generations required for speciation to occur
        :param float protracted_speciation_max: the maximum number of generations before speciation occurs
        :param float metacommunity_size: the size of the metacommunity to apply
        :param float metacommunity_speciation_rate: speciation rate for the metacommunity
        :param str metacommunity_option: either "simulated", "analytical", or a path to a database to read SADs from
        :param int metacommunity_reference: the metacommunity reference if using a database to provide the metacommunity

        :rtype: None
        """
        if self.is_setup_speciation:  # pragma: no cover
            self.logger.warning("Speciation parameters already set.")
        self._set_record_fragments(record_fragments)
        self._set_speciation_rates(speciation_rates)
        self._set_record_spatial(record_spatial)
        self._set_sample_file(sample_file)
        self._set_times(times)
        self._set_metacommunity_parameters(
            metacommunity_size=metacommunity_size,
            metacommunity_speciation_rate=metacommunity_speciation_rate,
            metacommunity_option=metacommunity_option,
            metacommunity_reference=metacommunity_reference,
        )
        self._set_protracted_parameters(protracted_speciation_min, protracted_speciation_max)

        if self.sample_file == "null" and self.record_fragments == "null":
            raise ValueError(
                "Cannot specify a null samplemask and expect automatic fragment detection; "
                "provide a samplemask or set record_fragments=False."
            )
        self._setup_c_community()

    def _set_c_community(self):
        """
        Sets the C++ object depending on if a metacommunity is used or not.

        :rtype: None
        """
        if self.c_community is None:
            if self._check_metacommunity():
                self.c_community = libnecsim.CMetacommunity(self.logger, write_to_log)
            else:
                self.c_community = libnecsim.CCommunity(self.logger, write_to_log)

    def _setup_c_community(self):
        """
        Generates the initial parameters for the libnecsim object

        :rtype: None
        """
        self._set_c_community()
        self.c_community.setup(
            self.file,
            self.record_spatial,
            self.sample_file,
            self.record_fragments,
            self.applied_speciation_rates_list,
            self.times,
        )

    def _check_metacommunity(self):
        """
        Checks if the simulation needs to use a metacommunity.

        :return: true if the community is a metacommunity simulation
        :rtype: bool
        """
        if self.metacommunity_option in [None, "none", "simulated", "analytical"]:
            return self.metacommunity_size not in [0, None]
        else:
            return self.metacommunity_reference not in [0, None]

    def add_time(self, time):
        """
        Adds the time to the list to be applied.

        :param time: the time to be applied
        """
        if self.times is None:
            self.times = [0.0]
        try:
            self.times.append(float(time))
        except ValueError as ve:
            raise TypeError("Times must be floats: {}.".format(ve))
        self._set_c_community()
        self.c_community.add_time(float(time))

    def add_times(self, times):
        """
        Adds the list of times to those to be applied.

        :param times: list of times to be applied
        """
        if not isinstance(times, Iterable):
            raise TypeError("Times list must be iterable.")
        for each in times:
            self.add_time(each)

    def add_protracted_parameters(self, min_speciation_gen, max_speciation_gen):
        """
        Adds the protracted parameter set.

        .. note:: Wipes (0.0, 0.0) from protracted parameters, if it is there alone.

        :param min_speciation_gen: the minimum number of generations required before speciation is permitted
        :param max_speciation_gen: the maximum number of generations required before speciation is permitted
        """
        if self.protracted_parameters == [(0.0, 0.0)]:
            self.protracted_parameters = []
            self.c_community.wipe_protracted_parameters()
        if (min_speciation_gen, max_speciation_gen) not in self.protracted_parameters:
            self._check_protracted_parameters(min_speciation_gen, max_speciation_gen)
            self.protracted_parameters.append((min_speciation_gen, max_speciation_gen))
            self._set_c_community()
            self.c_community.add_protracted_parameters(float(min_speciation_gen), float(max_speciation_gen))

    def add_multiple_protracted_parameters(
        self, min_speciation_gens=None, max_speciation_gens=None, speciation_gens=None
    ):
        """
        Adds the protracted parameter set, taking an iterable as an input.

        .. note:: Using the keyword arguments, one can supply either a list of tuples for pairs of speciation
                  generations, or two lists of generations for the min and max, matching in order.

        :param min_speciation_gens: the minimum number of generations required before speciation is permitted. Order
                                    should match that of :attr:`max_speciation_gens`
        :param max_speciation_gens: the maximum number of generations required before speciation is permitted. Order
                                    should match that of :attr:`min_speciation_gens`
        :param speciation_gens: a list of tuples of min/max speciation generations.
        """
        if min_speciation_gens and max_speciation_gens:
            tmp = zip(min_speciation_gens, max_speciation_gens)
        elif speciation_gens:
            tmp = speciation_gens
        else:
            raise ValueError(
                "Must supply either minimum and maximum speciation gens, or a list of tuples containing "
                "matching speciation generations."
            )
        for min_g, max_g in tmp:
            self.add_protracted_parameters(min_g, max_g)

    def add_metacommunity_parameters(
        self,
        metacommunity_size=None,
        metacommunity_speciation_rate=None,
        metacommunity_option=None,
        metacommunity_reference=0,
    ):
        """
        Adds the metacommunity parameters to the object.

        :param float metacommunity_size: the number of individuals in the metacommunity
        :param float metacommunity_speciation_rate: the speciation rate within the metacommunity
        :param str metacommunity_option: either "simulated", "analytical", or a path to a database to read SADs from
        :param int metacommunity_reference: the metacommunity reference if using a database to provide the metacommunity

        :rtype: None
        """
        self._set_metacommunity_parameters(
            metacommunity_size, metacommunity_speciation_rate, metacommunity_option, metacommunity_reference
        )

    def apply(self):
        """
        Generates the cooalescence tree for the set of speciation parameters.
        This must be run after the main coalescence simulations are complete.
        It will create additional fields and tables in the SQLite database which contains the requested data.
        """
        self.apply_incremental()
        self.c_community.output()
        self.has_outputted = True

    def apply_incremental(self):
        """
        Generates the coalescence tree for the set of speciation parameters. Does not write changes to the database,
        just holds the changes internally.
        """
        # Check file exists
        if self.times is None:
            self.times = [0.0]
        if not os.path.exists(self.file):  # pragma: no cover
            self.logger.warning(
                "Check file existance for {}. "
                "Potential lack of access (verify that definition "
                "is a relative path).\n".format(self.file)
            )
        self._set_c_community()
        if self.has_outputted:
            self.logger.warning("Output has already been written to file - regenerating internal object.\n")
            self.logger.info(
                "To avoid this message in future, use apply_incremental() and then output() to generate " "the file.\n"
            )
            self.c_community.reset()
        self.has_applied = True
        self.c_community.apply()

    def output(self):
        """
        Outputs the coalescence trees to the same simulation database object.
        """
        if self.has_applied:
            if self.has_outputted:  # pragma: no cover
                self.logger.error("Coalescence tree has already been written to output database.\n")
            else:
                self.c_community.output()
        else:
            raise RuntimeError("No changes have been applied to the coalescence tree for outputting.")

    def speciate_remaining(self, database):
        """
        Speciates the remaining lineages in a paused database.

        :param str/pycoalescence.simulation.Simulation database: the paused database to open

        :rtype: None
        """
        try:
            self.set_database(database)
        except Exception as e:
            if self.is_complete or not isinstance(e, IOError) or isinstance(e, FileNotFoundError):
                raise e
        else:
            raise IOError("Database at {} is not a paused database.".format(self.file))
        self.database.close()
        self._set_c_community()
        self.c_community.speciate_remaining_lineages(self.file)

    def get_species_richness(self, reference=1):
        """
        Get the system richness for the parameters associated with the supplied community reference.

        .. note::

            Richness of 0 is returned if there has been some problem; it is assumed that species richness
            will be above 0 for any simulation.

        .. note:: if species richness has previously been calculated and stored in SPECIES_RICHNESS table, it gets
                  the species richness value from there, otherwise it calculates the species richness

        :param reference: community reference which contains the parameters of interest

        :return: either a list containing the community references and respective species richness values
                 OR (if community_reference is provided), the species richness for that community reference.

        :rtype: int, list
        """
        self._check_database()
        try:
            return self.cursor.execute(
                "SELECT richness FROM SPECIES_RICHNESS " "WHERE community_reference==?", (reference,)
            ).fetchone()[0]
        except (TypeError, sqlite3.Error):
            try:
                c = self.cursor.execute(
                    "SELECT species_id FROM SPECIES_ABUNDANCES WHERE no_individuals > 0 AND "
                    "community_reference == ?",
                    (reference,),
                ).fetchall()
                return len(set([x[0] for x in c]))
            except sqlite3.Error as oe:  # pragma: no cover
                self.logger.warning(str(oe) + "\n")
                self.logger.warning("Could not find SPECIES_ABUNDANCES table in database " + self.file + "\n")
                return 0

    def get_species_richness_pd(self):
        """
        Gets the species richness for all calculated parameters from the database.

        :return: all species richness values with their associated community reference
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if check_sql_table_exist(self.database, "SPECIES_RICHNESS"):
            output = pd.read_sql_query("SELECT community_reference, richness FROM SPECIES_RICHNESS", self.database)
        else:
            output = pd.read_sql_query(
                "SELECT community_reference, COUNT(DISTINCT(species_id)) FROM SPECIES_ABUNDANCES WHERE "
                "no_individuals > 0 GROUP BY community_reference",
                self.database,
            )
            output = output.rename(index=str, columns={"COUNT(DISTINCT(species_id))": "richness"})
        return output

    def get_octaves(self, reference):
        """
        Get the pre-calculated octave data for the parameters associated with the supplied reference.
        This will call self.calculate_octaves() if it hasn't been called previously.

        Returns are of form [id, 'whole', time, speciation rate, octave class, number of species]

        :param reference: community reference which contains the parameters of interest
        :return: output from FRAGMENT_OCTAVES on the whole landscape for the selected variables
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
            self.calculate_octaves()
        return self.get_fragment_octaves(fragment="whole", reference=reference)

    def get_octaves_pd(self):
        """
        Gets the species octaves for all calculated community parameters

        :return: all octave classes for the whole landscape
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
            self.calculate_octaves()
        return pd.read_sql_query(
            "SELECT community_reference, octave, richness FROM FRAGMENT_OCTAVES WHERE fragment == 'whole'",
            self.database,
        )

    def get_number_individuals(self, fragment=None, community_reference=None):
        """
        Gets the number of individuals that exist, either in the provided fragment, or on the whole landscape.
        Counts individuals from FRAGMENT_ABUNDANCES or SPECIES_ABUNDANCES, respectively.

        If a community reference is provided, only individuals for that time slice will be counted, otherwise a mean is
        taken across time slices.

        :param fragment: the name of the fragment to get a count of individuals from
        :param community_reference: the reference to the community parameters

        :return: the number of individuals that exists in the desired location
        """
        self._check_database()
        if fragment:
            if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
                raise IOError("No FRAGMENT_ABUNDANCES table - cannot get a count from a fragment.")
            if not community_reference:
                return self.cursor.execute(
                    "SELECT SUM(no_individuals)/COUNT(DISTINCT(community_reference))"
                    " FROM FRAGMENT_ABUNDANCES WHERE fragment == ?",
                    (fragment,),
                ).fetchone()[0]
            else:
                return self.cursor.execute(
                    "SELECT SUM(no_individuals) FROM FRAGMENT_ABUNDANCES "
                    "WHERE community_reference==? AND fragment == ?",
                    (community_reference, fragment),
                ).fetchone()[0]
        else:
            if not check_sql_table_exist(self.database, "SPECIES_ABUNDANCES"):
                raise IOError("No species abundances table to fetch data from. Ensure your simulation is complete.")
            if not community_reference:
                return self.cursor.execute(
                    "SELECT SUM(no_individuals)/COUNT(DISTINCT(community_reference)) " "FROM SPECIES_ABUNDANCES"
                ).fetchone()[0]
            else:
                return self.cursor.execute(
                    "SELECT SUM(no_individuals) FROM SPECIES_ABUNDANCES " "WHERE community_reference==?",
                    (community_reference,),
                ).fetchone()[0]

    def check_biodiversity_table_exists(self):
        """
        Checks whether the biodiversity table exists and creates the table if required.

        :return: the max reference value currently existing
        """
        self._check_database()
        tmp_create = (
            "CREATE TABLE BIODIVERSITY_METRICS (ref INT PRIMARY KEY NOT NULL, metric TEXT NOT NULL,"
            " fragment TEXT NOT NULL, community_reference INT NOT NULL,"
            " value FLOAT NOT NULL, simulated FLOAT, actual FLOAT)"
        )
        if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):
            try:
                self.cursor.execute(tmp_create)
                self.database.commit()
            except sqlite3.Error as e:  # pragma: no cover
                raise sqlite3.Error("Error creating biodiversity metric table: " + str(e))
            return 0
        else:
            maxval = self.database.cursor().execute("SELECT MAX(ref) FROM BIODIVERSITY_METRICS").fetchone()[0]
            if maxval is None:  # pragma: no cover
                return 0
            return maxval

    def calculate_richness(self, output_metrics=True):
        """
        Calculates the landscape richness from across all fragments and stores result in a new table in
        SPECIES_RICHNESS
        Stores a separate result for each community reference.

        :param bool output_metrics: output to the BIODIVERSITY_METRICS table
        """
        self._check_database()
        tmp_create = (
            "CREATE TABLE SPECIES_RICHNESS (ref INT PRIMARY KEY NOT NULL, community_reference INT NOT NULL,"
            " richness INT NOT NULL)"
        )
        existing_references = []
        ref = 0
        if not check_sql_table_exist(self.database, "SPECIES_RICHNESS"):
            try:
                self.cursor.execute(tmp_create)
                self.database.commit()
            except Exception as e:  # pragma: no cover
                e.message = "Error creating SPECIES_RICHNESS table: ".format(e)
                raise e
        else:
            all_refs = [x[0] for x in self.cursor.execute("SELECT ref FROM SPECIES_RICHNESS").fetchall()]
            if len(all_refs) == 0:  # pragma: no cover
                all_refs = [0]
            ref = max(all_refs) + 1
            existing_references.extend(all_refs)
        references = self.get_community_references()
        output = []
        for reference in references:
            if reference not in existing_references:
                spec_richness = self.get_species_richness(reference)
                output.append([ref, reference, spec_richness])
                ref += 1
        if len(output) > 0:
            ref = self.check_biodiversity_table_exists()
            if output_metrics:
                bio_output = []
                for x in output:
                    ref += 1
                    tmp = [ref, "fragment_richness", "whole"]
                    tmp.extend([x[1], x[2]])
                    bio_output.append(tmp)
                self.cursor.executemany(
                    "INSERT INTO BIODIVERSITY_METRICS VALUES (?, ?, ?, ?, ?, NULL, NULL)", bio_output
                )
            self.cursor.executemany("INSERT INTO SPECIES_RICHNESS VALUES(?,?,?)", output)
            self.database.commit()

    def calculate_fragment_abundances(self):
        """
        Calculates the fragment abundances, including equalising with the comparison database, if it has already been
        set.

        Sets fragment_abundances object.
        """
        if not self.fragment_abundances:
            self._check_database()
            if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
                raise IOError("Database does not contain FRAGMENT_ABUNDANCES table.")
            self.fragment_abundances = [
                list(x)
                for x in self.cursor.execute(
                    "SELECT fragment, species_id," " no_individuals, community_reference " "FROM FRAGMENT_ABUNDANCES"
                ).fetchall()
                if x[2] > 0
            ]
            if not self.fragment_abundances:  # pragma: no cover
                self.fragment_abundances = None
                raise ValueError("Fragment abundances table may be empty, or not properly stored.")
            if self.comparison_abundances is not None:
                self._equalise_all_fragment_numbers()
        else:  # pragma: no cover
            self.logger.warning("Fragment abundances already imported.")

    def calculate_fragment_richness(self, output_metrics=True):
        """
        Calculates the fragment richness and stores it in a new table called FRAGMENT_RICHNESS. Also adds the record to
        BIODIVERSITY METRICS for
        If the table already exists, it will simply be returned. Each time point and speciation rate combination will be
        recorded as a new variable.

        :param bool output_metrics: output to the BIODIVERSITY_METRICS table
        """
        self._check_database()
        tmp_create = (
            "CREATE TABLE FRAGMENT_RICHNESS (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL,"
            " community_reference INT NOT NULL,  richness INT NOT NULL)"
        )
        # First check the FRAGMENT_ABUNDANCES TABLE EXISTS
        if self.fragment_abundances is None or len(self.fragment_abundances) == 0:
            self.calculate_fragment_abundances()
        if len(self.fragment_abundances) == 0 or self.fragment_abundances is None:  # pragma: no cover
            raise IOError("No fragment abundances detected.")
        # Now try and create FRAGMENT_RICHNESS
        if not check_sql_table_exist(self.database, "FRAGMENT_RICHNESS"):
            try:
                self.cursor.execute(tmp_create)
                self.database.commit()
            except sqlite3.Error as soe:  # pragma: no cover
                raise sqlite3.Error("Could not create FRAGMENT_RICHNESS table: {}".format(soe))
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
        self.fragments = [
            list(x)
            for x in self.cursor.execute(
                "SELECT fragment, community_reference, richness" " FROM FRAGMENT_RICHNESS"
            ).fetchall()
        ]
        # Move fragment richnesses into BIODIVERSITY METRICS
        if output_metrics:
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

    def calculate_alpha_diversity(self, output_metrics=True):
        """
        Calculates the system alpha diversity for each set of parameters stored in COMMUNITY_PARAMETERS.
        Stores the output in ALPHA_DIVERSITY table.

        :param bool output_metrics: output to the BIODIVERSITY_METRICS table
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES") or not check_sql_table_exist(
            self.database, "FRAGMENT_RICHNESS"
        ):
            raise IOError("Fragment abundances and richnesses must be calculated before alpha diversity.")
        if not check_sql_table_exist(self.database, "ALPHA_DIVERSITY"):
            tmp_create = (
                "CREATE TABLE ALPHA_DIVERSITY (reference INT PRIMARY KEY NOT NULL, " "alpha_diversity INT NOT NULL)"
            )
            try:
                self.cursor.execute(tmp_create)
                self.database.commit()
            except sqlite3.Error as soe:  # pragma: no cover
                raise sqlite3.Error("Could not create ALPHA_DIVERSITY table: {}".format(soe))
            all_community_references = self.get_community_references()
            all_fragments = self.get_fragment_list()
            output = []
            for reference in all_community_references:
                total = 0
                for fragment in all_fragments:
                    total += self.get_fragment_richness(fragment=fragment, reference=reference)
                alpha = total / len(all_fragments)
                output.append([reference, alpha])
            self.cursor.executemany("INSERT INTO ALPHA_DIVERSITY VALUES(?,?)", output)
            # Now also insert into BIODIVERSITY metrics
            if output_metrics:
                ref = self.check_biodiversity_table_exists() + 1
                output = [[i + ref, "alpha_diversity", "whole", x[0], x[1]] for i, x in enumerate(output)]
                self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES(?,?,?,?,?, NULL, NULL)", output)
            self.database.commit()
        else:
            self.logger.warning("Alpha diversity already calculated.")

    def calculate_beta_diversity(self, output_metrics=True):
        """
        Calculates the beta diversity for the system for each speciation parameter set and stores the output in
        BETA_DIVERSITY.
        Will calculate alpha diversity and species richness tables if they have not already been performed.

        :param bool output_metrics: output to the BIODIVERSITY_METRICS table
        """
        self._check_database()
        tmp_create = "CREATE TABLE BETA_DIVERSITY (reference INT PRIMARY KEY NOT NULL, " "beta_diversity INT NOT NULL)"
        if not check_sql_table_exist(self.database, "ALPHA_DIVERSITY"):
            self.calculate_alpha_diversity()
        if not check_sql_table_exist(self.database, "SPECIES_RICHNESS"):  # pragma: no cover
            self.calculate_richness()
        if not check_sql_table_exist(self.database, "BETA_DIVERSITY"):
            try:
                self.cursor.execute(tmp_create)
                self.database.commit()
            except sqlite3.Error:  # pragma: no cover
                raise sqlite3.Error("Could not create BETA_DIVERSITY table")
            all_community_references = self.get_community_references()
            output = []
            for reference in all_community_references:
                beta = float(self.get_species_richness(reference)) / float(self.get_alpha_diversity(reference))
                output.append([reference, beta])
            self.cursor.executemany("INSERT INTO BETA_DIVERSITY VALUES(?,?)", output)
            # Now also insert into BIODIVERSITY metrics
            if output_metrics:
                ref = self.check_biodiversity_table_exists() + 1
                output = [[i + ref, "beta_diversity", "whole", x[0], x[1]] for i, x in enumerate(output)]
                self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES(?,?,?,?,?, NULL, NULL)", output)
            self.database.commit()
        else:  # pragma: no cover
            self.logger.warning("Beta diversity already calculated.")

    def get_alpha_diversity(self, reference=1):
        """
        Gets the system alpha diversity for the provided community reference parameters.
        Alpha diversity is the mean number of species per fragment.
        :param reference: the community reference for speciation parameters
        :return: the alpha diversity of the system
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "ALPHA_DIVERSITY"):  # pragma: no cover
            self.calculate_alpha_diversity()
        self.cursor.execute("SELECT alpha_diversity FROM ALPHA_DIVERSITY WHERE reference == ?", (reference,))
        res = self.cursor.fetchone()
        if res is None:  # pragma: no cover
            raise ValueError("No alpha diversity value for reference = {}".format(reference))
        return res[0]

    def get_alpha_diversity_pd(self):
        """
        Gets the alpha diversity for each set of community parameters.

        :return: all alpha diversity values
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "ALPHA_DIVERSITY"):  # pragma: no cover
            self.calculate_alpha_diversity()
        output = pd.read_sql_query("SELECT reference, alpha_diversity FROM ALPHA_DIVERSITY", self.database)
        output = output.rename(index=str, columns={"reference": "community_reference"})
        return output

    def get_beta_diversity(self, reference=1):
        """
        Gets the system beta diversity for the provided community reference parameters.
        Beta diversity is the true beta diversity (gamma / alpha).
        :param reference: the community reference for speciation parameters
        :return: the beta diversity of the system
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "BETA_DIVERSITY"):  # pragma: no cover
            self.calculate_beta_diversity()
        self.cursor.execute("SELECT beta_diversity FROM BETA_DIVERSITY WHERE reference == ?", (reference,))
        res = self.cursor.fetchone()
        if res is None:  # pragma: no cover
            raise ValueError("No beta diversity value for reference = {}.".format(reference))
        return res[0]

    def get_beta_diversity_pd(self):
        """
        Gets the beta diversity for each set of community parameters.

        :return: all beta diversity values
        :rtype: pd.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "BETA_DIVERSITY"):  # pragma: no cover
            self.calculate_beta_diversity()
        output = pd.read_sql_query("SELECT reference, beta_diversity FROM BETA_DIVERSITY", self.database)
        output = output.rename(index=str, columns={"reference": "community_reference"})
        return output

    def import_comparison_data(self, filename, ignore_mismatch=False):
        """
        Imports the SQL database that contains the biodiversity metrics that we want to compare against.

        This can either be real data (for comparing simulated data) or other simulated data (for comparing between
        models).

        If the SQL database does not contain the relevant biodiversity metrics, they will be calculated (if possible)
        or skipped.

        The expected form of the database is the same as the BIODIVERSITY_METRICS table, except without any speciation
        rates or time references, and a new column containing the number of individuals involved in each metric.

        .. note::

            This also equalises the comparison data if ignore_mismatch is not True, so that the number of individuals
            is equal between the simulated and comparison datasets.

        :param str filename: the file containing the comparison biodiversity metrics.
        :param bool ignore_mismatch: set to true to ignore abundance mismatches between the comparison and simulated
        data.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError("Comparison database does not exist at {}.".format(filename))
        conn = sqlite3.connect(filename)
        tmp_cursor = conn.cursor()
        if self.comparison_file is not None:
            self.logger.warning("Comparison data has already been imported.")
        try:
            if check_sql_table_exist(conn, "BIODIVERSITY_METRICS"):
                self.comparison_data = tmp_cursor.execute(
                    "SELECT metric, fragment, value, no_individuals" " FROM BIODIVERSITY_METRICS"
                ).fetchall()
            try:
                self.comparison_abundances = [
                    list(x)
                    for x in tmp_cursor.execute(
                        "SELECT fragment, species_id, no_individuals FROM FRAGMENT_ABUNDANCES"
                    ).fetchall()
                ]
                self.comparison_abundances_whole = [
                    list(x)
                    for x in tmp_cursor.execute("SELECT species_id, no_individuals FROM SPECIES_ABUNDANCES").fetchall()
                ]
            except sqlite3.Error as oe:  # pragma: no cover
                raise sqlite3.Error("Problem executing fetches from comparison data: {}".format(oe))
            self.comparison_file = filename
        except sqlite3.Error as oe:  # pragma: no cover
            conn = None
            raise RuntimeError("Could not import from comparison data: {}".format(oe))
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

        .. note::

             If store is True, will store an EDITED version of the comparison octaves, such that the number of
            individuals is equal between the comparison and simulated data.

        :param store: if True, stores within the comparison database.
        """
        if self.comparison_octaves is None:
            # If comparison_octaves has not been calculated, then do that now.
            if self.comparison_abundances is None:  # pragma: no cover
                self.logger.warning(
                    "Comparison abundances not yet imported, or FRAGMENT_ABUNDANCES does not exist in comparison file."
                )
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
            if not self.fragment_abundances:
                self.calculate_fragment_abundances()
            # Need to calculate again if the fragment numbers don't match
            if not self._check_fragment_numbers_match():  # pragma: no cover
                self.comparison_octaves = None
            # Otherwise, if comparison abundances exists, we can calculate the comparison octaves manually
            if self.comparison_abundances is not None and self.comparison_octaves is None:
                if not self._check_fragment_numbers_match():  # pragma: no cover
                    self._equalise_all_fragment_numbers()
                self.comparison_octaves = []
                ref = 0
                fragments = set([x[0] for x in self.comparison_abundances])
                for f in fragments:
                    octaves = [[], []]
                    octaves[0] = []
                    octaves[1] = []
                    abundances = [x for x in self.comparison_abundances if str(x[0]) == f]
                    for each in abundances:
                        this_octave = int(math.floor(math.log(each[2], 2)))
                        if this_octave in octaves[0]:
                            pos = [i for i, x in enumerate(octaves[0]) if x == this_octave]
                            self.comparison_octaves[octaves[1][pos[0]]][2] += 1
                        else:
                            self.comparison_octaves.append([str(f), this_octave, 1])
                            octaves[0].append(this_octave)
                            octaves[1].append(ref)
                            ref += 1
                octaves = [[], []]
                octaves[0] = []
                octaves[1] = []
                abundances = self.comparison_abundances_whole
                for each in abundances:
                    this_octave = int(math.floor(math.log(each[1], 2)))
                    if this_octave in octaves[0]:
                        pos = [i for i, x in enumerate(octaves[0]) if x == this_octave]
                        self.comparison_octaves[octaves[1][pos[0]]][2] += 1
                    else:
                        self.comparison_octaves.append(["whole", this_octave, 1])
                        octaves[0].append(this_octave)
                        octaves[1].append(ref)
                        ref += 1
            # If we want to store the comparison octaves, overwrite the original FRAGMENT_OCTAVES table (if it exists
            # with the new calculated data
            if store:
                if self.comparison_file is None:  # pragma: no cover
                    raise ValueError("Comparison file has not been imported yet, and therefore cannot be written to.")
                conn = sqlite3.connect(self.comparison_file)
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS FRAGMENT_OCTAVES")
                cursor.execute(
                    "CREATE TABLE FRAGMENT_OCTAVES (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL, "
                    "octave INT NOT NULL, richness INT NOT NULL)"
                )
                cursor.executemany(
                    "INSERT INTO FRAGMENT_OCTAVES VALUES(?,?,?,?)",
                    [[i, x[0], x[1], x[2]] for i, x in enumerate(self.comparison_octaves)],
                )
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
            "community_reference INT NOT NULL, octave INT NOT NULL, richness INT NOT NULL)"
        )
        abundances = self.cursor.execute(
            "SELECT species_id, no_individuals, community_reference FROM SPECIES_ABUNDANCES" " WHERE no_individuals>0"
        ).fetchall()
        references = set([x[2] for x in abundances])
        # Check what the maximum reference is in FRAGMENT_OCTAVES
        try:
            c = self.cursor.execute("SELECT max(ref) FROM FRAGMENT_OCTAVES").fetchone()[0] + 1
        except (sqlite3.Error, TypeError):
            c = 0
        for ref in references:
            select_abundances = [x[1] for x in abundances if x[2] == ref]
            log_select = [math.floor(math.log(x, 2)) for x in select_abundances]
            out = []
            for i in range(0, int(max(log_select)), 1):
                tot = log_select.count(i)
                out.append([c, "whole", ref, i, tot])
                c += 1
            try:
                self.cursor.executemany("INSERT INTO FRAGMENT_OCTAVES VALUES (?,?,?,?,?)", out)
                self.database.commit()
            except sqlite3.Error as oe:  # pragma: no cover
                raise sqlite3.Error("Could not insert into FRAGMENT_OCTAVES." + str(oe))

    def calculate_fragment_octaves(self):
        """
        Calculates the octave classes for each fragment. Outputs the calculated richness into the SQL database within a
        FRAGMENT_OCTAVES table
        """
        self._check_database()
        if check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
            raise IOError("FRAGMENT_OCTAVES already exists")
        if self.fragment_abundances is None or len(self.fragment_abundances) == 0:  # pragma: no cover
            self.calculate_fragment_abundances()
        if len(self.fragment_abundances) == 0:  # pragma: no cover
            raise RuntimeError("Fragments not imported correctly")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS FRAGMENT_OCTAVES (ref INT PRIMARY KEY NOT NULL, fragment TEXT NOT NULL, "
            "community_reference INT NOT NULL, octave INT NOT NULL, richness INT NOT NULL)"
        )
        fragments = set([x[0] for x in self.fragment_abundances])
        references = set([x[3] for x in self.fragment_abundances])
        c = 0
        for f in fragments:
            for ref in references:
                select_abundances = [int(x[2]) for x in self.fragment_abundances if x[0] == f and x[3] == ref]
                if len(select_abundances) == 0:  # pragma: no cover
                    raise ValueError("Could not calculate fragment octaves for {}, with reference = {}".format(f, ref))
                log_select = [math.floor(math.log(x, 2)) for x in select_abundances]
                out = []
                for i in range(0, int(max(log_select)), 1):
                    tot = log_select.count(i)
                    out.append([c, f, ref, i, tot])
                    c += 1
                try:
                    self.cursor.executemany("INSERT INTO FRAGMENT_OCTAVES VALUES (?,?,?,?,?)", out)
                except sqlite3.Error as oe:  # pragma: no cover
                    raise sqlite3.Error("Could not insert into FRAGMENT_OCTAVES." + str(oe))
        self.database.commit()
        self.calculate_octaves()

    def get_fragment_richness(self, fragment=None, reference=None):
        """
        Gets the fragment richness for each speciation rate and time for the specified simulation.

        If the fragment richness has not yet been calculated, it tries to calculate the fragment richness,

        :param str fragment: the desired fragment (defaults to None)
        :param int reference: the reference key for the calculated community parameters

        :raises: sqlite3.Error if no table FRAGMENT_ABUNDANCES exists
        :raises: RuntimeError if no data for the specified fragment, speciation rate and time exists.

        :return: A list containing the fragment richness, or a value of the fragment richness
        :rtype: list
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
        output = self.cursor.execute(
            "SELECT richness FROM FRAGMENT_RICHNESS WHERE community_reference == ? AND " "fragment ==  ?",
            (reference, fragment),
        ).fetchall()
        if len(output) == 0:
            raise IOError("No output while fetching fragment data for {}.".format(fragment))
        else:
            return output[0][0]

    def get_fragment_richness_pd(self):
        """
        Gets the fragment richness for each set of community parameters.

        :return: the fragment richness for each associated community reference
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
            raise IOError("Fragments abundances must be calculated before attempting to get fragment richness.")
        output = pd.read_sql_query(
            "SELECT fragment, community_reference, COUNT(DISTINCT(species_id)) FROM FRAGMENT_ABUNDANCES "
            "GROUP BY fragment, community_reference",
            self.database,
        ).rename(index=str, columns={"COUNT(DISTINCT(species_id))": "fragment_richness"})
        return output

    def get_fragment_abundances(self, fragment, reference):
        """
        Gets the species abundances for the supplied fragment and community reference.

        :param fragment: the name of the fragment to obtain
        :param reference: the reference for speciation parameters to obtain for

        :return: a list of species ids and abundances
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
            raise IOError("Fragments abundances must be calculated before attempting to get fragment abundances.")
        output = self.cursor.execute(
            "SELECT species_id, no_individuals FROM FRAGMENT_ABUNDANCES WHERE "
            "community_reference == ? AND fragment ==  ?",
            (reference, fragment),
        ).fetchall()
        if len(output) == 0:  # pragma: no cover
            raise RuntimeError("No output while fetching fragment data for {}.".format(fragment))
        return [list(x) for x in output]

    def get_fragment_abundances_pd(self):
        """
        Gets the fragment abundances for each set of community parameters.

        :return: the fragment abundances for each associated community reference
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
            raise IOError("Fragments abundances must be calculated before attempting to get fragment abundances.")
        output = pd.read_sql_query(
            "SELECT fragment, community_reference, species_id, no_individuals FROM FRAGMENT_ABUNDANCES", self.database
        )
        return output

    def get_all_fragment_abundances(self):
        """
        Returns the whole table of fragment abundances from the database.

        :return: a list of reference, fragment, species_id, no_individuals
        """
        self.logger.warning("Deprecated - please use get_fragment_abundances_pd() instead.")
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):  # pragma: no cover
            raise IOError("Fragments abundances must be calculated before attempting to get fragment abundances.")
        output = self.cursor.execute(
            "SELECT community_reference, fragment, species_id, no_individuals FROM " "FRAGMENT_ABUNDANCES"
        ).fetchall()
        if len(output) == 0:  # pragma: no cover
            raise RuntimeError("No output while fetching all fragment abundances")
        return [list(x) for x in output]

    def get_fragment_list(self, community_reference=1):
        """
        Returns a list of all fragments that exist in FRAGMENT_ABUNDANCES.

        :param community_reference: community reference to obtain for (default 1)
        :return: list all all fragment names
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_ABUNDANCES"):
            raise IOError("Fragment abundances have not been calculated: cannot obtain fragment list.")
        fetch = self.cursor.execute(
            "SELECT DISTINCT(fragment) FROM FRAGMENT_ABUNDANCES WHERE " "community_reference == ?",
            (community_reference,),
        ).fetchall()
        if len(fetch) == 0:  # pragma: no cover
            raise sqlite3.Error("No fragments exist in FRAGMENT_ABUNDANCES.")
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
            return [
                list(x)
                for x in self.cursor.execute(
                    "SELECT fragment, community_reference, octave, richness" " FROM FRAGMENT_OCTAVES"
                )
            ]
        elif fragment is None or reference is None:
            raise SyntaxError("Only one of fragment or reference supplied: must supply both, or neither.")
        try:
            output = [
                list(x)
                for x in self.cursor.execute(
                    "SELECT octave, richness FROM FRAGMENT_OCTAVES WHERE " "community_reference == ? AND fragment == ?",
                    (reference, fragment),
                ).fetchall()
            ]
            if len(output) == 0:
                raise RuntimeError(
                    "No output while fetching fragment data for {} with ref: {}".format(fragment, reference)
                )
        except sqlite3.Error as oe:
            raise sqlite3.Error("Failure whilst fetching fragment octave data." + str(oe))
        output.sort(key=lambda x: x[0])
        return output

    def get_fragment_octaves_pd(self):
        """
        Gets the octave classes for each fragment and community parameter set

        :return: all fragment octave classes
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):  # pragma: no cover
            self.calculate_octaves()
        return pd.read_sql_query(
            "SELECT fragment, community_reference, octave, richness FROM FRAGMENT_OCTAVES", self.database
        )

    def get_species_abundances(self, fragment=None, reference=None):
        """
        Gets the species abundance for a particular fragment, speciation rate and time. If fragment is None, returns the
        whole landscape species abundances.

        :param str fragment: the fragment to obtain the species abundance of. If None, returns landscape abundances.
        :param int reference: the commmunity reference to obtain metrics for

        :return: list of species abundances [reference, species ID, speciation rate, number of individuals, generation]
        """
        self._check_database()
        if fragment is None:
            if reference is None:  # pragma: no cover
                reference = 1
            return [
                list(x)
                for x in self.cursor.execute(
                    "SELECT species_id, no_individuals FROM SPECIES_ABUNDANCES WHERE " "community_reference==?",
                    (reference,),
                ).fetchall()
            ]
        elif reference is None:
            raise ValueError("Must specify a community reference to get a fragment species abundance")
        else:
            return [
                list(x)
                for x in self.cursor.execute(
                    "SELECT species_id, no_individuals FROM FRAGMENT_ABUNDANCES WHERE"
                    " fragment == ? AND "
                    "community_reference == ?",
                    (fragment, reference),
                )
            ]

    def get_species_abundances_pd(self):
        """
        Gets the species abundances for all community parameter sets.

        :return: all species abundances
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "SPECIES_ABUNDANCES"):  # pragma: no cover
            self.calculate_octaves()
        return pd.read_sql_query(
            "SELECT species_id, community_reference, no_individuals FROM SPECIES_ABUNDANCES", self.database
        )

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
        if not check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):  # pragma: no cover
            self.calculate_fragment_octaves()

        data = self.cursor.execute("SELECT fragment, community_reference FROM FRAGMENT_OCTAVES").fetchall()
        if len(data) == 0:  # pragma: no cover
            self.calculate_fragment_octaves()
        try:
            self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN comparison FLOAT")
            self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN error FLOAT")
            col_add = True
        except sqlite3.Error as soe:  # pragma: no cover
            raise sqlite3.Error("Could not alter FRAGMENT_OCTAVES table: " + str(soe))
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
                except ValueError:  # pragma: no cover
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
                    except (ValueError, IndexError):  # pragma: no cover
                        difference.append(1.0)
                        comp_val = 1.0
                    else:
                        ## The error is calculated
                        difference.append(
                            float(max(richness_val, comp_val) - min(richness_val, comp_val))
                            / max(comp_val, richness_val)
                        )
                    if col_add:
                        self.cursor.execute(
                            "UPDATE FRAGMENT_OCTAVES SET comparison = ?, error = ? WHERE ref == ?",
                            (comp_val, difference[-1], reference),
                        )
                # now average the errors
                ref += 1
                fragment_errors.append(
                    [ref, "fragment_octaves", f, reference, float(sum(difference) / float(len(difference)))]
                )

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
        if self.comparison_data is None:  # pragma: no cover
            raise RuntimeError("Comparison data not yet imported.")
        self._check_database()
        if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):  # pragma: no cover
            raise ValueError("BIODIVERSITY_METRICS table does not exist in database: cannot calculate goodness of fit.")
        bio_metrics = self.cursor.execute(
            "SELECT metric, fragment, community_reference, value FROM BIODIVERSITY_METRICS"
            " WHERE metric != 'goodness_of_fit'"
        ).fetchall()
        if check_sql_table_exist(self.database, "FRAGMENT_OCTAVES"):
            self.total_individuals = self.cursor.execute(
                "SELECT COUNT(tip) FROM SPECIES_LIST" " WHERE tip==1 AND gen_added==0.0"
            ).fetchone()[0]
            try:
                self.cursor.execute("SELECT comparison, error from FRAGMENT_OCTAVES")
            except sqlite3.Error:  # pragma: no cover
                self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN comparison FLOAT")
                self.cursor.execute("ALTER TABLE FRAGMENT_OCTAVES ADD COLUMN error FLOAT")
        # Remove the extra goodness of fit values
        # TODO first print out biodiversity metrics in each database
        bio_metrics = [b for b in bio_metrics if "goodness_of_fit" not in b[0]]
        references = set([x[2] for x in bio_metrics])
        categories = set([f[0] for f in bio_metrics])
        # this will contain: metric, fragment, community_reference, relative_goodness_of_fit, num_individuals,
        # simulated, actual
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
                except IndexError:  # pragma: no cover
                    self.logger.warning(
                        "Could not find comparable metric for {} and {}".format(category[0], category[1])
                    )
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
                        raise ValueError("Could not find comparable metric for" " {}, in {}".format(category, fragment))
                    actual_val = fragment_comparison[2]
                    no_ind = fragment_comparison[3]
                else:
                    actual_val = 0.0
                    try:
                        no_ind = [p[1] for p in plot_data if p[0] == fragment][0]
                    except IndexError:  # pragma: no cover
                        raise IndexError(
                            "Could not get fragment {} from comparison plot data for {}.".format(fragment, category)
                        )
                for ref in references:
                    select_metrics = [b for b in bio_metrics if b[0] == category and b[1] == fragment and b[2] == ref]
                    if len(select_metrics) != 1:  # pragma: no cover
                        if len(select_metrics) == 0:
                            raise ValueError(
                                "Could not find metric for metric, {}, fragment = {}"
                                " and community_reference = {}".format(category, fragment, ref)
                            )
                        raise ValueError(
                            "Achieved multiple matches for biodiversity metrics"
                            " for fragment {} and community reference = {}.".format(fragment, ref)
                        )
                    if category != "fragment_octaves":
                        sim_val = select_metrics[0][3]
                        scaled_fit = scale_simulation_fit(sim_val, actual_val, no_ind, total_ind)
                        self.cursor.execute(
                            "UPDATE BIODIVERSITY_METRICS SET simulated = ?, actual = ?, value=?"
                            " WHERE metric == ? AND fragment == ? AND community_reference == ?",
                            (sim_val, actual_val, scaled_fit, category, fragment, ref),
                        )
                    else:
                        scaled_fit = (1 - select_metrics[0][3]) * float(no_ind) / float(total_ind)
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
            return [
                list(x)
                for x in self.cursor.execute(
                    "SELECT species_id, x, y" " FROM SPECIES_LOCATIONS WHERE community_reference==?",
                    (community_reference,),
                )
            ]
        return [
            list(x)
            for x in self.cursor.execute("SELECT species_id, x, y, community_reference" " FROM SPECIES_LOCATIONS")
        ]

    def get_goodness_of_fit(self, reference=1):
        """
        Returns the goodness of fit from the file.

        :param reference: the community reference to get from
        :return: the full output from the SQL query

        :rtype: float
        """
        self._check_database()
        if self.check_biodiversity_table_exists() == 0:  # pragma: no cover
            raise IOError("Biodiversity table does not contain any values.")
        ret = self.cursor.execute(
            "SELECT value FROM BIODIVERSITY_METRICS WHERE fragment=='whole' AND metric=='goodness_of_fit' AND "
            "community_reference == ?",
            (reference,),
        ).fetchall()
        if len(ret) is 0:  # pragma: no cover
            raise RuntimeError("Biodiversity table does not contain goodness-of-fit values.")
        else:
            return ret[0][0]

    def get_biodiversity_metrics(self):
        """
        Get calculated biodiversity metrics.

        :return: all biodiversity metrics
        :rtype: pandas.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):  # pragma: no cover
            raise IOError("Biodiversity table does not exist in database.")
        try:
            output = pd.read_sql_query(
                "SELECT community_reference, metric, fragment, value, simulated, actual FROM BIODIVERSITY_METRICS",
                self.database,
            )
        except sqlite3.OperationalError:  # pragma: no cover
            output = pd.read_sql_query(
                "SELECT community_reference, metric, fragment, value FROM BIODIVERSITY_METRICS", self.database
            )
        return output

    def get_goodness_of_fit_metric(self, metric, reference=1):
        """
        Gets the goodness-of-fit measure for the specified metric and community reference.

        :param metric: the metric goodness of fit has been calculated for to obtain
        :param reference: the community reference to fetch fits for
        :return: the goodness of fit value
        :rtype: float
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):  # pragma: no cover
            raise ValueError("Biodiversity table does not contain any values.")
        metric_sql = "goodness_of_fit_{}".format(metric)
        ret = self.cursor.execute(
            "SELECT value FROM BIODIVERSITY_METRICS WHERE fragment=='whole' AND metric==? and "
            "community_reference == ?",
            (metric_sql, reference),
        ).fetchone()
        if len(ret) == 0:  # pragma: no cover
            raise ValueError("No goodness-of-fit for {} with" " community reference = {}".format(metric, reference))
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

        .. note:: If more than one metric matches the specified criteria, only the first will be returned.

        :raises ValueError: if BIODIVERSITY_METRICS table does not exist.

        :param reference: the community reference number
        :return: the full output from the SQL query

        :rtype: double
        """
        # TODO This needs to be fixed (still)
        self._check_database()
        if not check_sql_table_exist(self.database, "BIODIVERSITY_METRICS"):  # pragma: no cover
            raise ValueError("Biodiversity table does not contain any values.")
        ret = self.cursor.execute(
            "SELECT value FROM BIODIVERSITY_METRICS WHERE fragment=='whole' AND "
            "metric=='goodness_of_fit_fragment_octaves' and "
            "community_reference == ?",
            (reference,),
        ).fetchone()
        if len(ret) == 0:  # pragma: no cover
            raise ValueError(
                "No goodness-of-fit for fragment octaves with" " community reference = {}".format(reference)
            )
        return ret[0]

    def dispersal_parameters(self):
        """
        Reads the dispersal parameters from the database and returns them.

        :return: a dict of the dispersal parameters (dispersal method, sigma, tau, m_probability and cutoff)
        """
        ret = self.get_simulation_parameters()
        return {
            "dispersal_method": ret["dispersal_method"],
            "sigma": ret["sigma"],
            "tau": ret["tau"],
            "m_probability": ret["m_probability"],
            "cutoff": ret["cutoff"],
        }

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

        :return: a dictionary mapping names to values for seed, job_type, output_dir, speciation_rate, sigma,
        L_value, deme,
        sample_size, maxtime, dispersal_relative_cost, min_spec, habitat_change_rate, gen_since_historical, time_config,
        coarse_map vars, fine map vars, sample_file, gridx, gridy, historical coarse map, historical fine map,
        sim_complete,
        dispersal_method, m_probability, cutoff, landscape_type, protracted, min_speciation_gen, max_speciation_gen,
        dispersal_map
        """
        self._check_database()
        if not guild:
            try:
                self.cursor.execute(
                    "SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme, sample_size, "
                    "max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, gen_since_historical, "
                    "time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                    "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, "
                    "fine_map_x_offset, fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, "
                    "sample_x_offset, sample_y_offset, historical_coarse_map, "
                    " historical_fine_map, sim_complete, dispersal_method, m_probability, cutoff,"
                    " landscape_type,  protracted, min_speciation_gen, max_speciation_gen, dispersal_map"
                    " FROM SIMULATION_PARAMETERS"
                )
            except sqlite3.Error as e:
                self.logger.error("Failure to get SIMULATION_PARAMETERS table from database. Check table exists.")
                raise e
            column_names = [member[0] for member in self.cursor.description]
            values = [x for x in self.cursor.fetchone()]
            if sys.version_info[0] is not 3:  # pragma: no cover
                for i, each in enumerate(values):
                    if isinstance(each, unicode):
                        values[i] = each.encode("ascii")
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
        except sqlite3.Error as e:  # pragma: no cover
            self.logger.error(
                "Failure to fetch references from COMMUNITY_PARAMETERS table in database." " Check table exists."
            )
            raise e
        references = [x[0] for x in self.cursor.fetchall()]
        return references

    def get_community_parameters(self, reference=1):
        """
        Returns a dictionary containing the parameters for the calculated community.

        :param reference: the reference key for the calculated parameters (default is 1)

        :return: dictionary containing the speciation_rate, time, fragments, metacommunity_reference and min/max
                 speciation generation for protracted sims

        :rtype: dict
        """
        self._check_database()
        try:
            try:
                self.cursor.execute(
                    "SELECT speciation_rate, time, fragments, metacommunity_reference, "
                    "min_speciation_gen, max_speciation_gen "
                    "FROM COMMUNITY_PARAMETERS WHERE reference==?",
                    (reference,),
                )
            except sqlite3.Error:
                self.cursor.execute(
                    "SELECT speciation_rate, time, fragments, metacommunity_reference "
                    "FROM COMMUNITY_PARAMETERS WHERE reference==?",
                    (reference,),
                )
        except sqlite3.Error as e:  # pragma: no cover
            self.logger.error("Failure to fetch COMMUNITY_PARAMETERS table from database. Check table exists.")
            raise e
        fetch = self.cursor.fetchone()
        if fetch is None:
            raise KeyError("No community parameters found for reference of {}".format(reference))
        values = [x for x in fetch]
        column_names = [member[0] for member in self.cursor.description]
        if sys.version_info[0] is not 3:  # pragma: no cover
            for i, each in enumerate(values):
                if isinstance(each, unicode):
                    values[i] = each.encode("ascii")
        # Now convert it into a dictionary
        return dict(zip(column_names, values))

    def get_community_parameters_pd(self):
        """
        Gets all the calculated community parameter sets from the database.

        :return: the community parameters
        :rtype: pd.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "COMMUNITY_PARAMETERS"):
            raise IOError("No community parameters table exists in the database - no communities have been calculated.")
        return pd.read_sql_query("SELECT * FROM COMMUNITY_PARAMETERS", self.database)

    def get_community_reference(
        self,
        speciation_rate,
        time,
        fragments,
        metacommunity_size=0,
        metacommunity_speciation_rate=0.0,
        metacommunity_option=None,
        external_reference=0,
        min_speciation_gen=0.0,
        max_speciation_gen=0.0,
    ):
        """
        Gets the community reference associated with the supplied community parameters

        :raises KeyError: if COMMUNITY_PARAMETERS (or METACOMMUNITY_PARAMETERS) does not exist in database or no
            reference exists for the supplied parameters

        :param float speciation_rate: the speciation rate of the community
        :param float time: the time in generations of the community
        :param bool/int fragments: whether fragments were determined for the community
        :param int/float metacommunity_size: the metacommunity size
        :param float metacommunity_speciation_rate: the metacommunity speciation rate
        :param str metacommunity_option: option used for metacommunity creation
        :param int external_reference: the metacommunity reference for external metacommunity databases
        :param float min_speciation_gen: the minimum number of generations required before speciation
        :param float max_speciation_gen: the maximum number of generations required before speciation
        :return: the reference associated with this set of simulation parameters
        """
        fragments = int(fragments)
        if metacommunity_size == 0 and external_reference == 0:
            metacommunity_reference = 0
        else:
            self._check_database()
            if not check_sql_table_exist(self.database, "METACOMMUNITY_PARAMETERS"):  # pragma: no cover
                raise KeyError("No table METACOMMUNITY_PARAMETERS exists in database {}".format(self.file))
            self.cursor.execute(
                "SELECT reference FROM METACOMMUNITY_PARAMETERS WHERE metacommunity_size == ? AND "
                "speciation_rate == ? AND option == ? and external_reference == ?",
                (float(metacommunity_size), metacommunity_speciation_rate, metacommunity_option, external_reference),
            )
            try:
                metacommunity_reference = self.cursor.fetchone()[0]
            except (IndexError, TypeError):
                raise KeyError("Cannot obtain metacommunity reference from database with provided parameters.")
        try:
            if check_sql_table_exist(self.database, "COMMUNITY_PARAMETERS"):
                try:
                    self.cursor.execute(
                        "SELECT reference FROM COMMUNITY_PARAMETERS WHERE speciation_rate == ? AND "
                        "time == ? AND fragments == ? AND metacommunity_reference == ? AND "
                        "min_speciation_gen == ? AND max_speciation_gen == ?",
                        (
                            speciation_rate,
                            time,
                            int(fragments),
                            metacommunity_reference,
                            min_speciation_gen,
                            max_speciation_gen,
                        ),
                    )
                except sqlite3.Error:
                    if min_speciation_gen != 0.0 or max_speciation_gen != 0.0:
                        raise IndexError
                    self.cursor.execute(
                        "SELECT reference FROM COMMUNITY_PARAMETERS WHERE speciation_rate == ? AND "
                        "time == ? AND fragments == ? AND metacommunity_reference == ?",
                        (speciation_rate, time, int(fragments), metacommunity_reference),
                    )
                return self.cursor.fetchone()[0]
        except (IndexError, TypeError):
            raise KeyError("Cannot obtain community reference from database with provided parameters.")

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
        except sqlite3.Error as e:  # pragma: no cover
            self.logger.error(
                "Failure to fetch references from METACOMMUNITY_PARAMETERS table in database." " Check table exists."
            )
            raise e
        references = [x[0] for x in self.cursor.fetchall()]
        return references

    def get_metacommunity_parameters(self, reference=1):
        """
        Returns a dictionary containing the parameters for the calculated community.

        :param reference: the reference key for the calculated parameters. (default is 1)

        :raises sqlite3.Error: if the METACOMMUNITY_PARAMETERS table does not exist, or some other sqlite
            error occurs

        :raises KeyError: if the supplied reference does not exist in the METACOMMUNITY_PARAMETERS table

        :return: dictionary containing the speciation_rate, metacommunity_size, metacommunity option and metacommunity
                 reference.
        :rtype: dict
        """
        self._check_database()
        try:
            self.cursor.execute(
                "SELECT speciation_rate, metacommunity_size, option, external_reference FROM"
                " METACOMMUNITY_PARAMETERS  WHERE reference== ?",
                (reference,),
            )
        except sqlite3.Error as e:
            self.logger.error("Failure to fetch METACOMMUNITY_PARAMETERS table from database. Check table exists. \n")
            raise e
        fetch = self.cursor.fetchone()
        if fetch is None:
            raise KeyError("No metacommunity parameters found for reference of {}".format(reference))
        values = [x for x in fetch]
        if len(values) == 0:  # pragma: no cover
            raise KeyError("No metacommunity parameters found for reference of {}".format(reference))
        column_names = [member[0] for member in self.cursor.description]
        if sys.version_info[0] is not 3:  # pragma: no cover
            for i, each in enumerate(values):
                if isinstance(each, unicode):
                    values[i] = each.encode("ascii")
        # Now convert it into a dictionary
        return dict(zip(column_names, values))

    def get_metacommunity_parameters_pd(self):
        """
        Gets all the calculated metacommunity parameter sets from the database.

        :return: the metacommunity parameters
        :rtype: pd.DataFrame
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "METACOMMUNITY_PARAMETERS"):
            raise IOError("No metacommunity parameters table exists in the database.")
        return pd.read_sql_query("SELECT * FROM METACOMMUNITY_PARAMETERS", self.database)

    def get_parameter_description(self, key=None):
        """
        Gets the description of the parameter matching the key from those contained in SIMULATION_PARAMETERS

        Simply accesses the _parameter_descriptions data stored in parameter_descriptions.json

        :return: string containing the parameter description or a dict containing all values if no key is supplied

        :rtype: str
        """
        return get_parameter_description(key)

    def is_protracted(self):
        """
        Indicates whether the simulation is a protracted simulation or not. This is read from the completed database
        file.

        :return: boolean, true if the simulation was performed with protracted speciation.
        """
        return bool(self.get_simulation_parameters().get("protracted", False))

    def clear_calculations(self):
        """
        Removes the BIODIVERSITY_METRICS and FRAGMENT_OCTAVES tables completely.

        .. note:: that this cannot be undone (other than re-running the calculations).
        """
        self._check_database()
        self.cursor.execute("DROP TABLE IF EXISTS BIODIVERSITY_METRICS")
        self.cursor.execute("DROP TABLE IF EXISTS FRAGMENT_OCTAVES")
        self.cursor.execute("DROP TABLE IF EXISTS FRAGMENT_RICHNESS")
        self.cursor.execute("DROP TABLE IF EXISTS PLOT_DATA")
        self.cursor.execute("DROP TABLE IF EXISTS SPECIES_RICHNESS")
        self.cursor.execute("DROP TABLE IF EXISTS ALPHA_DIVERSITY")
        self.cursor.execute("DROP TABLE IF EXISTS BETA_DIVERSITY")
        self.cursor.execute("DROP TABLE IF EXISTS SPECIES_DISTANCE_SIMILARITY")
        self.database.commit()
        if self.c_community is not None:  # pragma: no cover
            self.c_community.reset()

    def wipe_data(self):
        """
        Wipes all calculated data apart from the original, unformatted coalescence tree.
        The Speciation_Counter program will have to be re-run to perform any analyses.
        """
        self._check_database()
        self.cursor.execute("DROP TABLE IF EXISTS FRAGMENT_ABUNDANCES")
        self.cursor.execute("DROP TABLE IF EXISTS SPECIES_ABUNDANCES")
        self.cursor.execute("DROP TABLE IF EXISTS COMMUNITY_PARAMETERS")
        self.cursor.execute("DROP TABLE IF EXISTS METACOMMUNITY_PARAMETERS")
        self.cursor.execute("DROP TABLE IF EXISTS SPECIES_LOCATIONS")
        self.clear_calculations()
        self.database.commit()
        if self.c_community is not None:  # pragma: no cover
            self.c_community.reset()

    def _backup_species_list(self):
        """
        Backs up the SPECIES_LIST table to SPECIES_LIST_ORIGINAL

        :return: None
        :rtype: None
        """
        self._check_database()
        if check_sql_table_exist(self.database, "SPECIES_LIST_ORIGINAL"):  # pragma: no cover
            raise IOError("SPECIES_LIST_ORIGINAL already exists in database.")
        self.cursor.execute("ALTER TABLE SPECIES_LIST RENAME TO SPECIES_LIST_ORIGINAL")
        self.database.commit()

    def _restore_backup_species_list(self):
        """
        Restores the backed up SPECIES_LIST table.

        :return: None
        :rtype: None
        """
        self.cursor.execute("ALTER TABLE SPECIES_LIST_ORIGINAL RENAME TO SPECIES_LIST")
        self.database.commit()

    def downsample(self, sample_proportion):
        """
        Down-samples the individuals by a given proportion globally, and at each location.

        The original SPECIES_LIST is stored in a new table called SPECIES_LIST_ORIGINAL and a new SPECIES_LIST object is
        created containing the down-sampled coalescence tree.

        :param float sample_proportion: the proportion of individuals to sample at each location

        :return: None
        :rtype: None
        """
        if sample_proportion > 1.0:
            raise ValueError("Sample proportion cannot be greater than 1.0: supplied {}.".format(sample_proportion))
        self._check_database()
        species_list = [list(x) for x in self.cursor.execute("SELECT * FROM SPECIES_LIST").fetchall()]
        try:
            self._backup_species_list()
            tips = [x for x in species_list if x[6] == 1]
            no_tips = [x for x in species_list if x[6] == 0]
            for row in tips:
                row.append("{}-{}-{}-{}".format(row[2], row[3], row[4], row[5]))
            unique_locations = set([x[13] for x in tips])
            out_tips = []
            for i in unique_locations:
                select_tips = [x[0:13] for x in tips if x[13] == i]
                out_number = max(math.floor(sample_proportion * len(select_tips)), 1)
                if out_number > len(select_tips):  # pragma: no cover
                    if out_number == len(select_tips) + 1: # correct for rounding errors
                        out_number = len(select_tips)
                    else:
                        raise ValueError(
                            "Number of tips at location {} ({}) too few for sampling {} individuals.".format(
                                i, len(select_tips), out_number
                            )
                        )
                select_indices = random.sample(range(0, len(select_tips)), out_number)
                for i, each in enumerate(select_tips):
                    if i not in select_indices:
                        each[6] = 0
                out_tips.extend(select_tips)
            out_tips.extend(no_tips)
            out_tips = sorted(out_tips, key=itemgetter(0))
            self.cursor.execute(
                "CREATE TABLE SPECIES_LIST (ID int PRIMARY KEY NOT NULL, unique_spec INT NOT NULL, xval INT NOT NULL, "
                "yval INT NOT NULL, xwrap INT NOT NULL, ywrap INT NOT NULL, tip INT NOT NULL, speciated INT NOT "
                "NULL, parent INT NOT NULL, existence INT NOT NULL, randnum REAL NOT NULL, gen_alive INT NOT "
                "NULL, gen_added REAL NOT NULL)"
            )
            self.cursor.executemany(
                "INSERT INTO SPECIES_LIST (ID,unique_spec,xval,yval,xwrap,ywrap,tip,speciated,parent,existence, "
                "randnum,gen_alive,gen_added) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                out_tips,
            )
            self.database.commit()
        except Exception as e:  # pragma: no cover
            try:
                self._restore_backup_species_list()
            except Exception as e2:
                self.logger.error(e2)
            raise e

    def revert_downsample(self):
        """
        Reverts the downsample process by restoring the original SPECIES_LIST table.

        :return: None
        :rtype: None
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "SPECIES_LIST_ORIGINAL"):
            raise IOError("SPECIES_LIST_ORIGINAL table does not exist in database")
        self.cursor.execute("DROP TABLE IF EXISTS SPECIES_LIST")
        self._restore_backup_species_list()

    def downsample_at_locations(self, fragment_csv, ignore_errors=False):
        """
        Downsamples the SPECIES_LIST object using a fragment csv.

        Each row in the csv file should contain the fragment name, x min, y min, x max, y max and the number of
        individuals per cell in that fragment.

        :param fragment_csv: a csv file to use for downsampling individuals
        :param ignore_errors: ignore the errors from mismatches in numbers of individuals

        :return: None
        :rtype: None
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "SPECIES_LIST"):  # pragma: no cover
            raise IOError("SPECIES_LIST table does not exist in {}.".format(self.file))
        if not os.path.exists(fragment_csv):
            raise IOError("Fragment csv does not exist at {}.".format(fragment_csv))
        species_list = [list(x) for x in self.cursor.execute("SELECT * FROM SPECIES_LIST").fetchall()]
        self._backup_species_list()
        try:
            location_dict = {}
            with open(fragment_csv, "r") as csv_file:
                rows = csv.reader(csv_file)
                # Check that the rows contains the correct number of elements.
                for row in rows:
                    if len(row) != 6:
                        raise ValueError("Row length in {} contains {} instead of 6 elements.".format(fragment_csv,
                                                                                                      len(row)))
                    name, x_min, y_min, x_max, y_max, no_individuals = row
                    for x in range(int(x_min), int(x_max) + 1, 1):
                        for y in range(int(y_min), int(y_max) + 1, 1):
                            location_dict["{}-{}-{}-{}".format(x_min, y_min, 0, 0)] = int(no_individuals)
            tips = [x for x in species_list if x[6] == 1]
            no_tips = [x for x in species_list if x[6] == 0]
            for row in tips:
                row.append("{}-{}-{}-{}".format(row[2], row[3], row[4], row[5]))
            out_tips = []
            for k, out_number in location_dict.items():
                select_tips = [x[0:13] for x in tips if x[13] == k]
                if len(select_tips) == 0:  # pragma: no cover
                    self.logger.info("Skipping sampling location {} as there are no recorded individuals.".format(k))
                if out_number > len(select_tips):  # pragma: no cover
                    if not ignore_errors:
                        raise ValueError(
                            "Number of tips at location {} ({}) too few for sampling {} individuals.".format(
                                k, len(select_tips), out_number
                            )
                        )
                    out_number = len(select_tips)
                select_indices = random.sample(range(0, len(select_tips)), out_number)
                for i, each in enumerate(select_tips):
                    if i not in select_indices:
                        each[6] = 0
                out_tips.extend(select_tips)
            zero_tips = [x[0:13] for x in tips if x[13] not in location_dict.keys()]
            for each in zero_tips:
                each[6] = 0
            out_tips.extend(zero_tips)
            out_tips.extend(no_tips)
            out_tips = sorted(out_tips, key=itemgetter(0))
            self.cursor.execute(
                "CREATE TABLE SPECIES_LIST (ID int PRIMARY KEY NOT NULL, unique_spec INT NOT NULL, xval INT NOT NULL, "
                "yval INT NOT NULL, xwrap INT NOT NULL, ywrap INT NOT NULL, tip INT NOT NULL, speciated INT NOT "
                "NULL, parent INT NOT NULL, existence INT NOT NULL, randnum REAL NOT NULL, gen_alive INT NOT "
                "NULL, gen_added REAL NOT NULL)"
            )
            self.cursor.executemany(
                "INSERT INTO SPECIES_LIST (ID,unique_spec,xval,yval,xwrap,ywrap,tip,speciated,parent,existence, "
                "randnum,gen_alive,gen_added) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                out_tips,
            )
            self.database.commit()
        except Exception as e:
            try:
                self._restore_backup_species_list()
            except Exception as e1:  # pragma: no cover
                self.logger.info("{}.".format(e1))
            raise e



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
        if not self.fragment_abundances:  # pragma: no cover
            self.calculate_fragment_abundances()
        try:
            chosen, richness = zip(
                *[[x[1], x[2]] for x in self.fragment_abundances if x[0] == fragment and x[3] == community_reference]
            )
        except ValueError as ve:  # pragma: no cover
            raise ValueError(
                "Fragment abundances do not contain data"
                " for {} with reference={}: {}".format(fragment, number_of_individuals, ve)
            )
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
            if not self.fragment_abundances:  # pragma: no cover
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
                    raise KeyError(
                        "Sampled number of individuals is greater"
                        " than exists for fragment {}: {} < {}".format(f, sum_total, number_of_individuals[f])
                    )
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

    def calculate_species_distance_similarity(self, output_metrics=True):
        """
        Calculates the probability two individuals are of the same species as a function of distance.

        Stores the mean distance between individuals of the same species in the BIODIVERSITY_METRICS table, and stores
        the full data in new table (SPECIES_DISTANCE_SIMILARITY). Distances are binned to the nearest integer.

        :param output_metrics: if true, outputs to the BIODIVERSITY_METRICS table as well, for metric comparison

        .. note:: Extremely slow for large landscape sizes.

        """
        self._check_database()
        species_locations = self.cursor.execute(
            "SELECT species_id, x, y, community_reference FROM " "SPECIES_LOCATIONS"
        ).fetchall()
        tmp_create = (
            "CREATE TABLE SPECIES_DISTANCE_SIMILARITY (ref INT PRIMARY KEY NOT NULL, distance INT NOT NULL,"
            " no_individuals INT NOT NULL, community_reference INT NOT NULL)"
        )
        if not check_sql_table_exist(self.database, "SPECIES_DISTANCE_SIMILARITY"):
            try:
                self.cursor.execute(tmp_create)
                self.database.commit()
            except Exception as e:  # pragma: no cover
                e.message = "Error creating SPECIES_RICHNESS table: " + str(e)
                raise e
        else:  # pragma: no cover
            raise IOError("SPECIES_DISTANCE_SIMILARITY table already exists in the output database.")
        if not check_sql_table_exist(self.database, "SPECIES_LOCATIONS"):  # pragma: no cover
            raise IOError(
                "SPECIES_LOCATIONS table does not exist in output database - calculate species locations first."
            )
        max_val = [
            x for x in self.cursor.execute("SELECT min(x), max(x)," " min(y), max(y) FROM SPECIES_LOCATIONS").fetchone()
        ]
        references = set([x[3] for x in species_locations])
        ref = 0
        output = []
        means = []
        max_distance = int(calculate_distance_between(max_val[0], max_val[2], max_val[1], max_val[3])) + 1
        for reference in references:
            select = [x[0:3] for x in species_locations if x[3] == reference]
            species_list = {}
            if len(select) == 0:  # pragma: no cover
                continue
            sum_distances = [0] * max_distance
            # first loop over every individual
            for row in select:
                if row[0] not in species_list.keys():
                    species_list[row[0]] = []
                species_list[row[0]].append([row[1], row[2]])
            # Now loop over every species and calculate the mean distance
            for species_id, locations in species_list.items():
                total_length = len(locations)
                for i, location in enumerate(locations):
                    for j in range(i + 1, total_length):
                        distance = int(
                            calculate_distance_between(location[0], location[1], locations[j][0], locations[j][1])
                        )
                        sum_distances[distance] += 1
            total_sim = 0
            number_all = 0
            for distance, item in enumerate(sum_distances):
                if item == 0:
                    continue
                output.append([distance, item, reference])
                total_sim += item * distance
                number_all += item
            if number_all == 0:  # pragma: no cover
                self.logger.info(
                    "No distances found for {} - likely no species exist with more than one"
                    " location.".format(reference)
                )
                mean = 0
            else:
                mean = total_sim / number_all
            means.append([reference, mean])
        sql_output = []
        for row in output:
            ref += 1
            tmp = [ref]
            tmp.extend(row)
            sql_output.append(tmp)
        if output_metrics:
            ref = self.check_biodiversity_table_exists()
            bio_output = []
            for x in means:
                ref += 1
                tmp = [ref, "mean_distance_between_individuals", "whole"]
                tmp.extend([x[0], float(x[1])])
                bio_output.append(tmp)
            self.cursor.executemany("INSERT INTO BIODIVERSITY_METRICS VALUES (?, ?, ?, ?, ?, NULL, NULL)", bio_output)
        self.cursor.executemany("INSERT INTO SPECIES_DISTANCE_SIMILARITY VALUES(?,?,?,?)", sql_output)
        self.database.commit()

    def get_species_distance_similarity(self, community_reference=1):
        """
        Gets the species distance similarity table for the provided community reference.

        :return: list containing the distance, number of similar species with that distance
        """
        self._check_database()
        if not check_sql_table_exist(self.database, "SPECIES_DISTANCE_SIMILARITY"):  # pragma: no cover
            raise IOError("Database {} does not contain SPECIES_DISTANCE_SIMILARITY table".format(self.file))
        sql_fetch = self.cursor.execute(
            "SELECT distance, no_individuals FROM SPECIES_DISTANCE_SIMILARITY " "WHERE community_reference == ?",
            (community_reference,),
        ).fetchall()
        return [list(x) for x in sql_fetch]

    def write_to_csv(self, output_csv, table_name):
        """
        Writes a specified table from the database to the output database.

        :param str output_csv: path to the csv output location
        :param str table_name: name of the output table

        :return: None
        :rtype: None
        """
        self._check_database()
        if os.path.exists(output_csv):
            raise FileExistsError("File already exists at {}.".format(output_csv))
        if not check_sql_table_exist(self.database, table_name):
            raise KeyError("No table of {} exists in the database.".format(table_name))
        table_data = fetch_table_from_sql(self.database, table_name, column_names=True)
        if sys.version_info[0] < 3:  # pragma: no cover
            infile = open(output_csv, "wb")
        else:
            infile = open(output_csv, "w", newline="")
        with infile as csv_file:
            csv_writer = csv.writer(csv_file)
            for each in table_data:
                csv_writer.writerow(each)

    def write_all_to_csvs(self, output_location, file_naming):
        """
        Outputs all tables from the database to csvs contained in the provided directory and following the naming
        structure of the supplied file naming.

        :param str output_location: the folder to generate files in
        :param file_naming: the naming for the output csvs - will be appended with _{table_name}.csv
        :return:

        .. note:: dots and ".csv" extensions are removed from the file_naming output
        """
        if not os.path.exists(output_location):
            os.makedirs(output_location)
        file_str = file_naming.replace(".csv", "").replace(".", "")
        for table in get_table_names(self.database):
            output_csv = os.path.join(output_location, "{}_{}.csv".format(file_str, table))
            self.write_to_csv(output_csv, table)


def scale_simulation_fit(simulated_value, actual_value, number_individuals, total_individuals):
    """
    Calculates goodness of fit for the provided values, and scales based on the total number of individuals that exist.
    The calculation is 1 - (abs(x - y)/max(x, y)) * n/n_tot for x, y simulated and actual values, n, n_tot for metric
    and total
    number of individuals.

    :param simulated_value: the simulated value of the metric
    :param actual_value: the actual value of the metric
    :param number_individuals: the number of individuals this metric relates to
    :param total_individuals: the total number of individuals across all sites for this metric
    :return: the scaled fit value
    """
    return (
        (1 - (abs(simulated_value - actual_value)) / max(simulated_value, actual_value))
        * number_individuals
        / total_individuals
    )
