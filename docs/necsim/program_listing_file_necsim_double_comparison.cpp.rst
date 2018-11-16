
.. _program_listing_file_necsim_double_comparison.cpp:

Program Listing for File double_comparison.cpp
==============================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_double_comparison.cpp>` (``necsim/double_comparison.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #include <cmath>
   
   using namespace std;
   
   bool doubleCompare(double d1, double d2, double epsilon)
   {
       return (abs(float(d1 - d2)) < epsilon);
   }
   
   bool doubleCompare(long double d1, long double d2, long double epsilon)
   {
       return abs((d1 - d2)) < epsilon;
   }
   
   bool doubleCompare(long double d1, long double d2, double epsilon)
   {
       return abs((d1 - d2)) < epsilon;
   }
