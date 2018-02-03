
.. _program_listing_file_Logging.cpp:

Program Listing for File Logging.cpp
========================================================================================

- Return to documentation for :ref:`file_Logging.cpp`

.. code-block:: cpp

   
   #include "Logging.h"
   #ifdef PYTHON_COMPILE
   #include "necsimmodule.h"
   #endif
   
   using namespace std;
   void write_cout(string message)
   {
       #ifndef PYTHON_COMPILE
       cout << message << flush;
       #else
       write_log(20, message);
       #endif
   }
   
   void write_cerr(string message)
   {
       #ifndef PYTHON_COMPILE
       cerr << message << flush;
       #else
       write_log(30, message);
       #endif
   }
   
   void write_error(string message)
   {
       #ifndef PYTHON_COMPILE
       cerr << message << flush;
       #else
       write_log(40, message);
       #endif
   }
   
   void write_critical(string message)
   {
       #ifndef PYTHON_COMPILE
       cerr << message << flush;
       #else
       write_log(50, message);
       #endif
   }
   
   #ifdef PYTHON_COMPILE
   PyObject * set_log_function(PyObject *dummy, PyObject *args)
   {
       PyObject *res = NULL;
       PyObject *temp;
       if(PyArg_ParseTuple(args, "O:set_callback", &temp)) 
       {
           if (!PyCallable_Check(temp))
           {
               PyErr_SetString(PyExc_TypeError, "parameter must be callable");
               return NULL;
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
       if(!logger_set)
       {
           throw runtime_error(
               "Logger object has not been set. Check set_logging_function() has been called in python");
       }
       if(logger == NULL)
       {
           throw invalid_argument("Logger object has been deferenced, please report this bug!");
       }
       arglist = Py_BuildValue("isO", level, message, logger);
       // Throw different errors if logging function has not been set
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
       res = PyObject_CallObject(call_logging, arglist);
       Py_DECREF(arglist);
       Py_XDECREF(res);
       return;
   }
   
   void write_log(int level, string message)
   {
       char * msg;
       msg = (char* )message.c_str();
       write_log(level, msg);
       return;
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
   #endif
