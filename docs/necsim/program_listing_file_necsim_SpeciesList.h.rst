
.. _program_listing_file_necsim_SpeciesList.h:

Program Listing for File SpeciesList.h
======================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_SpeciesList.h>` (``necsim/SpeciesList.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
    #ifndef SPECIESLIST
    #define SPECIESLIST
   
   #ifdef CXX14_SUPPORT
   #include "memory.h"
   #else
   #include <memory>
   #endif
   #include "Matrix.h"
   #include "NRrand.h"
   using namespace std;
   class SpeciesList
   {
   private:
       unsigned long list_size, maxsize; // List size and maximum size of the cell (based on percentage cover).
       unsigned long next_active; // For calculating the wrapping, using the next and last system.
       vector<unsigned long> species_id_list; // list of the active reference number, with zeros for empty cells.
       unsigned long nwrap; // The number of wrapping (next and last possibilities) that there are.
   public:
       SpeciesList();
   
       ~SpeciesList() = default;
   
       void initialise(unsigned long maxsizein);
       
       // special case if just the maxsize wants to be change, but want to maintain the species_id_list variables.
       void setMaxsize(unsigned long maxsizein);
       
       void setSpecies(unsigned long index, unsigned long new_val);
       
       void setSpeciesEmpty(unsigned long index, unsigned long new_val);
       
       void setNext(unsigned long n);
       
       
       void setNwrap(unsigned long nr);
       
       unsigned long addSpecies(const unsigned long &new_spec);
   
       void deleteSpecies(unsigned long index);
       
       void decreaseNwrap();
       void increaseListSize();
       
       void increaseNwrap();
       
       void changePercentCover(unsigned long newmaxsize);
       
       unsigned long getRandLineage(shared_ptr<NRrand> rand_no);
       
       unsigned long getSpecies(unsigned long index);
       
       unsigned long getNext();
       
       unsigned long getNwrap();
       
       unsigned long getListSize();
       
       unsigned long getMaxSize();
   
   
       unsigned long getListLength();
   
       void wipeList();
       
       friend ostream& operator<<(ostream& os,const SpeciesList& r);
       
       friend istream& operator>>(istream& is, SpeciesList& r);
   };
   
   #endif
