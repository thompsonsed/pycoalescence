
.. _program_listing_file_necsim_double_comparison.h:

Program Listing for File double_comparison.h
============================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_double_comparison.h>` (``necsim/double_comparison.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #ifndef NECSIM_DOUBLECOMPARISON_H
   #define NECSIM_DOUBLECOMPARISON_H
   
   bool doubleCompare(double d1, double d2, double epsilon);
   
   bool doubleCompare(long double d1, long double d2, long double epsilon);
   
   bool doubleCompare(long double d1, long double d2, double epsilon);
   
   #endif //NECSIM_DOUBLECOMPARISON_H
