
.. _program_listing_file_Datamask.h:

Program Listing for File Datamask.h
========================================================================================

- Return to documentation for :ref:`file_Datamask.h`

.. code-block:: cpp

   //
   // Created by Sam Thompson on 10/09/2017.
   //
   
   #ifndef SPECIATIONCOUNTER_DATAMASK_H
   #define SPECIATIONCOUNTER_DATAMASK_H
   
   #include <string>
   
   #include "Matrix.h"
   #include "SimParameters.h"
   #include "Logging.h"
   
   // Class which contains the Datamask object, telling us where to sample from within the habitat map.
   class Datamask
   {
   protected:
       // the file to read in from
       string inputfile;
       bool bDefault;
       unsigned long x_offset, y_offset;
       // Stores the size of the grid which is stored as a ful species list
       unsigned long x_dim, y_dim;
       // Stores the size of the samplemask from which spatially sampling is read
       unsigned long mask_x_dim, mask_y_dim;
   public:
       Matrix<bool> sample_mask; 
       Datamask()
       {
           bDefault = true;
           x_dim = 0;
           y_dim = 0;
           x_offset = 0;
           y_offset = 0;
           mask_x_dim = 0;
           mask_y_dim = 0;
       }
   
       bool getDefault()
       {
           return bDefault;
       }
   
       void importDatamask(SimParameters& mapvarin)
       {
           inputfile = mapvarin.samplemaskfile;
   //      os << "inputfile: " << inputfile;
           x_dim = mapvarin.vargridxsize;
           y_dim = mapvarin.vargridysize;
           mask_x_dim = mapvarin.varsamplexsize;
           mask_y_dim  = mapvarin.varsampleysize;
           if(inputfile == "null" || inputfile == "none")
           {
               bDefault = true;
               x_offset = 0;
               y_offset = 0;
           }
           else
           {
               x_offset = mapvarin.varsamplexoffset;
               y_offset = mapvarin.varsampleyoffset;
               sample_mask.SetSize(mask_y_dim, mask_x_dim);
               bDefault = false;
               sample_mask.import(inputfile);
           }
       }
   
       void importDatamask(unsigned long xdim, unsigned long ydim, unsigned long mask_xdim, unsigned long mask_ydim,
                           unsigned long xoffset, unsigned long yoffset, string inputfile)
       {
           x_dim = xdim;
           y_dim = ydim;
           mask_x_dim = mask_xdim;
           mask_y_dim = mask_ydim;
           x_offset = xoffset;
           y_offset = yoffset;
           if(inputfile == "null" || inputfile == "none")
           {
               bDefault = true;
           }
           else
           {
               sample_mask.SetSize(mask_ydim, mask_xdim);
               bDefault = false;
               sample_mask.import(inputfile);
           }
       }
   
       bool getVal(long x, long y, long xwrap, long ywrap)
       {
           long xval = x + (xwrap * x_dim) + x_offset;
           long yval = y + (ywrap * y_dim) + y_offset;
   #ifdef DEBUG
           if(xval < 0 || xval >= (long) mask_x_dim || yval < 0 ||
              yval >= (long) mask_y_dim)
           {
               stringstream ss;
               ss << "Get value on samplemask requested for non index." << endl;
               ss << "x, y: " << x << ", " << y << endl;
               ss << "x, y wrap: " << xwrap << ", " << ywrap << endl;
               ss << "xval, yval: " << xval << ", " << yval << endl;
               throw out_of_range(ss.str());
           }
   #endif
           if(bDefault)
           {
               return true;
           }
           return sample_mask[yval][xval];
       }
   
       void recalculate_coordinates(long &x, long &y, long &x_wrap, long &y_wrap)
       {
           if(!bDefault)
           {
               x_wrap = (long)((floor((x - (double) x_offset) / (double) x_dim)));
               y_wrap = (long)((floor((y - (double) y_offset) / (double) y_dim)));
               x += -x_offset - (x_wrap * x_dim);
               y += -y_offset - (y_wrap * y_dim);
           }
       }
   };
   
   
   #endif //SPECIATIONCOUNTER_DATAMASK_H
