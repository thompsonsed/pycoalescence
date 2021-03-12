# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

from typing import List
from cython.operator cimport dereference as deref
from libcpp.memory cimport shared_ptr, make_shared

from pycoalescence.system_operations import write_to_log

from pycoalescence.necsim.necsim cimport SpatialTree, Tree, GenericTree, ProtractedSpatialTree, ProtractedTree, \
    SpecSimParameters, Community, Metacommunity
from pycoalescence.necsim.necsim cimport setGlobalLogger

# Create a Cython extension type which holds a C++ instance
# as an attribute and create a bunch of forwarding methods
# Python extension type.


cdef class CSpatialSimulation:
    cdef GenericTree[SpatialTree] c_simulation  # Hold a C++ instance which we're wrapping
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_simulation = GenericTree[SpatialTree]()

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def import_from_config(self, config_file):
        self.set_logger()
        self.c_simulation.importSimulationVariables(config_file)

    def import_from_config_string(self, config):
        self.set_logger()
        cdef string config_str = config
        self.c_simulation.importSimulationVariablesFromString(config_str)

    def setup(self):
        self.set_logger()
        self.c_simulation.setup()

    def setup_resume(self, pause_directory, out_directory, seed, task, max_time):
        self.set_logger()
        self.c_simulation.wipeSimulationVariables()
        cdef string pause_directory_str = pause_directory
        cdef string out_directory_str = out_directory
        self.c_simulation.setResumeParameters(pause_directory_str, out_directory_str, seed, task, max_time)
        self.c_simulation.checkSims(pause_directory_str, seed, task)
        if self.c_simulation.hasPaused():
            self.c_simulation.setup()
        else:
            raise RuntimeError("Couldn't find paused simulation")

    def add_gillespie(self, gillespie_threshold):
        self.set_logger()
        self.c_simulation.addGillespie(gillespie_threshold)

    def run(self) -> bool:
        self.set_logger()
        return self.c_simulation.runSimulation()

    def apply_speciation_rates(self, speciation_rates: List[float]):
        self.set_logger()
        self.c_simulation.addSpeciationRates(speciation_rates)
        self.c_simulation.applyMultipleRates()

cdef class CNSESimulation:
    cdef GenericTree[Tree] c_simulation  # Hold a C++ instance which we're wrapping
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_simulation = GenericTree[Tree]()

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def import_from_config(self, config_file):
        self.set_logger()
        self.c_simulation.importSimulationVariables(config_file)

    def import_from_config_string(self, config):
        self.set_logger()
        cdef string config_str = config
        self.c_simulation.importSimulationVariablesFromString(config_str)

    def setup(self):
        self.set_logger()
        self.c_simulation.setup()

    def setup_resume(self, pause_directory, out_directory, seed, task, max_time):
        self.set_logger()
        self.c_simulation.wipeSimulationVariables()
        cdef string pause_directory_str = pause_directory
        cdef string out_directory_str = out_directory
        self.c_simulation.setResumeParameters(pause_directory_str, out_directory_str, seed, task, max_time)
        self.c_simulation.checkSims(pause_directory_str, seed, task)
        if self.c_simulation.hasPaused():
            self.c_simulation.setup()
        else:
            raise RuntimeError("Couldn't find paused simulation")

    def add_gillespie(self, gillespie_threshold):
        self.set_logger()
        self.c_simulation.addGillespie(gillespie_threshold)

    def run(self) -> bool:
        self.set_logger()
        return self.c_simulation.runSimulation()

    def apply_speciation_rates(self, speciation_rates: List[float]):
        self.set_logger()
        self.c_simulation.addSpeciationRates(speciation_rates)
        self.c_simulation.applyMultipleRates()

cdef class CPNSESimulation:
    cdef GenericTree[ProtractedTree] c_simulation  # Hold a C++ instance which we're wrapping
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_simulation = GenericTree[ProtractedTree]()

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def import_from_config(self, config_file):
        self.set_logger()
        self.c_simulation.importSimulationVariables(config_file)

    def import_from_config_string(self, config):
        self.set_logger()
        cdef string config_str = config
        self.c_simulation.importSimulationVariablesFromString(config_str)

    def setup(self):
        self.set_logger()
        self.c_simulation.setup()

    def setup_resume(self, pause_directory, out_directory, seed, task, max_time):
        self.set_logger()
        self.c_simulation.wipeSimulationVariables()
        cdef string pause_directory_str = pause_directory
        cdef string out_directory_str = out_directory
        self.c_simulation.setResumeParameters(pause_directory_str, out_directory_str, seed, task, max_time)
        self.c_simulation.checkSims(pause_directory_str, seed, task)
        if self.c_simulation.hasPaused():
            self.c_simulation.setup()
        else:
            raise RuntimeError("Couldn't find paused simulation")

    def add_gillespie(self, gillespie_threshold):
        self.set_logger()
        self.c_simulation.addGillespie(gillespie_threshold)

    def run(self) -> bool:
        self.set_logger()
        return self.c_simulation.runSimulation()

    def apply_speciation_rates(self, speciation_rates: List[float]):
        self.set_logger()
        self.c_simulation.addSpeciationRates(speciation_rates)
        self.c_simulation.applyMultipleRates()

