
.. _program_listing_file_Step.h:

Program Listing for File Step.h
========================================================================================

- Return to documentation for :ref:`file_Step.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef STEP_H
   #define STEP_H
   
   struct Step
   {
       unsigned long chosen, coalchosen;
       long oldx, oldy, oldxwrap, oldywrap;
       bool coal, bContinueSim;
       unsigned int iAutoComplete;
       double distance;
       double angle;
   #ifdef DEBUG
       string location; //  stores the location for debugging purposes.
   #endif
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
           iAutoComplete = 0;
           distance = 0.0;
           angle = 0.0;
   #ifdef DEBUG
           location = "none";
   #endif
   #ifdef verbose
           number_printed =0;
   #endif
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
           distance = 0.0;
           angle = 0.0;
   #ifdef DEBUG
           location = "none";
   #endif
       }
       
       
   };
   
   #endif
