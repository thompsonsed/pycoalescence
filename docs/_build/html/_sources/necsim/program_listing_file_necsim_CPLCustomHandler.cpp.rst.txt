
.. _program_listing_file_necsim_CPLCustomHandler.cpp:

Program Listing for File CPLCustomHandler.cpp
=============================================

- Return to documentation for :ref:`file_necsim_CPLCustomHandler.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   #include "CPLCustomHandler.h"
   #include <sstream>
   #include "Logging.h"
   #ifdef with_gdal
   void cplCustomErrorHandler(CPLErr eErrClass, int err_no, const char *msg)
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
