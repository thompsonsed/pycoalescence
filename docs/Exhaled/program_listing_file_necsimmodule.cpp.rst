
.. _program_listing_file_necsimmodule.cpp:

Program Listing for File necsimmodule.cpp
========================================================================================

- Return to documentation for :ref:`file_necsimmodule.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details
   #define PYTHON_COMPILE
   #include <Python.h>
   #include <vector>
   #include <string>
   #include <unistd.h>
   #include <signal.h>
   
   // These are included here for compabilitity reasons
   #include "Setup.h"
   #include "Logging.h"
    // This provides compability for protracted speciation events.
   #include "Tree.h"
   #include "ProtractedTree.h"
   #include "necsimmodule.h"
   
   
   using namespace std;
   PyObject * loggingmodule;
   PyGILState_STATE gstate;
   bool log_set = false;
   bool logger_set = false;
   PyObject * logger;
   
   
   static PyObject * necsim(PyObject * self, PyObject * args)
   {
       char * input;
       // parse arguments
       if(!PyArg_ParseTuple(args, "s", &input))
       {
           return NULL;
       }
       
       // Run the main simulation
       // Mimic a command-line simulation call
       vector<string> comargs;
       comargs.push_back("./NECSim");
       comargs.push_back("-c");
       comargs.push_back(input);
       int ret = 0;
       // Check that the logging function has been set
       if(!log_set)
       {
           PyErr_SetString(NECSimError, "Logging function has not been set. Make sure set_logging_function() has been called");
           return NULL;
       }
       if(!logger_set)
       {
           PyErr_SetString(NECSimError, "Logger object has not been set. Make sure set_logger() has been called");
           return NULL;
       }
       // Run the program, catch and return any errors.
       try
       {
           Py_INCREF(logger);
           ret = runMain(comargs.size(), comargs);
           Py_DECREF(logger);
       }
       catch(exception &e)
       {
           Py_DECREF(logger);
           PyErr_SetString(NECSimError, e.what());
           return NULL;
       }
       PyObject * pyret;
       pyret = PyLong_FromLong(ret);
       return pyret;
   }
   
   static PyObject * resume_sim(PyObject * self, PyObject * args)
   {
       char * pause_directory;
       char* out_directory;
       int size1, size2, seed, task, max_time;
       // parse arguments
       if(!PyArg_ParseTuple(args, "ssiii", &pause_directory, &out_directory, &seed, &task, &max_time))
       {
           return NULL;
       }
       if(!log_set)
       {
           PyErr_SetString(NECSimError, "Logging function has not been set. Make sure set_logging_function() has been called");
           return NULL;
       }
       if(!logger_set)
       {
           PyErr_SetString(NECSimError, "Logger object has not been set. Make sure set_logger() has been called");
           return NULL;
       }
       // Run the main simulation
       int ret = 0;
       // Run the program, catch and return any errors.
       string pause_directory_str, out_directory_str;
       pause_directory_str = pause_directory;
       out_directory_str = out_directory;
       bool sim_complete = false;
       try
       {
           Py_INCREF(logger);
           Tree t;
           t.setResumeParameters(pause_directory_str, out_directory_str, seed, task, max_time);
           t.checkSims(pause_directory_str, seed, task);
           if(t.getbPaused())
           {
               t.setup();
               sim_complete = t.runSimulation();
               if(sim_complete)
               {
                   t.applyMultipleRates();
               }
           }
           else
           {
               throw runtime_error("Couldn't find paused simulation");
           }
           Py_DECREF(logger);
           if(sim_complete)
           {
               Py_RETURN_TRUE;
           }
           else
           {
               Py_RETURN_FALSE;
           }
           
           
       }
       catch(exception &e)
       {
           Py_DECREF(logger);
   //      cout << e.what() << endl;
           PyErr_SetString(NECSimError, e.what());
           return NULL;
       }
   }
   
   
   static PyObject * necsim_protracted(PyObject * self, PyObject * args)
   {
       char * input;
       // parse arguments
       if(!PyArg_ParseTuple(args, "s", &input))
       {
           return NULL;
       }
       
       // Run the main simulation
       // Mimic a command-line simulation call
       vector<string> comargs;
       comargs.push_back("./NECSim");
       comargs.push_back("-c");
       comargs.push_back(input);
       int ret = 0;
       // Check that the logging function has been set
       if(!log_set)
       {
           PyErr_SetString(NECSimError, "Logging function has not been set. Make sure set_logging_function() has been called");
           return NULL;
       }
       if(!logger_set)
       {
           PyErr_SetString(NECSimError, "Logger object has not been set. Make sure set_logger() has been called");
           return NULL;
       }
       // Run the program, catch and return any errors.
       try
       {
           Py_INCREF(logger);
           ret = runMainProtracted(comargs.size(), comargs);
           Py_DECREF(logger);
       }
       catch(exception &e)
       {
           Py_DECREF(logger);
           PyErr_SetString(NECSimError, e.what());
           return NULL;
       }
       PyObject * pyret;
       pyret = PyLong_FromLong(ret);
       return pyret;
   }
   
   static PyObject * resume_protracted_sim(PyObject * self, PyObject * args)
   {
       char * pause_directory;
       char* out_directory;
       int size1, size2, seed, task, max_time;
       // parse arguments
       if(!PyArg_ParseTuple(args, "ssiii", &pause_directory, &out_directory, &seed, &task, &max_time))
       {
           return NULL;
       }
       if(!log_set)
       {
           PyErr_SetString(NECSimError, "Logging function has not been set. Make sure set_logging_function() has been called");
           return NULL;
       }
       if(!logger_set)
       {
           PyErr_SetString(NECSimError, "Logger object has not been set. Make sure set_logger() has been called");
           return NULL;
       }
       // Run the main simulation
       int ret = 0;
       // Run the program, catch and return any errors.
       string pause_directory_str, out_directory_str;
       pause_directory_str = pause_directory;
       out_directory_str = out_directory;
       bool sim_complete = false;
       try
       {
           Py_INCREF(logger);
           ProtractedTree t;
           t.setResumeParameters(pause_directory_str, out_directory_str, seed, task, max_time);
           t.checkSims(pause_directory_str, seed, task);
           if(t.getbPaused())
           {
               t.setup();
               sim_complete = t.runSimulation();
               if(sim_complete)
               {
                   t.applyMultipleRates();
               }
           }
           else
           {
               throw runtime_error("Couldn't find paused simulation");
           }
           Py_DECREF(logger);
           if(sim_complete)
           {
               Py_RETURN_TRUE;
           }
           else
           {
               Py_RETURN_FALSE;
           }
           
           
       }
       catch(exception &e)
       {
           Py_DECREF(logger);
   //      cout << e.what() << endl;
           PyErr_SetString(NECSimError, e.what());
           return NULL;
       }
   }
   
   
   static PyMethodDef NECSimMethods[] = 
   {
       {"run_from_config", necsim, METH_VARARGS, "Runs the simulation from the provided config file."},
       {"protracted_run_from_config", necsim_protracted, METH_VARARGS, "Runs the protracted simulation from the provided config file."},
       {"set_log_function", set_log_function, METH_VARARGS, "calls logging"},
       {"set_logger", set_logger, METH_VARARGS, "Sets the logger to use"},
       {"resume", resume_sim, METH_VARARGS, "Resumes the simulation with the given parameters"},
       {"protracted_resume", resume_protracted_sim, METH_VARARGS, "Resumes the protracted simulation with the given parameters"},
       {NULL, NULL, 0 , NULL}
   };
   
   // Conditional compilation for python >= 3.0 (changed how python integration worked)
   #if PY_MAJOR_VERSION >= 3
   static int necsim_traverse(PyObject *m, visitproc visit, void *arg)
   {
       Py_VISIT(GETSTATE(m)->error);
       return 0;
   }
   
   static int necsim_clear(PyObject *m)
   {
       Py_CLEAR(GETSTATE(m)->error);
       return 0;
   }
   
   #endif
   
   
   #if PY_MAJOR_VERSION >= 3
   static struct PyModuleDef moduledef =
   {
       PyModuleDef_HEAD_INIT,
       "necsimmodule",
       NULL,
       sizeof(struct module_state),
       NECSimMethods,
       NULL,
       necsim_traverse,
       necsim_clear,
       NULL
   };
   
   
   #define INITERROR return NULL
   
   PyMODINIT_FUNC
   PyInit_necsimmodule(void)
   #else
   #define INITERROR return
   
   PyMODINIT_FUNC
   initnecsimmodule(void)
   #endif
   {
       PyObject *module;
       #if PY_MAJOR_VERSION>=3
       module = PyModule_Create(&moduledef);
       #else
       module = Py_InitModule("necsimmodule", NECSimMethods);
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
       NECSimError = PyErr_NewException((char*)"necsimmodule.NECSimError", NULL, NULL);
       Py_INCREF(NECSimError);
       PyModule_AddObject(module, "NECSimError", NECSimError);
       #if PY_MAJOR_VERSION >= 3
       return module;
       #endif
   }
