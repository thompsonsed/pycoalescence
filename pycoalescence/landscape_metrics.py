"""
Calculates landscape-level metrics, including mean distance to nearest-neighbour for each habitat cell and clumpiness.
"""
import logging

from .system_operations import write_to_log
from .build import LandscapeMetricsLib
from .map import Map

class LandscapeMetrics(Map):
	"""
	Calculates the mean nearest-neighbour for cells across a landscape. See :ref:`here <landscape_metrics>` for details.
	"""

	def __init__(self, file=None, logging_level=logging.WARNING):
		"""
		Initialises the loggers and default map variables.
		:param file: the path to the map file
		:param logging_level: the logging level to report at
		"""
		Map.__init__(self, file)
		self.logger = logging.Logger("mnncalculatorlogger")
		self._create_logger(logging_level=logging_level)

	def _setup(self):
		"""
		Sets the loggers
		"""
		LandscapeMetricsLib.set_logger(self.logger)
		LandscapeMetricsLib.set_log_function(write_to_log)

	def get_mnn(self):
		"""
		Calculates the mean nearest-neighbour for cells across a landscape. See :ref:`here <landscape_metrics_mnn>` for
		details.

		:return: the mean distance to the nearest neighbour of a cell.

		:rtype: float
		"""
		self._setup()
		return LandscapeMetricsLib.calc_mean_distance(self.file_name)


	def get_clumpiness(self):
		"""
		Calculates the clumpiness metric for the landscape, a measure of how spread out the points are across the
		landscape. See :ref:`here <landscape_metrics_clumpy>` for details.

		:return: the CLUMPY metric

		:rtype: float
		"""
		self._setup()
		return LandscapeMetricsLib.calc_clumpiness(self.file_name)



