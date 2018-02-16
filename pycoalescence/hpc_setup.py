"""
Sets up pycoalescence for usage on HPC systems, including providing intel compiler flags for optimisation, and specific
verbose patterns to add support for certain types of file systems.
"""
from __future__ import absolute_import
import logging

try:
	from .setup import configure_and_compile
except (ImportError, SystemError, ValueError):
	from setup import configure_and_compile


def build_hpc():
	"""
	Compiles NECSim with the ``--with-hpc`` and ``--with-verbose`` flags, which adds extra support for intel compilers
	and provides a selection of optimisation flags for high-performance systems.
	:return:
	"""
	configure_and_compile(argv=["--with-hpc", "--with-verbose"], logging_level=logging.INFO)


if __name__ == "__main__":
	build_hpc()
