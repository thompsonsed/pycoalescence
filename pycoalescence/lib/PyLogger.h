// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file PyLogger.h
 * @brief Routines for controlling logger from C++ to Python.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */

#ifndef NECSIM_PYLOGGER_H
#define NECSIM_PYLOGGER_H
#ifndef PYTHON_COMPILE
#define PYTHON_COMPILE
#endif
#include <Python.h>
#include <string>
#include <sstream>
#include "necsim/Logger.h"

class PyLogger : public Logger
{
private:
	PyObject * py_logger;
	PyObject * py_log_function;
	bool logger_set;
	bool log_function_set;

public:
	/**
	 * @brief Default constructor for PyLogger.
	 */
	PyLogger() :  Logger::Logger(), py_logger(nullptr), py_log_function(nullptr), logger_set(false),
				  log_function_set(false)
	{

	}

	/**
	 * @brief Safely deletes the Python references.
	 */
	~PyLogger() override
	{
		Py_CLEAR(py_logger);
		Py_CLEAR(py_log_function);
	}

	/**
	 * @brief Sets the logger object
	 * @param logger the log object that is written out to
	 */
	void setLogger(PyObject * logger);

	/**
	* @brief Sets the logger function
	* @param log_function the function that will be used for writing out logs
	*/
	void setLogFunction(PyObject * log_function);

	/**
	 * @brief Checks if the logger has been setup.
	 * @return true if the logger object and the logger function have been set
	 */
	bool isSetup();

	/**
	 * @brief Writes a message to the log object with level 20.
	 * @param message the message to write out
	 */
	void writeInfo(string message) override;

	/**
	 * @brief Writes a message to the log object with level 30.
	 * @param message the message to write out
	 */
	void writeWarning(string message) override;

	/**
	 * @brief Writes a message to the log object with level 40.
	 * @param message the message to write out
	 */
	void writeError(string message) override;

	/**
	 * @brief Writes a message to the log object with level 50.
	 * @param message the message to write out
	 */
	void writeCritical(string message) override;
//#ifdef DEBUG
	/**
	 * @brief Writes a message to the log object with the supplied leve
	 * @param level the logging level to write out at
	 * @param message the message to write out
	 */
	void write(const int &level, string message);

	/**
	 * @brief Writes a message to the log object with the supplied leve
	 * @param level the logging level to write out at
	 * @param message the message to write out
	 */
	void write(const int &level, stringstream &message);
//#endif // DEBUG
};
#endif // NECSIM_PYLOGGER_H
