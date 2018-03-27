
.. _program_listing_file_necsim_CPLCustomHandler.h:

Program Listing for File CPLCustomHandler.h
===========================================

- Return to documentation for :ref:`file_necsim_CPLCustomHandler.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   #ifndef SPECIATIONCOUNTER_CPLCUSTOMHANDLER_H
   #define SPECIATIONCOUNTER_CPLCUSTOMHANDLER_H
   #ifdef with_gdal
   #include <cpl_error.h>
   void cplCustomErrorHandler(CPLErr eErrClass, int err_no, const char *msg);
   
   #endif // with_gdal
   
   
   #endif //SPECIATIONCOUNTER_CPLCUSTOMHANDLER_H
