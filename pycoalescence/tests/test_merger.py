"""
Tests the Merger module for combining the outputs of multiple simulations
"""

import os
import sys
import unittest

from setup_tests import setUpAll, tearDownAll

from pycoalescence import Merger, CoalescenceTree
from pycoalescence.sqlite_connection import fetch_table_from_sql, check_sql_table_exist


def setUpModule():
    """
    Creates the output directory and moves logging files
    """
    setUpAll()


def tearDownModule():
    """
    Removes the output directory
    """
    tearDownAll()


class TestSimulationReadingViaMerger(unittest.TestCase):
    """
    Tests that simulation can successfully read tables from a database.
    """

    dbname = "output/mergers/combined1.db"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.dbname):
            os.remove(cls.dbname)

    def testReadsSimulationParameters(self):
        """
        Tests that simulation parameters are correctly read from the database.
        """
        simulation_parameters = Merger()._read_simulation_parameters(input_simulation="sample/mergers/data_0_0.db")
        expected_parameters = [
            6,
            6,
            "output",
            0.5,
            4.0,
            4.0,
            1,
            0.1,
            10,
            1.0,
            1,
            0.0,
            200.0,
            "set",
            "sample/SA_sample_coarse.tif",
            35,
            41,
            11,
            14,
            1.0,
            "sample/SA_sample_fine.tif",
            13,
            13,
            0,
            0,
            "null",
            13,
            13,
            13,
            13,
            0,
            0,
            "none",
            "none",
            1,
            "normal",
            0.0,
            0.0,
            0,
            "closed",
            0,
            0.0,
            0.0,
            "none",
        ]
        self.assertListEqual(simulation_parameters, expected_parameters)

    def testReadsSpeciesList(self):
        """
        Tests that the species list object is correctly read from the database.
        """
        species_list = Merger()._read_species_list(input_simulation="sample/mergers/data_0_0.db")[0:5]
        expected_list = [
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0.0, 0, 0.0],
            [1, 0, 0, 0, 0, 0, 1, 0, 3761, 0, 0.712285394568117, 0, 0.0],
            [2, 0, 0, 0, 0, 0, 1, 0, 3762, 0, 0.113159547847957, 0, 0.0],
            [3, 0, 0, 0, 0, 0, 1, 0, 3763, 0, 0.95236636044045, 0, 0.0],
            [4, 0, 0, 0, 0, 0, 1, 0, 3764, 0, 0.679672305831754, 0, 0.0],
        ]
        for i, row in enumerate(expected_list):
            for j, each in enumerate(row):
                if j == 10 or j == 12:
                    self.assertAlmostEqual(each, species_list[i][j])
                else:
                    self.assertEqual(each, species_list[i][j])

    def testReadsSpeciesRichness(self):
        """
        Tests that the species richness object is correctly read from the database
        """
        species_richness = Merger()._read_species_richness(input_simulation="sample/mergers/data_0_0.db")
        expected_richness = [[0, 1, 3644], [1, 2, 3643], [2, 3, 3674], [3, 4, 3675], [4, 5, 3697], [5, 6, 3695]]
        for i, row in enumerate(expected_richness):
            self.assertListEqual(row, species_richness[i])

    def testReadsSpeciesAbundances(self):
        """
        Tests that the species abundances object is correctly read from the database
        """
        species_abundances = Merger()._read_species_abundances(input_simulation="sample/mergers/data_0_0.db")[-6:]
        expected_abundances = [
            [22029, 3690, 2, 6],
            [22030, 3691, 1, 6],
            [22031, 3692, 1, 6],
            [22032, 3693, 1, 6],
            [22033, 3694, 1, 6],
            [22034, 3695, 3, 6],
        ]
        for i, row in enumerate(expected_abundances):
            self.assertListEqual(row, species_abundances[i])

    def testReadsFragmentOctaves(self):
        """
        Tests that the fragment octaves object is correctly read from the database.
        """
        fragment_octaves = Merger()._read_fragment_octaves(input_simulation="sample/mergers/data_0_0.db")
        expected_octaves = [
            [0, "whole", 0, 3560],
            [1, "whole", 0, 3559],
            [2, "whole", 0, 3617],
            [3, "whole", 0, 3619],
            [4, "whole", 0, 3662],
            [5, "whole", 0, 3658],
        ]
        for i, row in enumerate(expected_octaves):
            self.assertListEqual(row, fragment_octaves[i])


