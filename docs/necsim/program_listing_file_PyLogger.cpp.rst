
.. _program_listing_file_PyLogger.cpp:

Program Listing for File PyLogger.cpp
=====================================

- Return to documentation for :ref:`file_PyLogger.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #include "necsim/CustomExceptions.h"
   #include "necsim/Logger.h"
   #include "PyLogger.h"
   
   
   extern PyLogger * pyLogger;
   
   
   void PyLogger::setLogger(PyObject *logger)
   {
       if(logger == nullptr)
       {
           throw FatalException("Cannot set logger object to null pointer.");
       }
       Py_XINCREF(logger);
       Py_XDECREF(py_logger);
       py_logger = logger;
       logger_set = true;
   }
   
   void PyLogger::setLogFunction(PyObject *log_function)
   {
       if(log_function == nullptr)
       {
           throw FatalException("Cannot set log function object to null pointer.");
       }
       Py_XINCREF(log_function);
       Py_XDECREF(py_log_function);
       py_log_function = log_function;
       log_function_set = true;
   
   }
   
   void PyLogger::writeInfo(string message)
   {
   
       write(20, std::move(message));
   }
   
   void PyLogger::writeWarning(string message)
   {
       write(30, std::move(message));
   }
   
   void PyLogger::writeError(string message)
   {
       write(40, std::move(message));
   }
   
   void PyLogger::writeCritical(string message)
   {
       write(50, std::move(message));
   }
   //#ifdef DEBUG
   
   void PyLogger::write(const int &level, string message)
   {
       
       if(PyErr_CheckSignals()!=0)
       {
           throw runtime_error("Keyboard interrupt detected.");
       }
       PyObject *arglist, *res;
   #ifdef DEBUG
       writeLog(level, message);
       if(!log_function_set)
       {
           throw runtime_error(
                   "Logger object has not been set. Check set_logging_function() has been called in python");
       }
       if(py_logger == nullptr)
       {
           throw invalid_argument("Logger object has been deferenced, please report this bug!");
       }
   #endif // DEBUG
       const char * msg = const_cast<char *>(message.c_str());
       arglist = Py_BuildValue("isO", level, msg, py_logger);
       // Throw different errors if logger function has not been set
   #ifdef DEBUG
       if(!logger_set)
       {
           Py_XDECREF(arglist);
           throw runtime_error(
                   "Logging function has not been set. Check set_logging_function() has been called in python");
       }
       if(py_log_function == nullptr)
       {
           Py_XDECREF(arglist);
           throw invalid_argument("Logging function has been dereferenced, please report this bug!");
       }
   #endif // DEBUG
       res = PyObject_CallObject(py_log_function, arglist);
       Py_DECREF(arglist);
       Py_XDECREF(res);
   }
   
   void PyLogger::write(const int &level, stringstream &message)
   {
       write(level, message.str());
   }
   
   
   //#endif // DEBUG
   
   void writeInfo(string message)
   {
       pyLogger->writeInfo(message);
   }
   
   void writeWarning(string message)
   {
       pyLogger->writeWarning(message);
   }
   
   void writeError(string message)
   {
       pyLogger->writeError(message);
   }
   
   void writeCritical(string message)
   {
       pyLogger->writeCritical(message);
   }
   #ifdef DEBUG
   void writeLog(const int &level, string message)
   {
       pyLogger->writeLog(level, message);
   }
   
   void writeLog(const int &level, stringstream &message)
   {
       writeLog(level, message.str());
   }
   #endif // DEBUG
   
