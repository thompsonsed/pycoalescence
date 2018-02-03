"""
Sets up the NECSim executables. It configures the install by detecting system components and compiles the ``c++`` files,
if possible. Command line flags can be provided (see :ref:`Compilation Options <sec Compilation Options>` for more
information) to modify the install.
"""

from __future__ import print_function, absolute_import  # Only Python 2.x
import sys
import subprocess
import os
import shutil
import warnings
import logging
import re
from distutils import sysconfig
import platform

# Import system operations for subprocess executation and log file handling

try:
	from .system_operations import execute_log_info, set_logging_method, mod_directory, execute_silent
except (ImportError, SystemError, ValueError):
	from system_operations import execute_log_info, set_logging_method, mod_directory, execute_silent



def do_compile():
	"""
	Compiles the c++ NECSim program by running make. This changes the working directory to wherever the module has been
	installed for the subprocess call.
	"""
	# Check that the make file exists
	if os.path.exists(os.path.join(mod_directory, "lib/")):
		try:
			execute_silent(["make", "depend"], cwd=os.path.join(mod_directory, "lib/"))
			execute_log_info(["make", "all"], cwd=os.path.join(mod_directory, "lib/"))
			logging.info("Compilation exited successfully.")
		except subprocess.CalledProcessError as cpe:
			warnings.warn(str(cpe))
			warnings.warn("Compilation attempted, but error thrown.")
	else:
		raise IOError("C++ library does not exist! Check relative file path")

def move_shared_object_file():
	"""
	Moves the shared object (.so) file to the build directory.
	:return:
	"""
	directory=os.path.join(mod_directory, "build")
	dirv = 'sharedpy'+sys.version[0]
	for file in ["necsimmodule.so", "dispersalmodule.so", "applyspecmodule.so"]:
		src = os.path.join(mod_directory, "lib", file)
		version_dir = os.path.join(directory, dirv)
		if not os.path.exists(src):
			raise IOError("Shared object file {} does not exists. Check installation was successful.".format(src))
		if not os.path.exists(directory):
			os.mkdir(directory)
		if not os.path.exists(version_dir):
			os.mkdir(version_dir)
		if not os.path.exists(os.path.join(version_dir, '__init__.py')):
			open(os.path.join(version_dir, '__init__.py'), 'a').close()
		dst = os.path.join(directory, dirv, file)
		if os.path.exists(dst):
			os.remove(dst)
		shutil.copy(src, dst)

def get_build_dir():
	"""
	Gets the build directory for this python version.
	:return: the build directory path for the current python interpreter
	"""
	directory = os.path.join(mod_directory, "build")
	return os.path.join(directory, 'sharedpy' + sys.version[0])


def move_executable(directory=os.path.join(mod_directory, "build/default/")):
	"""
	Moves the executable to the specified directory from within NECSim. Will always look for NECSim relative to the
	setup.py (so can be called from another module location).
	This allows for multiple compilation options with different versions stored in different folders.

	Throws an IOError when the NECSim executable is not found.

	:param directory: the directory to move the NECSim excecutable to.
	"""
	# Get absolute paths so that NECSim location is correct, and directory to move to can be supplied in relative format
	# from the parent file working directory.
	source_file = os.path.join(mod_directory, "lib/NECSim")
	source_file2 = os.path.join(mod_directory, "lib/SpeciationCounter")
	if not os.path.exists(source_file):
		raise IOError("Could not find " + source_file + ". Check program has been successfully compiled")
	if not os.path.exists(source_file2):
		raise IOError("Could not find " + source_file2 + ". Check program has been successfully compiled")
	if not os.path.exists(directory):
		dirname = os.path.dirname(directory)
		try:
			os.makedirs(dirname)
		except OSError:
			try:
				os.mkdir(dirname)
			except OSError as ose:
				warnings.warn("Could not create directory " + directory)
				raise ose
	os.rename(source_file, os.path.join(directory, "NECSim"))
	os.rename(source_file2, os.path.join(directory, "SpeciationCounter"))


def configure(opts=None):
	"""
	Runs ./configure --opts with the supplied options. This should create the makefile for compilation, otherwise a
	RuntimeError will be thrown.

	:param opts: a list of options to pass to the ./configure call
	"""
	if os.path.exists(os.path.join(mod_directory, "lib/configure")):
		try:
			if opts is None:
				execute_log_info(["./configure", "--with-verbose", "BUILDIR={}".format(get_build_dir()),  "OBJDIR=obj"],
								 cwd=os.path.join(mod_directory, "lib/"))
			else:
				command = ["./configure"]
				command.extend(opts)
				execute_log_info(command, cwd=os.path.join(mod_directory, "lib/"))
		except subprocess.CalledProcessError as cpe:
			cpe.message += "Configuration attempted, but error thrown"
			raise cpe
	else:
		raise RuntimeError("File src/configure does not exist. Check installation has been successful.")


def autoconf():
	"""
	Runs the `autoconf` bash function (assuming that autoconf is available) to create the `configure` executable.
	"""
	try:
		execute_log_info(["autoconf"], cwd=os.path.join(mod_directory, "lib/"))
	except (RuntimeError, subprocess.CalledProcessError) as cpe:
		warnings.warn("Could not run autoconf function to generate configure executable. "
					  "Please run this functionality manually if installation fails.")
		warnings.warn(str(cpe))


def clean():
	"""
	Runs make clean in the NECSim directory to wipe any previous potential compile attempts.
	"""
	try:
		execute_log_info(["make", "clean"], cwd=os.path.join(mod_directory, "lib/"))
	except subprocess.CalledProcessError as cpe:
		warnings.warn(cpe.message)
		raise RuntimeError("Make file has not been generated. Cannot clean.")

