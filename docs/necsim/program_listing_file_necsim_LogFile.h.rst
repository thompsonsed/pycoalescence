
.. _program_listing_file_necsim_LogFile.h:

Program Listing for File LogFile.h
==================================

- Return to documentation for :ref:`file_necsim_LogFile.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef LOGFILE_H
   #define LOGFILE_H
   
   #include <cstring>
   #include <fstream>
   #include <ctime>
   #include <map>
   
   #define LOGNAME_FORMAT "%d%m%Y_%H%M%S"
   
   using namespace std;
   
   
   string getTime();
   
   string getDefaultLogFile();
   
   void getUniqueFileName(string &basic_string);
   
   class LogFile
   {
   protected:
       // output stream to log file
       ofstream output_stream;
       // log file name
       string file_name;
       // mapping integer levels to logger level
       map<int, string> levels_map;
   
       // Makes the class non-copyable as we don't want to copy file streams
       LogFile(const LogFile &) = delete;
   
       LogFile &operator=(const LogFile &) = delete;
   
   public:
       LogFile();
   
       explicit LogFile(string file_name_in);
   
       ~LogFile();
   
       void init(string file_name_in);
   
       void write(const int &level, string message);
   
       void write(const int &level, stringstream &message);
   };
   
   #endif //LOGFILE_H
