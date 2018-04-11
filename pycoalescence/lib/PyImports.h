//
// Created by Sam Thompson on 02/04/2018.
//

#ifndef PYIMPORTS_H
#define PYIMPORTS_H

#include <Python.h>
#include <utility>
#include <vector>
#include <string>
using namespace std;


/**
 * @brief Imports the provided input list to the output vector.
 * Sets the python error message and returns false if one of the list elements is not a string type.
 * @param list_input a python list object to iterate over
 * @param output the output vector of strings to push to
 * @param err_msg error message to through if an element is not of float type
 * @return true if no error is thrown, false otherwise
 */
bool importPyListToVectorString(PyObject *list_input, vector<string> &output, const string &err_msg);

/**
 * @brief Imports the provided input list to the output vector.
 * Sets the python error message and returns false if one of the list elements is not of int type.
 * @param list_input a python list object to iterate over
 * @param output the output vector of int to push to
 * @param err_msg error message to through if an element is not of float type
 * @return true if no error is thrown, false otherwise
 */
bool importPyListToVectorULong(PyObject *list_input, vector<unsigned long> &output, const string &err_msg);


/**
 * @brief Imports the provided input list to the output vector.
 * Sets the python error message and returns false if one of the list elements is not a float type.
 * @param list_input a python list object to iterate over
 * @param output the output vector of doubles to push to
 * @param err_msg error message to through if an element is not of float type
 * @return true if no error is thrown, false otherwise
 */
bool importPyListToVectorDouble(PyObject *list_input, vector<double> &output, const string &err_msg);
#endif //SPECIATIONCOUNTER_PYIMPORTS_H
