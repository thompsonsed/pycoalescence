"""
pycoalescence provides the facilities for running spatially explicit neutral coalescence ecological simulations
and performing basic analysis of the simulation outputs. The program requires necsim to function properly.

"""
__version__ = "1.2.7a38"

import logging

__author__ = "Samuel Thompson"
__copyright__ = "Copyright 2016, pycoalescence"
__credits__ = ["Samuel Thompson"]
__license__ = "MIT"
__maintainer__ = "Samuel Thompson"
__email__ = "thompsonsed@gmail.com"

try:
    from pycoalescence.simulation import Simulation, Map
    from pycoalescence.coalescence_tree import CoalescenceTree
    from pycoalescence.system_operations import set_logging_method
    from pycoalescence.merger import Merger
    from pycoalescence.dispersal_simulation import DispersalSimulation
    from pycoalescence.landscape_metrics import LandscapeMetrics

    # Support for no scipy installed
    try:
        from pycoalescence.fragments import FragmentedLandscape
    except ImportError as ie:  # pragma: no cover
        logging.warning("Cannot generate fragmented landscapes: {}".format(ie))
except ImportError as ie:  # pragma: no cover
    logging.warning(ie)
    logging.warning("Cannot import package - are you sure that it has been installed correctly?")
