# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

from typing import List
from logging import Logger

from pycoalescence.system_operations import write_to_log

from pycoalescence.necsim.necsim cimport SpatialTree
from pycoalescence.necsim.necsim cimport setGlobalLogger


# Create a Cython extension type which holds a C++ instance
# as an attribute and create a bunch of forwarding methods
# Python extension type.


cdef class CSpatialSimulation:
    cdef SpatialTree c_simulation  # Hold a C++ instance which we're wrapping
    cdef object logger

    def __cinit__(self, object logger):
        self.logger = logger
        self.c_simulation = SpatialTree()

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
        self.c_simulation.setResumeParameters(pause_directory, out_directory, seed, task, max_time)
        self.c_simulation.checkSims(pause_directory, seed, task)
        if self.c_simulation.hasPaused():
            self.c_simulation.setup()
        else:
            raise RuntimeError("Couldn't find paused simulation")

    def add_gillespie(self, gillespie_threshold):
        self.set_logger()
        self.c_simulation.addGillespie(gillespie_threshold);

    def run(self) -> bool:
        self.set_logger()
        return self.c_simulation.runSimulation()

    def apply_speciation_rates(self, speciation_rates: List[float]):
        self.set_logger()
        self.c_simulation.addSpeciationRates(speciation_rates)
        self.c_simulation.applyMultipleRates()