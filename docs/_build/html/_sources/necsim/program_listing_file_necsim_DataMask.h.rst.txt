
.. _program_listing_file_necsim_DataMask.h:

Program Listing for File DataMask.h
===================================

- Return to documentation for :ref:`file_necsim_DataMask.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   
   #ifndef SPECIATIONCOUNTER_DataMask_H
   #define SPECIATIONCOUNTER_DataMask_H
   
   // Forward declaration of Landscape class
   class Landscape;
   
   #include <string>
   #include <memory>
   
   #include "SimParameters.h"
   #include "Map.h"
   
   
   // Class which contains the DataMask object, telling us where to sample from within the habitat map.
   class DataMask
   {
   protected:
       // the file to read in from
       string inputfile;
       // True if the sample mask is true everywhere
       bool isNullSample;
       // True if the grid is smaller than the sample mask
       bool isGridOffset;
       unsigned long x_offset, y_offset;
       // Stores the size of the grid which is stored as a full species species_id_list
       unsigned long x_dim, y_dim;
       // Stores the size of the samplemask from which spatially sampling is read
       unsigned long mask_x_dim, mask_y_dim;
       // Function pointer for obtaining the proportional sampling from the sample mask.
       typedef double (DataMask::*fptr)(const long &x, const long &y, const long &xwrap, const long &ywrap);
       fptr getProportionfptr;
   public:
       Map<bool> sample_mask;
       Map<double> sample_mask_exact;
   
       DataMask();
   
       ~DataMask() = default;
   
       bool isNull();
   
       void setup(const SimParameters &sim_parameters);
   
       bool checkCanUseDefault(const SimParameters &sim_parameters);
       void importBooleanMask(unsigned long xdim, unsigned long ydim, unsigned long mask_xdim, unsigned long mask_ydim,
                              unsigned long xoffset, unsigned long yoffset, string inputfile_in);
   
       void doImport();
   
       void completeBoolImport();
   
       void setupNull(SimParameters &mapvarin);
   
       void importSampleMask(SimParameters &mapvarin);
   
   
       bool getVal(const long &x, const long &y, const long &xwrap, const long &ywrap);
   
       double getNullProportion(const long &x, const long &y, const long &xwrap, const long &ywrap);
   
       double getBoolProportion(const long &x, const long &y, const long &xwrap, const long &ywrap);
   
       double getSampleProportion(const long &x, const long &y, const long &xwrap, const long &ywrap);
   
       double getExactValue(const long &x, const long &y, const long &xwrap, const long &ywrap);
   
       void convertBoolean(shared_ptr<Landscape> map1, const double &deme_sampling, const double &generation);
   
       void clearSpatialMask();
   
       void recalculateCoordinates(long &x, long &y, long &x_wrap, long &y_wrap);
   };
   
   
   #endif //SPECIATIONCOUNTER_DataMask_H
