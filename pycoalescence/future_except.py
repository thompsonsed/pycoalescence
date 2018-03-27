"""
Contains compatibility imports for Python 2.x.
"""
try:
	FileExistsError = FileExistsError
	FileNotFoundError = FileNotFoundError
except NameError:
	class FileExistsError(IOError):
		pass

	class FileNotFoundError(IOError):
		pass