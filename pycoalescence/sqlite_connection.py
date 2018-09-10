"""
Safely open, close and fetch data from an sqlite connection.

:class:`.SQLiteConnection` contains context management for opening sql connections, plus basic functionality for
detecting existence and structure of databases.
"""
import sqlite3


class SQLiteConnection():
	"""
	Class containing context management for opening sqlite3 connections. The file name provided can either be a string
	containing the path to the file, or an sqlite3.Connection object, which will NOT be closed on destruction. This
	provides two points of entry to the system with the same interface.
	"""
	def __init__(self, filename):
		"""
		Initialises the SQLiteConnection object.

		:param filename: Should be either a string containing a path to a file to open, or an already-open
						 sqlite3.Connection object. If the latter, the connection will not be closed on destruction.
					 	 filename can also be a sqlite3.Cursor object, in which case it will simply be returned.
		"""
		self.filename = filename
		self.opened_here = False
		self.database = None

	def __enter__(self):
		"""
		Opens the connection to the file and returns an active cursor.
		:return:
		"""
		if isinstance(self.filename, sqlite3.Connection):
			self.database = self.filename
		elif isinstance(self.filename, sqlite3.Cursor):
			return self.filename
		else:
			self.opened_here = True
			try:
				self.database = sqlite3.connect(self.filename)
			except sqlite3.OperationalError as soe:
				self.opened_here = False
				raise soe
		return self.database.cursor()

	def __exit__(self, *args):
		if self.opened_here:
			self.database.commit()
			self.database.close()
			self.database = None



def check_sql_table_exist(database, table_name):
	"""
	Checks that the supplied table exists in the supplied database.

	:param database: the database to check existence in
	:param table_name: the table name to check for

	:return: true if the table exists
	:rtype: bool
	"""
	with SQLiteConnection(database) as cursor:
		table_names = [x[0] for x in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
	return table_name in table_names

def check_sql_column_exists(database, table_name, column_name):
	"""
	Checks if the column exists in the database.

	:param database: the database to check existence in
	:param table_name: the table name to check within
	:param column_name: the column name to check for

	:return: true if the column exists.
	:rtype: bool
	"""
	with SQLiteConnection(database) as cursor:
		c = [i[1] for i in cursor.execute('PRAGMA table_info({})'.format(table_name)) if i[1] == column_name]
		return len(c) != 0

def fetch_table_from_sql(database, table_name):
	"""
	Returns a list of the data contained by the provided table in the database.

	:raises sqlite3.OperationalError: if the table is not contained in the database (protects SQL injections).

	:param database: the database to obtain from
	:param table_name: the table name to fetch data from
	:return: a list of lists, containing all data within the provided table in the database
	"""
	try:
		with SQLiteConnection(database) as c:
			if not check_sql_table_exist(c, table_name):
				raise sqlite3.OperationalError("Table {} does not exist in database.".format(table_name))
			c.execute("SELECT * FROM {}".format(table_name))
			return [list(x) for x in c.fetchall()]
	except sqlite3.OperationalError as soe:
		raise IOError("Cannot fetch {} from database {}: {}".format(table_name, database, soe))



def sql_get_max_from_column(database, table_name, column_name):
	"""
	Returns the maximum value from the specified column.

	:param database: the database to fetch from
	:param table_name: the table name to attain
	:param column_name:
	:return:
	"""
	with SQLiteConnection(database) as cursor:
		if not check_sql_table_exist(cursor, table_name):
			raise sqlite3.OperationalError("Table {} does not exist in database.".format(table_name))
		if not check_sql_column_exists(cursor, table_name, column_name):
			raise sqlite3.OperationalError("Column {} does not exist in {}.".format(column_name, table_name))
		ex_str = "SELECT max({}) FROM {}".format(column_name, table_name)
		cursor.execute(ex_str)
		return cursor.fetchone()[0]
