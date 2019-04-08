"""Tests system_operations module for basic system routines."""
import logging
import os
import platform
import sys
import unittest

try:
    if sys.version_info[0] < 3:  # pragma: no cover
        raise ImportError()
    from io import StringIO
except ImportError:
    from io import BytesIO as StringIO

from pycoalescence.system_operations import (
    cantor_pairing,
    check_file_exists,
    check_parent,
    create_logger,
    elegant_pairing,
    execute,
    execute_log_info,
    execute_silent,
    set_logging_method,
)
from setup_tests import setUpAll, tearDownAll, skipLongTest


def setUpModule():
    """
    Creates the output directory and moves logging files
    """
    setUpAll()


def tearDownModule():
    """
    Removes the output directory
    """
    tearDownAll()


@skipLongTest
class TestCantorPairing(unittest.TestCase):
    """
    Tests that cantor pairing successfully creates unique numbers for a very large set of guilds and species
    """

    def testCantorCreatesUniqueIds(self):
        """
        Tests that the cantor pairing function creates unique ids for any given pair of numbers.
        Tests up to 1000 individuals in 1000 guilds
        """
        unique_ids = set()
        for species in range(1000):
            for guild in range(1000):
                ref = cantor_pairing(species, guild)
                self.assertNotIn(ref, unique_ids)
                unique_ids.add(ref)


class TestSystemOperations(unittest.TestCase):
    """
    Tests the functions associated with the system operations.
    """

    def testFileExistence(self):
        """
        Tests that the file existence checks work
        """
        check_file_exists("null")
        check_file_exists("sample/null.tif")
        check_file_exists("test_merger.py")

    def testFileExistenceErrors(self):
        """
        Tests that the correct errors are thrown when files don't exist.
        """
        with self.assertRaises(IOError):
            check_file_exists("not_a_file.tif")
        with self.assertRaises(IOError):
            check_file_exists("sample/not_a_file.tif")
        with self.assertRaises(IOError):
            check_file_exists("sample/also_notta_tile")

    def testCheckDirectory(self):
        """
        Verifies that the parent directory checks work correctly.
        """
        with self.assertRaises(ValueError):
            check_parent("")
        with self.assertRaises(ValueError):
            check_parent(None)
        check_parent("sample/not_here.tif")
        check_parent("output/create_me/create_me_as_well/")
        check_parent("output/create_me_too/file_here.tif")
        self.assertTrue(os.path.exists("output/create_me/"))
        self.assertTrue(os.path.exists("output/create_me/create_me_as_well"))
        self.assertTrue(os.path.exists("output/create_me_too/"))

    def testFileLogger(self):
        """
        Tests that the creation of a logger to file works correctly.
        """
        logger = logging.Logger("temp")
        file_name = "output/log.txt"
        create_logger(logger, file=file_name)
        logger.warning("test output")
        with open(file_name, "r") as f:
            s = f.readline()
            self.assertTrue("test output" in s)
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)

    def testCantorPairing(self):
        """
        Tests that the cantor pairing produces the expected result
        """
        self.assertEqual(cantor_pairing(10, 100), 6205)
        self.assertEqual(cantor_pairing(0, 1), 2)
        self.assertEqual(cantor_pairing(1, 0), 1)
        self.assertEqual(cantor_pairing(100000, 1000000), 605001550000)

    def testElegantPairing(self):
        """
        Tests the elegant pairing produces the expected output
        """
        self.assertEqual(elegant_pairing(10, 100), 10010)
        self.assertEqual(elegant_pairing(0, 1), 1)
        self.assertEqual(elegant_pairing(1, 0), 2)
        self.assertEqual(elegant_pairing(100000, 1000000), 1000000100000)

    @unittest.skipIf(platform.platform == "Windows", "Skipping tests not compatible with Windows.")
    def testExecute(self):
        """Tests that execution from command line produces the correct output."""
        all_lines = []
        for line in execute(["echo", "123"]):
            all_lines.append(line)
        self.assertEqual(["123\n"], all_lines)

    @unittest.skipIf(platform.platform == "Windows", "Skipping tests not compatible with Windows.")
    def testExecuteSilent(self):
        """Tests that silent execution from command line produces no output."""
        execute_silent(["echo", "123"])
        self.assertTrue(True)

    @unittest.skipIf(platform.platform == "Windows", "Skipping tests not compatible with Windows.")
    def testExecuteInfo(self):
        """Tests that logging info from command line output works as expected."""
        log_stream = StringIO()
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        execute_log_info(["echo", "123"])
        self.assertEqual("INFO:root:123\n", log_stream.getvalue())
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        set_logging_method()

    def testLoggingToFile(self):
        """Tests that logging the file works as intended."""
        log_file = os.path.join("output", "log_output1.txt")
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        set_logging_method(logging_level=logging.INFO, output=log_file)
        logging.info("Test1")
        logging.warning("Test2")
        with open(log_file, "r") as open_log_file:
            self.assertEqual("INFO:Test1\n", open_log_file.readline())
            self.assertEqual("WARNING:Test2\n", open_log_file.readline())
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        set_logging_method()

    def testLoggingToStream(self):
        """Tests that logging the stream works as intended."""
        log_stream = StringIO()
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        logger = create_logger(logging.Logger("temp"), logging_level=logging.INFO, stream=log_stream)
        logger.info("123\n")
        logger.warning("123w\n")
        self.assertEqual("123123w", log_stream.getvalue().replace("\n", ""))
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        set_logging_method()
