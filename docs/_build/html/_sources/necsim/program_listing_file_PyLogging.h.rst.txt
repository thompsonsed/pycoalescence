
.. _program_listing_file_PyLogging.h:

Program Listing for File PyLogging.h
====================================

- Return to documentation for :ref:`file_PyLogging.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef PYLOGGING_H
   #define PYLOGGING_H
   #include "Python.h"
   #include <string>
   #include "necsim/LogFile.h"
   #include "PyLogger.h"
   
   PyLogger * getGlobalLogger(PyObject * logger, PyObject * log_function);
   
   void removeGlobalLogger();
   #endif // PYLOGGING_H
