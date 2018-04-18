
.. _program_listing_file_applyspecmodule.h:

Program Listing for File applyspecmodule.h
==========================================

- Return to documentation for :ref:`file_applyspecmodule.h`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   
   #include <Python.h>
   #ifndef PYTHON_COMPILE
   #define PYTHON_COMPILE
   #endif
   #include <vector>
   #include <string>
   
   
   #ifndef APPLY_SPEC_IMPORT
   #define APPLY_SPEC_IMPORT
   using namespace std;
   struct module_state
   {
       PyObject *error;
   };
   
   #if PY_MAJOR_VERSION >= 3
   #define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
   #else
   #define GETSTATE(m) (&_state)
   static struct module_state _state;
   #endif
   
   static PyObject *ApplySpeciationError;
   
   // Conditional compilation for python >= 3.0 (changed how python integration worked)
   #if PY_MAJOR_VERSION >= 3
   #define INITERROR return NULL
   
   PyMODINIT_FUNC
   PyInit_applyspecmodule(void)
   #else
   #define INITERROR return
   
   PyMODINIT_FUNC
   initapplyspecmodule(void)
   #endif
   ;
   #endif
   
