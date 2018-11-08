
.. _program_listing_file_necsim_file_system.h:

Program Listing for File file_system.h
======================================

- Return to documentation for :ref:`file_necsim_file_system.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #define _USE_MATH_DEFINES
   
   #include <cmath>
   #include <sqlite3.h>
   #include <string>
   
   #ifndef SPECIATIONCOUNTER_FILESYSTEM_H
   #define SPECIATIONCOUNTER_FILESYSTEM_H
   
   using namespace std;
   
   void openSQLiteDatabase(const string &database_name, sqlite3 *&database);
   
   void createParent(string file);
   
   bool doesExist(string testfile);
   
   bool doesExistNull(string testfile);
   
   unsigned long cantorPairing(const unsigned long &x1, const unsigned long &x2);
   
   unsigned long elegantPairing(const unsigned long &x1, const unsigned long &x2);
   
   vector<string> getCsvLineAndSplitIntoTokens(istream &str);
   
   template<class T>
   ostream &operator<<(ostream &os, const vector<T> &v)
   {
       os << v.size() << ",";
       for(const auto &item: v)
       {
           os << item << ",";
       }
       return os;
   }
   
   template<class T>
   istream &operator>>(istream &is, vector<T> &v)
   {
       char delim;
       int n;
       is >> n;
       v.resize(n);
       is >> delim;
       for(unsigned long c = 0; c < static_cast<unsigned long>(n); c++)
       {
           is >> v[c];
           is >> delim;
       }
       return is;
   }
   
   #endif //SPECIATIONCOUNTER_FILESYSTEM_H
