
.. _program_listing_file_necsim_Logging.h:

Program Listing for File Logging.h
==================================

- Return to documentation for :ref:`file_necsim_Logging.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   #include <string>
   #include <iostream>
   #include <cstdio>
   #include <stdexcept>
   #include "LogFile.h"
   
   using namespace std;
   #ifndef LOGGING_IMPORT
   #define LOGGING_IMPORT
   
   void writeInfo(string message);
   
   void writeWarning(string message);
   
   void writeError(string message);
   
   void writeCritical(string message);
   
   
   #ifdef DEBUG
   
   void writeLog(const int &level, string message);
   
   void writeLog(const int &level, stringstream &message);
   #endif
   #endif
