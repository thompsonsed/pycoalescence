
.. _program_listing_file_applyspecmodule.cpp:

Program Listing for File applyspecmodule.cpp
============================================

- Return to documentation for :ref:`file_applyspecmodule.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef PYTHON_COMPILE
   #define PYTHON_COMPILE
   #endif
   #include <Python.h>
   #include <vector>
   #include <string>
   #include <cstring>
   #include <unistd.h>
   #include <signal.h>
   
   #include "applyspecmodule.h"
   #include "PyLogging.h"
   #include "necsim/Community.h"
   #include "necsim/Metacommunity.h"
   
   PyObject * loggingmodule;
   PyGILState_STATE gstate;
   bool log_set = false;
   bool logger_set = false;
   PyObject * logger;
   
   template<class T> void createCommunity(string database_str, bool use_spatial, string sample_file,
                                          string time_config_file, string fragment_file, vector<double> & speciation_rates,
                                          double min_speciation_gen, double max_speciation_gen,
                                          unsigned long metacommunity_size, double metacommunity_speciation_rate)
   {
       T community;
       SpecSimParameters speciation_parameters;
       speciation_parameters.setup(database_str, use_spatial, sample_file, time_config_file,
                                   fragment_file, speciation_rates, min_speciation_gen, max_speciation_gen,
                                   metacommunity_size, metacommunity_speciation_rate);
       community.apply(&speciation_parameters);
   }
   
   static PyObject * apply(PyObject * self, PyObject * args)
   {
       char * database;
       int record_spatial;
       char * sample_file;
       char * time_config_file;
       char * fragment_file;
       double min_spec_gen = 0.0;
       double max_spec_gen = 0.0;
       unsigned long metacommunity_size = 0;
       double metacommunity_speciation_rate = 0.0;
       PyObject *pList;
       PyObject *pItem;
       Py_ssize_t n;
       if (!PyArg_ParseTuple(args, "sisssO!|ddkd", &database, &record_spatial, &sample_file, &time_config_file,
                             &fragment_file, &PyList_Type, &pList, &min_spec_gen,
                             &max_spec_gen, &metacommunity_size, &metacommunity_speciation_rate))
       {
           return NULL;
       }
   #ifdef DEBUG
       if(metacommunity_size == 0)
       {
           writeLog(10, "Metacommunity size not set.");
       }
       else
       {
           writeLog(10, "Metacommunity size: " + to_string(metacommunity_size));
       }
   #endif // DEBUG
       if(max_spec_gen > 0.0 && min_spec_gen >= max_spec_gen)
       {
           PyErr_SetString(PyExc_TypeError, "Minimum protracted speciation generation must be less than maximum.");
       }
       else
       {
           min_spec_gen=0.0;
           max_spec_gen=0.0;
       }
       // Convert all our variables to the relevant form
       string database_str = database;
       bool use_spatial = record_spatial;
       string sample_file_str = sample_file;
       string time_config_file_str = time_config_file;
       string fragment_file_str = fragment_file;
   
       n = PyList_Size(pList);
       vector<double> spec_rates;
       for (int i=0; i<n; i++)
       {
           pItem = PyList_GetItem(pList, i);
           if(!PyFloat_Check(pItem))
           {
               PyErr_SetString(PyExc_TypeError, "Speciation rates must be floats.");
               return NULL;
           }
           double tmpspec = PyFloat_AS_DOUBLE(pItem);
           spec_rates.push_back(tmpspec);
       }
       // Now run the actual simulation
       try
       {
           if(metacommunity_size == 0)
           {
               Py_INCREF(logger);
               createCommunity<Community>(database_str, use_spatial, sample_file_str, time_config_file_str,
                                          fragment_file_str, spec_rates, min_spec_gen, max_spec_gen,
                                          metacommunity_size, metacommunity_speciation_rate);
               Py_DECREF(logger);
           }
           else
           {
               Py_INCREF(logger);
               createCommunity<Metacommunity>(database_str, use_spatial, sample_file_str, time_config_file_str,
                                          fragment_file_str, spec_rates, min_spec_gen, max_spec_gen,
                                          metacommunity_size, metacommunity_speciation_rate);
               Py_DECREF(logger);
           }
       }
       catch(exception &e)
       {
           Py_DECREF(logger);
           PyErr_SetString(ApplySpeciationError, e.what());
           return NULL;
       }
       Py_RETURN_NONE;
   }
   
   static PyMethodDef ApplySpecMethods[] = 
   {
       {"apply", apply, METH_VARARGS, "Applies the new speciation rate(s) to the coalescence tree."},
       {"set_log_function", set_log_function, METH_VARARGS, "calls logging"},
       {"set_logger", set_logger, METH_VARARGS, "Sets the logger to use"},
       {NULL, NULL, 0 , NULL}
   };
   
   // Conditional compilation for python >= 3.0 (changed how python integration worked)
   #if PY_MAJOR_VERSION >= 3
   static int applyspec_traverse(PyObject *m, visitproc visit, void *arg)
   {
       Py_VISIT(GETSTATE(m)->error);
       return 0;
   }
   
   static int applyspec_clear(PyObject *m)
   {
       Py_CLEAR(GETSTATE(m)->error);
       return 0;
   }
   
   #endif
   
   
   #if PY_MAJOR_VERSION >= 3
   static struct PyModuleDef moduledef =
   {
       PyModuleDef_HEAD_INIT,
       "applyspecmodule",
       NULL,
       sizeof(struct module_state),
       ApplySpecMethods,
       NULL,
       applyspec_traverse,
       applyspec_clear,
       NULL
   };
   
   
   #define INITERROR return NULL
   
   PyMODINIT_FUNC
   PyInit_applyspecmodule(void)
   #else
   #define INITERROR return
   
   PyMODINIT_FUNC
   initapplyspecmodule(void)
   #endif
   {
       PyObject *module;
       #if PY_MAJOR_VERSION>=3
       module = PyModule_Create(&moduledef);
       #else
       module = Py_InitModule("applyspecmodule", ApplySpecMethods);
       #endif
       if(module == NULL)
       {
           INITERROR;
       }
       // Threading support
       if(!PyEval_ThreadsInitialized())
       {
           PyEval_InitThreads();
           
       }
       ApplySpeciationError = PyErr_NewException((char*)"applyspec.Error", NULL, NULL);
       Py_INCREF(ApplySpeciationError);
       PyModule_AddObject(module, "ApplySpecError", ApplySpeciationError);
       #if PY_MAJOR_VERSION >= 3
       return module;
       #endif
   }
