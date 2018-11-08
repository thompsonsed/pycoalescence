// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file necsim.h
 * @brief Contains the functions allowing integration of the pycoalescence Python module directly to the c++
 * @copyright <a href="https://opensource.org/licenses/MIT">MIT Licence.</a>
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
 * @brief A Python error container for all run-time errors.
 */
static PyObject *necsimError;


// Conditional compilation for Python >= 3.0 (changed how Python integration worked)
#if PY_MAJOR_VERSION >= 3
#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_libnecsim(void)
#else
#define INITERROR return

PyMODINIT_FUNC
initlibnecsim(void)
#endif
;
#endif

