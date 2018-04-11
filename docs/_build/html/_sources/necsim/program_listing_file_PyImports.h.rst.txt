
.. _program_listing_file_PyImports.h:

Program Listing for File PyImports.h
====================================

- Return to documentation for :ref:`file_PyImports.h`

.. code-block:: cpp

   //
   // Created by Sam Thompson on 02/04/2018.
   //
   
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
