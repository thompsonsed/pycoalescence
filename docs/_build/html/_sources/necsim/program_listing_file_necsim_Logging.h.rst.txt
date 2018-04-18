
.. _program_listing_file_necsim_Logging.h:

Program Listing for File Logging.h
==================================

- Return to documentation for :ref:`file_necsim_Logging.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef LOGGING_IMPORT_H
   #define LOGGING_IMPORT_H
   #include <string>
   #include <iostream>
   #include <cstdio>
   #include <stdexcept>
   #include <sstream>
   #include "LogFile.h"
   #include "CPLCustomHandler.h"
   
   using namespace std;
   
   void writeInfo(string message);
   
   void writeWarning(string message);
   
   void writeError(string message);
   
   void writeCritical(string message);
   
   
   #ifdef DEBUG
   
   void writeLog(const int &level, string message);
   
   void writeLog(const int &level, stringstream &message);
   #endif // DEBUG
   #endif // LOGGING_IMPORT_H
