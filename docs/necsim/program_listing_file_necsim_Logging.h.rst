
.. _program_listing_file_necsim_Logging.h:

Program Listing for File Logging.h
==================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_Logging.h>` (``necsim/Logging.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #ifndef NECSIM_LOGGING_H
   #define NECSIM_LOGGING_H
   
   #include <string>
   #include "Logger.h"
   // Global declaration of logger
   extern Logger *logger;
   
   void writeInfo(string message);
   
   void writeWarning(string message);
   
   void writeError(string message);
   
   void writeCritical(string message);
   
   #ifdef DEBUG
   
   void writeLog(const int &level, string message);
   
   void writeLog(const int &level, stringstream &message);
   
   #endif // DEBUG
   
   #endif //MEANDISTANCEMODULE_LOGGING_H
