
.. _program_listing_file_necsim_ProtractedSpatialTree.h:

Program Listing for File ProtractedSpatialTree.h
================================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_ProtractedSpatialTree.h>` (``necsim/ProtractedSpatialTree.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   //
   #include "SpatialTree.h"
   #include "ProtractedTree.h"
   
   #ifndef SPECIATIONCOUNTER_PROTRACTEDSPATIALTREE_H
   #define SPECIATIONCOUNTER_PROTRACTEDSPATIALTREE_H
   
   
   class ProtractedSpatialTree : public virtual SpatialTree, public virtual ProtractedTree
   {
   
   };
   
   
   #endif //SPECIATIONCOUNTER_PROTRACTEDSPATIALTREE_H