class TestSimulationMerging(unittest.TestCase):
    """
    Tests that simulations can be successfully merged with a variety of tables and parameters.
    """

    @classmethod
    def setUpClass(cls):
        cls.dbname = "output/mergers/combined2.db"
        cls.dbname2 = "output/mergers/combined3.db"
        for each in [cls.dbname, cls.dbname2]:
            if os.path.exists(each):
                os.remove(each)
        cls.merger = Merger(database=cls.dbname)
        cls.merger.add_simulation("sample/mergers/data_0_0.db")
        cls.merger.add_simulation("sample/mergers/data_1_1.db")
        cls.merger.write()
        cls.merger2 = Merger(database=cls.dbname2)
        cls.merger2.add_simulations(["sample/mergers/data_2_2.db", "sample/mergers/data_3_3.db"])

    @classmethod
    def tearDownClass(cls):
        """
        Removes the output database
        """
        cls.merger.database.close()
        cls.merger.database = None
        if os.path.exists(cls.dbname):
            os.remove(cls.dbname)

    def testSetDatabase(self):
        """Tests that an error is raised if the output database already exists."""
        m = Merger()
        with self.assertRaises(IOError):
            m.set_database(self.dbname)

    def testMergerDeletion(self):
        """Tests that the merger deletes the database successfully."""
        m = Merger()
        m._open_database(filename=os.path.join("output", "mergertmp.db"))
        self.assertFalse(m.database is None)
        m.__del__()
        self.assertTrue(m.database is None)

    def testCreateTableErrors(self):
        """Tests that creating the simulation parameters raises the expected errors."""
        m = Merger()
        with self.assertRaises(IOError):
            m._create_simulation_parameters()
        with self.assertRaises(IOError):
            m._create_community_parameters()
        with self.assertRaises(IOError):
            m._create_metacommunity_parameters()
        with self.assertRaises(IOError):
            m._create_species_list()
        with self.assertRaises(IOError):
            m._create_species_locations()
        with self.assertRaises(IOError):
            m._create_species_abundances()
        with self.assertRaises(IOError):
            m._create_fragment_abundances()
        with self.assertRaises(IOError):
            m._create_fragment_octaves()
        with self.assertRaises(IOError):
            m._create_species_richness()
        with self.assertRaises(IOError):
            m._create_fragment_richness()
        with self.assertRaises(IOError):
            m._write_simulation_parameters()
        with self.assertRaises(IOError):
            m._write_species_list()
        with self.assertRaises(IOError):
            m._write_species_locations()
        with self.assertRaises(IOError):
            m._write_species_abundances()
        with self.assertRaises(IOError):
            m._write_fragment_abundances()
        with self.assertRaises(IOError):
            m._write_species_richness()
        with self.assertRaises(IOError):
            m._write_fragment_richness()
        with self.assertRaises(IOError):
            m._write_fragment_octaves()
        with self.assertRaises(IOError):
            m._write_community_parameters()
        with self.assertRaises(IOError):
            m._write_metacommunity_parameters()
        with self.assertRaises(ValueError):
            m._create_combined_species_richness()
        with self.assertRaises(ValueError):
            m._create_combined_fragment_richness()
        with self.assertRaises(ValueError):
            m._create_combined_fragment_octaves()

    def testSpeciesList(self):
        """
        Tests that the species list object is correctly calculates for the database
        """
        species_richness = fetch_table_from_sql(self.dbname, "SPECIES_LIST")
        check_richness = [x for x in species_richness if x[0] in [57236791, 57251923, 4, 5]]
        check_richness.sort(key=lambda x: x[0])
        expected_richness = [
            [4, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0.0, 0, 0.0, 2],
            [5, 0, 0, 0, 0, 0, 1, 0, 11328, 0, 0.712285394568117, 0, 0.0, 2],
            [57236791, 0, 8, 6, -1, 0, 0, 1, 0, 0, 0.59455712863121, 2, 0.0, 1],
            [57251923, 0, 7, 3, 0, 0, 0, 1, 0, 0, 0.603760047033245, 2, 0.0, 1],
        ]
        for i, row in enumerate(expected_richness):
            for j, each in enumerate(row):
                if j == 10 or j == 12:
                    self.assertAlmostEqual(each, check_richness[i][j])
                else:
                    self.assertEqual(each, check_richness[i][j])

    def testSpeciesRichness(self):
        """
        Tests that the landscape species richness is correctly calculated from the databases.
        """
        richness = [[0, 1, 7288], [1, 2, 7286], [2, 3, 7348], [3, 4, 7350], [4, 5, 7394], [5, 6, 7390]]
        self.assertListEqual(fetch_table_from_sql(self.dbname, "SPECIES_RICHNESS"), richness)

    def testSpeciesAbundances(self):
        """
        Tests that the species abundances are correctly calculated in the merged database
        """
        expected_abundances = [[5, 3697, 0, 1, 2], [1944632, 5090, 1, 1, 2], [485519191, 3695, 3, 6, 1]]
        real_abundances = fetch_table_from_sql(self.dbname, "SPECIES_ABUNDANCES")
        abundances = [x for x in real_abundances if x[0] == 1944632 or x[0] == 485519191 or x[0] == 5]
        if sys.version_info[0] >= 3:
            self.assertCountEqual(expected_abundances, abundances)
        else:  # pragma: no cover
            self.assertItemsEqual(expected_abundances, abundances)

    def testSimulationParameters(self):
        """
        Tests that the simulation parameters are correctly calculated in the merged database.
        """
        sim_pars = [
            [
                6,
                6,
                "output",
                0.5,
                4.0,
                4.0,
                1,
                0.1,
                10,
                1.0,
                1,
                0.0,
                200.0,
                "set",
                "sample/SA_sample_coarse.tif",
                35,
                41,
                11,
                14,
                1.0,
                "sample/SA_sample_fine.tif",
                13,
                13,
                0,
                0,
                "null",
                13,
                13,
                13,
                13,
                0,
                0,
                "none",
                "none",
                1,
                "normal",
                0.0,
                0.0,
                0,
                "closed",
                0,
                0.0,
                0.0,
                "none",
                1,
                "sample/mergers/data_0_0.db",
            ],
            [
                6,
                6,
                "output",
                0.5,
                4.0,
                4.0,
                2,
                0.1,
                10,
                1.0,
                1,
                0.0,
                200.0,
                "set",
                "sample/SA_sample_coarse.tif",
                35,
                41,
                11,
                14,
                1.0,
                "sample/SA_sample_fine.tif",
                13,
                13,
                0,
                0,
                "null",
                13,
                13,
                13,
                13,
                0,
                0,
                "none",
                "none",
                1,
                "normal",
                0.0,
                0.0,
                0,
                "closed",
                0,
                0.0,
                0.0,
                "none",
                2,
                "sample/mergers/data_1_1.db",
            ],
        ]
        actual = fetch_table_from_sql(self.dbname, "SIMULATION_PARAMETERS")
        for i, each in enumerate(sim_pars):
            self.assertListEqual(actual[i], each)

    def testSimulationParametersFetching(self):
        output_pars1 = {
            "coarse_map_file": "sample/SA_sample_coarse.tif",
            "coarse_map_scale": 1.0,
            "coarse_map_x": 35,
            "coarse_map_x_offset": 11,
            "coarse_map_y": 41,
            "coarse_map_y_offset": 14,
            "cutoff": 0.0,
            "deme": 1,
            "dispersal_map": "none",
            "dispersal_method": "normal",
            "dispersal_relative_cost": 1.0,
            "fine_map_file": "sample/SA_sample_fine.tif",
            "fine_map_x": 13,
            "fine_map_x_offset": 0,
            "fine_map_y": 13,
            "fine_map_y_offset": 0,
            "gen_since_historical": 200.0,
            "grid_x": 13,
            "grid_y": 13,
            "habitat_change_rate": 0.0,
            "landscape_type": "closed",
            "task": 6,
            "m_probability": 0.0,
            "max_speciation_gen": 0.0,
            "max_time": 10,
            "min_num_species": 1,
            "min_speciation_gen": 0.0,
            "output_dir": "output",
            "historical_coarse_map": "none",
            "historical_fine_map": "none",
            "protracted": 0,
            "sample_file": "null",
            "sample_size": 0.1,
            "sample_x": 13,
            "sample_x_offset": 0,
            "sample_y": 13,
            "sample_y_offset": 0,
            "seed": 6,
            "sigma": 4.0,
            "sim_complete": 1,
            "speciation_rate": 0.5,
            "tau": 4.0,
            "time_config_file": "set",
        }
        output_pars2 = {
            "coarse_map_file": "sample/SA_sample_coarse.tif",
            "coarse_map_scale": 1.0,
            "coarse_map_x": 35,
            "coarse_map_x_offset": 11,
            "coarse_map_y": 41,
            "coarse_map_y_offset": 14,
            "cutoff": 0.0,
            "deme": 2,
            "dispersal_map": "none",
            "dispersal_method": "normal",
            "dispersal_relative_cost": 1.0,
            "fine_map_file": "sample/SA_sample_fine.tif",
            "fine_map_x": 13,
            "fine_map_x_offset": 0,
            "fine_map_y": 13,
            "fine_map_y_offset": 0,
            "gen_since_historical": 200.0,
            "grid_x": 13,
            "grid_y": 13,
            "habitat_change_rate": 0.0,
            "landscape_type": "closed",
            "task": 6,
            "m_probability": 0.0,
            "max_speciation_gen": 0.0,
            "max_time": 10,
            "min_num_species": 1,
            "min_speciation_gen": 0.0,
            "output_dir": "output",
            "historical_coarse_map": "none",
            "historical_fine_map": "none",
            "protracted": 0,
            "sample_file": "null",
            "sample_size": 0.1,
            "sample_x": 13,
            "sample_x_offset": 0,
            "sample_y": 13,
            "sample_y_offset": 0,
            "seed": 6,
            "sigma": 4.0,
            "sim_complete": 1,
            "speciation_rate": 0.5,
            "tau": 4.0,
            "time_config_file": "set",
        }
        sim_pars1 = self.merger.get_simulation_parameters(guild=1)
        sim_pars2 = self.merger.get_simulation_parameters(guild=2)
        self.assertEqual(output_pars1, sim_pars1)
        self.assertEqual(output_pars2, sim_pars2)

    def testCommunityParameters(self):
        """Tests that the community parameters are correctly calculated in the merged database."""
        community_params = [
            [1, 0.5, 0.0, 0, 0],
            [2, 0.5, 0.5, 0, 0],
            [3, 0.6, 0.0, 0, 0],
            [4, 0.6, 0.5, 0, 0],
            [5, 0.7, 0.0, 0, 0],
            [6, 0.7, 0.5, 0, 0],
        ]
        actual = fetch_table_from_sql(self.dbname, "COMMUNITY_PARAMETERS")
        for i, each in enumerate(community_params):
            self.assertListEqual(each, actual[i])

    def testGenerateGuildTables(self):
        """Tests that the guild tables are generated properly."""
        self.assertFalse(check_sql_table_exist(self.merger2.file, "SPECIES_RICHNESS_GUILDS"))
        self.assertFalse(check_sql_table_exist(self.merger2.file, "FRAGMENT_RICHNESS_GUILDS"))
        self.assertFalse(check_sql_table_exist(self.merger2.file, "FRAGMENT_OCTAVES_GUILDS"))
        self.merger2.generate_guild_tables()
        self.assertTrue(check_sql_table_exist(self.merger2.file, "SPECIES_RICHNESS_GUILDS"))
        self.assertTrue(check_sql_table_exist(self.merger2.file, "FRAGMENT_RICHNESS_GUILDS"))
        self.assertTrue(check_sql_table_exist(self.merger2.file, "FRAGMENT_OCTAVES_GUILDS"))
        fragment_octaves = [
            [1, "fragment1", 0, 2, 1],
            [2, "fragment1", 1, 3, 1],
            [7, "fragment1", 0, 3, 1],
            [13, "fragment2", 0, 7, 1],
            [21, "fragment2", 1, 7, 1],
            [31, "fragment2", 0, 9, 1],
            [43, "fragment2", 1, 6, 1],
            [57, "whole", 0, 626, 1],
            [73, "whole", 1, 593, 1],
            [91, "whole", 2, 478, 1],
            [111, "whole", 3, 287, 1],
            [133, "whole", 4, 97, 1],
            [157, "whole", 0, 1035, 1],
            [183, "whole", 1, 985, 1],
            [211, "whole", 2, 651, 1],
            [241, "whole", 3, 238, 1],
            [273, "whole", 4, 44, 1],
            [4, "fragment1", 0, 6, 2],
            [5, "fragment1", 0, 10, 2],
            [6, "fragment2", 0, 10, 2],
            [14, "fragment2", 1, 6, 2],
            [22, "fragment2", 0, 18, 2],
            [32, "whole", 0, 708, 2],
            [44, "whole", 1, 563, 2],
            [58, "whole", 2, 494, 2],
            [74, "whole", 3, 275, 2],
            [92, "whole", 4, 97, 2],
            [112, "whole", 0, 1035, 2],
            [134, "whole", 1, 920, 2],
            [158, "whole", 2, 674, 2],
            [184, "whole", 3, 256, 2],
            [212, "whole", 0, 708, 2],
            [242, "whole", 1, 563, 2],
            [274, "whole", 2, 494, 2],
            [308, "whole", 3, 275, 2],
            [344, "whole", 4, 97, 2],
            [382, "whole", 0, 1035, 2],
            [422, "whole", 1, 920, 2],
            [464, "whole", 2, 674, 2],
            [508, "whole", 3, 256, 2],
        ]
        actual = fetch_table_from_sql(self.dbname2, "FRAGMENT_OCTAVES_GUILDS")
        for i, each in enumerate(fragment_octaves):
            self.assertListEqual(each, actual[i])
        richness = [[1, 1, 2095, 1], [2, 2, 2954, 1], [4, 1, 2147, 2], [5, 2, 2923, 2]]
        self.assertListEqual(fetch_table_from_sql(self.dbname2, "SPECIES_RICHNESS_GUILDS"), richness)


