"""
Compiles NECSim for several simulation scenarios and tests the output to make sure simulation results are as expected.
Also performs limited tests of the PyCoalescence setup routines.

.. note:: If test_install.py has not been run before, compilation may take a while, depending on your system, as it
   compiles NECSim for several different options.
"""
from __future__ import absolute_import

import argparse
import inspect
import logging
import sys
import unittest

import os

sys.path.append("../")

# Conditional import for python 2 being stupid
from system_operations import set_logging_method
import pycoalescence.tests.setup
if sys.version_info[0] is not 3:
	class FileExistsError(IOError):
		pass

try:
	import sqlite3
except ImportError:
	import sqlite as sqlite3


def main(verbosity=1):
	"""
	Set the logging method, run the program compilation (if required) and test the install.

	:param verbosity: the level of information to display from the unittest module

	.. note:: The working directory is changed to the package install location for the duration of this execution.
	"""
	set_logging_method(logging_level=logging.CRITICAL, output=None)
	test_loader = unittest.TestLoader().discover("tests")
	unittest.TextTestRunner(verbosity=verbosity).run(test_loader)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Test pycoalescence functions correctly")
	parser.add_argument('--quick', help='Run only quick tests.', action='store_true', default=False)
	parser.add_argument('-v', '--verbose', help='Use verbose mode.', action='store_true', default=False)
	args, unknown = parser.parse_known_args()
	if args.quick:
		pycoalescence.tests.setup.quick_test = True
		sys.argv.remove('--quick')
	else:
		pycoalescence.tests.setup.quick_test = False
	if args.verbose:
		main(2)
	else:
		main()
