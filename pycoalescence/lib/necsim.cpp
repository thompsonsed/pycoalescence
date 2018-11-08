// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file necsim.cpp
 * @brief Contains the functions allowing integration of the pycoalescence Python module directly to the c++
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */


#define PYTHON_COMPILE
#include <Python.h>
#include <string>
#include <vector>
#include <csignal>

// These are included here for compabilitity reasons
#include "setup.h"
// This provides compability for protracted speciation events.
#include "necsim.h"
#include "PyLogging.h"
#include "CSimulation.h"
#include "CCommunity.h"
#include "CSimulateDispersal.h"
#include "CLandscapeMetricsCalculator.h"


using namespace std;

#if PY_MAJOR_VERSION < 3
static PyMethodDef NecsimMethods[] =
{
	{NULL, NULL, 0 , NULL}
};
#endif // PY_MAJOR_VERSION



inline void readyPyTypeObject(PyTypeObject * obj)
{
	if (PyType_Ready(obj) < 0)
	{
		throw runtime_error("Cannot initialise PyTypeObject.");
	}
	Py_INCREF(obj);
}

#if PY_MAJOR_VERSION >= 3
static PyModuleDef genPyModuleDef()
{
	PyModuleDef tmpModuleDef = {
			PyModuleDef_HEAD_INIT,
	};
	tmpModuleDef.m_name = "libnecsim";
	tmpModuleDef.m_doc = "Wrapper for c++ library which performs simulations and analysis.";
	tmpModuleDef.m_size = -1;
	return tmpModuleDef;
}
static PyModuleDef moduledef = genPyModuleDef();


#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_libnecsim(void)
#else
#define INITERROR return

PyMODINIT_FUNC
initlibnecsim(void)
#endif
{

	PyObject *module;
	#if PY_MAJOR_VERSION >= 3
	module = PyModule_Create(&moduledef);
	#else
	module = Py_InitModule("libnecsim", NecsimMethods);
	#endif
	if(module == nullptr)
	{
		INITERROR;
	}
	try
	{
		readyPyTypeObject(&C_SpatialSimulationType);
		readyPyTypeObject(&C_NSESimulationType);
		readyPyTypeObject(&C_CommunityType);
		readyPyTypeObject(&C_MetacommunityType);
		readyPyTypeObject(&C_ProtractedSpatialSimulationType);
		readyPyTypeObject(&C_ProtractedNSESimulationType);
		readyPyTypeObject(&C_SimulateDispersalType);
		readyPyTypeObject(&C_LMCType);
	}
	catch(runtime_error &re)
	{
		INITERROR;
	}
	// Threading support
	if(!PyEval_ThreadsInitialized())
	{
		PyEval_InitThreads();
		
	}
	necsimError = PyErr_NewException((char*)"libnecsim.necsimError", NULL, NULL);
	Py_INCREF(necsimError);
	PyModule_AddObject(module, "necsimError", necsimError);
	PyModule_AddObject(module, (char*)"CSpatialSimulation", (PyObject *) &C_SpatialSimulationType);
	PyModule_AddObject(module, (char*)"CNSESimulation", (PyObject *) &C_NSESimulationType);
	PyModule_AddObject(module, (char*)"CCommunity", (PyObject *) &C_CommunityType);
	PyModule_AddObject(module, (char*)"CMetacommunity", (PyObject *) &C_MetacommunityType);
	PyModule_AddObject(module, (char*)"CPSpatialSimulation", (PyObject *) &C_ProtractedSpatialSimulationType);
	PyModule_AddObject(module, (char*)"CPNSESimulation", (PyObject *) &C_ProtractedNSESimulationType);
	PyModule_AddObject(module, (char*)"CDispersalSimulation", (PyObject *) &C_SimulateDispersalType);
	PyModule_AddObject(module, (char *)"CLandscapeMetricsCalculator", (PyObject *) &C_LMCType);
#if PY_MAJOR_VERSION >= 3
	return module;
#endif
}