
.. _program_listing_file_necsim_CustomExceptions.h:

Program Listing for File CustomExceptions.h
===========================================

- Return to documentation for :ref:`file_necsim_CustomExceptions.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   // Author: Samuel Thompson
   // Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
   #ifndef CUSTOM_EXCEPTION_H
   #define CUSTOM_EXCEPTION_H
   
   #include <stdexcept>
   #include <utility>
   #include "Logging.h"
   
   using namespace std;
   
   struct FatalException : public runtime_error
   {
       FatalException() : runtime_error("Fatal exception thrown at run time, quitting program. "){}
   
       explicit FatalException(string msg) : runtime_error(msg)
       {
   #ifdef DEBUG
           writeLog(50, msg);
   #endif //DEBUG
       }
   };
   
   struct ConfigException : public FatalException
   {
       ConfigException() : FatalException("Exception thrown at run time in config: "){};
   
       explicit ConfigException(string msg) : FatalException(std::move(msg)){}
   };
   
   
   struct SpeciesException : public FatalException
   {
       SpeciesException() : FatalException("Exception thrown at run time in SpeciationCounter: "){}
   
       explicit SpeciesException(string msg) : FatalException(msg){}
   };
   
   
   #endif // CUSTOM_EXCEPTION_H
