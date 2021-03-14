"""When run from the command line, installs pycoalescence to the environment.

Run ```python setup.py build``` to build the C++ module.

Run ```python setup.py install``` to build the C++ module and install it to the environment.

Run ```python setup.py develop``` to install the package in development mode.
"""
import logging
import os
import pathlib
from typing import List

from setuptools import setup, Extension, find_packages

logging.basicConfig()
logging.getLogger().setLevel(logging.CRITICAL)
necsim_path = os.path.join("pycoalescence", "necsim", "libnecsim.so")
from Cython.Build import cythonize

if os.path.exists(necsim_path):
    os.remove(necsim_path)
try:
    from pycoalescence import __version__ as p_version
    from pycoalescence.installer import Installer, get_lib_and_gdal
except ImportError:
    # Means that one of the dependencies isn't installed properly - this is fine
    pass


with open("README.rst") as f:
    long_description = f.read()

excluded_files = ["main.cpp", "Logging.cpp"]
root_files = ["PyLogger.cpp", "PyLogging.cpp", "LandscapeMetricsCalculator.cpp"]
included_subfolders = ["eastl", "ghc"]


def get_all_sources(folder: pathlib.Path) -> List[pathlib.Path]:
    output = []
    for f_i in folder.iterdir():
        if f_i.is_file():
            if f_i.suffix == ".cpp" and f_i.name not in excluded_files:
                output.append(f_i)
        if f_i.is_dir() and f.name in included_subfolders:
            output.extend(get_all_sources(f_i))
    return output


_, gdal_inc_path, gdal_dir = get_lib_and_gdal()
extensions = [
    Extension(
        "pycoalescence.necsim.necsim",
        ["pycoalescence/necsim/necsim.pyx"]
        + [str(x) for x in get_all_sources(pathlib.Path("pycoalescence", "lib", "necsim"))]
        +[str(pathlib.Path("pycoalescence", "lib", x)) for x in root_files],
        include_dirs=[gdal_inc_path] if gdal_inc_path else None,
        libraries=["gdal"],
        library_dirs=[gdal_dir] if gdal_dir else None,
    )
]


setup(
    name="pycoalescence",
    version=p_version,
    description="A spatially explicit neutral ecology simulator using coalescence methods",
    author="Sam Thompson",
    author_email="thompsonsed@gmail.com",
    url="http://pycoalescence.readthedocs.io/",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    ext_modules=cythonize(extensions, language_level="3", nthreads=4),
    license="MIT",
    packages=find_packages(exclude=["*tests*", "docs"]),
    package_data={
        "pycoalescence": ["reference/*.json", "reference/*.json"],
        "": ["*.pyx", "*.pxd", "*.h", "*.c", "*.cpp", "*.hpp"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX",
        "Programming Language :: C++",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    zip_safe=False,
    keywords="neutral simulation ecology spatially explicit",
    install_requires=["GDAL>=1.11.2", "numpy", "cython", "pandas", "configparser;python_version < '3.0'"],
    extras_require={"scipy": ["scipy>=0.12.0"], "plotting": ["matplotlib"]},
    include_dirs=["pycoalescence/lib/"],
)
