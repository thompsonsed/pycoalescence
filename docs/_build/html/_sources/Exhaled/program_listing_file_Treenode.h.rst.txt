
.. _program_listing_file_Treenode.h:

Program Listing for File Treenode.h
========================================================================================

- Return to documentation for :ref:`file_Treenode.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   // Datapoint.cpp version 1.01
   // Author - Samuel Thompson - Imperial College London
   // with large use of code supplied by James Rosindell (Imperial College London)
   // This file contains the datapoint class for usage in coalescence simulations.
   #ifndef TREENODE
   #define TREENODE
   # define version1_01
   
   /************************************************************
                           TREENODE OBJECT
    ************************************************************/
   #include <stdio.h>
   #include <iostream>
   #include <iomanip>
   #include "Logging.h"
   
   using namespace std;
   class Treenode
   {
       
   private:
       bool tip;
       // 0 means that this node is just here to mark a coalescense
       // and therefore this node of no real other relevance
       // 1 means that this node is a leaf node and counts towards diversity
       unsigned long parent;
       // this stores the parent of the individual
       // 0 means there is no parent - we are at the end of the tree
       // (as far as has been calculated)
       bool speciated;
       // true if this lineage has speciated in which case it should not have a parent
       // because under the present implementation lineages are not traced beyond speciation
       
       // boolean for checking whether the lineage actually exists at the end. If all children of the lineages have speciated, then the lineage no longer exists.
       bool does_exist;
       
       // the species identity of the node
       unsigned long species_id;
      
       // the following 4 variables describe the position of the lineage in the present day.
       unsigned long xpos;
       // x position
       unsigned long ypos;
       // y position
       long xwrap;
       // number of wraps of x around the torus
       long ywrap;
       // number of wraps of y around the torus
       
       long double dSpec;
       // the speciation probability. This needs to be multiplied by the number of generations in order to generate the actual probability.
       unsigned long iGen;
       long double generation_added;
   public:
       Treenode() : tip(false),parent(0),speciated(false),does_exist(false),species_id(0),xpos(0),ypos(0),xwrap(0),ywrap(0), dSpec(0), iGen(0),generation_added(0)
       {
           
       }
       
       ~Treenode()
       = default;
   
       void setup(bool z, unsigned long xp, unsigned long yp, long xi, long yi)
       {
           tip = z;
           parent = 0;
           speciated = false;
           
           species_id = 0;
           
           xpos = xp;
           ypos = yp;
           xwrap = xi;
           ywrap = yi;
           dSpec =0;
           iGen = 0;
           generation_added = 0;
       }
       
       void setup(bool z , long xp , long yp , long xi , long yi, long double generation)
       {
           tip = z;
           parent = 0;
           speciated = false;
           
           species_id = 0;
           xpos = xp;
           ypos = yp;
           xwrap = xi;
           ywrap = yi;
           dSpec =0;
           iGen = 0;
           generation_added = generation;
       }
       // standard setters
       
       void setExistance(bool b)
       {
           does_exist = b;
       }
       
       void setParent(unsigned long x)
       {
           parent = x;
       }
       
       void qReset()
       {
           species_id = 0;
           does_exist = false;
           speciated = false;
       }
       
       void setPosition(long x,long y, long xw, long yw)
       {
           xpos = x;
           ypos = y;
           xwrap = xw;
           ywrap = yw;
       }
       
       void setSpec(long double d)
       {
           dSpec = d;
       }
       
       void setIGen(unsigned long g)
       {
           iGen = g;
       }
       
       void setGeneration(long double d)
       {
           generation_added = d;
       }
       
       void setSpeciation(bool s)
       {
           speciated = s;
       }
       
       void burnSpecies(unsigned long idin)
       {
           if (species_id == 0)
           {
               species_id = idin;
           }
       }
       
       void setTip(bool b)
       {
           tip = b;
       }
       
       void resetSpecies()
       {
           species_id =0;
       }
       
       void increaseGen()
       {
           iGen++;
       }
       // we don't allow the other variables to be changed
       // because they only need to be set once at the start of the coalescence
       // it's actually safer to leave out setters.
       // similarly we don't allow speciation to be changed once it has been set.
       
       // standard getters
       
       bool getExistance()
       {
           return does_exist;
       }
       
       bool isTip()
       {
           return tip;
       }
       
       unsigned long getParent()
       {
           return parent;
       }
   
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
       
       bool hasSpeciated()
       {
           return (speciated);
       }
       
       unsigned long getSpeciesID()
       {
           return (species_id);
       }
       
       long double getSpecRate()
       {
           return dSpec;
       }
       
       unsigned long getGenRate()
       {
           return iGen;
       }
       
       long double getGeneration()
       {
           return generation_added;
       }
       // routines
       
       void speciate()
       {
           speciated = true;
   //      parent = -1;
       }
       
       friend ostream& operator<<(ostream& os,const Treenode& t) 
       { 
           //os << m.numRows<<" , "<<m.numCols<<" , "<<endl; 
           //
           os << setprecision(64);
           os <<t.tip << "," << t.parent << "," << t.speciated << "," << t.does_exist << "," << t.species_id << "," << t.xpos << "," << t.ypos << "," << t.xwrap << ",";
           os << t.ywrap << "," << t.dSpec << "," << t.iGen << "," << t.generation_added << "\n";
           return os; 
       }
       
       friend istream& operator>>(istream& is,Treenode& t) 
       { 
           //is << m.numRows<<" , "<<m.numCols<<" , "<<endl; 
           char delim;
           is >>t.tip >> delim >> t.parent >> delim >> t.speciated >> delim >> t.does_exist >> delim >> t.species_id >> delim >> t.xpos >> delim;
           is >> t.ypos >> delim >> t.xwrap >> delim >> t.ywrap >> delim >> t.dSpec >> delim >> t.iGen >> delim >> t.generation_added;
           return is; 
       }
   };
   
   #endif
