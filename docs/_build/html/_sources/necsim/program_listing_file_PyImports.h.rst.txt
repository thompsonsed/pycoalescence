
.. _program_listing_file_PyImports.h:

Program Listing for File PyImports.h
====================================

- Return to documentation for :ref:`file_PyImports.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #ifndef PYIMPORTS_H
   #define PYIMPORTS_H
   
   #include <Python.h>
   #include <utility>
   #include <vector>
   #include <string>
   using namespace std;
   
   
   bool importPyListToVectorString(PyObject *list_input, vector<string> &output, const string &err_msg);
   
   bool importPyListToVectorULong(PyObject *list_input, vector<unsigned long> &output, const string &err_msg);
   
   
   bool importPyListToVectorDouble(PyObject *list_input, vector<double> &output, const string &err_msg);
   #endif //SPECIATIONCOUNTER_PYIMPORTS_H
