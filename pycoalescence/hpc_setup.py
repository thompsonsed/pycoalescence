"""
Compile **necsim** with a number of intel compiler optimisations for running on high-performance computing systems.
"""

from __future__ import absolute_import

import logging

try:  # pragma: no cover
    from .installer import Installer
except (ImportError, SystemError, ValueError):  # pragma: no cover
    from installer import Installer


def build_hpc():  # pragma: no cover
    """
    Compiles necsim with the flags for optimisation on high-performance intel-based systems. On systems with a global
    variable containing INTEL_LICENSE_FILE, most of these options will be turned on automatically.

    :rtype: None
    """
    from distutils.dist import Distribution

    dist = Distribution()
    installer = Installer(dist)

    installer.configure_and_compile(argv=["--with-hpc", "--with-verbose"], logging_level=logging.INFO)


if __name__ == "__main__":  # pragma: no cover
    build_hpc()
