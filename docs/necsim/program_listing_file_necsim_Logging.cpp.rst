
.. _program_listing_file_necsim_Logging.cpp:

Program Listing for File Logging.cpp
====================================

- Return to documentation for :ref:`file_necsim_Logging.cpp`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #include "Logging.h"
   #include "Logger.h"
   void writeInfo(string message)
   {
       logger->writeInfo(message);
   }
   
   void writeWarning(string message)
   {
       logger->writeWarning(message);
   }
   
   void writeError(string message)
   {
       logger->writeError(message);
   }
   
   void writeCritical(string message)
   {
       logger->writeCritical(message);
   }
   
   #ifdef DEBUG
   void writeLog(const int &level, string message)
   {
       logger->writeLog(level, message);
   }
   
   void writeLog(const int &level, stringstream &message)
   {
       logger->writeLog(level, message.str());
   }
   
   #endif //DEBUG
