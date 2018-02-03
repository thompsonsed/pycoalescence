// This file is part of NECSim project which is released under BSD-3 license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details
/**
 * @author Samuel Thompson
 * @file dispersalmodule.cpp
 * @brief Contains the functions for testing dispersal methods using efficient c++ routines.
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 */

#ifndef PYTHON_COMPILE
#define PYTHON_COMPILE
#endif
#include <Python.h>
#include <vector>
#include <string>
#include "dispersalmodule.h"
#include "PyLogging.h"
#include "necsim/SimulateDispersal.h"

PyObject * loggingmodule;
PyGILState_STATE gstate;
bool log_set = false;
bool logger_set = false;
PyObject * logger;

/**
 * @brief Simulates the provided dispersal kernel on the map file, saving the mean dispersal distance to the output
 * database.
 *
 * @param self the python self pointer
 * @param args the arguments passed in from python
 * @return Py_None if successful, otherwise will return NULL.
 */
static PyObject * test_mean_dispersal(PyObject *self, PyObject *args)
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
		return nullptr;
	}
	try
	{
		Py_INCREF(logger);
		SimulateDispersal disp_sim;
		disp_sim.setDispersalParameters(dispersal_method, sigma, tau, m_prob, cutoff, landscape_type);
		disp_sim.setSequential(bool(is_sequential));
		disp_sim.setOutputDatabase(output_database);
		disp_sim.setSeed(static_cast<unsigned long>(seed));
		disp_sim.setNumberRepeats(static_cast<unsigned long>(num_repeats));
		disp_sim.setSizes(static_cast<unsigned long>(map_x), static_cast<unsigned long>(map_y));
		disp_sim.importMaps(map_file);
		disp_sim.runMeanDispersalDistance();
		disp_sim.writeDatabase("DISPERSAL_DISTANCES");
		Py_DECREF(logger);
	}
	catch(exception &e)
	{
		Py_DECREF(logger);
		PyErr_SetString(DispersalError, e.what());
		return nullptr;
	}
	Py_RETURN_NONE;
}
/**
 * @brief Simulates the provided dispersal kernel on the map file, saving the mean distance travelled to the output
 * database.
 *
 * @param self the python self pointer
 * @param args the arguments passed in from python
 * @return Py_None if successful, otherwise will return NULL.
 */
static PyObject * test_mean_distance_travelled(PyObject *self, PyObject *args)
{
	char * output_database;
	char * map_file;
	char * dispersal_method;
	char * landscape_type;
	int map_x, map_y;
	double sigma, tau, m_prob, cutoff;
	int num_repeats, seed, num_steps;

	// parse arguments
	if(!PyArg_ParseTuple(args, "ssssddddiiiii", &output_database, &map_file, &dispersal_method, &landscape_type,
						 &sigma, &tau, &m_prob, &cutoff, &num_repeats, &num_steps, &seed, &map_x, &map_y))
	{
		return nullptr;
	}
	try
	{
		Py_INCREF(logger);
		SimulateDispersal disp_sim;
		disp_sim.setDispersalParameters(dispersal_method, sigma, tau, m_prob, cutoff, landscape_type);
		disp_sim.setOutputDatabase(output_database);
		disp_sim.setSeed(static_cast<unsigned long>(seed));
		disp_sim.setNumberRepeats(static_cast<unsigned long>(num_repeats));
		disp_sim.setNumberSteps(static_cast<unsigned long>(num_steps));
		disp_sim.setSizes(static_cast<unsigned long>(map_x), static_cast<unsigned long>(map_y));
		disp_sim.importMaps(map_file);
		disp_sim.runMeanDistanceTravelled();
		disp_sim.writeDatabase("DISTANCES_TRAVELLED");
		Py_DECREF(logger);
	}
	catch(exception &e)
	{
#ifdef DEBUG
		writeLog(50, e.what());
#endif // DEBUG
		Py_DECREF(logger);
		PyErr_SetString(DispersalError, e.what());
		return nullptr;
	}
	Py_RETURN_NONE;
}


static PyMethodDef DispersalMethods[] = 
{
	{"test_mean_dispersal", test_mean_dispersal, METH_VARARGS,
	 "Simulates the dispersal function on the provided map, recording the mean dispersal distance."},
	{"test_mean_distance_travelled", test_mean_distance_travelled, METH_VARARGS,
	 "Simulates the dispersal function on the provided map,"
			 " recording the mean distance travelled in the number of steps."},
	{"set_log_function", set_log_function, METH_VARARGS, "calls logging"},
	{"set_logger", set_logger, METH_VARARGS, "Sets the logger to use"},
	{nullptr, nullptr, 0 , nullptr}
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
	nullptr,
	sizeof(struct module_state),
	DispersalMethods,
	nullptr,
	dispersal_traverse,
	dispersal_clear,
	nullptr
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
	if(module == nullptr)
	{
		INITERROR;
	}
	// Threading support
	if(!PyEval_ThreadsInitialized())
	{
		PyEval_InitThreads();
		
	}
	DispersalError = PyErr_NewException((char*)"dispersal.Error", nullptr, nullptr);
	Py_INCREF(DispersalError);
	PyModule_AddObject(module, "DispersalError", DispersalError);
	#if PY_MAJOR_VERSION >= 3
	return module;
	#endif
}