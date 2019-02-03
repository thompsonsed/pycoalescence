// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.

/**
 * @file CSimulateDispersal.h
 * @brief Python wrappers for dispersal simulation objects.
 *
 * @copyright <a href="https://opensource.org/licenses/MIT"> MIT Licence.</a>
 */

#ifndef NECSIM_CSIMULATEDISPERSAL_H
#define NECSIM_CSIMULATEDISPERSAL_H

#include <Python.h>
#include <structmember.h>
#include <cstring>
#include <string>
#include <memory>
#include "PyImports.h"
#include "PyTemplates.h"
#include "necsim.h"
#include "necsim/SimParameters.h"
#include "necsim/SimulateDispersal.h"
#include "CSimulation.h"

using namespace std;

class PySimulateDispersal : public PyTemplate<SimulateDispersal>
{
public:
    shared_ptr<SimParameters> dispersalParameters;
    bool has_imported_maps;
    unique_ptr<std::string> output_database;
    bool printing;
    bool needs_update;

    PySimulateDispersal() : dispersalParameters(nullptr), has_imported_maps(false), output_database(nullptr),
                            printing(true), needs_update(true)
    {

    }

    /**
     * @brief Checks that the output database has been set, and the maps have been imported.
     * Raises an error if either case is no true.
     */
    void checkCompleted()
    {
        if(*output_database == "none")
        {
            throw runtime_error("Output database has not been set.");
        }
        if(!has_imported_maps)
        {
            throw runtime_error("Maps have not been imported - cannot start simulations.");
        }
    }

    /**
     * @brief Sets the dispersal parameters in the base object.
     */
    void setDispersalParameters()
    {
        if(needs_update)
        {
            getGlobalLogger(logger, log_function);
            base_object->setSimulationParameters(dispersalParameters, printing);
            base_object->setDispersalParameters();
            printing = false;
            needs_update = false;
        }
    }
};

/**
 * @brief Sets all the map parameters, including historical maps, with a single import.
 * @param self the Python self object
 * @param args arguments to parse
 * @return pointer to the Python object
 */
static PyObject *set_all_map_parameters(PySimulateDispersal *self, PyObject *args)
{
    char *landscape_type;
    char *fine_map_file;
    char *coarse_map_file;
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
    if(!PyArg_ParseTuple(args, "isiiiiiisiiiiisO!O!O!O!O!O!O!O!", &self->dispersalParameters->deme, &fine_map_file,
                         &self->dispersalParameters->fine_map_x_size, &self->dispersalParameters->fine_map_y_size,
                         &self->dispersalParameters->fine_map_x_offset, &self->dispersalParameters->fine_map_y_offset,
                         &self->dispersalParameters->sample_x_size, &self->dispersalParameters->sample_y_size,
                         &coarse_map_file, &self->dispersalParameters->coarse_map_x_size,
                         &self->dispersalParameters->coarse_map_y_size, &self->dispersalParameters->coarse_map_x_offset,
                         &self->dispersalParameters->coarse_map_y_offset, &self->dispersalParameters->coarse_map_scale,
                         &landscape_type, &PyList_Type, &p_path_fine, &PyList_Type, &p_number_fine,
                         &PyList_Type, &p_rate_fine, &PyList_Type, &p_time_fine, &PyList_Type, &p_path_coarse,
                         &PyList_Type, &p_number_coarse, &PyList_Type, &p_rate_coarse, &PyList_Type, &p_time_coarse))
    {
        return nullptr;
    }
    if(self->has_imported_maps)
    {
        PyErr_SetString(necsimError, (char *) "Maps have already been imported");
        return nullptr;
    }
    try
    {

        getGlobalLogger(self->logger, self->log_function);
        self->dispersalParameters->sample_x_offset = 0;
        self->dispersalParameters->sample_y_offset = 0;
        self->dispersalParameters->grid_x_size = self->dispersalParameters->sample_x_size;
        self->dispersalParameters->grid_y_size = self->dispersalParameters->sample_y_size;
        self->dispersalParameters->fine_map_file = fine_map_file;
        self->dispersalParameters->coarse_map_file = coarse_map_file;
        self->dispersalParameters->landscape_type = landscape_type;
        // Check for errors in each parsing of vector
        vector<bool> passed_errors;
        passed_errors.emplace_back(importPyListToVectorString(p_path_fine,
                                                              path_fine, "Fine map paths must be strings."));
        passed_errors.emplace_back(importPyListToVectorULong(p_number_fine,
                                                             number_fine, "Fine map numbers must be integers."));
        passed_errors.emplace_back(importPyListToVectorDouble(p_rate_fine,
                                                              rate_fine, "Fine map rates must be floats."));
        passed_errors.emplace_back(importPyListToVectorDouble(p_time_fine,
                                                              time_fine, "Fine map times must be floats."));
        passed_errors.emplace_back(importPyListToVectorString(p_path_coarse,
                                                              path_coarse, "Coarse map paths must be strings."));
        passed_errors.emplace_back(importPyListToVectorULong(p_number_coarse,
                                                             number_coarse, "Coarse map numbers must be integers."));
        passed_errors.emplace_back(importPyListToVectorDouble(p_rate_coarse,
                                                              rate_coarse, "Coarse map rates must be floats."));
        passed_errors.emplace_back(importPyListToVectorDouble(p_time_coarse,
                                                              time_coarse, "Coarse map times must be floats."));
        for(const auto &item: passed_errors)
        {
            if(!item)
            {
                removeGlobalLogger();
                return nullptr;
            }
        }
        self->dispersalParameters->setHistoricalMapParameters(path_fine, number_fine, rate_fine, time_fine, path_coarse,
                                                              number_coarse, rate_coarse, time_coarse);
        self->setDispersalParameters();
        self->base_object->importMaps();
        self->has_imported_maps = true;

    }
    catch(exception &e)
    {
        removeGlobalLogger();
        PyErr_SetString(necsimError, e.what());
        return nullptr;
    }
    Py_RETURN_NONE;
}

