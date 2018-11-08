##
## Makefile input for automatic system configuration and compilation of necsim and SpeciationCounter.
##
CXX=g++ -std=gnu++14
LD=@LD@
CXXFLAGS=-g -O2
CPPFLAGS=-I/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/include/python3.6m  -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -fwrapv -O3    -I. -std=c++14 -I/usr/local/Cellar/gdal2/2.2.4/include  -Dwith_gdal  -Dverbose -O3 
LDFLAGS=  -L/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6/lib-dynload -L. -L/usr/local/Cellar/gdal2/2.2.4/lib -lgdal -L/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6/lib-dynload
LIBS= -lsqlite3 -lpython3.6m -lboost_filesystem -lboost_system -lpthread -lgdal
PLATFORM_SO=-dynamiclib
VPATH=necsim:
OBJDIR=obj
BUILDDIR=/Users/samthompson/Documents/PhD/Code/pycoalescence/pycoalescence/necsim
override CXXFLAGS += -fPIC
override CPPFLAGS += -fPIC


ACLOCAL_AMFLAGS = -I m4 --install

all: start_msg obj_dir build_dir $(BUILDDIR)/necsimmodule.so end_msg

complete: all necsim SpeciationCounter end_msg

obj_dir:
	mkdir -p $(OBJDIR)

build_dir:
	mkdir -p $(BUILDDIR)

spec: start_msg_spec SpeciationCounter end_msg

# The old compilation methods for executables - now deprecated
SpeciationCounter: SpeciationCounter.o SpeciationCommands.o Community.o TreeNode.o DataMask.o SimParameters.o ConfigFileParser.o
	$(CXX) -o SpeciationCounter SpeciationCounter.o SpeciationCommands.o Community.o TreeNode.o Matrix.o DataMask.o SimParameters.o ConfigFileParser.o CPLCustomHandlerNecsim.o $(LDFLAGS) $(CPPFLAGS) $(LIBS)

# necsim compilation
necsim: main.o Tree.o Logging.o ConfigFileParser.o DataPoint.o TreeNode.o SpeciesList.o Landscape.o DataMask.o Community.o Setup.o DispersalCoordinator.o ReproductionMap.o LogFile.o Cell.o
	$(CXX) -o necsim main.o Tree.o Matrix.o Logging.o ConfigFileParser.o DataPoint.o TreeNode.o SpeciesList.o Landscape.o DataMask.o Community.o Setup.o DispersalCoordinator.o ReproductionMap.o Logging.o LogFile.o CPLCustomHandlerNecsim.o Cell.o $(LDFLAGS) $(CPPFLAGS) $(LIBS)

start_msg: 
	@echo "-----------------------------------------------"
	@echo "------------ COMPILATION STARTING -------------"
	@echo "-----------------------------------------------"

end_msg: 
	@echo "-----------------------------------------------"
	@echo "------------ COMPILATION COMPLETE -------------"
	@echo "-----------------------------------------------"

## Compile necsim
coal: start_msg necsim end_msg

# Python shared object files
necsim_objects = $(addprefix $(OBJDIR)/, Setup.o PyLogging.o Tree.o ConfigFileParser.o DataPoint.o TreeNode.o SpeciesList.o Landscape.o DataMask.o Community.o DispersalCoordinator.o ReproductionMap.o ProtractedTree.o Filesystem.o SpatialTree.o LogFile.o CPLCustomHandlerNecsim.o Cell.o DoubleComparison.o Logger.o PyLogger.o PyImports.o Metacommunity.o SimulateDispersal.o LandscapeMetricsCalculator.o)

dispersal_objects = $(addprefix $(OBJDIR)/, PyLogging.o SimulateDispersal.o LogFile.o Filesystem.o CPLCustomHandlerNecsim.o Landscape.o DataMask.o ConfigFileParser.o PyImports.o DispersalCoordinator.o Cell.o DoubleComparison.o Logger.o PyLogger.o)

#applyspec_objects = $(addprefix $(OBJDIR)/, PyLogging.o LogFile.o Community.o TreeNode.o DataMask.o ConfigFileParser.o Metacommunity.o Tree.o DataPoint.o Filesystem.o Landscape.o CPLCustomHandlerNecsim.o PyImports.o Cell.o DoubleComparison.o Logger.o PyLogger.o)

