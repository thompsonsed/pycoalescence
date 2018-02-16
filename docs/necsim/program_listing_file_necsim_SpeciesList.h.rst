
.. _program_listing_file_necsim_SpeciesList.h:

Program Listing for File SpeciesList.h
======================================

- Return to documentation for :ref:`file_necsim_SpeciesList.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
    #ifndef SPECIESLIST
    #define SPECIESLIST
   
   
   using namespace std;
   #include "Matrix.h"
   #include "NRrand.h"
   
   class SpeciesList
   {
   private:
       unsigned long list_size,maxsize; // List size and maximum size of the cell (based on percentage cover).
       unsigned long next_active; // For calculating the wrapping, using the next and last system.
       Row<unsigned long> list; // list of the active reference number, with zeros for empty cells.
       unsigned long nwrap; // The number of wrapping (next and last possibilities) that there are.
   public:
       SpeciesList();
   
       ~SpeciesList() = default;
       // Sets the list size to the required length.
       // Note this will delete any species currently stored in the list
   
       // Fill the list with empty 0s.
       void fillList();
       
       // Standard setters
       void initialise(unsigned long maxsizein);
       
       // special case if just the maxsize wants to be change, but want to maintain the list variables.
       void setMaxsize(unsigned long maxsizein);
       
       void setSpecies(unsigned long index, unsigned long new_val);
       
       void setSpeciesEmpty(int index, unsigned long new_val);
       
       void setNext(unsigned long n);
       
       
       void setNwrap(unsigned long nr);
       
       unsigned long addSpecies(unsigned long new_spec);
       
       void addSpeciesSilent(unsigned long new_spec);
       
       void deleteSpecies(unsigned long index);
       
       void decreaseNwrap();
       void increaseListSize();
       
       void increaseNwrap();
       
       void changePercentCover(unsigned long newmaxsize);
       
       unsigned long getRandLineage(NRrand &rand_no);
       
       unsigned long getSpecies(unsigned long index);
       
       unsigned long getNext();
       
       unsigned long getNwrap();
       
       unsigned long getListsize();
       
       unsigned long getMaxsize();
       
       void wipeList();
       
       friend ostream& operator<<(ostream& os,const SpeciesList& r);
       
       friend istream& operator>>(istream& is, SpeciesList& r);
   };
   
   #endif