/**
 * @brief Sets the map parameters and imports the maps
 * @param self the Python self object
 * @param args arguments to parse, should contain all key map parameters
 * @return pointer to the Python object
 */
PyObject *set_maps(PySimulateDispersal *self, PyObject *args)
{
    char *landscape_type;
    char *fine_map_file;
    char *coarse_map_file;
    // parse arguments
#ifdef DEBUG
    if(self == nullptr)
    {
        PyErr_SetString(necsimError, (char *) "self pointer is null. Please report this bug.");
        return nullptr;
    }
#endif // DEBUG
    if(!PyArg_ParseTuple(args, "isiiiiiisiiiiis", &self->dispersalParameters->deme, &fine_map_file,
                         &self->dispersalParameters->fine_map_x_size, &self->dispersalParameters->fine_map_y_size,
                         &self->dispersalParameters->fine_map_x_offset, &self->dispersalParameters->fine_map_y_offset,
                         &self->dispersalParameters->sample_x_size, &self->dispersalParameters->sample_y_size,
                         &coarse_map_file, &self->dispersalParameters->coarse_map_x_size,
                         &self->dispersalParameters->coarse_map_y_size, &self->dispersalParameters->coarse_map_x_offset,
                         &self->dispersalParameters->coarse_map_y_offset, &self->dispersalParameters->coarse_map_scale,
                         &landscape_type))
    {
        return nullptr;
    }
    if(self->has_imported_maps)
    {
        PyErr_SetString(necsimError, (char *) "Maps have already been imported");
        return nullptr;
    }
    try
    {
        getGlobalLogger(self->logger, self->log_function);
        self->dispersalParameters->sample_x_offset = 0;
        self->dispersalParameters->sample_y_offset = 0;
        self->dispersalParameters->grid_x_size = self->dispersalParameters->sample_x_size;
        self->dispersalParameters->grid_y_size = self->dispersalParameters->sample_y_size;
        self->dispersalParameters->fine_map_file = fine_map_file;
        self->dispersalParameters->coarse_map_file = coarse_map_file;
        self->dispersalParameters->landscape_type = landscape_type;
        self->needs_update = true;
        self->setDispersalParameters();
        self->base_object->importMaps();
        self->has_imported_maps = true;
    }
    catch(exception &e)
    {
        removeGlobalLogger();
        PyErr_SetString(necsimError, e.what());
        return nullptr;
    }
    Py_RETURN_NONE;

}

/**
 * @brief Sets the historical map parameters.
 * @param self the Python self object
 * @param args arguments to parse, should be lists of the fine and coarse map parameters
 * @return pointer to the Python object
 */
