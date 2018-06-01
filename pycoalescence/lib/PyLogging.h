//This file is part of NECSim project which is released under MIT license.
//See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.

/**
 * @author Sam Thompson
 * @file PyLogging.h
 * @brief Routines for writing to python logging module.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */
#ifndef PYLOGGING_H
#define PYLOGGING_H
#include "Python.h"
#include <string>
#include "necsim/LogFile.h"
#include "PyLogger.h"

/**
 * @brief Generates the global logger object and adds the logger and log functions to the python logger.
 *
 * Each call to getGlobalLogger should be matched by a call to removeGlobalLogger
 * @param logger the python logger object to use
 * @param log_function the python logging function to use
 * @return the global logger object as a pointer.
 */
PyLogger * getGlobalLogger(PyObject * logger, PyObject * log_function);

/**
 * @brief Safely deletes the global logger object.
 */
void removeGlobalLogger();
#endif // PYLOGGING_H
