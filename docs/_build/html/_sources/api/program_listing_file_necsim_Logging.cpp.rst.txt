
.. _program_listing_file_necsim_Logging.cpp:

Program Listing for File Logging.cpp
====================================

- Return to documentation for :ref:`file_necsim_Logging.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   #include <sstream>
   #include "Logging.h"
   
   
   using namespace std;
   
   void writeInfo(string message)
   {
   #ifdef DEBUG
       writeLog(10, message);
   #endif // DEBUG
       cout << message << flush;
   }
   
   void writeWarning(string message)
   {
   #ifdef DEBUG
       writeLog(20, message);
   #endif // DEBUG
       cerr << message << flush;
   }
   
   void writeError(string message)
   {
   #ifdef DEBUG
       writeLog(30, message);
   #endif // DEBUG
       cerr << message << flush;
   }
   
   void writeCritical(string message)
   {
   #ifdef DEBUG
       writeLog(40, message);
   #endif // DEBUG
       cerr << message << flush;
   }
   
   #ifdef DEBUG
   void writeLog(const int &level, string message)
   {
       static LogFile logfile;
       logfile.write(level, std::move(message));
   }
   
   void writeLog(const int &level, stringstream &message)
   {
       writeLog(level, message.str());
   }
   
   #endif // DEBUG
