// This file is part of NECSim project which is released under BSD-3 license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.

/**
 * @author Samuel Thompson
 * @date 01/08/2017
 * @file applyspecmodule.h
 *
 * @copyright <a href="https://opensource.org/licenses/BSD-3-Clause">BSD-3 Licence.</a>
 * @brief Contains the module for python integration for additional applying speciation rates after a 
 * simulation is completed.
 *
 * Requires command line parameters and generates a data object from them.
 * Contact: samuel.thompson14@imperial.ac.uk or thompsonsed@gmail.com
 */
 
#include <Python.h>
#ifndef PYTHON_COMPILE
#define PYTHON_COMPILE
#endif
#include <vector>
#include <string>


#ifndef APPLY_SPEC_IMPORT
#define APPLY_SPEC_IMPORT
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
static PyObject *ApplySpeciationError;

// Conditional compilation for python >= 3.0 (changed how python integration worked)
#if PY_MAJOR_VERSION >= 3
#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_applyspecmodule(void)
#else
#define INITERROR return

PyMODINIT_FUNC
initapplyspecmodule(void)
#endif
;
#endif

