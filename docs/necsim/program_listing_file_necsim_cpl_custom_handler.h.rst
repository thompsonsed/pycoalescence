
.. _program_listing_file_necsim_cpl_custom_handler.h:

Program Listing for File cpl_custom_handler.h
=============================================

- Return to documentation for :ref:`file_necsim_cpl_custom_handler.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef SPECIATIONCOUNTER_cplCustomHandlerNecsim_H
   #define SPECIATIONCOUNTER_cplCustomHandlerNecsim_H
   #ifdef with_gdal
   #include <cpl_error.h>
   void cplNecsimCustomErrorHandler(CPLErr eErrClass, int err_no, const char *msg);
   
   #endif // with_gdal
   
   
   #endif //SPECIATIONCOUNTER_cplCustomHandlerNecsim_H
