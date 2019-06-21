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

class CustomExtension(Extension):
	def __init__(self, name, sourcedir=''):
		Extension.__init__(self, name, sources=[])
		self.sourcedir = os.path.abspath(sourcedir)


with open("README.rst") as f:
	long_description = f.read()


setup(name='pycoalescence',
	  version=p_version,
	  description='A spatially explicit neutral ecology simulator using coalescence methods',
	  author='Sam Thompson',
	  author_email='samuel.thompson14@imperial.ac.uk',
	  url='http://pycoalescence.readthedocs.io/',
	  long_description=long_description,
	  long_description_content_type="text/x-rst",
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
				   'Programming Language :: Python :: 3.7',
				   'Programming Language :: Python :: 3',
				   'Programming Language :: Python :: Implementation :: CPython',
				   'Topic :: Scientific/Engineering',
				   'Intended Audience :: Science/Research',
				   'Natural Language :: English',],
	  zip_safe=False,
	  keywords='neutral simulation ecology spatially explicit',
	  install_requires=['GDAL>=1.11.2', 'numpy', "pandas", "configparser;python_version < '3.0'"],
	  extras_require={
		  'scipy': ['scipy>=0.12.0'],
		  'plotting': ['matplotlib']}
      )

