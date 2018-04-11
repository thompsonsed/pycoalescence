##
## Makefile input for automatic system configuration and compilation of NECSim and SpeciationCounter. 
##
## Do everything
CXX=g++
LD=@LD@
CXXFLAGS=-g -O2
CPPFLAGS=-I/usr/local/Cellar/python3/3.6.1/Frameworks/Python.framework/Versions/3.6/include/python3.6m  -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -fwrapv -O3   -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.12.sdk -I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.12.sdk/System/Library/Frameworks/Tk.framework/Versions/8.5/Headers -I. -std=c++11 -I/usr/local/include -I/usr/local/Cellar/gdal2/2.2.1_1/include  -Dwith_gdal  -Dverbose -O3 
LDFLAGS=-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.12.sdk -L/usr/local/Cellar/python3/3.6.1/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6 -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6/lib -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6/lib/python3.6/lib-dynload -L. -L/usr/local/lib -L/usr/local/Cellar/gdal2/2.2.1_1/lib -lgdal -L/usr/local/Cellar/python3/3.6.1/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6 -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6/lib -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6/lib/python3.6/lib-dynload
LIBS=-lpython3.6m -lsqlite3 -lboost_filesystem -lboost_system -lpthread -lgdal
PLATFORM_SO=-dynamiclib
VPATH=necsim:
OBJDIR=obj
BUILDDIR=/Users/samthompson/Documents/PhD/Code/pycoalescence/pycoalescence/build/sharedpy3
override CXXFLAGS += -fPIC
override CPPFLAGS += -fPIC


ACLOCAL_AMFLAGS = -I m4 --install
##-std=c++11 -Wall -o3 -Wall -D normal_dispersal -D infinite_landscape  -D record_space -lsqlite3 -lboost_filesystem -lboost_system -lpthread -DNDEBUG

complete: all NECSim SpeciationCounter end_msg

all: start_msg obj_dir build_dir $(BUILDDIR)/necsimmodule.so $(BUILDDIR)/applyspecmodule.so $(BUILDDIR)/dispersalmodule.so end_msg

obj_dir:
	mkdir -p $(OBJDIR)

build_dir:
	mkdir -p $(BUILDDIR)

spec: start_msg_spec SpeciationCounter end_msg

# The old compilation methods for executables - now deprecated
SpeciationCounter: SpeciationCounter.o SpeciationCommands.o Community.o TreeNode.o Matrix.o DataMask.o SimParameters.o ConfigFileParser.o
	$(CXX) -o SpeciationCounter SpeciationCounter.o SpeciationCommands.o Community.o TreeNode.o Matrix.o DataMask.o SimParameters.o ConfigFileParser.o CPLCustomHandler.o $(LDFLAGS) $(CPPFLAGS) $(LIBS)

# NECSim compilation
NECSim: main.o Tree.o Matrix.o NRrand.o Logging.o ConfigFileParser.o DataPoint.o TreeNode.o SpeciesList.o Landscape.o DataMask.o Community.o Setup.o DispersalCoordinator.o ReproductionMap.o LogFile.o
	$(CXX) -o NECSim main.o Tree.o Matrix.o NRrand.o Logging.o ConfigFileParser.o DataPoint.o TreeNode.o SpeciesList.o Landscape.o DataMask.o Community.o Setup.o DispersalCoordinator.o ReproductionMap.o Logging.o LogFile.o CPLCustomHandler.o $(LDFLAGS) $(CPPFLAGS) $(LIBS)

start_msg: 
	@echo "-----------------------------------------------"
	@echo "------------ COMPILATION STARTING -------------"
	@echo "-----------------------------------------------"

end_msg: 
	@echo "-----------------------------------------------"
	@echo "------------ COMPILATION COMPLETE -------------"
	@echo "-----------------------------------------------"

## Compile NECSim
coal: start_msg NECSim end_msg

# python shared object files
necsim_objects = $(addprefix $(OBJDIR)/, Setup.o PyLogging.o Tree.o ConfigFileParser.o DataPoint.o TreeNode.o SpeciesList.o Landscape.o DataMask.o Community.o DispersalCoordinator.o ReproductionMap.o ProtractedTree.o Filesystem.o SpatialTree.o LogFile.o CPLCustomHandler.o)

dispersal_objects = $(addprefix $(OBJDIR)/, PyLogging.o SimulateDispersal.o LogFile.o Filesystem.o CPLCustomHandler.o Landscape.o Datamask.o ConfigFileParser.o PyImports.o DispersalCoordinator.o)

applyspec_objects = $(addprefix $(OBJDIR)/, PyLogging.o LogFile.o Community.o TreeNode.o DataMask.o ConfigFileParser.o Metacommunity.o Tree.o DataPoint.o Filesystem.o Landscape.o CPLCustomHandler.o PyImports.o)

$(BUILDDIR)/necsimmodule.so: $(necsim_objects)

$(BUILDDIR)/dispersalmodule.so: $(dispersal_objects)

$(BUILDDIR)/applyspecmodule.so: $(applyspec_objects)


# now every other object files

