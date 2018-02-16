//This file is part of NECSim project which is released under BSD-3 license.
//See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.

/**
 * @author Sam Thompson
 * @file PyLogging.h
 * @brief Routines for writing to python logging module.
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 */
#ifndef PYLOGGING_H
#define PYLOGGING_H
#include "Python.h"
#include <string>
#include "necsim/LogFile.h"

extern PyObject * loggingmodule;
extern PyGILState_STATE gstate;
extern bool log_set;
extern bool logger_set;

static PyObject * call_logging = nullptr;


/**
 * @brief A python object container for the logger object for outputting using python's logging module.
 */
extern PyObject *logger;

/**
 * @brief Sets the logging function to the provided specification
 * @param dummy the dummy object
 * @param args the args provided (should be one callable logging function)
 */
PyObject * set_log_function(PyObject *dummy, PyObject *args);

/**
 * @brief Sets the logger to the inputted object
 * Saves the logger in loggingmodule
 * @param self required for python objects
 * @param args the logger to link for error outputting
 */
PyObject * set_logger(PyObject * self, PyObject * args);

/**
 * @brief Writes the message out to python's logging module at the level supplied.
 * @param level logging level to write out at (10: Debug, 20: Info, 30: Warning, 40: Error, 50: Critical)
 * @param message the string to write out
 * @return the python object as a result (should be Py_RETURN_NONE)
 */
void write_log(int level, char * message);

/**
 * @brief Writes the message out to python's logging module at the level supplied.
 * Overloaded version with support for normal strings.
 * @param level logging level to write out at (10: Debug, 20: Info, 30: Warning, 40: Error, 50: Critical)
 * @param message the string to write out
 * @return the python object as a result (should be Py_RETURN_NONE)
 */
void write_log(int level, string message);

#endif // PYLOGGING_H