#landscape_metrics_objects = $(addprefix $(OBJDIR)/, LandscapeMetricsCalculator.o PyLogging.o CPLCustomHandlerNecsim.o Cell.o Logger.o PyLogger.o LogFile.o FileSystem.o)

$(BUILDDIR)/necsimmodule.so: $(necsim_objects)

#$(BUILDDIR)/dispersalmodule.so: $(dispersal_objects)

#$(BUILDDIR)/applyspecmodule.so: $(applyspec_objects)

#$(BUILDDIR)/landscapemetricsmodule.so: $(landscape_metrics_objects)


# now every other object files

# Calculate dependencies
depend:
	@echo "----------Updating dependencies------"
	makedepend *.cpp necsim/*.cpp -f Makefile -p $(OBJDIR)/ -Y

## Clean up
clean:
	@echo "----------Cleaning projects----------"
	$(RM) *.o *.o.d *.so $(OBJDIR)/*.o $(OBJDIR)/*.o.d $(BUILDDIR)/*.so

## Pattern rule for compilation


$(BUILDDIR)/%.so: $(OBJDIR)/%.o
	$(CXX) $(PLATFORM_SO) $(CPPFLAGS) $(LDFLAGS) $(LIBS) -fPIC -o $@ $+

$(OBJDIR)/%.o: %.cpp %.h
	$(CXX) $(CPPFLAGS) -c -o $@ $<

# DO NOT DELETE

obj/LandscapeMetricsCalculator.o: necsim/Matrix.h necsim/Logging.h
obj/LandscapeMetricsCalculator.o: necsim/Logger.h necsim/LogFile.h
obj/LandscapeMetricsCalculator.o: necsim/CPLCustomHandlerNecsim.h
obj/LandscapeMetricsCalculator.o: necsim/Map.h LandscapeMetricsCalculator.h
obj/LandscapeMetricsCalculator.o: necsim/Cell.h
obj/PyImports.o: PyImports.h
obj/PyLogger.o: necsim/CustomExceptions.h necsim/Logging.h necsim/Logger.h
obj/PyLogger.o: necsim/LogFile.h necsim/CPLCustomHandlerNecsim.h
obj/PyLogger.o: necsim/Logger.h PyLogger.h
obj/PyLogging.o: necsim/Logger.h PyLogger.h PyLogging.h necsim/LogFile.h
obj/necsimmodule.o: necsim/Setup.h necsimmodule.h PyLogging.h
obj/necsimmodule.o: necsim/LogFile.h PyLogger.h necsim/Logger.h CSimulation.h
obj/necsimmodule.o: necsim/ConfigFileParser.h necsim/Tree.h necsim/TreeNode.h
obj/necsimmodule.o: necsim/Logger.h necsim/LogFile.h
obj/necsimmodule.o: necsim/CPLCustomHandlerNecsim.h necsim/Matrix.h
obj/necsimmodule.o: necsim/Logging.h necsim/SimParameters.h
obj/necsimmodule.o: necsim/ConfigFileParser.h necsim/CustomExceptions.h
obj/necsimmodule.o: necsim/NRrand.h necsim/DataPoint.h necsim/Community.h
obj/necsimmodule.o: necsim/DataMask.h necsim/Map.h necsim/SpecSimParameters.h
obj/necsimmodule.o: necsim/DoubleComparison.h necsim/Filesystem.h
obj/necsimmodule.o: necsim/Step.h necsim/Cell.h necsim/SpatialTree.h
obj/necsimmodule.o: necsim/Tree.h necsim/SpeciesList.h necsim/Landscape.h
obj/necsimmodule.o: necsim/Setup.h necsim/DispersalCoordinator.h
obj/necsimmodule.o: necsim/ReproductionMap.h necsim/ProtractedTree.h
obj/necsimmodule.o: necsim/SpatialTree.h necsim/ProtractedSpatialTree.h
obj/necsimmodule.o: necsim/ProtractedTree.h PyImports.h PyTemplates.h
obj/necsimmodule.o: CCommunity.h necsim/Community.h necsim/Metacommunity.h
obj/necsimmodule.o: CSimulateDispersal.h necsim/SimParameters.h
obj/necsimmodule.o: necsim/SimulateDispersal.h CLandscapeMetricsCalculator.h
obj/necsimmodule.o: LandscapeMetricsCalculator.h necsim/Map.h necsim/Cell.h
obj/necsimmodule.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/CPLCustomHandlerNecsim.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/CPLCustomHandlerNecsim.o: necsim/Logging.h necsim/Logger.h
obj/necsim/CPLCustomHandlerNecsim.o: necsim/LogFile.h
obj/necsim/Cell.o: necsim/Cell.h
obj/necsim/Community.o: necsim/Community.h necsim/TreeNode.h necsim/Logger.h
obj/necsim/Community.o: necsim/LogFile.h necsim/CPLCustomHandlerNecsim.h
obj/necsim/Community.o: necsim/Matrix.h necsim/Logging.h necsim/DataMask.h
obj/necsim/Community.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Community.o: necsim/CustomExceptions.h necsim/Map.h
obj/necsim/Community.o: necsim/SpecSimParameters.h necsim/DoubleComparison.h
obj/necsim/Community.o: necsim/Filesystem.h
obj/necsim/ConfigFileParser.o: necsim/ConfigFileParser.h
obj/necsim/ConfigFileParser.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/ConfigFileParser.o: necsim/Logger.h necsim/LogFile.h
obj/necsim/ConfigFileParser.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/DataMask.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/DataMask.o: necsim/ConfigFileParser.h necsim/Logger.h
obj/necsim/DataMask.o: necsim/LogFile.h necsim/CPLCustomHandlerNecsim.h
obj/necsim/DataMask.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/DataMask.o: necsim/Map.h necsim/Landscape.h
obj/necsim/DataPoint.o: necsim/Logging.h necsim/Logger.h necsim/LogFile.h
obj/necsim/DataPoint.o: necsim/CPLCustomHandlerNecsim.h necsim/DataPoint.h
obj/necsim/DispersalCoordinator.o: necsim/DispersalCoordinator.h
obj/necsim/DispersalCoordinator.o: necsim/NRrand.h necsim/Logger.h
obj/necsim/DispersalCoordinator.o: necsim/LogFile.h
obj/necsim/DispersalCoordinator.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/DispersalCoordinator.o: necsim/Map.h necsim/Step.h necsim/Cell.h
obj/necsim/DispersalCoordinator.o: necsim/Landscape.h necsim/DataMask.h
obj/necsim/DispersalCoordinator.o: necsim/SimParameters.h
obj/necsim/DispersalCoordinator.o: necsim/ConfigFileParser.h
obj/necsim/DispersalCoordinator.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/Filesystem.o: necsim/Filesystem.h necsim/CustomExceptions.h
obj/necsim/Filesystem.o: necsim/Logging.h necsim/Logger.h necsim/LogFile.h
obj/necsim/Filesystem.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/Landscape.o: necsim/Landscape.h necsim/Map.h necsim/DataMask.h
obj/necsim/Landscape.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Landscape.o: necsim/Logger.h necsim/LogFile.h
obj/necsim/Landscape.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/Landscape.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/Landscape.o: necsim/Filesystem.h
obj/necsim/LogFile.o: necsim/LogFile.h necsim/Filesystem.h
obj/necsim/LogFile.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/LogFile.o: necsim/Logger.h necsim/CPLCustomHandlerNecsim.h
obj/necsim/Logger.o: necsim/Logger.h necsim/LogFile.h
obj/necsim/Logger.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/Logging.o: necsim/Logging.h necsim/Logger.h necsim/LogFile.h
obj/necsim/Logging.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/Metacommunity.o: necsim/Metacommunity.h necsim/Community.h
obj/necsim/Metacommunity.o: necsim/TreeNode.h necsim/Logger.h
obj/necsim/Metacommunity.o: necsim/LogFile.h necsim/CPLCustomHandlerNecsim.h
obj/necsim/Metacommunity.o: necsim/Matrix.h necsim/Logging.h
obj/necsim/Metacommunity.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/Metacommunity.o: necsim/ConfigFileParser.h
obj/necsim/Metacommunity.o: necsim/CustomExceptions.h necsim/Map.h
obj/necsim/Metacommunity.o: necsim/SpecSimParameters.h
obj/necsim/Metacommunity.o: necsim/DoubleComparison.h necsim/Tree.h
obj/necsim/Metacommunity.o: necsim/NRrand.h
obj/necsim/ProtractedTree.o: necsim/ProtractedTree.h necsim/SpatialTree.h
obj/necsim/ReproductionMap.o: necsim/ReproductionMap.h necsim/Map.h
obj/necsim/ReproductionMap.o: necsim/NRrand.h necsim/Logger.h
obj/necsim/ReproductionMap.o: necsim/LogFile.h
obj/necsim/ReproductionMap.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/Setup.o: necsim/Setup.h necsim/Logging.h necsim/Logger.h
obj/necsim/Setup.o: necsim/LogFile.h necsim/CPLCustomHandlerNecsim.h
obj/necsim/SimulateDispersal.o: necsim/SimulateDispersal.h necsim/Landscape.h
obj/necsim/SimulateDispersal.o: necsim/Map.h necsim/DataMask.h
obj/necsim/SimulateDispersal.o: necsim/SimParameters.h
obj/necsim/SimulateDispersal.o: necsim/ConfigFileParser.h necsim/Logger.h
obj/necsim/SimulateDispersal.o: necsim/LogFile.h
obj/necsim/SimulateDispersal.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/SimulateDispersal.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/SimulateDispersal.o: necsim/DispersalCoordinator.h necsim/NRrand.h
obj/necsim/SimulateDispersal.o: necsim/Step.h necsim/Cell.h
obj/necsim/SimulateDispersal.o: necsim/Filesystem.h necsim/Community.h
obj/necsim/SimulateDispersal.o: necsim/TreeNode.h necsim/Matrix.h
obj/necsim/SimulateDispersal.o: necsim/SpecSimParameters.h
obj/necsim/SimulateDispersal.o: necsim/DoubleComparison.h
obj/necsim/SpatialTree.o: necsim/SpatialTree.h
obj/necsim/SpeciationCommands.o: necsim/SpeciationCommands.h
obj/necsim/SpeciationCommands.o: necsim/Community.h necsim/TreeNode.h
obj/necsim/SpeciationCommands.o: necsim/Logger.h necsim/LogFile.h
obj/necsim/SpeciationCommands.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/SpeciationCommands.o: necsim/Matrix.h necsim/Logging.h
obj/necsim/SpeciationCommands.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/SpeciationCommands.o: necsim/ConfigFileParser.h
obj/necsim/SpeciationCommands.o: necsim/CustomExceptions.h necsim/Map.h
obj/necsim/SpeciationCommands.o: necsim/SpecSimParameters.h
obj/necsim/SpeciationCommands.o: necsim/DoubleComparison.h
obj/necsim/SpeciesList.o: necsim/SpeciesList.h necsim/Matrix.h
obj/necsim/SpeciesList.o: necsim/Logging.h necsim/Logger.h necsim/LogFile.h
obj/necsim/SpeciesList.o: necsim/CPLCustomHandlerNecsim.h necsim/NRrand.h
obj/necsim/Tree.o: necsim/Tree.h necsim/Logger.h necsim/LogFile.h
obj/necsim/Tree.o: necsim/CPLCustomHandlerNecsim.h
obj/necsim/TreeNode.o: necsim/TreeNode.h necsim/Logger.h necsim/LogFile.h
obj/necsim/TreeNode.o: necsim/CPLCustomHandlerNecsim.h necsim/Logging.h
obj/necsim/main.o: necsim/Logging.h necsim/Logger.h necsim/LogFile.h
obj/necsim/main.o: necsim/CPLCustomHandlerNecsim.h necsim/SpatialTree.h
obj/necsim/main.o: necsim/SimulationTemplates.h necsim/CustomExceptions.h
