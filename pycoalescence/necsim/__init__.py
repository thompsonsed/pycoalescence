"""
This module contains the c++ shared object files which are accessed via python.
"""
from __future__ import absolute_import
try:
	try:
		from . import libnecsim
	except ImportError:
		import libnecsim
	NECSimError = libnecsim.NECSimError
except ImportError as ie:
	import logging
	logging.warning("Cannot import libnecsim: {}".format(ie))
	libnecsim = None
	NECSimError = None
