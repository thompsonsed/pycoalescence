
.. _program_listing_file_necsim_ConfigParser.h:

Program Listing for File ConfigParser.h
=======================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_ConfigParser.h>` (``necsim/ConfigParser.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
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
   #ifndef WIN_INSTALL
   #include <unistd.h>
   #endif
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
   
       SectionOption() : val(), refs()
       {
           section = "nullSectionOption";
       }
   
       string getOption(string refval);
   
       friend ostream &operator<<(ostream &os, const SectionOption &k);
   
       friend istream &operator>>(istream &is, SectionOption &k);
   };
   
   class ConfigParser
   {
   private:
       string config_file;
       bool configSet;
       bool isMain;  // is true if this is the main command line import (and therefore we want to delete the first few
       // command line options)
       bool isFullParser;  // if this is true, each KeyOption structure will be returned after each read.
       vector<SectionOption> configs;  // all config data if full parse is true.
   public:
       ConfigParser() : configs()
       {
           config_file = "none";
           configSet = false;
           isMain = false;
           isFullParser = false;
       }
   
       void setConfig(const string &file, bool main, bool full_parse = false);
   
       void parseConfig();
   
       void parseConfig(istream &istream1);
       vector<SectionOption> getSectionOptions();
   
       void setSectionOption(string section, string reference, string value);
   
       SectionOption operator[](unsigned long index);
   
       unsigned long getSectionOptionsSize();
   
       vector<string> getSections();
   
       bool hasSection(const string &sec);
   
       vector<string> getSectionValues(string sec);
   
       string getSectionOptions(string section, string ref);
   
       string getSectionOptions(string section, string ref, string def);
   
       int importConfig(vector<string> &comargs);
   
       friend ostream &operator<<(ostream &os, const ConfigParser &c);
   
       friend istream &operator>>(istream &is, ConfigParser &c);
   };
   
   #endif
