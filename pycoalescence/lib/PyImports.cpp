// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file PyImports.cpp
 * @brief Routines for importing Python objects to C++ vectors.
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
 */

#include <cstring>
#ifndef WIN_INSTALL
#include <unistd.h>
#endif
#include <csignal>
#include "PyImports.h"

bool importPyListToVectorString(PyObject *list_input, vector<string> &output, const string &err_msg)
{
	Py_ssize_t n = PyList_Size(list_input);
	PyObject * item;
	for(int i=0; i<n; i++)
	{
		item = PyList_GetItem(list_input, i);
#if PY_MAJOR_VERSION >= 3
		if(!PyUnicode_Check(item))
#else
		if(!PyString_Check(item))
#endif
		{
			PyErr_SetString(PyExc_TypeError, err_msg.c_str());
			return false;
		}
#if PY_MAJOR_VERSION >= 3
		const char * tmpspec = PyUnicode_AsUTF8(item);
#else
		char * tmpspec = PyString_AsString(item);
#endif
		output.emplace_back(tmpspec);
	}
	return true;
}

bool importPyListToVectorULong(PyObject *list_input, vector<unsigned long> &output, const string &err_msg)
{
	Py_ssize_t n = PyList_Size(list_input);
	PyObject * item;
	for(int i=0; i<n; i++)
	{
		item = PyList_GetItem(list_input, i);
		if(!PyLong_Check(item)
#if PY_MAJOR_VERSION < 3
		   && !PyInt_Check(item)
#endif // PY_MAJOR_VERSION < 3
				)
		{
			PyErr_SetString(PyExc_TypeError, err_msg.c_str());
			return false;
		}
		unsigned long tmpspec = PyLong_AsUnsignedLong(item);
		output.emplace_back(tmpspec);
	}
	return true;
}


bool importPyListToVectorDouble(PyObject *list_input, vector<double> &output, const string &err_msg)
{
	if(list_input == nullptr)
	{
		return true;
	}
	Py_ssize_t n = PyList_Size(list_input);
	PyObject * item;
	for(int i=0; i<n; i++)
	{
		item = PyList_GetItem(list_input, i);
		if(!PyFloat_Check(item))
		{
			PyErr_SetString(PyExc_TypeError, err_msg.c_str());
			return false;
		}
		double tmpspec = PyFloat_AS_DOUBLE(item);
		output.push_back(tmpspec);
	}
	return true;
}
