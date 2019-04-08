"""Tests the sqlite connection handler object for pycoalescence"""
import os
import sqlite3
import unittest

from setup_tests import setUpAll, tearDownAll

from pycoalescence.sqlite_connection import (
    check_sql_table_exist,
    fetch_table_from_sql,
    SQLiteConnection,
    sql_get_max_from_column,
    check_sql_column_exists,
    get_table_names,
)


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


class TestSqlConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Generates the SQLConnection object and tests that it works as intended with the different data types.

        :return:
        """

    def testFilePathOpens(self):
        """
        Tests that the context manager opens correctly with a file path
        """
        with SQLiteConnection("sample/mergers/data_0_0.db") as cursor:
            self.assertTrue(isinstance(cursor, sqlite3.Cursor))
            t = cursor.execute("SELECT max(reference) FROM COMMUNITY_PARAMETERS").fetchone()[0]
            self.assertEqual(6, t)

    def testDatabaseOpens(self):
        """
        Tests that the context manager works with an already-opened database.
        """
        d = sqlite3.connect("sample/mergers/data_0_0.db")
        with SQLiteConnection(d) as cursor:
            self.assertTrue(isinstance(cursor, sqlite3.Cursor))
            t = cursor.execute("SELECT max(reference) FROM COMMUNITY_PARAMETERS").fetchone()[0]
            self.assertEqual(6, t)
        self.assertTrue(isinstance(d, sqlite3.Connection))
        self.assertIsNotNone(d)
        d.close()
        d = None

    def testCursorOpens(self):
        """
        Tests that the context manager works with an already-opened database.
        """
        d = sqlite3.connect("sample/mergers/data_0_0.db")
        c = d.cursor()
        with SQLiteConnection(c) as cursor:
            self.assertTrue(isinstance(cursor, sqlite3.Cursor))
            t = cursor.execute("SELECT max(reference) FROM COMMUNITY_PARAMETERS").fetchone()[0]
            self.assertEqual(6, t)
        self.assertTrue(isinstance(d, sqlite3.Connection))
        self.assertTrue(isinstance(c, sqlite3.Cursor))
        self.assertIsNotNone(d)
        self.assertIsNotNone(c)
        d.close()
        d = None


class TestSqlFetchAndCheck(unittest.TestCase):
    """
    Tests that fetches and checks on the SQL databases work as intended.
    """

    def testReadsCommunityParameters(self):
        """
        Test that community parameters are correctly read from the database.
        """
        community_parameters = fetch_table_from_sql(
            database="sample/mergers/data_0_0.db", table_name="COMMUNITY_PARAMETERS"
        )
        expected_community_parameters = [
            [1, 0.5, 0.0, 0, 0],
            [2, 0.5, 0.5, 0, 0],
            [3, 0.6, 0.0, 0, 0],
            [4, 0.6, 0.5, 0, 0],
            [5, 0.7, 0.0, 0, 0],
            [6, 0.7, 0.5, 0, 0],
        ]
        for i, row in enumerate(expected_community_parameters):
            self.assertListEqual(row, community_parameters[i])
        community_parameters2 = fetch_table_from_sql(
            database="sample/mergers/data_0_0.db", table_name="COMMUNITY_PARAMETERS", column_names=True
        )
        expected_community_parameters2 = [
            ["reference", "speciation_rate", "time", "fragments", "metacommunity_reference"],
            [1, 0.5, 0.0, 0, 0],
            [2, 0.5, 0.5, 0, 0],
            [3, 0.6, 0.0, 0, 0],
            [4, 0.6, 0.5, 0, 0],
            [5, 0.7, 0.0, 0, 0],
            [6, 0.7, 0.5, 0, 0],
        ]
        for i, row in enumerate(expected_community_parameters2):
            self.assertListEqual(row, community_parameters2[i])
        with self.assertRaises(IOError):
            _ = fetch_table_from_sql(database="sample/mergers/data_0_0.db", table_name="COMMUNITY_PARAMETERSXX")

    def testDetectsTablesCorrectly(self):
        """
        Checks that check_sql_table_exist correctly detects the existence of tables
        """
        input_db = os.path.join("sample", "mergers", "data_0_0.db")
        expected_table_names = [
            "COMMUNITY_PARAMETERS",
            "FRAGMENT_OCTAVES",
            "SIMULATION_PARAMETERS",
            "SPECIES_ABUNDANCES",
            "SPECIES_LIST",
            "SPECIES_LOCATIONS",
            "SPECIES_RICHNESS",
        ]
        table_names = get_table_names(input_db)
        table_names.sort()
        self.assertEqual(expected_table_names, table_names)
        self.assertFalse(check_sql_table_exist(database=input_db, table_name="notarealtable"))
        self.assertTrue(check_sql_table_exist(database=input_db, table_name="COMMUNITY_PARAMETERS"))

    def testDetectsColumnCorrectly(self):
        """
        Checks that detection of the column names works as intended.
        """
        self.assertTrue(
            check_sql_column_exists(
                database="sample/mergers/data_0_0.db", table_name="COMMUNITY_PARAMETERS", column_name="reference"
            )
        )
        self.assertFalse(
            check_sql_column_exists(
                database="sample/mergers/data_0_0.db", table_name="COMMUNITY_PARAMETERS", column_name="referencenot"
            )
        )
        self.assertFalse(
            check_sql_column_exists(
                database="sample/mergers/data_0_0.db", table_name="COMMUNITY_PARAMET2ERS", column_name="referencenot"
            )
        )

    def testGetMaxValue(self):
        """
        Tests that the maximum value function works correctly.
        """
        self.assertEqual(6, sql_get_max_from_column("sample/mergers/data_0_0.db", "COMMUNITY_PARAMETERS", "reference"))
        with self.assertRaises(sqlite3.Error):
            self.assertEqual(
                6, sql_get_max_from_column("sample/mergers/data_0_0.db", "COMMUNITY_PARAMETERS", "reference2")
            )
        with self.assertRaises(sqlite3.Error):
            self.assertEqual(
                6, sql_get_max_from_column("sample/mergers/data_0_0.db", "COMMUNITY_PARAMETERS2", "reference")
            )
