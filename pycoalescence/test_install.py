"""
Compiles NECSim for several simulation scenarios and tests the output to make sure simulation results are as expected.
Also performs limited tests of the PyCoalescence setup routines.

.. note:: If test_install.py has not been run before, compilation may take a while, depending on your system, as it
   compiles NECSim for several different options.
"""
from __future__ import absolute_import

import inspect
import logging
import sys
import unittest

import os

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Conditional import for python 2 being stupid
from pycoalescence import set_logging_method
if sys.version_info[0] is not 3:
	class FileExistsError(IOError):
		pass

try:
	import sqlite3
except ImportError:
	import sqlite as sqlite3





def main():
	"""
	Set the logging method, run the program compilation (if required) and test the install.

	.. note:: The working directory is changed to the package install location for the duration of this execution.
	:return:
	"""
	set_logging_method(logging_level=logging.CRITICAL, output=None)
	test_loader = unittest.TestLoader().discover("tests")
	unittest.TextTestRunner(verbosity=1).run(test_loader)


if __name__ == "__main__":
	main()
