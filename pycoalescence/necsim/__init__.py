"""
This module contains the c++ shared object files which are accessed via python.
"""
from __future__ import absolute_import
try:
	try:
		from . import necsimmodule
	except ImportError:
		import necsimmodule
	NECSimError = necsimmodule.NECSimError
except ImportError as ie:
	import logging
	logging.warning("Cannot import necsimmodule: {}".format(ie))
	necsimmodule = None
	NECSimError = None
