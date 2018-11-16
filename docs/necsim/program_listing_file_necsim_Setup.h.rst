
.. _program_listing_file_necsim_setup.h:

Program Listing for File setup.h
================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_setup.h>` (``necsim/setup.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   // 
   #ifndef SETUP
   #define SETUP
   #include <string>
   #include <vector>
   #ifndef WIN_INSTALL
   #include <unistd.h>
   #endif
   #include <sstream>
   #include <ctime>
   #include <boost/filesystem.hpp>
   #include <cstdio>
   #include <ctime>
   #include <iostream>
   #include <iomanip>
   
   // Forward declaring the global variables
   // store the log file name for access anywhere.
   using namespace std;
   
   extern string log_name;
   // the old stdout
   extern int saved_stdout;
   #ifdef DEBUG
   
   void openLogFile(bool append);
   #endif
   
   void runAsDefault(vector<string>&comargs);
   
   
   void runLarge(vector<string>&comargs);
   
   void runXL(vector<string>&comargs);
   void removeComOption(unsigned long& argc, vector<string> & comargs);
   
   
   
   
   #endif // SETUP
