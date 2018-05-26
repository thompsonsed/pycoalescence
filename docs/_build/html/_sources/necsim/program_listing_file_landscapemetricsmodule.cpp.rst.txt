
.. _program_listing_file_landscapemetricsmodule.cpp:

Program Listing for File landscapemetricsmodule.cpp
===================================================

- Return to documentation for :ref:`file_landscapemetricsmodule.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #ifndef PYTHON_COMPILE
   #define PYTHON_COMPILE
   #endif
   #include <Python.h>
   #include <vector>
   #include <string>
   #include "landscapemetricsmodule.h"
   #include "LandscapeMetricsCalculator.h"
   #include "PyLogging.h"
   #include "necsim/CPLCustomHandler.h"
   
   bool log_set = false;
   bool logger_set = false;
   PyObject * logger = nullptr;
   PyObject * call_logging = nullptr;
   
   
   static PyObject * calc_mean_distance(PyObject *self, PyObject *args)
   {
       char * map_file;
       // parse arguments
       if(!PyArg_ParseTuple(args, "s", &map_file))
       {
           return nullptr;
       }
       try
       {
           string map_path = map_file;
           LandscapeMetricsCalculator meanDistanceCalculator;
           meanDistanceCalculator.import(map_file);
           double mean_distance = meanDistanceCalculator.calculateMNN();
           return PyFloat_FromDouble(mean_distance);
   
       }
       catch(exception &e)
       {
           PyErr_SetString(LandscapeMetricsError, e.what());
           return nullptr;
       }
       Py_RETURN_NONE;
   }
   
   static PyObject * calc_clumpiness(PyObject *self, PyObject *args)
   {
       char * map_file;
       // parse arguments
       if(!PyArg_ParseTuple(args, "s", &map_file))
       {
           return nullptr;
       }
       try
       {
           string map_path = map_file;
           LandscapeMetricsCalculator meanDistanceCalculator;
           meanDistanceCalculator.import(map_file);
           double c = meanDistanceCalculator.calculateClumpiness();
           return PyFloat_FromDouble(c);
       }
       catch(exception &e)
       {
           PyErr_SetString(LandscapeMetricsError, e.what());
           return nullptr;
       }
       Py_RETURN_NONE;
   }
   
   
   
   
   static PyMethodDef LandscapeMetricsMethods[] =
   {
       {"set_log_function", set_log_function, METH_VARARGS, "calls logging"},
       {"set_logger", set_logger, METH_VARARGS, "Sets the logger to use"},
       {"calc_mean_distance", calc_mean_distance, METH_VARARGS, "Calculates the mean distance to the nearest neighbour"},
       {"calc_clumpiness", calc_clumpiness, METH_VARARGS, "Calculates the clumpiness of the landscape"},
       {nullptr, nullptr, 0 , nullptr}
   };
   
   // Conditional compilation for python >= 3.0 (changed how python integration worked)
   #if PY_MAJOR_VERSION >= 3
   static int landscape_metrics_traverse(PyObject *m, visitproc visit, void *arg)
   {
       Py_VISIT(GETSTATE(m)->error);
       return 0;
   }
   
   static int landscape_metrics_clear(PyObject *m)
   {
       Py_CLEAR(GETSTATE(m)->error);
       return 0;
   }
   
   #endif
   
   
   #if PY_MAJOR_VERSION >= 3
   static struct PyModuleDef moduledef =
   {
       PyModuleDef_HEAD_INIT,
       "landscapemetricsmodule",
       nullptr,
       sizeof(struct module_state),
       LandscapeMetricsMethods,
       nullptr,
       landscape_metrics_traverse,
       landscape_metrics_clear,
       nullptr
   };
   
   
   #define INITERROR return NULL
   
   PyMODINIT_FUNC
   PyInit_landscapemetricsmodule(void)
   #else
   #define INITERROR return
   
   PyMODINIT_FUNC
   initlandscapemetricsmodule(void)
   #endif
   {
       PyObject *module;
       #if PY_MAJOR_VERSION>=3
       module = PyModule_Create(&moduledef);
       #else
       module = Py_InitModule("landscapemetricsmodule", LandscapeMetricsMethods);
       #endif
       if(module == nullptr)
       {
           INITERROR;
       }
       // Threading support
       if(!PyEval_ThreadsInitialized())
       {
           PyEval_InitThreads();
           
       }
       LandscapeMetricsError = PyErr_NewException((char*)"landscape_metrics.Error", nullptr, nullptr);
       Py_INCREF(LandscapeMetricsError);
       PyModule_AddObject(module, "LandscapeMetricsError", LandscapeMetricsError);
       #if PY_MAJOR_VERSION >= 3
       return module;
       #endif
   }
