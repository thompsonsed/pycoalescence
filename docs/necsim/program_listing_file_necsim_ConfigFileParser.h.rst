
.. _program_listing_file_necsim_ConfigFileParser.h:

Program Listing for File ConfigFileParser.h
===========================================

- Return to documentation for :ref:`file_necsim_ConfigFileParser.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   //
   #ifndef CONFIGCLASS
   #define CONFIGCLASS
   
   /************************************************************
                                                                                                                                                                                                   INCLUDES
    ************************************************************/
   #include <string>
   #include <iostream>
   #include <sstream>
   #include <fstream>
   #include <stdexcept>
   #include <vector>
   #include <cstring>
   #include <unistd.h>
   #include <cmath>
   #include <cctype>
   #include <algorithm>
   
   using namespace std;
   using std::string;
   
   void importArgs(const unsigned int &argc, char *argv[], vector<string> &comargs);
   
   //
   
   struct SectionOption
   {
       string section;
       vector<string> val;
       vector<string> refs;
   
       SectionOption()
       {
           section = "nullSectionOption";
       }
   
       string getOption(string refval);
   
       friend ostream &operator<<(ostream &os, const SectionOption &k);
   
       friend istream &operator>>(istream &is, SectionOption &k);
   };
   
   class ConfigOption
   {
   private:
       string configfile;
       bool bConfig;
       bool bMain;  // is true if this is the main command line import (and therefore we want to delete the first few
       // command line options)
       bool bFullParse;  // if this is true, each KeyOption structure will be returned after each read.
       vector<SectionOption> configs;  // all config data if full parse is true.
   public:
       ConfigOption()
       {
           bConfig = false;
           configfile = "none";
           bMain = false;
           bFullParse = false;
       }
   
       void setConfig(const string &file, bool main, bool full_parse = false);
   
       void parseConfig();
   
       vector<SectionOption> getSectionOptions();
   
       void setSectionOption(string section, string reference, string value);
   
       SectionOption operator[](int index);
   
       unsigned int getSectionOptionsSize();
   
       vector<string> getSections();
   
       bool hasSection(const string &sec);
   
       vector<string> getSectionValues(string sec);
   
       string getSectionOptions(string section, string ref);
   
       string getSectionOptions(string section, string ref, string def);
   
       int importConfig(vector<string> &comargs);
   
       friend ostream &operator<<(ostream &os, const ConfigOption &c);
   
       friend istream &operator>>(istream &is, ConfigOption &c);
   };
   
   #endif
