
.. _program_listing_file_PyLogging.cpp:

Program Listing for File PyLogging.cpp
======================================

- Return to documentation for :ref:`file_PyLogging.cpp`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef PYTHON_COMPILE
   #define PYTHON_COMPILE
   #endif
   #include <Python.h>
   #include <string>
   #include <sstream>
   #include "necsim/Logging.h"
   #include "PyLogging.h"
   
   void writeInfo(string message)
   {
   
       write_log(20, std::move(message));
   }
   
   void writeWarning(string message)
   {
       write_log(30, std::move(message));
   }
   
   void writeError(string message)
   {
       write_log(40, std::move(message));
   }
   
   void writeCritical(string message)
   {
       write_log(50, std::move(message));
   }
   #ifdef DEBUG
   void writeLog(const int &level, string message)
   {
       static LogFile logfile;
       logfile.write(level, std::move(message));
   }
   
   void writeLog(const int &level, stringstream &message)
   {
       writeLog(level, message.str());
   }
   
   #endif // DEBUG
   PyObject * set_log_function(PyObject *dummy, PyObject *args)
   {
       PyObject *res = nullptr;
       PyObject *temp;
       if(PyArg_ParseTuple(args, "O:set_callback", &temp))
       {
           if (!PyCallable_Check(temp))
           {
               PyErr_SetString(PyExc_TypeError, "parameter must be callable");
               return nullptr;
           }
           Py_XINCREF(temp);         /* Add a reference to new callback */
   
           Py_XDECREF(call_logging);  /* Dispose of previous callback */
           call_logging = temp;       /* Remember new callback */
           /* Boilerplate to return "None" */
           Py_INCREF(Py_None);
           res = Py_None;
           log_set = true;
       }
       return res;
   }
   
   void write_log(int level, char * message)
   {
       if(PyErr_CheckSignals()!=0)
       {
           throw runtime_error("Keyboard interrupt detected.");
       }
       PyObject *arglist, *res;
   #ifdef DEBUG
       if(!logger_set)
       {
           throw runtime_error(
               "Logger object has not been set. Check set_logging_function() has been called in python");
       }
       if(logger == nullptr)
       {
           throw invalid_argument("Logger object has been deferenced, please report this bug!");
       }
   #endif // DEBUG
       arglist = Py_BuildValue("isO", level, message, logger);
       // Throw different errors if logging function has not been set
   #ifdef DEBUG
       if(!log_set)
       {
           throw runtime_error(
               "Logging function has not been set. Check set_logging_function() has been called in python");
       }
       if(call_logging == NULL)
       {
           Py_DECREF(arglist);
           throw invalid_argument("Logging function has been dereferenced, please report this bug!");
       }
   #endif // DEBUG
       res = PyObject_CallObject(call_logging, arglist);
       Py_DECREF(arglist);
       Py_XDECREF(res);
   }
   
   void write_log(int level, string message)
   {
       char * msg;
       msg = (char* )message.c_str();
       write_log(level, msg);
   #ifdef DEBUG
       // Also write to the log file - stored in logfile.log
       writeLog(level, message);
   #endif // DEBUG
   }
   
   PyObject * set_logger(PyObject * self, PyObject * args)
   {
       PyObject * tmplogger;
       if(!PyArg_ParseTuple(args, "O", &tmplogger))
       {
           return NULL;
       }
       Py_XINCREF(tmplogger);         /* Add a reference to new callback */
       Py_XDECREF(logger);  /* Dispose of previous callback */
       logger = tmplogger;       /* Remember new callback */
       /* Boilerplate to return "None" */
       Py_INCREF(Py_None);
       logger_set = true;
       Py_RETURN_NONE;
   }
