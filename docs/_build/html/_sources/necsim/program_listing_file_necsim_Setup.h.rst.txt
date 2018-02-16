
.. _program_listing_file_necsim_Setup.h:

Program Listing for File Setup.h
================================

- Return to documentation for :ref:`file_necsim_Setup.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   // 
   #ifndef SETUP
   #define SETUP
   #include <string>
   #include <vector>
   #include <unistd.h>
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
