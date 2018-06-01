
.. _program_listing_file_PyLogger.h:

Program Listing for File PyLogger.h
===================================

- Return to documentation for :ref:`file_PyLogger.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
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
       PyLogger() :  Logger::Logger(), py_logger(nullptr), py_log_function(nullptr), logger_set(false),
                     log_function_set(false)
       {
   
       }
   
       ~PyLogger() override
       {
           Py_CLEAR(py_logger);
           Py_CLEAR(py_log_function);
       }
   
       void setLogger(PyObject * logger);
   
       void setLogFunction(PyObject * log_function);
   
       void writeInfo(string message) override;
   
       void writeWarning(string message) override;
   
       void writeError(string message) override;
   
       void writeCritical(string message) override;
   //#ifdef DEBUG
       void write(const int &level, string message);
   
       void write(const int &level, stringstream &message);
   //#endif // DEBUG
   };
   #endif // NECSIM_PYLOGGER_H
