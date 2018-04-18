
.. _program_listing_file_necsim_DataPoint.h:

Program Listing for File DataPoint.h
====================================

- Return to documentation for :ref:`file_necsim_DataPoint.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef DATAPOINT_H
   #define DATAPOINT_H
   
   #include <iostream>
   #include "Logging.h"
   
   using namespace std;
   class DataPoint
   {
       
   private:
       // x position
       unsigned long xpos;
       // y position
       unsigned long ypos;
       // number of wraps of x around the torus
       long xwrap;
       // number of wraps of y around the torus
       long ywrap;
       // the next individual in the loop of those that have the same xypos
       unsigned long next_lineage;
       // points to the position in output of this lineage
       unsigned long reference;
       // points to the position in the SpeciesList file.
       unsigned long list_position;
       // the reference number within the linked list of wrapped lineages
       unsigned long nwrap;
       // the max-min number
       double min_max;
   public:
       
       DataPoint() : xpos(0),ypos(0),xwrap(0),ywrap(0),next_lineage(0),reference(0),list_position(0),nwrap(0),min_max(0)
       {
           
       }
       
       ~DataPoint() = default;
   
       void setup(unsigned long x , unsigned long y , long xwrap_in, long ywrap_in, unsigned long reference_in,
                  unsigned long list_position_in, double min_max_in);
   
       void setup(unsigned long reference_in, unsigned long list_position_in, double min_max_in);
       void setup(DataPoint datin);
       
       
       void setReference(unsigned long z);
       void setNext(unsigned long x);
       
       void setListPosition(unsigned long l);
       void setNwrap(unsigned long n);
       
       void setMinmax(double d);
   
       
       unsigned long getXpos();
       
       unsigned long getYpos();
       
       long getXwrap();
       
       long getYwrap();
       
       unsigned long getReference();
   
       unsigned long getNext();
   
       unsigned long getListpos();
       
       unsigned long getNwrap();
       
       double getMinmax();
       
       void decreaseNwrap();
   
       void setEndpoint(long x, long y, long xwrapin, long ywrapin);
       
       friend ostream& operator<<(ostream& os, const DataPoint& d);
       
       friend istream& operator>>(istream& is, DataPoint& d);
   
   #ifdef DEBUG
       void logActive(const int &level)
       {
           writeLog(50, "x, y, (x wrap, y wrap): " + to_string(xpos) + ", " + to_string(ypos) + ", (" +
                   to_string(xwrap) + ", " + to_string(ywrap) + ")");
           writeLog(50, "Lineage next: " + to_string(next_lineage));
           writeLog(50, "Reference: " + to_string(reference));
           writeLog(50, "List position: " + to_string(list_position));
           writeLog(50, "Number in wrapped lineages: " + to_string(nwrap));
           writeLog(50, "Minimum maximum: " + to_string(min_max));
       }
   #endif // DEBUG
   };
   
   #endif // DATAPOINT_H
