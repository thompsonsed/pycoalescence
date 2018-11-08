"""
Calculates landscape-level metrics, including mean distance to nearest-neighbour for each habitat cell and clumpiness.
"""
import logging
try:
	from .necsim import libnecsim
	from .map import Map
	from .system_operations import write_to_log
except ImportError:
	from necsim import libnecsim
	from map import Map
	from system_operations import write_to_log


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
		self.logger = logging.Logger("pycoalescence.landscapemetric")
		self._create_logger(logging_level=logging_level)
		self.c_LM_calc = libnecsim.CLandscapeMetricsCalculator(self.logger, write_to_log)

	def __del__(self):
		"""Safely destroy the C++ objects."""
		self.c_LM_calc = None
		Map.__del__(self)

	def get_mnn(self):
		"""
		Calculates the mean nearest-neighbour for cells across a landscape. See :ref:`here <landscape_metrics_mnn>` for
		details.

		:return: the mean distance to the nearest neighbour of a cell.

		:rtype: float
		"""
		self.c_LM_calc.import_map(self.file_name)
		return self.c_LM_calc.calculate_MNN()

	def get_clumpiness(self):
		"""
		Calculates the clumpiness metric for the landscape, a measure of how spread out the points are across the
		landscape. See :ref:`here <landscape_metrics_clumpy>` for details.

		:return: the CLUMPY metric

		:rtype: float
		"""
		self.c_LM_calc.import_map(self.file_name)
		return self.c_LM_calc.calculate_CLUMPY()
