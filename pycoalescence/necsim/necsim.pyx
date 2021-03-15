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
              record_fragments,
              vector[double] speciation_rates,
              vector[double] times):
        self.set_logger()
        cdef string database_str = database
        cdef string sample_file_str = sample_file
        cdef string fragment_file_str = record_fragments
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
              record_fragments,
              vector[double] speciation_rates,
              vector[double] times):
        self.set_logger()
        cdef string database_str = database
        cdef string sample_file_str = sample_file
        cdef string fragment_file_str = record_fragments
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

cdef class CDispersalSimulator:
    cdef SimulateDispersal c_simulator
    cdef shared_ptr[SimParameters] c_sim_parameters
    cdef object logger
    cdef object output_database
    cdef bool has_imported_maps
    cdef bool needs_update
    cdef bool printing

    def __cinit__(self, logger):
        self.logger = logger
        self.c_simulator = SimulateDispersal()
        self.c_sim_parameters = make_shared[SimParameters]()
        self.output_database = "none"
        self.has_imported_maps = False
        self.needs_update = True
        self.printing = True

    def set_logger(self):
        setGlobalLogger(self.logger, write_to_log)

    def set_output_database(self, output_database):
        self.set_logger()
        cdef string output_f = output_database
        if self.output_database == "none":
            self.output_database = output_database
            self.c_simulator.setOutputDatabase(output_f)

    def import_maps_base(self,
                    double deme,
                    fine_map_file,
                    unsigned long fine_map_x_size,
                    unsigned long fine_map_y_size,
                    unsigned long fine_map_x_offset,
                    unsigned long fine_map_y_offset,
                    unsigned long sample_map_x_size,
                    unsigned long sample_map_y_size,
                    coarse_map_file,
                    unsigned long coarse_map_x_size,
                    unsigned long coarse_map_y_size,
                    unsigned long coarse_map_x_offset,
                    unsigned long coarse_map_y_offset,
                    unsigned long coarse_map_scale,
                    landscape_type,
                    ):
        self.set_logger()
        cdef string fine_map_file_str = fine_map_file
        cdef string coarse_map_file_str = coarse_map_file
        if self.has_imported_maps:
            raise RuntimeError("Maps have already been imported")
        deref(self.c_sim_parameters).setMapParameters(fine_map_file_str, coarse_map_file_str,
                                                      sample_map_x_size,
                                                      sample_map_y_size,
                                                      fine_map_x_size,
                                                      fine_map_y_size,
                                                      fine_map_x_offset,
                                                      fine_map_y_offset,
                                                      coarse_map_x_size,
                                                      coarse_map_y_size, coarse_map_x_offset,
                                                      coarse_map_y_offset, coarse_map_scale,
                                                      deme, landscape_type)
    def import_maps(self, double deme,
                    fine_map_file,
                    unsigned long fine_map_x_size,
                    unsigned long fine_map_y_size,
                    unsigned long fine_map_x_offset,
                    unsigned long fine_map_y_offset,
                    unsigned long sample_map_x_size,
                    unsigned long sample_map_y_size,
                    coarse_map_file,
                    unsigned long coarse_map_x_size,
                    unsigned long coarse_map_y_size,
                    unsigned long coarse_map_x_offset,
                    unsigned long coarse_map_y_offset,
                    unsigned long coarse_map_scale,
                    landscape_type):
        self.import_maps_base(deme,
                         fine_map_file,
                         fine_map_x_size,
                         fine_map_y_size,
                         fine_map_x_offset,
                         fine_map_y_offset,
                         sample_map_x_size,
                         sample_map_y_size,
                         coarse_map_file,
                         coarse_map_x_size,
                         coarse_map_y_size,
                         coarse_map_x_offset,
                         coarse_map_y_offset,
                         coarse_map_scale,
                         landscape_type)
        self.setup()
        self.c_simulator.importMaps()
        self.has_imported_maps = True

    def import_all_maps(self, double deme,
                        fine_map_file,
                        unsigned long int fine_map_x_size,
                        unsigned long fine_map_y_size,
                        unsigned long fine_map_x_offset,
                        unsigned long fine_map_y_offset,
                        unsigned long sample_map_x_size,
                        unsigned long sample_map_y_size,
                        coarse_map_file,
                        unsigned long coarse_map_x_size,
                        unsigned long coarse_map_y_size,
                        unsigned long coarse_map_x_offset,
                        unsigned long coarse_map_y_offset,
                        unsigned long coarse_map_scale,
                        landscape_type,
                        vector[string] path_fine,
                        vector[unsigned long] number_fine,
                        vector[double] rate_fine,
                        vector[double] time_fine,
                        vector[string] path_coarse,
                        vector[unsigned long] number_coarse,
                        vector[double] rate_coarse,
                        vector[double] time_coarse):
        self.set_logger()
        self.import_maps_base(deme,
                         fine_map_file,
                         fine_map_x_size,
                         fine_map_y_size,
                         fine_map_x_offset,
                         fine_map_y_offset,
                         sample_map_x_size,
                         sample_map_y_size,
                         coarse_map_file,
                         coarse_map_x_size,
                         coarse_map_y_size,
                         coarse_map_x_offset,
                         coarse_map_y_offset,
                         coarse_map_scale,
                         landscape_type)
        deref(self.c_sim_parameters).setHistoricalMapParameters(path_fine,
                                                                number_fine,
                                                                rate_fine,
                                                                time_fine,
                                                                path_coarse,
                                                                number_coarse,
                                                                rate_coarse,
                                                                time_coarse)
        self.setup()
        self.c_simulator.importMaps()
        self.has_imported_maps = True

    def check_completed(self):
        if self.output_database == "none":
            raise RuntimeError("Output database has not been set.")
        if not self.has_imported_maps:
            raise RuntimeError("Maps have not been imported - cannot start simulations.")

    def setup(self):
        if self.needs_update:
            self.set_logger()
            self.c_simulator.setSimulationParameters(self.c_sim_parameters, self.printing)
            self.c_simulator.setDispersalParameters()
            self.printing = False
            self.needs_update = False

    def set_dispersal_parameters(self,
                                 dispersal_method,
                                 dispersal_file,
                                 double sigma,
                                 double tau,
                                 double m_prob,
                                 double cutoff,
                                 double dispersal_relative_cost,
                                 bool restrict_self):
        cdef string dispersal_method_str = dispersal_method
        cdef string dispersal_file_str = dispersal_file
        cdef string closed_str = b"closed"
        self.set_logger()
        deref(self.c_sim_parameters).setDispersalParameters(dispersal_method,
                                                            sigma,
                                                            tau,
                                                            m_prob,
                                                            cutoff,
                                                            dispersal_relative_cost,
                                                            restrict_self,
                                                            closed_str,
                                                            dispersal_file_str)
        self.needs_update = True

    def base_setup(self, unsigned long number_repeats,
                   vector[unsigned long] number_steps, unsigned long seed, unsigned long number_workers):
        self.set_logger()
        self.setup()
        self.c_simulator.setSeed(seed)
        self.c_simulator.setNumberRepeats(number_repeats)
        self.c_simulator.setNumberSteps(number_steps)
        self.c_simulator.setNumberWorkers(number_workers)
        if not self.has_imported_maps:
            self.c_simulator.importMaps()
        self.check_completed()

    def write_database(self, table_name):
        cdef string table_name_str = table_name
        self.c_simulator.writeDatabase(table_name_str)

    def run_mean_distance_travelled(self, unsigned long number_repeats,
                                    vector[unsigned long] number_steps, unsigned long seed,
                                    unsigned long number_workers):
        self.base_setup(number_repeats, number_steps, seed, number_workers)
        self.c_simulator.runMeanDistanceTravelled()
        self.write_database("DISTANCES_TRAVELLED")

    def run_all_distance_travelled(self, unsigned long number_repeats, vector[unsigned long] number_steps,
                                   unsigned long seed, unsigned long number_workers):
        self.base_setup(number_repeats, number_steps, seed, number_workers)
        self.c_simulator.runAllDistanceTravelled()
        self.write_database("DISTANCES_TRAVELLED")

    def run_sample_distance_travelled(self, vector[long] samples_x,
                                      vector[long] samples_y, unsigned long number_repeats,
                                      vector[unsigned long] number_steps, unsigned long seed,
                                      unsigned long number_workers):
        self.base_setup(number_repeats, number_steps, seed, number_workers)
        self.c_simulator.runSampleDistanceTravelled(samples_x, samples_y)
        self.write_database("DISTANCES_TRAVELLED")

    def run_mean_dispersal_distance(self, unsigned long number_repeats, unsigned long seed, bool is_sequential):
        self.set_logger()
        self.setup()
        self.c_simulator.setSeed(seed)
        self.c_simulator.setNumberRepeats(number_repeats)
        self.c_simulator.setSequential(is_sequential)
        if not self.has_imported_maps:
            self.c_simulator.importMaps()
        self.check_completed()
        self.c_simulator.runMeanDispersalDistance()
        self.write_database("DISPERSAL_DISTANCES")
