
.. _program_listing_file_dispersalmodule.cpp:

Program Listing for File dispersalmodule.cpp
========================================================================================

- Return to documentation for :ref:`file_dispersalmodule.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details
   #ifndef PYTHON_COMPILE
   #define PYTHON_COMPILE
   #endif
   #include <Python.h>
   #include <vector>
   #include <string>
   #include <cstring>
   #include <unistd.h>
   #include <signal.h>
   #include "dispersalmodule.h"
   
   PyObject * loggingmodule;
   PyGILState_STATE gstate;
   bool log_set = false;
   bool logger_set = false;
   PyObject * logger;
   
   static PyObject * test_dispersal(PyObject * self, PyObject * args)
   {
       char * output_database;
       char * map_file;
       char * dispersal_method;
       char * landscape_type;
       int map_x, map_y;
       double sigma, tau, m_prob, cutoff;
       int num_repeats, seed, is_sequential;
       
       // parse arguments
       if(!PyArg_ParseTuple(args, "ssssddddiiiii", &output_database, &map_file, &dispersal_method, &landscape_type,
                            &sigma, &tau, &m_prob, &cutoff, &num_repeats, &seed, &map_x, &map_y, &is_sequential))
       {
           return NULL;
       }
       try
       {
           SimulateDispersal disp_sim;
           disp_sim.setDispersalParameters(dispersal_method, sigma, tau, m_prob, cutoff, landscape_type);
           disp_sim.setSequential(bool(is_sequential));
           disp_sim.setOutputDatabase(output_database);
           disp_sim.setSeed(seed);
           disp_sim.setNumberRepeats(num_repeats);
           disp_sim.setSizes(map_x, map_y);
           disp_sim.importMaps(map_file);
           disp_sim.runDispersal();
           disp_sim.writeDatabase();
       }
       catch(exception &e)
       {
           PyErr_SetString(DispersalError, e.what());
           return NULL;
       }
       Py_RETURN_NONE;
   }
   
   
   static PyMethodDef DispersalMethods[] = 
   {
       {"test_dispersal", test_dispersal, METH_VARARGS, "Runs the dispersal function on the provided map."},
       {"set_log_function", set_log_function, METH_VARARGS, "calls logging"},
       {"set_logger", set_logger, METH_VARARGS, "Sets the logger to use"},
       {NULL, NULL, 0 , NULL}
   };
   
   // Conditional compilation for python >= 3.0 (changed how python integration worked)
   #if PY_MAJOR_VERSION >= 3
   static int dispersal_traverse(PyObject *m, visitproc visit, void *arg)
   {
       Py_VISIT(GETSTATE(m)->error);
       return 0;
   }
   
   static int dispersal_clear(PyObject *m)
   {
       Py_CLEAR(GETSTATE(m)->error);
       return 0;
   }
   
   #endif
   
   
   #if PY_MAJOR_VERSION >= 3
   static struct PyModuleDef moduledef =
   {
       PyModuleDef_HEAD_INIT,
       "dispersalmodule",
       NULL,
       sizeof(struct module_state),
       DispersalMethods,
       NULL,
       dispersal_traverse,
       dispersal_clear,
       NULL
   };
   
   
   #define INITERROR return NULL
   
   PyMODINIT_FUNC
   PyInit_dispersalmodule(void)
   #else
   #define INITERROR return
   
   PyMODINIT_FUNC
   initdispersalmodule(void)
   #endif
   {
       PyObject *module;
       #if PY_MAJOR_VERSION>=3
       module = PyModule_Create(&moduledef);
       #else
       module = Py_InitModule("dispersalmodule", DispersalMethods);
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
       DispersalError = PyErr_NewException((char*)"dispersal.Error", NULL, NULL);
       Py_INCREF(DispersalError);
       PyModule_AddObject(module, "DispersalError", DispersalError);
       #if PY_MAJOR_VERSION >= 3
       return module;
       #endif
   }
