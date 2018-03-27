"""
Contains the set-up and clean-up routines for running all tests, namely, deleting the output folder and moving the
log files to their original location.
"""

import logging
import os
from shutil import rmtree
import numpy as np
from pycoalescence import set_logging_method

def setUpAll():
	"""
	Copies the log folder to a new folder so that the normal log folder can be removed entirely.
	"""
	set_logging_method(logging_level=logging.CRITICAL)
	np.random.seed(0)
	if os.path.exists("output"):
		rmtree("output")
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
	Overrides the in-built behaviour for tearing down the module. Removes the output folder to clean up after testing.
	"""
	rmtree("output", True)
	if os.path.exists("output"):
		for file in os.listdir("output"):
			p = os.path.join("output", file)
			if os.path.isdir(p):
				rmtree(p, ignore_errors=True)
			else:
				os.remove(p)
		try:
			os.removedirs("output")
		except OSError:
			raise OSError("Output not deleted")
	rmtree("Logs", True)
	rmtree("log", True)
	if log_path is not None:
		os.rename(log_path, "Logs")