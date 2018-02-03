// This file is part of NECSim project which is released under BSD-3 license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details
/**
 * @author Samuel Thompson
 * @file dispersalmodule.h
 * @brief Contains the functions for testing dispersal methods using efficient c++ routines.
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
// */
#include <Python.h>
#ifndef PYTHON_COMPILE
#define PYTHON_COMPILE
#endif
#include <vector>
#include <string>



#ifndef DISPERSAL_IMPORT
#define DISPERSAL_IMPORT
using namespace std;
struct module_state
{
	PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

/**
 * @brief A python error container for all dispersal run-time errors.
 */
static PyObject *DispersalError;

// Conditional compilation for python >= 3.0 (changed how python integration worked)
#if PY_MAJOR_VERSION >= 3
#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_dispersalmodule(void)
#else
#define INITERROR return

PyMODINIT_FUNC
initdispersalmodule(void)
#endif
;
#endif

