
"""
File for importing the necsim and dispersal modules from the shared object file, with checks for different python versions.
"""
from __future__ import absolute_import
import sys

# Make it easier to have two shared objects at the same time - one for python2, one for python3
# Attempt to solve problems of the shared libraries not being in the sys.path
# I think this is probably an absolutely terrible way of doing things! Would not recommend!
# But don't understand properly how to get it to work otherwise.
if sys.version[0] == '3':
	modfolder = "sharedpy3"
else:
	modfolder = "sharedpy2"
# Now actually try the import
if modfolder is 'sharedpy3':
	try:
		from sharedpy3 import necsimmodule
		from sharedpy3 import dispersalmodule as Dispersal
		from sharedpy3 import applyspecmodule
		from sharedpy3 import landscapemetricsmodule as LandscapeMetricsLib
	except ImportError:
		from .sharedpy3 import necsimmodule
		from .sharedpy3 import dispersalmodule as Dispersal
		from .sharedpy3 import applyspecmodule
		from .sharedpy3 import landscapemetricsmodule as LandscapeMetricsLib
elif modfolder is 'sharedpy2':
	try:
		from .sharedpy2 import necsimmodule
		from .sharedpy2 import dispersalmodule as Dispersal
		from .sharedpy2 import applyspecmodule
		from .sharedpy2 import landscapemetricsmodule as LandscapeMetricsLib
	except ImportError:
		from sharedpy2 import necsimmodule
		from sharedpy2 import dispersalmodule as Dispersal
		from sharedpy2 import applyspecmodule
		from sharedpy2 import landscapemetricsmodule as LandscapeMetricsLib

