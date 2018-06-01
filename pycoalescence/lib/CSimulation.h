// This file is part of NECSim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file CSimulation.h
 * @brief Wraps the various C++ tree objects for accessing via python.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */
#ifndef PY_TREE_NECSIM
#define PY_TREE_NECSIM

#include <Python.h>
#include <structmember.h>
#include "necsim/ConfigFileParser.h"
#include "necsim/Tree.h"
#include "necsim/SpatialTree.h"
#include "necsim/ProtractedTree.h"
#include "necsim/ProtractedSpatialTree.h"
#include "PyLogging.h"
#include "necsimmodule.h"
#include "PyImports.h"
#include "PyTemplates.h"

using namespace std;

/**
 * @brief Imports the config parameters from a file. The file should be of the format generated by
 * ConfigFileParser in python.
 * @tparam T the simulation type
 * @param self the python self object
 * @param args arguments to parse
 */
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
		PyErr_SetString(NECSimError, e.what());
		return nullptr;
	}
	Py_RETURN_NONE;
}

/**
 * @brief Imports the config parameters from a string. The string should be equivalent to a file written by
 * ConfigFileParser in python.
 * @tparam T the simulation type
 * @param self the python self object
 * @param args arguments to parse
 */
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
		ConfigOption config;
		config.parseConfig(istream1);
		self->base_object->importSimulationVariables(config);
	}
	catch(exception &e)
	{
		removeGlobalLogger();
		PyErr_SetString(NECSimError, e.what());
		return nullptr;
	}
	Py_RETURN_NONE;
}

/**
 * @brief Sets up the simulation, including importing map files and generating in-memory objects.
 * @tparam T the simulation type
 * @param self the python self object
 * @param args arguments to parse
 */
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
		PyErr_SetString(NECSimError, e.what());
		return nullptr;
	}
	Py_RETURN_NONE;
}

/**
 * @brief Runs the simulation.
 * @tparam T the simulation type
 * @param self the python self object
 * @param args arguments to parse
 * @return Py_RETURN_TRUE if the simulation completes, Py_RETURN_FALSE otherwise.
 */
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
		PyErr_SetString(NECSimError, e.what());
		return nullptr;
	}
	Py_RETURN_FALSE;
}

/**
 * @brief Applies the provided speciation rates to the simulation to generate multiple communities.
 * @tparam T the simulation type
 * @param self the python self object
 * @param args arguments to parse
 */
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
		PyErr_SetString(NECSimError, e.what());
		return nullptr;
	}
	Py_RETURN_NONE;
}

/**
 * @brief Sets up the simulation by reading the dumped files from a paused simulation.
 * @tparam T the simulation type
 * @param self the python self object
 * @param args arguments to parse
 */
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
	// Set up the resume parameters.
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
		PyErr_SetString(NECSimError, e.what());
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
static PyTypeObject genSimulationType(char *tp_name, char *tp_doc)
{
	auto genPyTemplateGetSetters = PyTemplate_gen_getsetters<T>();
	auto genPyTemplateNew = PyTemplate_new<T>;
	auto genPyTemplateInit = PyTemplate_init<T>;
	auto genPyTemplateDealloc = PyTemplate_dealloc<T>;
	auto genPyTemplateTraverse = PyTemplate_traverse<T>;
	auto genPyTemplateMethods = genPySimulationMethods<T>();
	static PyTypeObject ret_Simulation_Type = {
			PyVarObject_HEAD_INIT(nullptr, 0)
			.tp_name = tp_name,
			.tp_doc = tp_doc,
			.tp_basicsize = sizeof(PyTemplate<T>),
			.tp_itemsize = 0,
			.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
			.tp_new = genPyTemplateNew,
			.tp_init = (initproc) genPyTemplateInit,
			.tp_dealloc = (destructor) genPyTemplateDealloc,
			.tp_traverse = (traverseproc) genPyTemplateTraverse,
//		.tp_members = PyTemplate_members<T>,
			.tp_methods = genPyTemplateMethods,
			.tp_getset = genPyTemplateGetSetters
	};
	return ret_Simulation_Type;
}

static PyTypeObject C_SpatialSimulationType = genSimulationType<SpatialTree>((char *) "necsimmodule.CSpatialSimulation",
																			 (char *) "C class for spatial simulations.");
static PyTypeObject C_NSESimulationType = genSimulationType<Tree>((char *) "necsimmodule.CNSESimulation",
																  (char *) "C class for non-spatial simulations.");
static PyTypeObject C_ProtractedSpatialSimulationType = genSimulationType<ProtractedSpatialTree>(
		(char *) "necsimmodule.CPSpatialSimulation",
		(char *) "C class for protracted spatial simulations.");
static PyTypeObject C_ProtractedNSESimulationType = genSimulationType<ProtractedTree>(
		(char *) "necsimmodule.CPNSESimulation",
		(char *) "C class for protracted non-spatial simulations.");

#endif // PY_TREE_NECSIM