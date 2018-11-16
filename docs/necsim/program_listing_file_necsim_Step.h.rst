
.. _program_listing_file_necsim_Step.h:

Program Listing for File Step.h
===============================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_Step.h>` (``necsim/Step.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef STEP_H
   #define STEP_H
   
   #include "Cell.h"
   
   struct Step
   {
       unsigned long chosen, coalchosen;
       long oldx, oldy, oldxwrap, oldywrap;
       bool coal, bContinueSim;
       unsigned int time_reference;
   #ifdef verbose
       long number_printed;
   #endif
   
       Step()
       {
           chosen = 0;
           coalchosen = 0;
           oldx = 0;
           oldy = 0;
           oldxwrap = 0;
           oldywrap = 0;
           coal = false;
           bContinueSim = true;
           time_reference = 0;
   #ifdef verbose
           number_printed =0;
   #endif
       }
   
       Step(const Cell & cell)
       {
           oldx = cell.x;
           oldy = cell.y;
           oldxwrap = 0;
           oldywrap = 0;
           coal = false;
           bContinueSim = true;
       }
       
       
       void wipeData()
       {
           chosen = 0;
           coalchosen = 0;
           oldx = 0;
           oldy = 0;
           oldxwrap = 0;
           oldywrap = 0;
           coal = false;
       }
       
       
   };
   
   #endif