def get_compilation_flags(display_warnings=False):
	"""
	Generates the compilation flags for passing to ./configure.
	:param display_warnings: If true, runs with the -Wall flag for compilation (displaying all warnings). Default is False.

	:return: list of compilation flags.
	:rtype: list
	"""
	# Get the relevant flags that python was originally compiled with, to be passed to the c++ code.
	include =  str("CPPFLAGS=-I" + sysconfig.get_python_inc()).replace("\n", "")
	cflags = " " + sysconfig.get_config_var('CFLAGS')
	cflags = str(re.sub(r"-arch \b[^ ]*", "", cflags)).replace("\n", "") # remove any architecture flags
	pylib = str("-L" + sysconfig.get_python_lib(standard_lib=True) +
			  " -L" + sysconfig.get_config_var('DESTDIRS').replace(" ", " -L")).replace("\n", "")
	lib = "LIBS=-lpython"
	ldflags = re.sub(r"-arch \b[^ ]*[\ ]*", "", sysconfig.get_config_var("LDFLAGS"))
	ldflags = str("LDFLAGS=" + ldflags).replace("\n", " ")
	# Get the shared object platform-specific compilation flags.
	platform_so = "PLATFORM_SO="
	if platform.system() == "Linux":
		platform_so += "-shared"
	elif platform.system() == "Darwin":
		platform_so += "-dynamiclib"
	elif platform.system() == "Windows":
		raise SystemError("COMPILATION FAILURE: Windows is not yet supported. You must compile the libraries yourself.")
	else:
		logging.critical("OS not detected, compilation failures likely. Please report this error.")
	# Make sure that the linker directs to the correct python library (such as -lpython3.5m)
	# Eventually this will also detect if the install is for an anaconda distribution.
	if 'conda' not in sys.version and 'Continuum' not in sys.version:
		lib +=  sys.version[0:3]
		if 'm' in sysconfig.get_config_var('LIBRARY'):
			lib += 'm'
	else:
		cflags += " -DANACONDA" # TODO fix anaconda installation
	ldflags += " " + pylib
	pylib = "PYTHON_LIB=" + pylib
	call = [include + cflags, lib, ldflags, pylib, platform_so]
	# Remove the flags which would potentially cause unnecessary warnings to be thrown.
	# This can be disabled by passing display_warnings=True
	if not display_warnings:
		call = [re.sub('-Wstrict-prototypes|-Wno-unused-result|-Wunused-variable|-Wall', '', x) for x in call]
	return call

def run_configure(argv=[None], logging_level=logging.INFO, display_warnings=False):
	"""
	Configures the install for compile options provided via the command line, or with default options if no options exist.
	Running with ``-help`` or `-h` will display the compilation configurations called from ``./configure``.

	:param argv: the arguments to pass to configure script
	:param logging_level: the logging level to utilise (defaults to INFO).
	:param display_warnings: If true, runs with the -Wall flag for compilation (displaying all warnings). Default is False.
	"""
	call = get_compilation_flags(display_warnings=display_warnings)
	set_logging_method(logging_level=logging_level)
	autoconf()
	if len(argv) == 1:
		logging.info("No compile options provided, using defaults.")
		call.extend(["--with-verbose",  "OBJDIR=obj", "BUILDDIR={}".format(get_build_dir())])
	else:
		if argv[1] == "--h" or argv[1] == "-h" or argv[1] == "-help" or argv[1] == "--help":
			execute_log_info(["./configure", "--help"], cwd=os.path.join(mod_directory, "lib/"))
			exit(0)
		if isinstance(argv, str):
			call.append(argv[2])
		else:
			call.extend(argv[1:])
	logging.info(call)
	configure(opts=call)
	clean()

		# move_executable()

def backup_makefile():
	"""
	Copies the makefile to a saved folder so that even if the original is overwritten, the last successful
	compilation can be recorded.
	"""
	src = os.path.join("lib", "Makefile")
	dst = os.path.join("reference", "Makefile")
	if not os.path.exists(src):
		logging.error("Makefile does not exist at {}. Check successful compilation".format(src))
		return
	if os.path.exists(dst):
		os.remove(dst)
	shutil.copy2(src, dst)

def copy_makefile():
	"""
	Copies the backup makefile to the main directory, if it exists.
	Throws an IOError if no makefile is found.
	"""
	src = os.path.join("reference", "Makefile")
	dst = os.path.join("lib", "Makefile")
	if not os.path.exists(src):
		raise IOError("Cannot find backup Makefile, requires running of configuration scripts.")
	if os.path.exists(dst):
		os.remove(dst)
	shutil.copy2(src, dst)

def configure_and_compile(argv=[None], logging_level=logging.INFO):
	"""
	Calls the configure script, then runs the compilation.

	:param argv: the arguments to pass to configure script
	:param logging_level: the logging level to utilise (defaults to INFO).
	:rtype: None
	"""
	set_logging_method(logging_level=logging_level)
	display_warnings = "display_warnings=True" in argv
	run_configure(argv, logging_level=logging_level, display_warnings=display_warnings)
	do_compile()
	# move_shared_object_file()
	# move_executable()
	backup_makefile()

if __name__ == "__main__":
	fail = True
	if len(sys.argv) > 1:
		if sys.argv[1] == "compile" or sys.argv[1] == "-c" or sys.argv[1] == "-C":
			set_logging_method(logging_level=logging.INFO)
			copy_makefile()
			do_compile()
			# move_shared_object_file()
			# move_executable()
			fail= False
	if fail:
		configure_and_compile(sys.argv)
