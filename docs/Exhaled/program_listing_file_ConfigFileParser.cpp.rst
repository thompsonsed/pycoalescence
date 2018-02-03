
.. _program_listing_file_ConfigFileParser.cpp:

Program Listing for File ConfigFileParser.cpp
========================================================================================

- Return to documentation for :ref:`file_ConfigFileParser.cpp`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   // 
   #include "ConfigFileParser.h"
   void importArgs(const unsigned int& argc, char* argv [], vector<string>& comargs)
   {
       for(unsigned int i = 0; i < argc; i++)
       {
           comargs.push_back(string(argv[i]));
       }
       // check size is correct
       if(comargs.size() != argc)
       {
           cerr << "ERROR_MAIN_010: Incorrect command line parsing." << endl;
       }
   }
