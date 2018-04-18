// This file is part of NECSim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file dispersalmodule.cpp
 * @brief Contains the functions for testing dispersal methods using efficient c++ routines.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
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
#include "PyImports.h"

bool log_set = false;
bool logger_set = false;
PyObject * logger = nullptr;
PyObject * call_logging = nullptr;
SimParameters globalSimParameters;

/**
 * @brief Sets the map parameters.
 * @param self the python self object
 * @param args arguments to parse, should contain all key map parameters
 * @return pointer to the python object
 */
PyObject *set_map_parameters(PyObject *self, PyObject *args)
{
	char * landscape_type;
	char * fine_map_file;
	char * coarse_map_file;
	// parse arguments
	if(!PyArg_ParseTuple(args, "isiiiiiisiiiis", &globalSimParameters.deme, &fine_map_file,
						 &globalSimParameters.fine_map_x_size, &globalSimParameters.fine_map_y_size,
						 &globalSimParameters.fine_map_x_offset, &globalSimParameters.fine_map_y_offset,
						 &globalSimParameters.sample_x_size, &globalSimParameters.sample_y_size,
						 &coarse_map_file, &globalSimParameters.coarse_map_x_size,
						 &globalSimParameters.coarse_map_y_size, &globalSimParameters.coarse_map_x_offset,
						 &globalSimParameters.coarse_map_y_offset, &landscape_type))
	{
		return nullptr;
	}
	globalSimParameters.sample_x_offset = 0;
	globalSimParameters.sample_y_offset = 0;
	globalSimParameters.grid_x_size = globalSimParameters.sample_x_size;
	globalSimParameters.grid_y_size = globalSimParameters.sample_y_size;
	globalSimParameters.fine_map_file = fine_map_file;
	globalSimParameters.coarse_map_file = coarse_map_file;
	globalSimParameters.landscape_type = landscape_type;
	Py_RETURN_NONE;

}

/**
 * @brief Sets the historical map parameters.
 * @param self the python self object
 * @param args arguments to parse, should be lists of the fine and coarse map parameters
 * @return pointer to the python object
 */
static PyObject * set_historical_map_parameters(PyObject * self, PyObject * args)
{
	vector<string> path_fine;
	vector<unsigned long> number_fine;
	vector<double> rate_fine;
	vector<double> time_fine;
	vector<string> path_coarse;
	vector<unsigned long> number_coarse;
	vector<double> rate_coarse;
	vector<double> time_coarse;
	PyObject * p_path_fine;
	PyObject * p_number_fine;
	PyObject * p_rate_fine;
	PyObject * p_time_fine;
	PyObject * p_path_coarse;
	PyObject * p_number_coarse;
	PyObject * p_rate_coarse;
	PyObject * p_time_coarse;
	if(!PyArg_ParseTuple(args, "O!O!O!O!O!O!O!O!", &PyList_Type, &p_path_fine, &PyList_Type, &p_number_fine,
						 &PyList_Type, &p_rate_fine, &PyList_Type, &p_time_fine, &PyList_Type, &p_path_coarse,
						 &PyList_Type, &p_number_coarse, &PyList_Type, &p_rate_coarse, &PyList_Type, &p_time_coarse))
	{
		return nullptr;
	}
	try
	{
		Py_INCREF(logger);
		importPyListToVectorString(p_path_fine, path_fine, "Fine map paths must be strings.");
		importPyListToVectorULong(p_number_fine, number_fine, "Fine map numbers must be integers.");
		importPyListToVectorDouble(p_rate_fine, rate_fine, "Fine map rates must be floats.");
		importPyListToVectorDouble(p_time_fine, time_fine, "Fine map times must be floats.");
		importPyListToVectorString(p_path_coarse, path_coarse, "Coarse map paths must be strings.");
		importPyListToVectorULong(p_number_coarse, number_coarse, "Coarse map numbers must be integers.");
		importPyListToVectorDouble(p_rate_coarse, rate_coarse, "Coarse map rates must be floats.");
		importPyListToVectorDouble(p_time_coarse, time_coarse, "Coarse map times must be floats.");
		globalSimParameters.setHistoricalMapParameters(path_fine, number_fine, rate_fine, time_fine, path_coarse,
												  number_coarse, rate_coarse, time_coarse);
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
 * @brief Sets the dispersal parameters.
 * @param self the python self object
 * @param args arguments to parse
 * @return pointer to the python object
 */
static PyObject * set_dispersal_parameters(PyObject * self, PyObject *args)
{

	char * dispersal_method;
	char * dispersal_file;
	double sigma, tau, m_prob, cutoff, dispersal_rel_cost;
	int restrict_self;
	// parse arguments
	if(!PyArg_ParseTuple(args, "ssdddddi", &dispersal_method, &dispersal_file, &sigma, &tau, &m_prob, &cutoff,
						 &dispersal_rel_cost, &restrict_self))
	{
		return nullptr;
	}
	Py_INCREF(logger);
	globalSimParameters.dispersal_relative_cost = dispersal_rel_cost;
	globalSimParameters.dispersal_file = dispersal_file;
	globalSimParameters.dispersal_method = dispersal_method;
	globalSimParameters.restrict_self = static_cast<bool>(restrict_self);
	globalSimParameters.sigma = sigma;
	globalSimParameters.tau = tau;
	globalSimParameters.m_prob = m_prob;
	globalSimParameters.cutoff = cutoff;
	Py_DECREF(logger);
	Py_RETURN_NONE;
	
}


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
	int num_repeats, seed, is_sequential;
	// parse arguments
	if(!PyArg_ParseTuple(args, "siii", &output_database, &num_repeats, &seed, &is_sequential))
	{
		return nullptr;
	}
	try
	{
#ifdef DEBUG
		if(!logger || !log_set)
		{
			throw FatalException("Logger has not been set properly.");
		}
		if(!call_logging || !logger_set)
		{
			throw FatalException("Logging  module has not been set.");
		}
#endif // DEBUG
		Py_INCREF(logger);
		SimulateDispersal disp_sim;
		disp_sim.setSimulationParameters(&globalSimParameters);
		disp_sim.setSequential(static_cast<bool>(is_sequential));
		disp_sim.setOutputDatabase(output_database);
		disp_sim.setSeed(static_cast<unsigned long>(seed));
		disp_sim.setNumberRepeats(static_cast<unsigned long>(num_repeats));
		disp_sim.importMaps();
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
	int num_repeats, seed, num_steps;

	// parse arguments
	if(!PyArg_ParseTuple(args, "siii", &output_database, &num_repeats, &num_steps, &seed))
	{
		return nullptr;
	}
	try
	{
		Py_INCREF(logger);
		SimulateDispersal disp_sim;
		disp_sim.setSimulationParameters(&globalSimParameters);
		disp_sim.setOutputDatabase(output_database);
		disp_sim.setSeed(static_cast<unsigned long>(seed));
		disp_sim.setNumberRepeats(static_cast<unsigned long>(num_repeats));
		disp_sim.setNumberSteps(static_cast<unsigned long>(num_steps));
		disp_sim.importMaps();
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
	{"set_map_parameters", set_map_parameters, METH_VARARGS,
			"Sets the map parameters for the dispersal simulation."},
	{"set_historical_map_parameters", set_historical_map_parameters, METH_VARARGS,
			"Sets the historical map parameters for the dispersal simulation."},
	{"set_dispersal_parameters", set_dispersal_parameters, METH_VARARGS,
			"Sets the dispersal parameters for the dispersal simulation."},
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