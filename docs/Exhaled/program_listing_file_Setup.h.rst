
.. _program_listing_file_Setup.h:

Program Listing for File Setup.h
========================================================================================

- Return to documentation for :ref:`file_Setup.h`

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
   #include <stdio.h>
   #include <time.h>
   #include <iostream>
   #include <iomanip>
   #include "Tree.h"
   
   // Forward declaring the global variables
   // store the log file name for access anywhere.
   extern string log_name; 
   // the old stdout 
   extern int saved_stdout;
   
   using namespace std;
   
   #ifndef verbose
   
   void openLogFile(bool append);
   #endif
   
   void runAsDefault(vector<string>&comargs);
   
   
   void runLarge(vector<string>&comargs);
   
   void runXL(vector<string>&comargs);
   void removeComOption(unsigned long& argc, vector<string> & comargs);
   
   
   bool doesExist(string testfile);
   
   bool doesExistNull(string testfile);
   
   int runMain(int argc, vector<string> &argv);
   
   
   
   #endif // SETUP
