// This file is part of NECSim project which is released under BSD-3 license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details
/**
 * @author Samuel Thompson
 * @file necsimmodule.h
 * @brief Contains the functions allowing integration of the PyCoalescence python module directly to the c++
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
// */
#include <Python.h>

#include <vector>
#include <string>


#ifndef NECSIM_IMPORT
#define NECSIM_IMPORT
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
 * @brief A python error container for all run-time errors.
 */
static PyObject *NECSimError;


// Conditional compilation for python >= 3.0 (changed how python integration worked)
#if PY_MAJOR_VERSION >= 3
#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_necsimmodule(void)
#else
#define INITERROR return

PyMODINIT_FUNC
initnecsimmodule(void)
#endif
;
#endif