# Calculate dependencies
depend:
	makedepend *.cpp necsim/*.cpp -f Makefile -p $(OBJDIR)/

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

obj/PyImports.o: PyImports.h
obj/PyLogging.o: necsim/Logging.h necsim/LogFile.h necsim/CPLCustomHandler.h
obj/PyLogging.o: PyLogging.h necsim/LogFile.h
obj/SpeciationCounter.o: necsim/SpeciationCommands.h necsim/Community.h
obj/SpeciationCounter.o: necsim/TreeNode.h necsim/Logging.h necsim/LogFile.h
obj/SpeciationCounter.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/SpeciationCounter.o: necsim/DataMask.h necsim/SimParameters.h
obj/SpeciationCounter.o: necsim/ConfigFileParser.h necsim/Map.h
obj/SpeciationCounter.o: necsim/SpecSimParameters.h
obj/applyspecmodule.o: applyspecmodule.h PyLogging.h necsim/LogFile.h
obj/applyspecmodule.o: PyImports.h necsim/Community.h necsim/TreeNode.h
obj/applyspecmodule.o: necsim/Logging.h necsim/LogFile.h
obj/applyspecmodule.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/applyspecmodule.o: necsim/DataMask.h necsim/SimParameters.h
obj/applyspecmodule.o: necsim/ConfigFileParser.h necsim/Map.h
obj/applyspecmodule.o: necsim/SpecSimParameters.h necsim/Metacommunity.h
obj/applyspecmodule.o: necsim/Community.h necsim/Tree.h necsim/NRrand.h
obj/applyspecmodule.o: necsim/DataPoint.h necsim/Filesystem.h
obj/applyspecmodule.o: necsim/CustomExceptions.h necsim/Step.h necsim/Cell.h
obj/dispersalmodule.o: dispersalmodule.h PyLogging.h necsim/LogFile.h
obj/dispersalmodule.o: necsim/SimulateDispersal.h necsim/Landscape.h
obj/dispersalmodule.o: necsim/Map.h necsim/DataMask.h necsim/SimParameters.h
obj/dispersalmodule.o: necsim/ConfigFileParser.h necsim/Logging.h
obj/dispersalmodule.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/dispersalmodule.o: necsim/DispersalCoordinator.h necsim/NRrand.h
obj/dispersalmodule.o: necsim/Step.h necsim/Cell.h PyImports.h
obj/necsimmodule.o: necsim/Setup.h necsimmodule.h PyLogging.h
obj/necsimmodule.o: necsim/LogFile.h necsim/SpatialTree.h necsim/Tree.h
obj/necsimmodule.o: necsim/TreeNode.h necsim/Logging.h necsim/LogFile.h
obj/necsimmodule.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/necsimmodule.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsimmodule.o: necsim/NRrand.h necsim/DataPoint.h necsim/Community.h
obj/necsimmodule.o: necsim/DataMask.h necsim/Map.h necsim/SpecSimParameters.h
obj/necsimmodule.o: necsim/Filesystem.h necsim/CustomExceptions.h
obj/necsimmodule.o: necsim/Step.h necsim/Cell.h necsim/SpeciesList.h
obj/necsimmodule.o: necsim/Landscape.h necsim/Setup.h
obj/necsimmodule.o: necsim/DispersalCoordinator.h necsim/ReproductionMap.h
obj/necsimmodule.o: necsim/ProtractedTree.h necsim/SpatialTree.h
obj/necsimmodule.o: necsim/SimulationTemplates.h
obj/necsimmodule.o: necsim/ProtractedSpatialTree.h necsim/ProtractedTree.h
obj/necsim/CPLCustomHandler.o: necsim/CPLCustomHandler.h necsim/Logging.h
obj/necsim/CPLCustomHandler.o: necsim/LogFile.h
obj/necsim/Community.o: necsim/Community.h necsim/TreeNode.h necsim/Logging.h
obj/necsim/Community.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/Community.o: necsim/Matrix.h necsim/DataMask.h
obj/necsim/Community.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Community.o: necsim/Map.h necsim/SpecSimParameters.h
obj/necsim/Community.o: necsim/Filesystem.h
obj/necsim/ConfigFileParser.o: necsim/ConfigFileParser.h
obj/necsim/ConfigFileParser.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/ConfigFileParser.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/DataMask.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/DataMask.o: necsim/ConfigFileParser.h necsim/Logging.h
obj/necsim/DataMask.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/DataMask.o: necsim/Map.h necsim/Landscape.h
obj/necsim/DataPoint.o: necsim/DataPoint.h necsim/Logging.h necsim/LogFile.h
obj/necsim/DataPoint.o: necsim/CPLCustomHandler.h
obj/necsim/DispersalCoordinator.o: necsim/DispersalCoordinator.h
obj/necsim/DispersalCoordinator.o: necsim/NRrand.h necsim/Logging.h
obj/necsim/DispersalCoordinator.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/DispersalCoordinator.o: necsim/Map.h necsim/Step.h necsim/Cell.h
obj/necsim/DispersalCoordinator.o: necsim/Landscape.h necsim/DataMask.h
obj/necsim/DispersalCoordinator.o: necsim/SimParameters.h
obj/necsim/DispersalCoordinator.o: necsim/ConfigFileParser.h
obj/necsim/DispersalCoordinator.o: necsim/CustomExceptions.h
obj/necsim/Filesystem.o: necsim/Filesystem.h necsim/CustomExceptions.h
obj/necsim/Filesystem.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/Filesystem.o: necsim/CPLCustomHandler.h
obj/necsim/Landscape.o: necsim/Landscape.h necsim/Map.h necsim/DataMask.h
obj/necsim/Landscape.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Landscape.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/Landscape.o: necsim/CPLCustomHandler.h necsim/Filesystem.h
obj/necsim/LogFile.o: necsim/LogFile.h necsim/Filesystem.h
obj/necsim/LogFile.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/LogFile.o: necsim/CPLCustomHandler.h
obj/necsim/Logging.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/Logging.o: necsim/CPLCustomHandler.h
obj/necsim/Metacommunity.o: necsim/Metacommunity.h necsim/Community.h
obj/necsim/Metacommunity.o: necsim/TreeNode.h necsim/Logging.h
obj/necsim/Metacommunity.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/Metacommunity.o: necsim/Matrix.h necsim/DataMask.h
obj/necsim/Metacommunity.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Metacommunity.o: necsim/Map.h necsim/SpecSimParameters.h
obj/necsim/Metacommunity.o: necsim/Tree.h necsim/NRrand.h necsim/DataPoint.h
obj/necsim/Metacommunity.o: necsim/Filesystem.h necsim/CustomExceptions.h
obj/necsim/Metacommunity.o: necsim/Step.h necsim/Cell.h
obj/necsim/ProtractedTree.o: necsim/ProtractedTree.h necsim/SpatialTree.h
obj/necsim/ReproductionMap.o: necsim/ReproductionMap.h necsim/Map.h
obj/necsim/ReproductionMap.o: necsim/NRrand.h necsim/Logging.h
obj/necsim/ReproductionMap.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/Setup.o: necsim/Setup.h necsim/Logging.h necsim/LogFile.h
obj/necsim/Setup.o: necsim/CPLCustomHandler.h
obj/necsim/SimulateDispersal.o: necsim/SimulateDispersal.h necsim/Landscape.h
obj/necsim/SimulateDispersal.o: necsim/Map.h necsim/DataMask.h
obj/necsim/SimulateDispersal.o: necsim/SimParameters.h
obj/necsim/SimulateDispersal.o: necsim/ConfigFileParser.h necsim/Logging.h
obj/necsim/SimulateDispersal.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/SimulateDispersal.o: necsim/DispersalCoordinator.h necsim/NRrand.h
obj/necsim/SimulateDispersal.o: necsim/Step.h necsim/Cell.h
obj/necsim/SimulateDispersal.o: necsim/CustomExceptions.h necsim/Filesystem.h
obj/necsim/SimulateDispersal.o: necsim/Community.h necsim/TreeNode.h
obj/necsim/SimulateDispersal.o: necsim/Matrix.h necsim/SpecSimParameters.h
obj/necsim/SpatialTree.o: necsim/SpatialTree.h
obj/necsim/SpeciationCommands.o: necsim/SpeciationCommands.h
obj/necsim/SpeciationCommands.o: necsim/Community.h necsim/TreeNode.h
obj/necsim/SpeciationCommands.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/SpeciationCommands.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/necsim/SpeciationCommands.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/SpeciationCommands.o: necsim/ConfigFileParser.h necsim/Map.h
obj/necsim/SpeciationCommands.o: necsim/SpecSimParameters.h
obj/necsim/SpeciesGrid.o: necsim/SpeciesGrid.h necsim/SpeciesList.h
obj/necsim/SpeciesGrid.o: necsim/Matrix.h necsim/Logging.h necsim/LogFile.h
obj/necsim/SpeciesGrid.o: necsim/CPLCustomHandler.h necsim/NRrand.h
obj/necsim/SpeciesList.o: necsim/SpeciesList.h necsim/Matrix.h
obj/necsim/SpeciesList.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/SpeciesList.o: necsim/CPLCustomHandler.h necsim/NRrand.h
obj/necsim/Tree.o: necsim/Tree.h necsim/TreeNode.h necsim/Logging.h
obj/necsim/Tree.o: necsim/LogFile.h necsim/CPLCustomHandler.h necsim/Matrix.h
obj/necsim/Tree.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Tree.o: necsim/NRrand.h necsim/DataPoint.h necsim/Community.h
obj/necsim/Tree.o: necsim/DataMask.h necsim/Map.h necsim/SpecSimParameters.h
obj/necsim/Tree.o: necsim/Filesystem.h necsim/CustomExceptions.h
obj/necsim/Tree.o: necsim/Step.h necsim/Cell.h
obj/necsim/TreeNode.o: necsim/TreeNode.h necsim/Logging.h necsim/LogFile.h
obj/necsim/TreeNode.o: necsim/CPLCustomHandler.h
obj/necsim/main.o: necsim/SpatialTree.h necsim/SimulationTemplates.h
obj/necsim/main.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/main.o: necsim/CPLCustomHandler.h necsim/CustomExceptions.h
