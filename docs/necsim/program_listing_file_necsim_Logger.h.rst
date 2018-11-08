
.. _program_listing_file_necsim_Logger.h:

Program Listing for File Logger.h
=================================

- Return to documentation for :ref:`file_necsim_Logger.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef LOGGING_IMPORT_H
   #define LOGGING_IMPORT_H
   
   #include <string>
   #include <iostream>
   #include <cstdio>
   #include <stdexcept>
   #include <sstream>
   #include "LogFile.h"
   #include "cpl_custom_handler.h"
   
   using namespace std;
   
   class Logger
   {
   protected:
   #ifdef DEBUG
       LogFile logfile;
   #endif //DEBUG
   public:
       Logger() = default;
   
       virtual ~Logger() = default;
   
       virtual void writeInfo(string message);
   
       virtual void writeWarning(string message);
   
       virtual void writeError(string message);
   
       virtual void writeCritical(string message);
   
   #ifdef DEBUG
   
       virtual void writeLog(const int &level, string message);
   
       virtual void writeLog(const int &level, stringstream &message);
   
   #endif // DEBUG
   };
   
   
   #endif // LOGGING_IMPORT_H
