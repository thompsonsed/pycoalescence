// This file is part of NECSim project which is released under BSD-3 license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.

/**
 * @author Samuel Thompson
 * @date 01/08/2017
 * @file applyspecmodule.cpp
 *
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 * @brief Contains the module for python integration for additional applying speciation rates after a 
 * simulation is completed.
 *
 * Requires command line parameters and generates a data object from them.
 * Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
 */
 
#ifndef PYTHON_COMPILE
#define PYTHON_COMPILE
#endif
#include <Python.h>
#include <utility>
#include <vector>
#include <string>
#include <cstring>
#include <unistd.h>
#include <csignal>

#include "applyspecmodule.h"
#include "PyLogging.h"
#include "PyImports.h"
#include "necsim/Community.h"
#include "necsim/Metacommunity.h"

bool log_set = false;
bool logger_set = false;
PyObject * logger = nullptr;
PyObject * call_logging = nullptr;
/**
 * @brief Applies the speciation parameters to the provided template class, which can be a Metacommunity or a Community
 * @tparam T either a Metacommunity of Community object to calculate community structure for
 * @param database_str path to the database input/output
 * @param use_spatial flag for lineage location analysis
 * @param sample_file path to spatial sampling file, or "null"
 * @param times vector of times to apply
 * @param fragment_file path to fragment list, or "T" for fragment detection, or "null"
 * @param speciation_rates speciation rates to apply
 * @param min_speciation_gen minimum speciation rate for protracted simulations
 * @param max_speciation_gen maximum speciation rate for protracted simulations
 * @param metacommunity_size size of the metacommunity to apply
 * @param metacommunity_speciation_rate speciation rate to use in metacommunity generation
 */
template<class T> void createCommunity(string database_str, bool use_spatial, string sample_file,
									   vector<double> &times, string fragment_file, vector<double> &speciation_rates,
									   double min_speciation_gen, double max_speciation_gen,
									   unsigned long metacommunity_size, double metacommunity_speciation_rate)
{
	T community;
	SpecSimParameters speciation_parameters;
	speciation_parameters.setup(std::move(database_str), use_spatial, std::move(sample_file), times,
								std::move(fragment_file), speciation_rates, min_speciation_gen, max_speciation_gen,
								metacommunity_size, metacommunity_speciation_rate);
	community.apply(&speciation_parameters);
}

static PyObject * apply(PyObject * self, PyObject * args)
{
	char * database;
	int record_spatial;
	char * sample_file;
	char * fragment_file;
	double min_spec_gen = 0.0;
	double max_spec_gen = 0.0;
	unsigned long metacommunity_size = 0;
	double metacommunity_speciation_rate = 0.0;
	PyObject *list_speciation_rates;
	PyObject *list_times;
	if (!PyArg_ParseTuple(args, "sissO!O!|ddkd", &database, &record_spatial, &sample_file,
						  &fragment_file, &PyList_Type, &list_speciation_rates, &PyList_Type, &list_times,
						  &min_spec_gen,
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
	auto use_spatial = static_cast<bool>(record_spatial);
	string sample_file_str = sample_file;
	string fragment_file_str = fragment_file;
	vector<double> spec_rates;
	vector<double> times;
	if(!importPyListToVectorDouble(list_speciation_rates, spec_rates, "Speciation rates must be floats."))
	{
		return NULL;
	}
	if(!importPyListToVectorDouble(list_times, times, "Times must be floats."))
	{
		return NULL;
	}
	// Now run the actual simulation
	try
	{
		if(metacommunity_size == 0)
		{
			Py_INCREF(logger);
			createCommunity<Community>(database_str, use_spatial, sample_file_str, times,
									   fragment_file_str, spec_rates, min_spec_gen, max_spec_gen,
									   metacommunity_size, metacommunity_speciation_rate);
			Py_DECREF(logger);
		}
		else
		{
			Py_INCREF(logger);
			createCommunity<Metacommunity>(database_str, use_spatial, sample_file_str, times,
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