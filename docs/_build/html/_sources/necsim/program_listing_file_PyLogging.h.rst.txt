
.. _program_listing_file_PyLogging.h:

Program Listing for File PyLogging.h
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_PyLogging.h>` (``PyLogging.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
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
