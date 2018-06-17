// This file is part of NECSim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file necsim.cpp
 * @brief Contains the functions allowing integration of the PyCoalescence python module directly to the c++
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */


#define PYTHON_COMPILE
#include <Python.h>
#include <vector>
#include <string>
#include <csignal>

// These are included here for compabilitity reasons
#include "necsim/Setup.h"
// This provides compability for protracted speciation events.
#include "necsim.h"
#include "PyLogging.h"
#include "CSimulation.h"
#include "CCommunity.h"
#include "CSimulateDispersal.h"
#include "CLandscapeMetricsCalculator.h"


using namespace std;


static PyMethodDef NECSimMethods[] =
{
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
	#if PY_MAJOR_VERSION>=3
	module = PyModule_Create(&moduledef);
	#else
	module = Py_InitModule("libnecsim", NECSimMethods);
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
	NECSimError = PyErr_NewException((char*)"libnecsim.NECSimError", NULL, NULL);
	Py_INCREF(NECSimError);
	PyModule_AddObject(module, "NECSimError", NECSimError);
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