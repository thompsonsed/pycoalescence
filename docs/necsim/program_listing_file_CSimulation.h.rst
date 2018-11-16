
.. _program_listing_file_CSimulation.h:

Program Listing for File CSimulation.h
======================================

|exhale_lsh| :ref:`Return to documentation for file <file_CSimulation.h>` (``CSimulation.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #ifndef PY_TREE_NECSIM
   #define PY_TREE_NECSIM
   
   #include <Python.h>
   #include <structmember.h>
   #include <memory>
   #include "ConfigParser.h"
   #include "necsim/Tree.h"
   #include "necsim/SpatialTree.h"
   #include "necsim/ProtractedTree.h"
   #include "necsim/ProtractedSpatialTree.h"
   #include "PyLogging.h"
   #include "necsim.h"
   #include "PyImports.h"
   #include "PyTemplates.h"
   
   using namespace std;
   
   template<class T>
   static PyObject *importConfig(PyTemplate<T> *self, PyObject *args)
   {
       char *input;
       // parse arguments
       if(!PyArg_ParseTuple(args, "s", &input))
       {
           return nullptr;
       }
       try
       {
           string config_file = input;
           getGlobalLogger(self->logger, self->log_function);
           self->base_object->wipeSimulationVariables();
           self->base_object->importSimulationVariables(config_file);
       }
       catch(exception &e)
       {
           removeGlobalLogger();
           PyErr_SetString(necsimError, e.what());
           return nullptr;
       }
       Py_RETURN_NONE;
   }
   
   template<class T>
   static PyObject *importConfigFromString(PyTemplate<T> *self, PyObject *args)
   {
       char *input;
       // parse arguments
       if(!PyArg_ParseTuple(args, "s", &input))
       {
           return nullptr;
       }
       try
       {
           stringstream ss;
           ss << input;
           istream &istream1 = ss;
           getGlobalLogger(self->logger, self->log_function);
           self->base_object->wipeSimulationVariables();
           ConfigParser config;
           config.parseConfig(istream1);
           self->base_object->importSimulationVariables(config);
       }
       catch(exception &e)
       {
           removeGlobalLogger();
           PyErr_SetString(necsimError, e.what());
           return nullptr;
       }
       Py_RETURN_NONE;
   }
   
   template<class T>
   static PyObject *setup(PyTemplate<T> *self, PyObject *args)
   {
       // Set up the simulation, catch and return any errors.
       try
       {
           getGlobalLogger(self->logger, self->log_function);
           self->base_object->setup();
       }
       catch(exception &e)
       {
           removeGlobalLogger();
           PyErr_SetString(necsimError, e.what());
           return nullptr;
       }
       Py_RETURN_NONE;
   }
   
   template<class T>
   static PyObject *run(PyTemplate<T> *self, PyObject *args)
   {
       // Run the program, catch and return any errors.
       try
       {
           getGlobalLogger(self->logger, self->log_function);
           if(self->base_object->runSimulation())
           {
               Py_RETURN_TRUE;
           }
       }
       catch(exception &e)
       {
           removeGlobalLogger();
           PyErr_SetString(necsimError, e.what());
           return nullptr;
       }
       Py_RETURN_FALSE;
   }
   
   template<class T>
   static PyObject *applySpeciationRates(PyTemplate<T> *self, PyObject *args)
   {
       // parse arguments
       // Mimic a command-line simulation call
       // Run the program, catch and return any errors.
       try
       {
           PyObject *list_speciation_rates;
           vector<double> spec_rates;
           if(!PyArg_ParseTuple(args, "|O!", &PyList_Type, &list_speciation_rates))
           {
               return nullptr;
           }
           if(!importPyListToVectorDouble(list_speciation_rates, spec_rates, "Speciation rates must be floats."))
           {
               return nullptr;
           }
           getGlobalLogger(self->logger, self->log_function);
           if(!spec_rates.empty())
           {
               vector<long double> spec_rates_long(spec_rates.begin(), spec_rates.end());
               self->base_object->addSpeciationRates(spec_rates_long);
           }
           self->base_object->applyMultipleRates();
       }
       catch(exception &e)
       {
           removeGlobalLogger();
           PyErr_SetString(necsimError, e.what());
           return nullptr;
       }
       Py_RETURN_NONE;
   }
   
   template<class T>
   static PyObject *setupResume(PyTemplate<T> *self, PyObject *args)
   {
       char *pause_directory;
       char *out_directory;
       int seed, task, max_time;
       // parse arguments
       if(!PyArg_ParseTuple(args, "ssiii", &pause_directory, &out_directory, &seed, &task, &max_time))
       {
           return nullptr;
       }
       // Set up the resume current_metacommunity_parameters.
       string pause_directory_str, out_directory_str;
       pause_directory_str = pause_directory;
       out_directory_str = out_directory;
       try
       {
           getGlobalLogger(self->logger, self->log_function);
           self->base_object->wipeSimulationVariables();
           self->base_object->setResumeParameters(pause_directory_str, out_directory_str, seed, task, max_time);
           self->base_object->checkSims(pause_directory_str, seed, task);
           if(self->base_object->hasPaused())
           {
               self->base_object->setup();
           }
           else
           {
               throw runtime_error("Couldn't find paused simulation");
           }
       }
       catch(exception &e)
       {
           removeGlobalLogger();
           PyErr_SetString(necsimError, e.what());
           return nullptr;
       }
       Py_RETURN_NONE;
   }
   
   template<class T>
   static PyMethodDef *genPySimulationMethods()
   {
       static PyMethodDef PySimulationMethods[] = {
               {"import_from_config",        (PyCFunction) importConfig<T>,           METH_VARARGS,
                       "Import the simulation variables from a config file"},
               {"import_from_config_string", (PyCFunction) importConfigFromString<T>, METH_VARARGS,
                       "Import the simulation variables from a config file"},
               {"run",                       (PyCFunction) run<T>,                    METH_VARARGS,
                       "Run the simulation"},
               {"setup",                     (PyCFunction) setup<T>,                  METH_VARARGS,
                       "Set up the simulation, importing the maps and assigning the variables."},
               {"apply_speciation_rates",    (PyCFunction) applySpeciationRates<T>,   METH_VARARGS,
                       "Applies the speciation rates to the completed simulation. Can optionally provide a list of additional speciation rates to apply"},
               {"setup_resume",              (PyCFunction) setupResume<T>,            METH_VARARGS,
                       "Sets up for resuming from a paused simulation."},
               {nullptr}  /* Sentinel */
       };
       return PySimulationMethods;
   }
   
   template<class T>
   PyTypeObject genSimulationType(char *tp_name, char *tp_doc)
   {
       auto genPyTemplateGetSetters = PyTemplate_gen_getsetters<T>();
       auto genPyTemplateNew = PyTemplate_new<T>;
       auto genPyTemplateInit = PyTemplate_init<T>;
       auto genPyTemplateDealloc = PyTemplate_dealloc<T>;
       auto genPyTemplateTraverse = PyTemplate_traverse<T>;
       auto genPyTemplateMethods = genPySimulationMethods<T>();
       PyTypeObject ret_Simulation_Type = {
               PyVarObject_HEAD_INIT(nullptr, 0)
       };
       ret_Simulation_Type.tp_name = tp_name;
       ret_Simulation_Type.tp_doc = tp_doc;
   
       ret_Simulation_Type.tp_basicsize = sizeof(PyTemplate<T>);
       ret_Simulation_Type.tp_itemsize = 0;
       ret_Simulation_Type.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC;
       ret_Simulation_Type.tp_new = genPyTemplateNew;
       ret_Simulation_Type.tp_init = (initproc) genPyTemplateInit;
       ret_Simulation_Type.tp_dealloc = (destructor) genPyTemplateDealloc;
       ret_Simulation_Type.tp_traverse = (traverseproc) genPyTemplateTraverse;
   //      .tp_members = PyTemplate_members<T>,
       ret_Simulation_Type.tp_methods = genPyTemplateMethods;
       ret_Simulation_Type.tp_getset = genPyTemplateGetSetters;
       return ret_Simulation_Type;
   }
   
   static PyTypeObject C_SpatialSimulationType = genSimulationType<SpatialTree>((char *) "libnecsim.CSpatialSimulation",
                                                                                (char *) "C class for spatial simulations.");
   static PyTypeObject C_NSESimulationType = genSimulationType<Tree>((char *) "libnecsim.CNSESimulation",
                                                                     (char *) "C class for non-spatial simulations.");
   static PyTypeObject C_ProtractedSpatialSimulationType = genSimulationType<ProtractedSpatialTree>(
           (char *) "libnecsim.CPSpatialSimulation",
           (char *) "C class for protracted spatial simulations.");
   static PyTypeObject C_ProtractedNSESimulationType = genSimulationType<ProtractedTree>(
           (char *) "libnecsim.CPNSESimulation",
           (char *) "C class for protracted non-spatial simulations.");
   
   #endif // PY_TREE_NECSIM
