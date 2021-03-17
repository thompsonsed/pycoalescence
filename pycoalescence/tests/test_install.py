"""
Compiles necsim for several simulation scenarios and tests the output to make sure simulation results are as expected.
Also performs limited tests of the pycoalescence setup routines.

.. note:: If test_install.py has not been run before, compilation may take a while, depending on your system, as it
   compiles NECSim for several different options.
"""
from __future__ import absolute_import

import argparse
import logging
import sys
import unittest

try:
    import sqlite3
except ImportError:
    import sqlite as sqlite3

try:
    import pycoalescence
    from pycoalescence.system_operations import set_logging_method
    import setup_tests
except ImportError as ie:
    logging.warning("Cannot import pycoalescence globally, check package is properly installed: {}.".format(ie))
    logging.warning("Continuing with local package")
    sys.path.append("../")

    # Conditional import for Python 2 being stupid
    from system_operations import set_logging_method
    import setup_tests
if sys.version_info[0] != 3:

    class FileExistsError(IOError):
        pass


def main(verbosity=1):
    """
    Set the logging method, run the program compilation (if required) and test the install.

    :param verbosity: the level of information to display from the unittest module

    .. note:: The working directory is changed to the package install location for the duration of this execution.
    """
    set_logging_method(logging_level=logging.CRITICAL, output=None)
    test_loader = unittest.TestLoader().discover(".")
    unittest.TextTestRunner(verbosity=verbosity).run(test_loader)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test pycoalescence functions correctly")
    parser.add_argument("--quick", help="Run only quick tests.", action="store_true", default=False)
    parser.add_argument("--bypass_gdal_warp", help="Bypass gdal.Warp.", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Use verbose mode.", action="store_true", default=False)
    args, unknown = parser.parse_known_args()
    if args.quick:
        setup_tests.quick_test = True
        sys.argv.remove("--quick")
    else:
        setup_tests.quick_test = False
    if args.bypass_gdal_warp:
        setup_tests.bypass_gdal_warp = True
        sys.argv.remove("--bypass_gdal_warp")
    else:
        setup_tests.bypass_gdal_warp = False
    if args.verbose:
        main(2)
    else:
        main()
