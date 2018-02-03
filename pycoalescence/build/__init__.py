
from __future__ import absolute_import
import warnings
try:
	from .necsimlinker import necsimmodule, Dispersal, applyspecmodule
except ImportError as ie:
	try:
		from necsimlinker import necsimmodule, Dispersal, applyspecmodule
	except ImportError as ie:
		# Create a dummy NECSim object so readthedocs won't fail to build documentation without compiling the program
		necsimmodule = None
		Dispersal = None
		warnings.warn("Could not import NECSim cpp module: {}".format(str(ie)))