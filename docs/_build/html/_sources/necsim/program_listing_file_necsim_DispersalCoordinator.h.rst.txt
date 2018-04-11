
.. _program_listing_file_necsim_DispersalCoordinator.h:

Program Listing for File DispersalCoordinator.h
===============================================

- Return to documentation for :ref:`file_necsim_DispersalCoordinator.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef DISPERSALCOORDINATOR_H
   #define DISPERSALCOORDINATOR_H
   
   #include <cstring>
   #include <cstdio>
   #include <iostream>
   #include <fstream>
   #include <stdexcept>
   #include <cmath>
   
   #include "NRrand.h"
   #include "Map.h"
   #include "Step.h"
   #include "Landscape.h"
   
   class DispersalCoordinator
   {
   protected:
       
       // Our map of dispersal probabilities (if required)
       // This will contain cummulative probabilities across rows
       // So dispersal is from the y cell to each of the x cells.
       Map<double> dispersal_prob_map;
       // Our random number generator for dispersal distances
       // This is a pointer so that the random number generator is the same
       // across the program.
       
       NRrand * NR;
       // Pointer to the habitat map object for getting density values.
       Landscape * habitat_map;
       // Pointer to the generation counter for the simulation
       double * generation;
       
       // function ptr for our getDispersal function
       typedef void (DispersalCoordinator::*dispersal_fptr)(Step &this_step);
       dispersal_fptr doDispersal;
       
       // Function pointer for end checks
       typedef bool (DispersalCoordinator::*end_fptr)(const unsigned long &density, long &oldx, long &oldy, long &oldxwrap,
                                            long &oldywrap, const long &startx, const long &starty, 
                                            const long &startxwrap, const long &startywrap); 
       // once setup will contain the end check function to use for this simulation.
       end_fptr checkEndPointFptr;
       unsigned long xdim;
       
   public:
       DispersalCoordinator();
       
       ~DispersalCoordinator();
       
       void setRandomNumber(NRrand * NR_ptr);
       
       void setHabitatMap(Landscape *map_ptr);
       
       void setGenerationPtr(double * generation_ptr);
   
   
       void setDispersal(const string &dispersal_method, const string &dispersal_file,
                         const unsigned long dispersal_x, const unsigned long dispersal_y,
                         const double &m_probin, const double &cutoffin,
                         const double &sigmain, const double &tauin, const bool &restrict_self);
   
       void setDispersal(SimParameters * simParameters);
       void disperseNullDispersalMap(Step &this_step);
       
       void disperseDispersalMap(Step &this_step);
       
       
       void calculateCellCoordinates(Step & this_step, const unsigned long &col_ref);
       
       unsigned long calculateCellReference(Step &this_step);
       
       void disperseDensityMap(Step &this_step);
       
       void setEndPointFptr(const bool &restrict_self);
       
       bool checkEndPoint(const unsigned long & density, long &oldx, long &oldy, long &oldxwrap, long &oldywrap,
                           const long &startx, const long &starty, const long &startxwrap, const long &startywrap);
       
       
       bool checkEndPointDensity(const unsigned long &density, long &oldx, long &oldy, long &oldxwrap, long &oldywrap,
                                  const long &startx, const long &starty, const long &startxwrap, const long &startywrap);
       
       
       bool checkEndPointRestricted(const unsigned long &density, long &oldx, long &oldy, long &oldxwrap, long &oldywrap,
                                     const long &startx, const long &starty, const long &startxwrap, const long &startywrap);
       
       
       void disperse(Step &this_step);
       
   };
   
   #endif // DISPERSAL_H
