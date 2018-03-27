
.. _program_listing_file_PyLogging.h:

Program Listing for File PyLogging.h
====================================

- Return to documentation for :ref:`file_PyLogging.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
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
   
   
   extern PyObject *logger;
   
   PyObject * set_log_function(PyObject *dummy, PyObject *args);
   
   PyObject * set_logger(PyObject * self, PyObject * args);
   
   void write_log(int level, char * message);
   
   void write_log(int level, string message);
   
   #endif // PYLOGGING_H
