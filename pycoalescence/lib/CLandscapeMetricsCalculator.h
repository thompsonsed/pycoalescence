// This file is part of NECSim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file CLandscapeMetricsCalculator.h
 * @brief Wraps the C LandscapeMetricsCalculator objects for accessing via python.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */

#ifndef NECSIM_CLANDSCAPEMETRICSCALCULATOR_H
#define NECSIM_CLANDSCAPEMETRICSCALCULATOR_H
#include <Python.h>
#include <vector>
#include <string>
#include "necsimmodule.h"
#include "LandscapeMetricsCalculator.h"
#include "PyLogging.h"
#include "necsim/CPLCustomHandler.h"
#include "PyTemplates.h"

class PyLMC : public PyTemplate<LandscapeMetricsCalculator>
{
public:
	LandscapeMetricsCalculator *landscapeMetricsCalculator;
	bool has_imported_map;
};

/**
 * @brief Sets the map parameters and imports the maps
 * @param self the python self object
 * @param args arguments to parse, should contain all key map parameters
 * @return pointer to the python object
 */
PyObject *set_map(PyLMC *self, PyObject *args)
{
	char * map_file;
	// parse arguments
	if(!PyArg_ParseTuple(args, "s", &map_file))
	{
		return nullptr;
	}
	if(!self->has_imported_map)
	{
		try
		{
			getGlobalLogger(self->logger, self->log_function);
			string map_path = map_file;
			self->landscapeMetricsCalculator->import(map_path);
			self->has_imported_map = true;
		}
		catch(exception &e)
		{
			removeGlobalLogger();
			PyErr_SetString(NECSimError, e.what());
			return nullptr;
		}
	}
	Py_RETURN_NONE;
}


/**
 * @brief Calculates the CLUMPY metric for the imported map file.
 *
 * @param self the python self pointer
 * @return PyFloatType object containing the mean distance to the nearest neighbour
 */

static PyObject * calculateCLUMPY(PyLMC *self)
{
	// parse arguments
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		if(!self->has_imported_map)
		{
			throw runtime_error("Map has not been imported - cannot calculate CLUMPY metric.");
		}
		double c = self->landscapeMetricsCalculator->calculateClumpiness();
		return PyFloat_FromDouble(c);
	}
	catch(exception &e)
	{
		removeGlobalLogger();
		PyErr_SetString(NECSimError, e.what());
		return nullptr;
	}
}

/**
 * @brief Calculates the mean distance to the nearest neighbour for each cell on the imported map file.
 *
 * @param self the python self pointer
 * @return PyFloatType object containing the mean distance to the nearest neighbour
 */
static PyObject * calculateMNN(PyLMC *self)
{
	// parse arguments
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		if(!self->has_imported_map)
		{
			throw runtime_error("Map has not been imported - cannot calculate MNN metric.");
		}
		double c = self->landscapeMetricsCalculator->calculateMNN();
		return PyFloat_FromDouble(c);
	}
	catch(exception &e)
	{
		removeGlobalLogger();
		PyErr_SetString(NECSimError, e.what());
		return nullptr;
	}
}

static int
PyLMC_init(PyLMC*self, PyObject *args, PyObject *kwds)
{
	self->landscapeMetricsCalculator = new LandscapeMetricsCalculator();
	self->has_imported_map = false;
	return PyTemplate_init<LandscapeMetricsCalculator>(self, args, kwds);
}

static void PyLMC_dealloc(PyLMC *self)
{
	if(self->landscapeMetricsCalculator != nullptr)
	{
		delete self->landscapeMetricsCalculator;
		self->landscapeMetricsCalculator = nullptr;
	}
	PyTemplate_dealloc<LandscapeMetricsCalculator>(self);
}

static PyMethodDef PyLMCMethods[] =
		{
				{"import_map", (PyCFunction) set_map,                METH_VARARGS,
						"Imports the map file to calculate landscape metrics on. Should only be run once."},
				{"calculate_MNN", (PyCFunction) calculateMNN,                METH_NOARGS,
						"Calculates the mean nearest-neighbour for the landscape"},
				{"calculate_CLUMPY", (PyCFunction) calculateCLUMPY,                METH_NOARGS,
						"Calculates the CLUMPY metric for the landscape"},
				{nullptr, nullptr, 0, nullptr}
		};


static PyTypeObject C_LMCType = {
		PyVarObject_HEAD_INIT(nullptr, 0)
		.tp_name = (char *)"necsimmodule.CLandscapeMetricsCalculator",
		.tp_doc = (char *)"Calculate landscape metrics from a map file.",
		.tp_basicsize = sizeof(PyLMC),
		.tp_itemsize = 0,
		.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
		.tp_new = PyTemplate_new<LandscapeMetricsCalculator>,
		.tp_init = (initproc) PyLMC_init,
		.tp_dealloc = (destructor) PyLMC_dealloc,
		.tp_traverse = (traverseproc) PyTemplate_traverse<LandscapeMetricsCalculator>,
//		.tp_members = PyTemplate_members<T>,
		.tp_methods = PyLMCMethods,
		.tp_getset = PyTemplate_gen_getsetters<LandscapeMetricsCalculator>()
};




#endif // NECSIM_CLANDSCAPEMETRICSCALCULATOR_H
