# distutils: sources = necsim/CSimulation.cpp
from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector

cdef extern from "necsim/SpatialTree.h" namespace "necsim":
    cdef cppclass CSimulation:
        pass

cdef extern from "PyLogging.h" namespace "necsim":
    void setGlobalLogger(object logger, object log_function) except +

# Declare the class with cdef
cdef extern from "necsim/SpatialTree.cpp" namespace "necsim":
    cdef cppclass SpatialTree:
        SpatialTree() except +
        void wipeSimulationVariables() except +
        void importSimulationVariables(string config_file) except +
        void importSimulationVariablesFromString(string config_string) except +
        void setup() except +
        bool runSimulation() except +
        void setResumeParameters(string pause_directory_str, string out_directory_str, int seed, int task, int max_time) except +
        void checkSims(string pause_directory, int seed, int task) except +
        bool hasPaused() except +
        void addGillespie(const double &g_threshold) except +
        void addSpeciationRates(vector[long double] spec_rates_long) except +
        void applyMultipleRates() except +


