"""
Safely open, close and fetch data from an sqlite connection.

:class:`.SQLiteConnection` contains context management for opening sql connections, plus basic functionality for
detecting existence and structure of databases.
"""
import sqlite3


class SQLiteConnection:
    """
    Class containing context management for opening sqlite3 connections. The file name provided can either be a string
    containing the path to the file, or an sqlite3.Connection object, which will NOT be closed on destruction. This
    provides two points of entry to the system with the same interface.
    """

    def __init__(self, filename):
        """
        Initialises the SQLiteConnection object.

        :param str/sqlite3.Connection filename: Should be either a string containing a path to a file to open,
                                                or an already-open sqlite3.Connection object. If the latter,
                                                the connection will not be closed on destruction. filename can also
                                                be a sqlite3.Cursor object, in which case it will simply be returned.
        """
        self.filename = filename
        self.opened_here = False
        self.database = None

    def __enter__(self):
        """
        Opens the connection to the file and returns an active cursor.

        :return: Active cursor pointing to the file
        :rtype: sqlite3.Cursor
        """
        if isinstance(self.filename, sqlite3.Connection):
            self.database = self.filename
        elif isinstance(self.filename, sqlite3.Cursor):
            return self.filename
        else:
            self.opened_here = True
            try:
                self.database = sqlite3.connect(self.filename)
            except sqlite3.Error as soe:  # pragma: no cover
                self.opened_here = False
                raise soe
        return self.database.cursor()

    def __exit__(self, *args):
        if self.opened_here:
            self.database.commit()
            self.database.close()
            self.database = None


def get_table_names(database):
    """
    Gets a list of all table names in the database.

    :param str/sqlite3.Connection database: the path to the database connection or an already-open database object

    :return: a list of all table names from the database
    :rtype: list
    """
    with SQLiteConnection(database) as cursor:
        return [x[0] for x in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]


def check_sql_table_exist(database, table_name):
    """
    Checks that the supplied table exists in the supplied database.

    :param str/sqlite3.Connection database: the database to check existence in
    :param str table_name: the table name to check for

    :return: true if the table exists
    :rtype: bool
    """
    table_names = get_table_names(database)
    return table_name in table_names


def check_sql_column_exists(database, table_name, column_name):
    """
    Checks if the column exists in the database.

    :param str/sqlite3.Connection database: the database to check existence in
    :param str table_name: the table name to check within
    :param str column_name: the column name to check for

    :return: true if the column exists.
    :rtype: bool
    """
    with SQLiteConnection(database) as cursor:
        c = [i[1] for i in cursor.execute("PRAGMA table_info({})".format(table_name)) if i[1] == column_name]
        return len(c) != 0


def fetch_table_from_sql(database, table_name, column_names=False):
    """
    Returns a list of the data contained by the provided table in the database.

    :raises sqlite3.Error: if the table is not contained in the database (protects SQL injections).

    :param str/sqlite3.Connection database: the database to obtain from
    :param str table_name: the table name to fetch data from
    :param bool column_names: if true, return the column names as the first row in the output

    :return: a list of lists, containing all data within the provided table in the database
    """
    try:
        with SQLiteConnection(database) as c:
            if not check_sql_table_exist(c, table_name):
                raise sqlite3.Error("Table {} does not exist in database.".format(table_name))
            c.execute("SELECT * FROM {}".format(table_name))
            output = []
            if column_names:
                output.append([x[0] for x in c.description])
            output.extend([list(x) for x in c.fetchall()])
            return output
    except sqlite3.Error as soe:  # pragma: no cover
        raise IOError("Cannot fetch {} from database {}: {}".format(table_name, database, soe))


def sql_get_max_from_column(database, table_name, column_name):
    """
    Returns the maximum value from the specified column.

    :param str/sqlite3.Connection database: the database to fetch from
    :param str table_name: the table name to attain
    :param str column_name: the column name to obtain from
    :return:
    """
    with SQLiteConnection(database) as cursor:
        if not check_sql_table_exist(cursor, table_name):
            raise sqlite3.Error("Table {} does not exist in database.".format(table_name))
        if not check_sql_column_exists(cursor, table_name, column_name):
            raise sqlite3.Error("Column {} does not exist in {}.".format(column_name, table_name))
        ex_str = "SELECT max({}) FROM {}".format(column_name, table_name)
        cursor.execute(ex_str)
        return cursor.fetchone()[0]
