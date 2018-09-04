"""
Basic system-level operations required for package functionality, including subprocess calls, logging methods and file
management.

The functions are contained here as they are required by many different modules. Note that logging will not raise an
exception if there has been no call to set_logging_method()

"""

import logging
import os
import subprocess
import sys

# Logging will not raise an exception if there has been no logging file set.
logging.raiseExceptions = True
logging_set = False
mod_directory = os.path.dirname(os.path.abspath(__file__))

try:
	from math import isclose
except ImportError:
	# Python 2 compatibility
	def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
		"""
		Checks if the two floats are close.

		:param float a: value 1
		:param float b: value 2
		:param float rel_tol: percentage relative to larger value
		:param float abs_tol: absolute value for similarity

		:return: true for significantly different a and b, false otherwise
		"""
		return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def check_parent(file_path):
	"""
	Checks if the parent file exists, and creates it if it doesn't.

	.. note:: if file_path is a directory, it will be created

	:param file_path: the file or directory to check if the parent exists

	:rtype: None
	"""
	if file_path:
		if not os.path.exists(file_path):
			if os.path.isdir(file_path):
				os.makedirs(file_path)
			else:
				par_dir = os.path.dirname(file_path)
				if not os.path.exists(par_dir) and par_dir != "":
					os.makedirs(os.path.dirname(file_path))
	else:
		raise ValueError("File path is None")


def check_file_exists(file_name):
	"""
	Checks that the specified filename exists, if it is not "null" or "none".

	:param file_name: file path to check for

	:return: None

	:raises: IOError if no file exists
	"""
	if file_name not in {"null", "none", None} and not os.path.exists(file_name):
		err = "Map file " + file_name + " does not exist. Check that this is an absolute path or disable map " \
										"file check"
		raise IOError(err)


def execute(cmd, silent=False, **kwargs):
	"""
	Calls the command using subprocess and yields the running output for printing to terminal. Any errors produced by
	subprocess call will be redirected to logging.warning() after the subprocess call is complete.

	:param cmd: the command to execute using subprocess.Popen()
	:param silent: if true, does not log any warnings

	:return a line from the execution output
	"""
	popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
							 universal_newlines=True, **kwargs)
	while True:
		output = popen.stdout.readline()
		if output == '' and popen.poll() is not None:
			break
		if output:
			yield output
	error_logs = []
	for stderr_line in iter(popen.stderr.readline, ""):
		error_logs.append(stderr_line)
	popen.stdout.close()
	popen.stderr.close()
	popen.wait()
	if popen.returncode != 0:
		for log in error_logs:
			logging.critical(log)
		raise RuntimeError(error_logs[-1])
	else:
		if not silent:
			for log in error_logs:
				logging.warning(log)


def execute_log_info(cmd, **kwargs):
	"""
	Calls execute() with the supplied command and keyword arguments, and redirects stdout to the logging object.

	:param cmd: the command to execute using subprocess.Popen()
	:param kwargs: keyword arguments to be passed to subprocess.Popen()

	:return: None
	:rtype: None
	"""
	for line in execute(cmd, **kwargs):
		logging.info(line.strip("\n"))


def execute_silent(cmd, **kwargs):
	"""
	Calls execute() silently with the supplied command and keyword arguments.

	.. note:: If this function fails, no error will be thrown due to its silent nature, unless a full failure occurs.

	:param cmd: the command to execute using subprocess.Popen()
	:param kwargs: keyword arguments to be passed to subprocess.Popen()

	:return: None
	:rtype: None
	"""
	for _ in execute(cmd, silent=True, **kwargs):
		continue


def set_logging_method(logging_level=logging.INFO, output=None, **kwargs):
	"""
	Initiates the logging method.

	:param logging_level: the detail in logging output: can be one
	 				     of logging.INFO (default), logging.WARNING, logging.DEBUG, logging.ERROR or logging.CRITICAL
	:param output: the output logfile (or None to redirect to terminal via stdout)
	:param kwargs: additional arguments to pass to the logging.basicConfig() call

	:return: None
	"""
	if not logging_set:
		if output is None:
			logging.basicConfig(stream=sys.stdout, format='%(levelname)s:%(message)s', level=logging_level, **kwargs)
		else:
			logging.basicConfig(filename=output, format='%(levelname)s:%(message)s', level=logging_level, **kwargs)
		logging.captureWarnings(True)


def write_to_log(i, message, logger):
	"""
	Writes the message to the provided logger, at the provided level.

	This is used by **necsim** to access to logging module more easily.

	:param i: the level to log at (10: debug, 20: info, 30: warning, 40: error, 50: critical)
	:param message: the message to write to the logger.
	:param logger:

	:type i: int
	:type message: str
	:type logger: logging.Logger

	:rtype: None
	"""
	logger.log(level=i, msg=message)


def create_logger(logger, file=None, logging_level=logging.WARNING, **kwargs):
	"""
	Creates a logger object to be assigned to NECSim sims and dispersal tests.

	:param logger: the logger to alter
	:param file: the file to write out to, defaults to None, writing to terminal
	:param logging_level: the logging level to write out at (defaults to INFO)
	:param kwargs: optionally provide additional arguments for logging to

	:return:
	"""
	formatter = logging.Formatter('%(message)s')
	if file is None:
		sh = logging.StreamHandler(kwargs.get("stream", None))
	else:
		sh = logging.FileHandler(file)
	sh.setLevel(logging_level)
	sh.setFormatter(formatter)
	if sys.version[0] == "3":
		sh.terminator = ""
	logger.addHandler(sh)
	return logger


def elegant_pairing(x1, x2):
	"""
	A more elegant version of cantor pairing, which allows for storing of a greater number of digits without
	experiencing integer overflow issues.

	Cantor pairing assigns consecutive numbers to points along diagonals of a plane

	:param x1: the first number
	:param x2: the second number

	:return: a unique reference combining the two integers.
	"""
	if x1 > x2:
		return x1 ** 2 + x1 + x2
	return x2 ** 2 + x1


def cantor_pairing(x1, x2):
	"""
	Creates a unique integer from the two provided positive integers.

	Maps ZxZ -> N, so only relevant for positive numbers.
	For any A and B, generates C such that no D and E produce C unless D=A and B=E.

	Assigns consecutive numbers to points along diagonals of a plane

	.. note:
		For most use cases which are not performance-critical, :func:`~elegant_pairing` provides a more reliable outcome
		by reducing the size of the integers and therefore reducing the change of an integer overflow.

	:param x1: the first number
	:param x2: the second number

	:return: a unique reference combining the two integers
	"""
	return ((x1 + x2) * (x1 + x2 + 1) / 2) + x2
