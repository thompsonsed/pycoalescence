"""
This module contains the c++ shared object files which are accessed via python. The modfolders allow for two python
installs (2.x and 3.x) to be installed locally simultaneously, which is convenient for testing and debugging purposes.
"""
from __future__ import absolute_import
import sys
if sys.version[0] == '3':
	modfolder = "sharedpy3"
else:
	modfolder = "sharedpy2"

import importlib
# try:
necsimmodule = importlib.import_module(".{}.necsimmodule".format(modfolder), package="pycoalescence.build")
NECSimError = necsimmodule.NECSimError