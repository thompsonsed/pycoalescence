"""When run from the command line, installs pycoalescence to the environment.

Run ```python setup.py build``` to build the C++ module.

Run ```python setup.py install``` to build the C++ module and install it to the environment.

Run ```python setup.py develop``` to install the package in development mode.
"""
import logging
import os

from setuptools import setup, Extension, find_packages

logging.basicConfig()
logging.getLogger().setLevel(logging.CRITICAL)
necsim_path = os.path.join("pycoalescence", "necsim", "libnecsim.so")
if os.path.exists(necsim_path):
	os.remove(necsim_path)
try:
	from pycoalescence import __version__ as p_version
	from pycoalescence.installer import Installer
except ImportError:
	# Means that one of the dependencies isn't installed properly - this is fine
	pass

# Get all the C++ source files
# py_src_files = [os.path.join("pycoalescence/lib", x) for x in os.listdir("pycoalescence/lib")
# 				if ".cpp" in x]
# necsim_src_files = [os.path.join("pycoalescence/lib/necsim", x) for x in os.listdir("pycoalescence/lib/necsim") if
# 					".cpp" in x]
# all_srcs = [x for x in necsim_src_files + py_src_files if "main.cpp" not in x]
#
# data_dir = "pycoalescence/reference"
#
# data_files = [os.path.join(data_dir, x) for x in os.listdir(data_dir) if x not in ['Makefile', '.DS_Store',
# 																				   'log_12_2.txt']]


class CustomExtension(Extension):
	def __init__(self, name, sourcedir=''):
		Extension.__init__(self, name, sources=[])
		self.sourcedir = os.path.abspath(sourcedir)


with open('README.rst') as f:
	readme = f.read()

# libnecsim = Extension('pycoalescence/lib',
# 					  sources=all_srcs,
# 					  include_dirs = ["pycoalescence/lib" "pycoalescence/lib/necsim"],
# 					  libraries=['gdal', 'boost_filesystem', 'boost_system', 'sqlite3'],
# 					  extra_compile_args=['-std=c++14'],
# 					  language="C++",  # generate C++ code
# 					  )

setup(name='pycoalescence',
	  version=p_version,
	  description='A spatially-explicit neutral ecology simulator using coalescence methods',
	  author='Sam Thompson',
	  author_email='samuel.thompson14@imperial.ac.uk',
	  url='http://pycoalescence.readthedocs.io/',
	  long_description=readme,
	  # ext_modules=[libnecsim],
	  ext_modules=[CustomExtension("libnecsim", os.path.join("pycoalescence","lib"))],
	  cmdclass=dict(build_ext=Installer),
	  license='MIT',
	  packages=find_packages(exclude=["*tests*", 'docs']),
	  package_data={
		  'pycoalescence': ['reference/*.json', 'reference/*.json'],
	  },
	  classifiers=['Development Status :: 4 - Beta',
				   'License :: OSI Approved :: MIT License',
				   'Operating System :: MacOS',
				   'Operating System :: MacOS :: MacOS X',
				   'Operating System :: Microsoft :: Windows :: Windows 10',
				   'Operating System :: POSIX',
				   'Programming Language :: C++',
				   'Programming Language :: Python :: 2.7',
				   'Programming Language :: Python :: 3.6',
				   'Programming Language :: Python :: 3',
				   'Programming Language :: Python :: Implementation :: CPython',
				   'Topic :: Scientific/Engineering',
				   'Intended Audience :: Science/Research',
				   'Natural Language :: English',
				   ],
	  zip_safe=False,
	  keywords='neutral simulation ecology spatially-explicit',
	  install_requires=['GDAL>=1.11.2', 'numpy'],
	  extras_require={
		  'scipy': ['scipy>=0.12.0'],
		  'plotting': ['matplotlib']
	  }
	  )