static PyObject *set_historical_map_parameters(PySimulateDispersal *self, PyObject *args)
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
        getGlobalLogger(self->logger, self->log_function);
        importPyListToVectorString(p_path_fine, path_fine, "Fine map paths must be strings.");
        importPyListToVectorULong(p_number_fine, number_fine, "Fine map numbers must be integers.");
        importPyListToVectorDouble(p_rate_fine, rate_fine, "Fine map rates must be floats.");
        importPyListToVectorDouble(p_time_fine, time_fine, "Fine map times must be floats.");
        importPyListToVectorString(p_path_coarse, path_coarse, "Coarse map paths must be strings.");
        importPyListToVectorULong(p_number_coarse, number_coarse, "Coarse map numbers must be integers.");
        importPyListToVectorDouble(p_rate_coarse, rate_coarse, "Coarse map rates must be floats.");
        importPyListToVectorDouble(p_time_coarse, time_coarse, "Coarse map times must be floats.");
        self->dispersalParameters->setHistoricalMapParameters(path_fine, number_fine, rate_fine, time_fine, path_coarse,
                                                              number_coarse, rate_coarse, time_coarse);
        if(self->has_imported_maps && !path_fine.empty() && !number_fine.empty() && !rate_fine.empty() &&
           !time_fine.empty() && !path_coarse.empty() && !number_coarse.empty() && !rate_coarse.empty() &&
           !time_coarse.empty())
        {
            self->needs_update = true;
            self->setDispersalParameters();
            self->base_object->importMaps();
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

/**
 * @brief Sets the key simulation parameters.
 * @param self the Python self object
 * @param args arguments to parse
 * @return pointer to the Python object
 */
static PyObject *set_output_database(PySimulateDispersal *self, PyObject *args)
{

    char *output_file;
    // parse arguments
    if(!PyArg_ParseTuple(args, "s", &output_file))
    {
        return nullptr;
    }
    try
    {
        getGlobalLogger(self->logger, self->log_function);
        if(*self->output_database == "none")
        {
            string output_f = output_file;
            self->base_object->setOutputDatabase(output_f);
            *self->output_database = output_f;
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

/**
 * @brief Sets the dispersal parameters.
 * @param self the Python self object
 * @param args arguments to parse
 * @return pointer to the Python object
 */
static PyObject *set_dispersal_parameters(PySimulateDispersal *self, PyObject *args)
{

    char *dispersal_method;
    char *dispersal_file;
    double sigma, tau, m_prob, cutoff, dispersal_rel_cost;
    int restrict_self;
    // parse arguments
    if(!PyArg_ParseTuple(args, "ssdddddi", &dispersal_method, &dispersal_file, &sigma, &tau, &m_prob, &cutoff,
                         &dispersal_rel_cost, &restrict_self))
    {
        return nullptr;
    }
    try
    {
        getGlobalLogger(self->logger, self->log_function);
        self->dispersalParameters->setDispersalParameters(dispersal_method, sigma, tau, m_prob, cutoff,
                                                          dispersal_rel_cost, static_cast<bool>(restrict_self),
                                                          "closed",
                                                          dispersal_file, "none");
        self->needs_update = true;
    }
    catch(exception &e)
    {
        removeGlobalLogger();
        PyErr_SetString(necsimError, e.what());
        return nullptr;
    }

    Py_RETURN_NONE;

}

/**
 * @brief Runs the mean distance travelled simulation
 * @param self the Python self object
 * @param args arguments to parse
 * @return pointer to the Python object
 */
static PyObject *runMDT(PySimulateDispersal *self, PyObject *args)
{
    try
    {
        int num_repeats, seed, is_sequential;
        PyObject * p_num_steps;
        vector<unsigned long> num_steps;
        // parse arguments
        if(!PyArg_ParseTuple(args, "iO!ii", &num_repeats, &PyList_Type, &p_num_steps,
                             &seed, &is_sequential))
        {
            return nullptr;
        }
        getGlobalLogger(self->logger, self->log_function);
        if(!importPyListToVectorULong(p_num_steps, num_steps, "Number of steps must be integers."))
        {
            return nullptr;
        }
        self->setDispersalParameters();
        self->base_object->setSequential(static_cast<bool>(is_sequential));
        self->base_object->setSeed(static_cast<unsigned long>(seed));
        self->base_object->setNumberRepeats(static_cast<unsigned long>(num_repeats));
        self->base_object->setNumberSteps(num_steps);
        if(!self->has_imported_maps)
        {
            self->base_object->importMaps();
        }
        self->checkCompleted();
        self->base_object->runMeanDistanceTravelled();
        self->base_object->writeDatabase("DISTANCES_TRAVELLED");
    }
    catch(exception &e)
    {
        removeGlobalLogger();
        PyErr_SetString(necsimError, e.what());
        return nullptr;
    }
    Py_RETURN_NONE;

}

/**
 * @brief Runs the simulation for mean dispersal distance.
 * @param self the Python self object
 * @param args arguments to parse
 * @return pointer to the Python object
 */
static PyObject *runMeanDispersal(PySimulateDispersal *self, PyObject *args)
{
    try
    {
        int num_repeats, seed, is_sequential;
        // parse arguments
        if(!PyArg_ParseTuple(args, "iii", &num_repeats, &seed, &is_sequential))
        {
            return nullptr;
        }
        getGlobalLogger(self->logger, self->log_function);
        self->setDispersalParameters();
        if(!self->has_imported_maps)
        {
            self->base_object->importMaps();
        }
        self->base_object->setSequential(static_cast<bool>(is_sequential));
        self->base_object->setSeed(static_cast<unsigned long>(seed));
        self->base_object->setNumberRepeats(static_cast<unsigned long>(num_repeats));
        self->checkCompleted();
        self->base_object->runMeanDispersalDistance();
        self->base_object->writeDatabase("DISPERSAL_DISTANCES");
    }
    catch(exception &e)
    {
        removeGlobalLogger();
        PyErr_SetString(necsimError, e.what());
        return nullptr;
    }
    Py_RETURN_NONE;

}

static PyObject *
PySimulateDispersal_new(PyTypeObject * type, PyObject * args, PyObject * kwds)
{
    auto self = (PySimulateDispersal *) PyTemplate_new<SimulateDispersal>(type, args, kwds);
    return (PyObject *) self;
}

static int
PySimulateDispersal_init(PySimulateDispersal *self, PyObject *args, PyObject *kwds)
{
    auto out = PyTemplate_init<SimulateDispersal>(self, args, kwds);
    self->dispersalParameters = make_shared<SimParameters>();
    self->has_imported_maps = false;
    self->output_database = make_unique<std::string>("none");
    self->printing = true;
    self->needs_update = true;
    return out;
}

static void PySimulateDispersal_dealloc(PySimulateDispersal *self)
{
    if(self->dispersalParameters != nullptr)
    {
        self->dispersalParameters.reset();
        self->dispersalParameters = nullptr;
    }
    if(self->output_database != nullptr)
    {
        self->output_database.reset();
        self->output_database = nullptr;
    }
    PyTemplate_dealloc<SimulateDispersal>(self);
}

static PyMethodDef SimulateDispersalMethods[] =
        {
                {"set_dispersal_parameters",      (PyCFunction) set_dispersal_parameters,      METH_VARARGS,
                                                              "Sets the dispersal current_metacommunity_parameters for this simulation."},
                {"set_output_database",           (PyCFunction) set_output_database,           METH_VARARGS,
                                                              "Sets the output database for the simulation."},
                {"run_mean_dispersal_distance",   (PyCFunction) runMeanDispersal,              METH_VARARGS,
                                                              "Runs the dispersal simulation for the set current_metacommunity_parameters, calculating the mean distance per step."},
                {"run_mean_distance_travelled",   (PyCFunction) runMDT,                        METH_VARARGS,
                                                              "Runs the dispersal simulation for the set current_metacommunity_parameters, calculating the mean distance travelled."},
                {"import_maps",                   (PyCFunction) set_maps,                      METH_VARARGS,
                                                              "Imports the map files for the simulation. Should only be run once."},
                {"import_all_maps",               (PyCFunction) set_all_map_parameters,        METH_VARARGS,
                                                              "Imports all the map files with a single import."},
                {"set_historical_map_parameters", (PyCFunction) set_historical_map_parameters, METH_VARARGS,
                                                              "Sets the historical map current_metacommunity_parameters."},
                {nullptr,                         nullptr, 0, nullptr}
        };

static PyTypeObject genSimulateDispersalType()
{
    PyTypeObject retSimulateDispersalType = {
            PyVarObject_HEAD_INIT(nullptr, 0)
    };
    retSimulateDispersalType.tp_name = (char *) "libnecsim.CDispersalSimulation";
    retSimulateDispersalType.tp_basicsize = sizeof(PySimulateDispersal);
    retSimulateDispersalType.tp_itemsize = 0;
    retSimulateDispersalType.tp_dealloc = (destructor) PySimulateDispersal_dealloc;
    retSimulateDispersalType.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC;
    retSimulateDispersalType.tp_doc = (char *) "Simulate a dispersal kernel on a landscape.";
    retSimulateDispersalType.tp_traverse = (traverseproc) PyTemplate_traverse<SimulateDispersal>;
    retSimulateDispersalType.tp_methods = SimulateDispersalMethods;
    //		.tp_members = PyTemplate_members<T>,
    retSimulateDispersalType.tp_getset = PyTemplate_gen_getsetters<SimulateDispersal>();
    retSimulateDispersalType.tp_init = (initproc) PySimulateDispersal_init;
    retSimulateDispersalType.tp_new = PySimulateDispersal_new;
    return retSimulateDispersalType;
}

static PyTypeObject C_SimulateDispersalType = genSimulateDispersalType();
#endif //NECSIM_CSIMULATEDISPERSAL_H
