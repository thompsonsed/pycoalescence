
.. _program_listing_file_necsim_Logger.cpp:

Program Listing for File Logger.cpp
===================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_Logger.cpp>` (``necsim/Logger.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #include <sstream>
   #include "Logger.h"
   #include "LogFile.h"
   
   using namespace std;
   
   Logger *logger;
   
   
   void Logger::writeInfo(string message)
   {
   #ifdef DEBUG
       writeLog(20, message);
   #endif // DEBUG
       cout << message << flush;
   }
   
   void Logger::writeWarning(string message)
   {
   #ifdef DEBUG
       writeLog(30, message);
   #endif // DEBUG
       cerr << message << flush;
   }
   
   void Logger::writeError(string message)
   {
   #ifdef DEBUG
       writeLog(40, message);
   #endif // DEBUG
       cerr << message << flush;
   }
   
   void Logger::writeCritical(string message)
   {
   #ifdef DEBUG
       writeLog(50, message);
   #endif // DEBUG
       cerr << message << flush;
   }
   
   #ifdef DEBUG
   void Logger::writeLog(const int &level, string message)
   {
       logfile.write(level, message);
   }
   
   void Logger::writeLog(const int &level, stringstream &message)
   {
       writeLog(level, message.str());
   }
   #endif // DEBUG
   
   
   
