
.. _program_listing_file_necsim_TreeNode.h:

Program Listing for File TreeNode.h
===================================

- Return to documentation for :ref:`file_necsim_TreeNode.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef TREENODE
   #define TREENODE
   #include <cstdio>
   #include <iostream>
   #include <iomanip>
   #include "Logger.h"
   
   using namespace std;
   class TreeNode
   {
       
   private:
       // 0 means that this node is just here to mark a coalescense
       // and therefore this node of no real other relevance
       // 1 means that this node is a leaf node and counts towards diversity
       bool tip;
       // this stores the parent of the individual
       // 0 means there is no parent - we are at the end of the tree
       // (as far as has been calculated)
       unsigned long parent;
       // true if this lineage has speciated in which case it should not have a parent
       // because under the present implementation lineages are not traced beyond speciation
       // boolean for checking whether the lineage actually exists at the end. If all children of the lineages have
       // speciated, then the lineage no longer exists.
       bool speciated;
       // the species identity of the node
       bool does_exist;
       // the following 4 variables describe the position of the lineage in the present day.
       unsigned long species_id;
       // x position
       unsigned long xpos;
       // y position
       unsigned long ypos;
       // number of wraps of x around the torus
       long xwrap;
       // number of wraps of y around the torus
       long ywrap;
       // the speciation probability. This needs to be multiplied by the number of generations in order to generate the
       // actual probability.
       long double speciation_probability;
       // Number of generations this lineage has existed since coalescence (or tracking began).
       unsigned long generations_existed;
       // Simulation generation timer that the lineage was created at
       long double generation_added;
   public:
       TreeNode() : tip(false),parent(0),speciated(false),does_exist(false),species_id(0),xpos(0),ypos(0),xwrap(0),
                    ywrap(0), speciation_probability(0), generations_existed(0),generation_added(0)
       {
           
       }
       
       ~TreeNode()
       = default;
   
       void setup(bool z, unsigned long xp, unsigned long yp, long xi, long yi);
   
       void setup(bool z);
   
       void setup(const bool &is_tip, const long &xp, const long &yp, const long &xi, const long &yi,
                  const long double &generation);
   
       void setExistence(bool b);
       
       void setParent(unsigned long x);
       
       void qReset();
       
       void setPosition(long x,long y, long xw, long yw);
       
       void setSpec(long double d);
       
       void setGenerationRate(unsigned long g);
       
       void setGeneration(long double d);
       
       void setSpeciation(bool s);
       
       void burnSpecies(unsigned long idin);
       
       void setTip(bool b);
       
       void resetSpecies();
       
       void increaseGen();
       // we don't allow the other variables to be changed
       // because they only need to be set once at the start of the coalescence
       // it's actually safer to leave out setters.
       // similarly we don't allow speciation to be changed once it has been set.
       
       // standard getters
       
       bool getExistence();
       
       bool isTip();
       
       unsigned long getParent();
   
       unsigned long getXpos();
       
       unsigned long getYpos();
       
       long getXwrap();
       
       long getYwrap();
       
       bool hasSpeciated();
       
       unsigned long getSpeciesID();
       
       long double getSpecRate();
       
       unsigned long getGenRate();
       
       long double getGeneration();
   
       void speciate();
   
   
       
       friend ostream& operator<<(ostream& os,const TreeNode& t);
       
       friend istream& operator>>(istream& is,TreeNode& t);
   
       TreeNode & operator=(const TreeNode &t);
   #ifdef DEBUG
   
       void logLineageInformation(const int &level);
   #endif // DEBUG
   };
   #endif
