
.. _program_listing_file_necsim_cpl_custom_handler.cpp:

Program Listing for File cpl_custom_handler.cpp
===============================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_cpl_custom_handler.cpp>` (``necsim/cpl_custom_handler.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #include <sstream>
   #include "cpl_custom_handler.h"
   #include "Logging.h"
   
   #ifdef with_gdal
   
   void cplNecsimCustomErrorHandler(CPLErr eErrClass, int err_no, const char *msg)
   {
       stringstream error_msg;
       error_msg << "Gdal error: " << err_no << ". " << msg << endl;
       if(eErrClass == CE_Fatal)
       {
           writeCritical(error_msg.str());
       }
       else if(eErrClass == CE_Failure)
       {
           writeError(error_msg.str());
       }
       else if(eErrClass == CE_Warning)
       {
           writeWarning(error_msg.str());
       }
   #ifdef DEBUG
       else
       {
           writeLog(10, error_msg.str());
       }
   #endif // DEBUG
   }
   
   #endif //with_gdal
