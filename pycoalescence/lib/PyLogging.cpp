//This file is part of necsim project which is released under MIT license.
//See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
/**
 * @author Sam Thompson
 * @file PyLogging.cpp
 * @brief Routines for writing to Python logging module.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */
#ifndef PYTHON_COMPILE
#define PYTHON_COMPILE

#include <Python.h>
#include <string>
#include <sstream>
#include "necsim/Logger.h"

#include "PyLogger.h"
#include "PyLogging.h"

PyLogger *pyLogger = nullptr;

PyLogger *getGlobalLogger(PyObject *logger, PyObject *log_function)
{
	if(pyLogger != nullptr)
	{
		removeGlobalLogger();
	}
	pyLogger = new PyLogger();
	if(logger == nullptr || log_function == nullptr)
	{
		string errmsg = "logger or log_function is nullptr when attempting to getGlobalLogger(). "
				  "Please report this bug.";
		PyErr_SetString(PyExc_SystemError, errmsg.c_str());
		return nullptr;
	}
	pyLogger->setLogger(logger);
	pyLogger->setLogFunction(log_function);
	return pyLogger;
}

void removeGlobalLogger()
{
	if(pyLogger != nullptr)
	{
		delete pyLogger;
	}
	pyLogger = nullptr;
}

#endif