cdef class CPSpatialSimulation:
    cdef GenericTree[ProtractedSpatialTree] c_simulation  # Hold a C++ instance which we're wrapping
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_simulation = GenericTree[ProtractedSpatialTree]()

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def import_from_config(self, config_file):
        self.set_logger()
        self.c_simulation.importSimulationVariables(config_file)

    def import_from_config_string(self, config):
        self.set_logger()
        cdef string config_str = config
        self.c_simulation.importSimulationVariablesFromString(config_str)

    def setup(self):
        self.set_logger()
        self.c_simulation.setup()

    def setup_resume(self, pause_directory, out_directory, seed, task, max_time):
        self.set_logger()
        self.c_simulation.wipeSimulationVariables()
        cdef string pause_directory_str = pause_directory
        cdef string out_directory_str = out_directory
        self.c_simulation.setResumeParameters(pause_directory_str, out_directory_str, seed, task, max_time)
        self.c_simulation.checkSims(pause_directory_str, seed, task)
        if self.c_simulation.hasPaused():
            self.c_simulation.setup()
        else:
            raise RuntimeError("Couldn't find paused simulation")

    def add_gillespie(self, gillespie_threshold):
        self.set_logger()
        self.c_simulation.addGillespie(gillespie_threshold)

    def run(self) -> bool:
        self.set_logger()
        return self.c_simulation.runSimulation()

    def apply_speciation_rates(self, speciation_rates: List[float]):
        self.set_logger()
        self.c_simulation.addSpeciationRates(speciation_rates)
        self.c_simulation.applyMultipleRates()

cdef class CCommunity:
    cdef Community c_community  # Hold a C++ instance which we're wrapping
    cdef shared_ptr[SpecSimParameters] c_spec_parameters
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_community = Community()
        self.c_spec_parameters = make_shared[SpecSimParameters]()

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def wipe_protracted_parameters(self):
        self.set_logger()
        deref(self.c_spec_parameters).wipeProtractedParameters()

    def add_protracted_parameters(self, double min_speciation_gen, double max_speciation_gen):
        self.set_logger()
        deref(self.c_spec_parameters).addProtractedParameters(min_speciation_gen, max_speciation_gen)

    def add_metacommunity_parameters(self, const unsigned long & metacommunity_size,
                                     const double & speciation_rate,
                                     const string & metacommunity_option,
                                     const unsigned long & metacommunity_reference):
        self.set_logger()
        deref(self.c_spec_parameters).addMetacommunityParameters(metacommunity_size, speciation_rate,
                                                                 metacommunity_option,
                                                                 metacommunity_reference)

    def reset(self):
        self.set_logger()
        deref(self.c_spec_parameters).wipe()

    def setup(self,
              database,
              bool use_spatial,
              sample_file,
              vector[double] times,
              fragment_file,
              vector[double] speciation_rates):
        self.set_logger()
        cdef string database_str = database
        cdef string sample_file_str = sample_file
        cdef string fragment_file_str = fragment_file
        deref(self.c_spec_parameters).setup(database_str, use_spatial, sample_file_str, times, fragment_file_str,
                                            speciation_rates)

    def add_time(self, time):
        self.set_logger()
        deref(self.c_spec_parameters).addTime(time)

    def apply(self):
        self.set_logger()
        self.c_community.applyNoOutput(self.c_spec_parameters)

    def output(self):
        self.set_logger()
        self.c_community.output()

    def speciate_remaining_lineages(self, file):
        self.set_logger()
        cdef string file_str = file
        self.c_community.speciateRemainingLineages(file_str)


cdef class CMetacommunity:
    cdef Metacommunity c_community  # Hold a C++ instance which we're wrapping
    cdef shared_ptr[SpecSimParameters] c_spec_parameters
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_community = Metacommunity()
        self.c_spec_parameters = make_shared[SpecSimParameters]()

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def wipe_protracted_parameters(self):
        self.set_logger()
        deref(self.c_spec_parameters).wipeProtractedParameters()

    def add_protracted_parameters(self, double min_speciation_gen, double max_speciation_gen):
        self.set_logger()
        deref(self.c_spec_parameters).addProtractedParameters(min_speciation_gen, max_speciation_gen)

    def add_metacommunity_parameters(self, const unsigned long & metacommunity_size,
                                     const double & speciation_rate,
                                     const string & metacommunity_option,
                                     const unsigned long & metacommunity_reference):
        self.set_logger()
        deref(self.c_spec_parameters).addMetacommunityParameters(metacommunity_size, speciation_rate,
                                                                 metacommunity_option,
                                                                 metacommunity_reference)

    def reset(self):
        self.set_logger()
        deref(self.c_spec_parameters).wipe()

    def setup(self,
              database,
              bool use_spatial,
              sample_file,
              vector[double] times,
              fragment_file,
              vector[double] speciation_rates):
        self.set_logger()
        cdef string database_str = database
        cdef string sample_file_str = sample_file
        cdef string fragment_file_str = fragment_file
        deref(self.c_spec_parameters).setup(database_str, use_spatial, sample_file_str, times, fragment_file_str,
                                            speciation_rates)

    def add_time(self, time):
        self.set_logger()
        deref(self.c_spec_parameters).addTime(time)

    def apply(self):
        self.set_logger()
        self.c_community.applyNoOutput(self.c_spec_parameters)

    def output(self):
        self.set_logger()
        self.c_community.output()

    def speciate_remaining_lineages(self, file):
        self.set_logger()
        cdef string file_str = file
        self.c_community.speciateRemainingLineages(file_str)


cdef class CLandscapeMetricsCalculator:
    cdef LandscapeMetricsCalculator c_landscapes  # Hold a C++ instance which we're wrapping
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_landscapes = LandscapeMetricsCalculator()

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def import_map(self, file_name):
        self.set_logger()
        cdef string file_name_str = file_name
        self.c_landscapes.importMap(file_name_str)

    def calculate_MNN(self):
        self.set_logger()
        return self.c_landscapes.calculateMNN()

    def calculate_CLUMPY(self):
        self.set_logger()
        return self.c_landscapes.calculateClumpiness()
