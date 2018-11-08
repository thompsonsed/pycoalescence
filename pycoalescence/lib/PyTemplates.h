// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file PyTemplates.h
 * @brief Routines for controlling logger from C++ to python.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */

#ifndef NECSIM_PYTEMPLATES_H
#define NECSIM_PYTEMPLATES_H

#include <Python.h>
#include <structmember.h>
#include <memory>
#include "PyImports.h"

template<class T>
class PyTemplate
{
public:
	PyObject_HEAD
	PyObject *logger = nullptr;
	PyObject *log_function = nullptr;
	std::unique_ptr<T> base_object = nullptr;

	virtual ~PyTemplate();
//	virtual void init()
//	{
//
//	}
};

template<class T>
static int
PyTemplate_traverse(PyTemplate<T> *self, visitproc visit, void *arg)
{
	Py_VISIT(self->logger);
	Py_VISIT(self->log_function);
	return 0;
}

template<class T>

static int
PyTemplate_clear(PyTemplate<T> *self)
{
	Py_CLEAR(self->logger);
	Py_CLEAR(self->log_function);
	return 0;
}

template<class T>
static void
PyTemplate_dealloc(PyTemplate<T> *self)
{
	if(self->base_object != nullptr)
	{
		self->base_object.reset();
		self->base_object = nullptr;
	}
	removeGlobalLogger();
	PyObject_GC_UnTrack(self);
	PyTemplate_clear(self);
	Py_TYPE(self)->tp_free((PyObject *) self);
}

template<class T>
static PyObject *
PyTemplate_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyTemplate<T> *self;
	self = (PyTemplate<T> *) type->tp_alloc(type, 0);
	if(self != nullptr)
	{
		self->logger = nullptr;
		self->log_function = nullptr;
	}
	return (PyObject *) self;
}

template<class T>
void initialise_logger(PyTemplate<T> *self)
{
	if(self->logger == nullptr)
	{
		throw runtime_error("Logger has not been set");
	}
	PyObject *l;
	Py_INCREF(self->logger);
	l = self->logger;
	PyObject *c;
	Py_INCREF(self->log_function);
	c = self->log_function;
	getGlobalLogger(l, c);
}

template<class T>
static int
PyTemplate_init(PyTemplate<T> *self, PyObject *args, PyObject *kwds)
{
	PyObject *tmp_logger;
	PyObject *tmp_call_back;
	PyObject *tmp;
//	static char *kwlist[] = {const_cast<char *>("logger"), const_cast<char *>("logging_function"), NULL};

	if(PyArg_ParseTuple(args, "OO", &tmp_logger, &tmp_call_back))
	{
		if(!PyCallable_Check(tmp_call_back))
		{
			PyErr_SetString(PyExc_TypeError, "parameter must be callable");
			return -1;
		}
		// Dispose of previous references
		if(tmp_logger)
		{
			tmp = self->logger;
			Py_INCREF(tmp_logger);
			self->logger = tmp_logger;
			Py_XDECREF(tmp);
		}
		if(tmp_call_back)
		{
			tmp = self->log_function;
			Py_INCREF(tmp_call_back);
			self->log_function = tmp_call_back;
			Py_XDECREF(tmp);
		}
		try
		{
			initialise_logger(self);
			self->base_object = make_unique<T>();
//			self->init();
		}
		catch(exception &e)
		{
			removeGlobalLogger();
			string errmsg = "error initialising PyTemplate object: ";
			errmsg += e.what();
			PyErr_SetString(PyExc_TypeError, errmsg.c_str());
			return -1;
		}
		/* Boilerplate to return "None" */
		return 0;
	}
	return -1;
}

template<class T>
static PyObject *
PyTemplate_getLogging(PyTemplate<T> *self, void *closure)
{
	Py_INCREF(self->logger);
	return self->logger;
}

template<class T>
static int
PyTemplate_setLogging(PyTemplate<T> *self, PyObject *value, void *closure)
{
	PyObject *tmp;
	if(value == nullptr)
	{
		PyErr_SetString(PyExc_TypeError, "Cannot delete the logger attribute");
		return -1;
	}
	tmp = self->logger;
	Py_INCREF(value);
	self->logger = value;
	Py_XDECREF(tmp);
	return 0;
}

template<class T>
static PyObject *
PyTemplate_getCallLogger(PyTemplate<T> *self, void *closure)
{
	Py_INCREF(self->log_function);
	return self->log_function;
}

template<class T>
static int
PyTemplate_setCallLogger(PyTemplate<T> *self, PyObject *value, void *closure)
{
	PyObject *tmp;
	if(value == nullptr)
	{
		PyErr_SetString(PyExc_TypeError, "Cannot delete the logger attribute");
		return -1;
	}
	tmp = self->log_function;
	Py_INCREF(value);
	self->log_function = value;
	Py_XDECREF(tmp);
	return 0;
}

template<typename T>
PyGetSetDef *PyTemplate_gen_getsetters()
{
	static PyGetSetDef PyTemplate_getsetters[] = {
			{const_cast<char *>("logger"),       (getter) PyTemplate_getLogging<T>,    (setter) PyTemplate_setLogging<T>,
					const_cast<char *>("the reference to the logger module"), nullptr},
			{const_cast<char *>("log_function"), (getter) PyTemplate_getCallLogger<T>, (setter) PyTemplate_setCallLogger<T>,
					const_cast<char *>("the logger call function to use"),    nullptr},
			{nullptr}  /* Sentinel */
	};
	return PyTemplate_getsetters;
}

#endif // NECSIM_PYTEMPLATES_H