class TestMergerInheritance(unittest.TestCase):
    """
    Tests that the merger class correctly inherits from the CoalescenceTree class
    """

    @classmethod
    def setUpClass(cls):
        cls.dbname = "output/mergers/combined3.db"
        if os.path.exists(cls.dbname):
            os.remove(cls.dbname)
        cls.merger = Merger(database=cls.dbname)
        cls.merger.add_simulation("sample/mergers/data_0_0.db")
        cls.merger.add_simulation("sample/mergers/data_1_1.db")
        cls.merger.write()

    @classmethod
    def tearDownClass(cls):
        """
        Removes the output database
        """
        cls.merger.database.close()
        cls.merger.database = None
        if os.path.exists(cls.dbname):
            os.remove(cls.dbname)

    def testMergerGetSpeciesRichness(self):
        """
        Tests that species richness functions work properly.
        :return:
        """
        self.assertEqual(self.merger.get_species_richness(1), 7288)
        self.assertEqual(self.merger.get_species_richness(1), 7288)
        self.assertEqual(self.merger.get_species_richness(2), 7286)
        self.assertEqual(self.merger.get_species_richness(2), 7286)


class TestMergerAnalysis(unittest.TestCase):
    """
    Tests that the Merger can perform analysis in the same way as CoalescenceTree.
    """

    @classmethod
    def setUpClass(cls):
        cls.dbname = "output/mergers/combined4.db"
        if os.path.exists(cls.dbname):
            os.remove(cls.dbname)
        cls.merger = Merger(database=cls.dbname, logging_level=50)
        cls.merger.add_simulation("sample/mergers/data_0_0.db")
        cls.merger.add_simulation("sample/mergers/data_1_1.db")
        cls.merger.write()
        cls.merger.wipe_data()
        cls.merger.set_speciation_parameters(
            speciation_rates=[0.5, 0.6], record_spatial=False, record_fragments="sample/FragmentsTest.csv"
        )
        cls.merger.apply()
        cls.merger = Merger(database=cls.dbname, logging_level=50, expected=True)
        cls.merger.set_speciation_parameters(
            speciation_rates=[0.7, 0.8], record_spatial=False, record_fragments="sample/FragmentsTest.csv"
        )
        cls.merger.apply_incremental()
        cls.merger.output()
        cls.merger.calculate_fragment_richness()

    @classmethod
    def tearDownClass(cls):
        """
        Removes the output database
        """
        cls.merger.database.close()
        cls.merger.database = None
        if os.path.exists(cls.dbname):
            os.remove(cls.dbname)

    def testMergerRepeatSimAdding(self):
        """Tests that an error is raised when a repeat simulation is added."""
        ct = CoalescenceTree("sample/mergers/data_0_0.db")
        with self.assertRaises(ValueError):
            self.merger.add_simulation(ct)

    def testMergerAnalysisRichness(self):
        """
        Tests that speciation rates can be applied.
        """
        self.assertEqual(self.merger.get_species_richness(1), 7288)
        self.assertEqual(self.merger.get_species_richness(2), 7348)
        self.assertEqual(self.merger.get_species_richness(1), 7288)
        self.assertEqual(self.merger.get_species_richness(2), 7348)

    def testMergerAnalysisFragmentRichness(self):
        """
        Tests that the analysis can be performed.
        """
        self.assertEqual(self.merger.get_fragment_richness("fragment1", 1), 672)
        self.assertEqual(self.merger.get_fragment_richness("fragment2", 1), 1272)

    def testMergerOutput(self):
        """Tests that the Merger outputs correctly."""
        self.assertEqual(self.merger.get_species_richness(3), 7394)
        self.assertEqual(self.merger.get_species_richness(4), 7426)
        self.assertEqual(self.merger.get_fragment_richness("fragment2", 3), 1276)
        self.assertEqual(self.merger.get_fragment_richness("fragment2", 4), 1280)

    def testMergerAddedSimulations(self):
        """Tests that added simulations work as intended."""
        added_sims = self.merger.get_added_simulations()
        expected_sims = {"sample/mergers/data_0_0.db": 1, "sample/mergers/data_1_1.db": 2}
        self.assertEqual(added_sims, expected_sims)
        self.merger.simulation_list["sample/mergers/data_1_1.db"] = 4
        with self.assertRaises(ValueError):
            _ = self.merger.get_added_simulations()
        self.merger.simulation_list = expected_sims
