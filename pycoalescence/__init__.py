"""
PyCoalescence Package provides the facilities for running spatially-explicit neutral coalescence ecological simulations
and performing basic analysis of the simulation outputs. The program requires the NECSim program to function properly,
which will be included in the package at a later date.

"""
__version__ = '1.2.5'
# __all__ = ['coalescence', 'coal_analyse', 'system_operations', 'setup']
import logging
from pycoalescence.simulation import Simulation, Map
from pycoalescence.coalescence_tree import CoalescenceTree
from pycoalescence.setup import configure_and_compile as setup
from pycoalescence.system_operations import set_logging_method
from pycoalescence.merger import Merger
# Support for no scipy installed
try:
	from pycoalescence.fragments import FragmentedLandscape
except ImportError as ie:
	logging.warning("Cannot generate fragmented landscapes: {}".format(ie))


__author__ = "Samuel Thompson"
__copyright__ = "Copyright 2016, The pycoalescence Project"
__credits__ = ["Samuel Thompson"]
__license__ = "BSD-3"
__maintainer__ = "Samuel Thompson"
__email__ = "thompsonsed@gmail.com"