"""
Contains compatibility imports for Python 2.x.
"""

try:  # pragma: no cover
    FileExistsError = FileExistsError
    FileNotFoundError = FileNotFoundError
except NameError:  # pragma: no cover

    class FileExistsError(IOError):
        pass

    class FileNotFoundError(IOError):
        pass
