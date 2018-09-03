"""
Compile **necsim** with a number of intel compiler optimisations for running on high-performance computing systems.
"""
from __future__ import absolute_import
import logging

try:
	from .installer import Installer
except (ImportError, SystemError, ValueError):
	from installer import Installer


def build_hpc():
	"""
	Compiles NECSim with the ``--with-hpc`` and ``--with-verbose`` flags, which adds extra support for intel compilers
	and provides a selection of optimisation flags for high-performance systems.
	:return:
	"""
	from distutils.dist import Distribution
	dist = Distribution()
	installer = Installer(dist)

	installer.configure_and_compile(argv=["--with-hpc", "--with-verbose"], logging_level=logging.INFO)


if __name__ == "__main__":
	build_hpc()
