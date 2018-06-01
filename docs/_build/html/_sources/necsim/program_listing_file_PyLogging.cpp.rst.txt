
.. _program_listing_file_PyLogging.cpp:

Program Listing for File PyLogging.cpp
======================================

- Return to documentation for :ref:`file_PyLogging.cpp`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
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
