# distutils: sources = necsim/CSimulation.cpp
from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr

cdef extern from "necsim/SpatialTree.h" namespace "necsim":
    cdef cppclass SpatialTree:
        pass

cdef extern from "necsim/Tree.h" namespace "necsim":
    cdef cppclass Tree:
        pass


cdef extern from "necsim/ProtractedTree.h" namespace "necsim":
    cdef cppclass ProtractedTree:
        pass

cdef extern from "necsim/ProtractedSpatialTree.h" namespace "necsim":
    cdef cppclass ProtractedSpatialTree:
        pass

cdef extern from "necsim/SpecSimParameters.h" namespace "necsim":
    cdef struct SpecSimParameters:
        void addTime(double time) except +
        void setup(string database_str,
                   bool use_spatial,
                   string sample_file_str,
                   vector[double] times,
                   string fragment_file_str,
                   vector[double] speciation_rates) except +
        void addProtractedParameters(double proc_min, double proc_max) except +
        void addMetacommunityParameters(const unsigned long & metacommunity_size,
                                        const double & speciation_rate,
                                        const string & metacommunity_option,
                                        const unsigned long & metacommunity_reference) except +
        void wipeProtractedParameters() except +
        void wipe() except +


cdef extern from "PyLogging.h" namespace "necsim":
    void setGlobalLogger(object logger, object log_function) except +



# Declare the class with cdef
cdef extern from "necsim/GenericTree.h" namespace "necsim":
    cdef cppclass GenericTree[T]:
        GenericTree() except +
        void wipeSimulationVariables() except +
        void importSimulationVariables(string config_file) except +
        void importSimulationVariablesFromString(string config_string) except +
        void setup() except +
        bool runSimulation() except +
        void setResumeParameters(string pause_directory_str, string out_directory_str, int seed, int task,
                                 int max_time) except +
        void checkSims(string pause_directory, int seed, int task) except +
        bool hasPaused() except +
        void addGillespie(const double & g_threshold) except +
        void addSpeciationRates(vector[long double] spec_rates_long) except +
        void applyMultipleRates() except +
        void output() except +


# Declare the class with cdef
cdef extern from "necsim/Community.h" namespace "necsim":
    cdef cppclass Community:
        Community() except +

        void applyNoOutput(shared_ptr[SpecSimParameters] sp) except +
        void output() except +
        void speciateRemainingLineages(const string & filename) except +

# Declare the class with cdef
cdef extern from "necsim/Metacommunity.h" namespace "necsim":
    cdef cppclass Metacommunity:
        Metacommunity() except +

        void applyNoOutput(shared_ptr[SpecSimParameters] sp) except +
        void output() except +
        void speciateRemainingLineages(const string & filename) except +

cdef extern from "LandscapeMetricsCalculator.h":
    cdef cppclass LandscapeMetricsCalculator:
        LandscapeMetricsCalculator() except +

        void importMap(const string &filename) except +
        double calculateMNN() except +
        double calculateClumpiness() except +
