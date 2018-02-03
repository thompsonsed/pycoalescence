"""
Sets up the code for the hpc and moves the executable to the correct directory.
"""
from __future__ import absolute_import
import logging

try:
	from .setup import configure_and_compile
except (ImportError, SystemError, ValueError):
	from setup import configure_and_compile


def build_hpc():
	"""
	Compiles NECSim with the ``--with-hpc``, ``--with-verbose`` and ``--with-fat_tail_dispersal`` flags, and moves the
	executable to ../../Code/ relative to the file location.
	:return:
	"""
	configure_and_compile(argv=["--with-hpc", "--with-verbose"], logging_level=logging.INFO)


if __name__ == "__main__":
	build_hpc()
