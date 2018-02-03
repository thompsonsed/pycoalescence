
.. _program_listing_file_Logging.h:

Program Listing for File Logging.h
========================================================================================

- Return to documentation for :ref:`file_Logging.h`

.. code-block:: cpp

   
   #include <string>
   #include <iostream>
   #include <stdio.h>
   #include <stdexcept>
   #ifdef PYTHON_COMPILE
   #include <Python.h>
   #endif
   using namespace std;
   #ifndef LOGGING_IMPORT
   #define LOGGING_IMPORT
   
   void write_cout(string message);
   
   void write_cerr(string message);
   
   void write_error(string message);
   
   void write_critical(string message);
   
   // The python specific definitions
   #ifdef PYTHON_COMPILE
   
   extern PyObject * loggingmodule;
   extern PyGILState_STATE gstate;
   extern bool log_set;
   extern bool logger_set;
   
   extern PyObject *logger;
   
   PyObject * set_log_function(PyObject *dummy, PyObject *args);
   
   PyObject * set_logger(PyObject * self, PyObject * args);
   
   void write_log(int level, char * message);
   
   void write_log(int level, string message);
   #endif
   #endif
