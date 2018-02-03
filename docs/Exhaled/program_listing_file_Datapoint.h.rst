
.. _program_listing_file_Datapoint.h:

Program Listing for File Datapoint.h
========================================================================================

- Return to documentation for :ref:`file_Datapoint.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   // Datapoint.cpp version 3.1
   // Author - Samuel Thompson - Imperial College London
   // with large use of code supplied by James Rosindell (Imperial College London)
   // This file contains the datapoint class for usage in coalescence simulations.
   // Version 2.01 removes any references to matrix vs grid x and y coordinates, instead simplifying to a single coordinate system.
   
   
   # define version1_01
   
   /************************************************************
                       DATA POINT OBJECT
    ************************************************************/
    #include <iostream>
    #include "Logging.h"
   
   using namespace std;
   class Datapoint
   {
       
   private:
       unsigned long xpos;
       // x position
       unsigned long ypos;
       // y position
       long xwrap;
       // number of wraps of x around the torus
       long ywrap;
       // number of wraps of y around the torus
       unsigned long iNext;
       // the next individual in the loop of those that have the same xypos
   //  unsigned long last; // removed as of version 3.1
   //  // the last individual in the loop 0 means the only one
       unsigned long mpos;
       // points to the position in output of this lineage
       unsigned long listpos;
       // points to the position in the SpeciesList file.
       unsigned long nwrap;
       
       // the max-min number
       double dMinmax;
   public:
       
       Datapoint() : xpos(0),ypos(0),xwrap(0),ywrap(0),iNext(0),mpos(0),listpos(0),nwrap(0),dMinmax(0)
       {
           
       }
       
       ~Datapoint()
       {
           
       }
       
       void setup(unsigned long x , unsigned long y , long xwrapin, long ywrapin, unsigned long matrix_position,
                  unsigned long listposin, double dMinmaxin)
       {
           xpos = x;
           ypos = y;
           xwrap = xwrapin;
           ywrap = ywrapin;
           iNext = 0;
   //      last =0;// removed as of version 3.1
           mpos = matrix_position;
           listpos = listposin;
           nwrap = 0;
           dMinmax = dMinmaxin;
       }
       
       void setup(Datapoint datin)
       {
           xpos = datin.getXpos();
           ypos = datin.getYpos();
           xwrap = datin.getXwrap();
           ywrap = datin.getYwrap();
           iNext = datin.getNext();
   //      last = datin.get_last(); // removed as of version 3.1
           mpos = datin.getMpos();
           listpos = datin.getListpos();
           nwrap = datin.getNwrap();
           dMinmax = datin.getMinmax();
       }
       
       
       void setMpos(unsigned long z)
       {
           mpos = z;
       }
       void setNext(unsigned long x)
       {
           iNext = x;
       }
       
       void setListpos(unsigned long l)
       {
           listpos = l;
       }
       void setNwrap(unsigned long n)
       {
           nwrap = n;
       }
       
       void setMinmax(double d)
       {
           dMinmax = d;
       }
       
       void subtractListpos()
       {
           listpos --;
       }
       // note that position variables (8 of them) are set by lineage move routines below
       
       unsigned long getXpos()
       {
           return xpos;
       }
       
       unsigned long getYpos()
       {
           return ypos;
       }
       
       long getXwrap()
       {
           return xwrap;
       }
       
       long getYwrap()
       {
           return ywrap;
       }
       
       unsigned long getMpos()
       {
           return mpos;
       }
       
       unsigned long getNext()
       {
           return iNext;
       }
       
       // removed as of version 3.1
   //  unsigned long get_last()
   //  {
   //      return last;
   //  }
       unsigned long getListpos()
       {
           return listpos;
       }
       
       unsigned long getNwrap()
       {
           return nwrap;
       }
       
       double getMinmax()
       {
           return dMinmax;
       }
       
       void decreaseNwrap()
       {
           try
           {
               if(nwrap==0)
               {
                   throw out_of_range("ERROR_DATA_001: Trying to decrease  nwrap less than 0.");
               }
               else
               {
                   nwrap --;
               }
           }
           catch(out_of_range& oor)
           {
               cerr << oor.what() << endl;
           }
       }
       // routines
       // removed the move and checkpos routines as they are no longer relevant.
       void setEndpoint(long x, long y, long xwrapin, long ywrapin)
       {
           xpos = x;
           ypos = y;
           xwrap = xwrapin;
           ywrap = ywrapin;
       }
       
       friend ostream& operator<<(ostream& os, const Datapoint& d)
       { 
           os << d.xpos << "," << d.ypos  << "," << d.xwrap << "," << d.ywrap << "," << d.iNext << "," << d.mpos << "," << d.listpos << "," << d.nwrap<< ",";
           os << d.dMinmax << "\n";
           return os;
       }
       
       friend istream& operator>>(istream& is, Datapoint& d)
       { 
           //os << m.numRows<<" , "<<m.numCols<<" , "<<endl; 
           char delim;
           //os << "datapoint" << endl;
           is >> d.xpos >> delim >> d.ypos  >> delim >> d.xwrap >> delim >> d.ywrap >> delim >> d.iNext >> delim >> d.mpos >> delim >> d.listpos >> delim >> d.nwrap>> delim;
           is >> d.dMinmax;
           return is;
       }
   };
