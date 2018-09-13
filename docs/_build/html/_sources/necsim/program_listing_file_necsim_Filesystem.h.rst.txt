
.. _program_listing_file_necsim_Filesystem.h:

Program Listing for File Filesystem.h
=====================================

- Return to documentation for :ref:`file_necsim_Filesystem.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #define _USE_MATH_DEFINES
   #include <cmath>
   #include <sqlite3.h>
   #include <string>
   
   #ifndef SPECIATIONCOUNTER_FILESYSTEM_H
   #define SPECIATIONCOUNTER_FILESYSTEM_H
   
   using namespace std;
   
   void openSQLiteDatabase(const string &database_name, sqlite3 *& database);
   
   void createParent(string file);
   
   
   bool doesExist(string testfile);
   
   bool doesExistNull(string testfile);
   
   unsigned long cantorPairing(unsigned long x1, unsigned long x2);
   
   vector<string> getCsvLineAndSplitIntoTokens(istream& str);
   
   #endif //SPECIATIONCOUNTER_FILESYSTEM_H
