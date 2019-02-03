// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file CLandscapeMetricsCalculator.h
 * @brief Wraps the C LandscapeMetricsCalculator objects for accessing via Python.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */

#ifndef NECSIM_CLANDSCAPEMETRICSCALCULATOR_H
#define NECSIM_CLANDSCAPEMETRICSCALCULATOR_H

#include <Python.h>
#include <vector>
#include <string>
#include <memory>
#include "necsim.h"
#include "LandscapeMetricsCalculator.h"
#include "PyLogging.h"
#include "cpl_custom_handler.h"
#include "PyTemplates.h"

class PyLMC : public PyTemplate<LandscapeMetricsCalculator>
{
public:
    unique_ptr<LandscapeMetricsCalculator> landscapeMetricsCalculator;
    bool has_imported_map;
};

/**
 * @brief Sets the map parameters and imports the maps
 * @param self the Python self object
 * @param args arguments to parse, should contain all key map parameters
 * @return pointer to the Python object
 */
PyObject *set_map(PyLMC *self, PyObject *args)
{
    char *map_file;
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
            PyErr_SetString(necsimError, e.what());
            return nullptr;
        }
    }
    Py_RETURN_NONE;
}

/**
 * @brief Calculates the CLUMPY metric for the imported map file.
 *
 * @param self the Python self pointer
 * @return PyFloatType object containing the mean distance to the nearest neighbour
 */

static PyObject *calculateCLUMPY(PyLMC *self)
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
        PyErr_SetString(necsimError, e.what());
        return nullptr;
    }
}

/**
 * @brief Calculates the mean distance to the nearest neighbour for each cell on the imported map file.
 *
 * @param self the Python self pointer
 * @return PyFloatType object containing the mean distance to the nearest neighbour
 */
static PyObject *calculateMNN(PyLMC *self)
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
        PyErr_SetString(necsimError, e.what());
        return nullptr;
    }
}

static int
PyLMC_init(PyLMC *self, PyObject *args, PyObject *kwds)
{
    self->landscapeMetricsCalculator = make_unique<LandscapeMetricsCalculator>();
    self->has_imported_map = false;
    return PyTemplate_init<LandscapeMetricsCalculator>(self, args, kwds);
}

static void PyLMC_dealloc(PyLMC *self)
{
    if(self->landscapeMetricsCalculator != nullptr)
    {
        self->landscapeMetricsCalculator.reset();
        self->landscapeMetricsCalculator = nullptr;
    }
    PyTemplate_dealloc<LandscapeMetricsCalculator>(self);
}

static PyMethodDef PyLMCMethods[] =
        {
                {"import_map",       (PyCFunction) set_map,         METH_VARARGS,
                                                 "Imports the map file to calculate landscape metrics on. Should only be run once."},
                {"calculate_MNN",    (PyCFunction) calculateMNN,    METH_NOARGS,
                                                 "Calculates the mean nearest-neighbour for the landscape"},
                {"calculate_CLUMPY", (PyCFunction) calculateCLUMPY, METH_NOARGS,
                                                 "Calculates the CLUMPY metric for the landscape"},
                {nullptr,            nullptr, 0, nullptr}
        };

PyTypeObject genLMCType()
{
    PyTypeObject ret_Simulation_Type = {
            PyVarObject_HEAD_INIT(nullptr, 0)
    };
    ret_Simulation_Type.tp_name = (char *) "libnecsim.CLandscapeMetricsCalculator";
    ret_Simulation_Type.tp_doc = (char *) "Calculate landscape metrics from a map file.";
    ret_Simulation_Type.tp_basicsize = sizeof(PyLMC);
    ret_Simulation_Type.tp_itemsize = 0;
    ret_Simulation_Type.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC;
    ret_Simulation_Type.tp_new = PyTemplate_new<LandscapeMetricsCalculator>;
    ret_Simulation_Type.tp_init = (initproc) PyLMC_init;
    ret_Simulation_Type.tp_dealloc = (destructor) PyLMC_dealloc;
    ret_Simulation_Type.tp_traverse = (traverseproc) PyTemplate_traverse<LandscapeMetricsCalculator>;
//		.tp_members = PyTemplate_members<T>,
    ret_Simulation_Type.tp_methods = PyLMCMethods;
    ret_Simulation_Type.tp_getset = PyTemplate_gen_getsetters<LandscapeMetricsCalculator>();
    return ret_Simulation_Type;
}

static PyTypeObject C_LMCType = genLMCType();

#endif // NECSIM_CLANDSCAPEMETRICSCALCULATOR_H
