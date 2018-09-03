// This file is part of NECSim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file CCommunity.h
 * @brief Wraps the various C++ community objects for accessing via python.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */

#ifndef NECSIM_C_COMMUNITY_H
#define NECSIM_C_COMMUNITY_H

#include <Python.h>
#include <string>
#include <structmember.h>
#include "PyImports.h"
#include "necsim/Community.h"
#include "necsim/Metacommunity.h"
#include "PyTemplates.h"
#include "necsim.h"

using namespace std;

/**
 * @brief Template for CCommunity and CMetacommunity objects for exporting to python
 * @tparam T the type of the Community
 */
template<class T>
class PyCommunityTemplate : public PyTemplate<T>
{
public:
	SpecSimParameters *specSimParameters;
};

/**
 * @brief Sets up the speciation parameters.
 * @tparam T the type of the Community
 * @param self the reference to the python self object
 * @param args the arguments to pass
 * @return Py_RETURN_NONE
 */
template<class T>
static PyObject *setupApplySpeciation(PyCommunityTemplate<T> *self, PyObject *args)
{
	char *database;
	int record_spatial;
	char *sample_file;
	char *fragment_file;
	unsigned long metacommunity_size = 0;
	double metacommunity_speciation_rate = 0.0;
	PyObject *list_speciation_rates;
	PyObject *list_times;
	PyObject *list_min_spec_gen = nullptr;
	PyObject *list_max_spec_gen = nullptr;
	if(!PyArg_ParseTuple(args, "sissO!O!|O!O!kd", &database, &record_spatial, &sample_file,
						 &fragment_file, &PyList_Type, &list_speciation_rates, &PyList_Type, &list_times, &PyList_Type,
						 &list_min_spec_gen, &PyList_Type,
						 &list_max_spec_gen, &metacommunity_size, &metacommunity_speciation_rate))
	{
		return nullptr;
	}
	getGlobalLogger(self->logger, self->log_function);
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

	// Convert all our variables to the relevant form
	string database_str = database;
	auto use_spatial = static_cast<bool>(record_spatial);
	string sample_file_str = sample_file;
	string fragment_file_str = fragment_file;
	vector<double> speciation_rates;
	vector<double> times;
	vector<double> min_speciation_gen;
	vector<double> max_speciation_gen;
	if(!importPyListToVectorDouble(list_speciation_rates, speciation_rates, "Speciation rates must be floats."))
	{
		return nullptr;
	}
	if(!importPyListToVectorDouble(list_times, times, "Times must be floats."))
	{
		return nullptr;
	}
	if(!list_min_spec_gen || !list_max_spec_gen)
	{
		min_speciation_gen.push_back(0.0);
		max_speciation_gen.push_back(0.0);
	}
	else
	{
		if(!importPyListToVectorDouble(list_min_spec_gen, min_speciation_gen,
									   "Minimum protracted generations must be floats."))
		{
			return nullptr;
		}
		if(!importPyListToVectorDouble(list_max_spec_gen, max_speciation_gen,
									   "Maximum protracted generations must be floats."))
		{
			return nullptr;
		}
	}
	try
	{
		self->specSimParameters->setup(std::move(database_str), use_spatial, sample_file_str, times,
									   fragment_file_str, speciation_rates, min_speciation_gen,
									   max_speciation_gen, metacommunity_size, metacommunity_speciation_rate);
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
 * @brief Adds a time to the speciation parameters.
 * @tparam T the type of the Community
 * @param self the reference to the python self object
 * @param args the arguments to pass
 * @return Py_RETURN_NONE
 */
template<class T>
static PyObject *addTime(PyCommunityTemplate<T> *self, PyObject *args)
{
	double time;
	if(!PyArg_ParseTuple(args, "d", &time))
	{
		return nullptr;
	}
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		self->specSimParameters->addTime(time);
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
 * @brief Adds a set of protracted parameters to the speciation parameters.
 * @tparam T the type of the Community
 * @param self the reference to the python self object
 * @param args the arguments to pass
 * @return Py_RETURN_NONE
 */
template<class T>
static PyObject *addProtractedParameters(PyCommunityTemplate<T> *self, PyObject *args)
{
	double proc_min, proc_max;
	if(!PyArg_ParseTuple(args, "dd", &proc_min, &proc_max))
	{
		return nullptr;
	}
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		self->specSimParameters->addProtractedParameters(proc_min, proc_max);
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
 * @brief Wipes the protracted parameters vectors
 * @tparam T the type of the Community
 * @param self the reference to the python self object
 * @return Py_RETURN_NONE
 */
template<class T>
static PyObject *wipeProtractedParameters(PyCommunityTemplate<T> *self)
{
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		self->specSimParameters->protracted_parameters.clear();
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
 * @brief Applies the speciation parameters to the coalescence tree to generate the community.
 * @tparam T the type of the Community
 * @param self the reference to the python self object
 * @return Py_RETURN_NONE
 */
template<class T>
static PyObject *apply(PyCommunityTemplate<T> *self)
{

	// Now run the actual simulation
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		self->base_object->applyNoOutput(self->specSimParameters);
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
 * @brief Outputs the community to database.
 * @tparam T the type of the Community
 * @param self the reference to the python self object
 * @return Py_RETURN_NONE
 */
template<class T>
static PyObject *output(PyCommunityTemplate<T> *self)
{

	// Now run the actual simulation
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		self->base_object->output();
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
 * @brief Resets the internal community object.
 * @tparam T the type of the Community
 * @param self the reference to the python self object
 * @return Py_RETURN_NONE
 */
template<class T>
static PyObject *reset(PyCommunityTemplate<T> *self)
{

	// Now run the actual simulation
	try
	{
		getGlobalLogger(self->logger, self->log_function);
		if(self->base_object != nullptr)
		{
			self->base_object.reset();
		}
		self->base_object = make_unique<T>();
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
static void
PyCommunity_dealloc(PyCommunityTemplate<T> *self)
{
	if(self->specSimParameters != nullptr)
	{
		delete self->specSimParameters;
		self->specSimParameters = nullptr;
	}
	PyTemplate_dealloc<T>(self);
}

/**
 * @brief Initialises the Community object.
 * @tparam T the template type
 * @param self the python self object
 * @param args arguments to pass to constructor
 * @param kwds keyword arguments to pass to constructor
 * @return
 */
template<class T>
static int
PyCommunity_init(PyCommunityTemplate<T> *self, PyObject *args, PyObject *kwds)
{
	self->specSimParameters = new SpecSimParameters();
	return PyTemplate_init<T>(self, args, kwds);
}

/**
 * @brief Methods associated with the python CCommunity object
 * @tparam T the type of the Community
 */
template<class T>
PyMethodDef *genCommunityMethods()
{
	static PyMethodDef CommunityMethods[] =
			{
					{"setup",                      (PyCFunction) setupApplySpeciation<T>,     METH_VARARGS,
															   "Sets the speciation parameters to be applied to the tree."},
					{"add_time",                   (PyCFunction) addTime<T>,                  METH_VARARGS,
															   "Adds a time to apply to the simulation."},
					{"wipe_protracted_parameters", (PyCFunction) wipeProtractedParameters<T>, METH_NOARGS,
															   "Wipes the protracted parameters."},
					{"add_protracted_parameters",  (PyCFunction) addProtractedParameters<T>,  METH_VARARGS,
															   "Adds protracted speciation parameters to apply to the simulation."},
					{"apply",                      (PyCFunction) apply<T>,                    METH_NOARGS,
															   "Applies the new speciation rate(s) to the coalescence tree."},
					{"output",                     (PyCFunction) output<T>,                   METH_NOARGS,
															   "Outputs the database to file."},
					{"reset",                      (PyCFunction) reset<T>,                    METH_NOARGS,
															   "Resets the internal object."},

					{nullptr,                      nullptr, 0, nullptr}
			};
	return CommunityMethods;
}

template<class T>
static PyTypeObject genCommunityType(char *tp_name, char *tp_doc)
{
	PyTypeObject ret_Community_Type = {
			PyVarObject_HEAD_INIT(nullptr, 0)
	};
	ret_Community_Type.tp_name = tp_name;
	ret_Community_Type.tp_doc = tp_doc;
	ret_Community_Type.tp_basicsize = sizeof(PyCommunityTemplate<T>);
	ret_Community_Type.tp_itemsize = 0;
	ret_Community_Type.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC;
	ret_Community_Type.tp_new = PyTemplate_new<T>;
	ret_Community_Type.tp_init = (initproc) PyCommunity_init<T>;
	ret_Community_Type.tp_dealloc = (destructor) PyCommunity_dealloc<T>;
	ret_Community_Type.tp_traverse = (traverseproc) PyTemplate_traverse<T>;
//		.tp_members = PyTemplate_members<T>,
	ret_Community_Type.tp_methods = genCommunityMethods<T>();
	ret_Community_Type.tp_getset = PyTemplate_gen_getsetters<T>();
//	static PyTypeObject outType = ret_Community_Type;
	return ret_Community_Type;
}

template<class T>
static PyTypeObject genCommunityType(string tp_name, string tp_doc)
{
	return genCommunityType<T>(const_cast<char *>(tp_name.c_str()), const_cast<char *>(tp_doc.c_str()));
}

static PyTypeObject
		C_CommunityType = genCommunityType<Community>((char *) "libnecsim.CCommunity",
													  (char *) "C class for generating communities from neutral simulations");
static PyTypeObject C_MetacommunityType = genCommunityType<Metacommunity>((char *) "libnecsim.CMetacommunity",
																		  (char *) "C class for generating communities from neutral simulations");

#endif //NECSIM_C_COMMUNITY_H
