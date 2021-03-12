"""
Contains the set-up and clean-up routines for running all tests, namely, deleting the output folder and moving the
log files to their original location.
"""

import logging
import os
import time
import unittest
from shutil import rmtree

import numpy as np

from pycoalescence import set_logging_method

try:
    quick_test = os.environ["quick_test"]
except KeyError:
    quick_test = None

try:
    bypass_gdal_warp = os.environ["bypass_gdal_warp"]
except KeyError:
    bypass_gdal_warp = None


def setUpAll():
    """Copies the log folder to a new folder so that the normal log folder can be removed entirely."""
    set_logging_method(logging_level=logging.CRITICAL)
    np.random.seed(0)
    if os.path.exists("output"):
        try:
            rmtree("output", True)
        except OSError:
            time.sleep(0.01)
            rmtree("output", True)
    if not os.path.exists("output"):
        os.mkdir("output")
    global log_path
    log_path = None
    if os.path.exists("Logs"):
        try:
            log_path = "Logs2"
            os.rename("Logs/", "Logs2")
        except OSError:
            try:
                log_path = "Logs_tmp"
                os.rename("Logs/", "Logs_tmp")
            except OSError as oe:
                logging.warning(str(oe))
                logging.warning("Cannot rename Log directory: deleting instead.")
                log_path = None


def tearDownAll():
    """
    Overrides the in-built behaviour for tearing down the module.

    Removes the output folder to clean up after testing.
    """
    rmtree("output", True)
    start = time.time()
    end = time.time()
    while os.path.exists("output") and end - start < 10:
        time.sleep(1)
        end = time.time()
    rmtree("Logs", True)
    rmtree("log", True)
    if log_path is not None:
        os.rename(log_path, "Logs")


def skipLongTest(f):
    """Decorator to skip a long test"""
    name = f.__name__
    if quick_test:

        @unittest.skip("skipping {} due to length...".format(name))
        def g():
            pass

        return g
    else:
        return f


def skipGdalWarp(f):
    """
    Decorator to skip a test containing gdal warp.

    Required for systems where gdal.Warp does not function properly
    """
    name = f.__name__
    if bypass_gdal_warp:

        @unittest.skip("skipping {} due to lack of gdal.Warp ...".format(name))
        def g():
            pass

        return g
    else:
        return f
