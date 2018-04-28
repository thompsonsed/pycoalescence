##
## Makefile input for automatic system configuration and compilation of NECSim and SpeciationCounter. 
##
## Do everything
CXX=g++
LD=@LD@
CXXFLAGS=-g -O2
CPPFLAGS=-I/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/include/python3.6m  -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -fwrapv -O3   -I. -std=c++11 -I/usr/local/Cellar/gdal2/2.2.4/include  -Dwith_gdal  -Dverbose -O3 
LDFLAGS= -L/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6/lib-dynload -L. -L/usr/local/Cellar/gdal2/2.2.4/lib -lgdal -L/usr/local/Cellar/python/3.6.5/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6 -L/usr/local/opt/python/Frameworks/Python.framework/Versions/3.6/lib/python3.6/lib-dynload
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

dispersal_objects = $(addprefix $(OBJDIR)/, PyLogging.o SimulateDispersal.o LogFile.o Filesystem.o CPLCustomHandler.o Landscape.o DataMask.o ConfigFileParser.o PyImports.o DispersalCoordinator.o)

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

obj/PyImports.o: /usr/include/unistd.h /usr/include/_types.h
obj/PyImports.o: /usr/include/sys/_types.h /usr/include/sys/cdefs.h
obj/PyImports.o: /usr/include/sys/_symbol_aliasing.h
obj/PyImports.o: /usr/include/sys/_posix_availability.h
obj/PyImports.o: /usr/include/machine/_types.h /usr/include/i386/_types.h
obj/PyImports.o: /usr/include/sys/_pthread/_pthread_types.h
obj/PyImports.o: /usr/include/sys/unistd.h
obj/PyImports.o: /usr/include/sys/_types/_posix_vdisable.h
obj/PyImports.o: /usr/include/sys/_types/_seek_set.h
obj/PyImports.o: /usr/include/sys/_types/_size_t.h
obj/PyImports.o: /usr/include/_types/_uint64_t.h /usr/include/Availability.h
obj/PyImports.o: /usr/include/AvailabilityInternal.h
obj/PyImports.o: /usr/include/sys/_types/_ssize_t.h
obj/PyImports.o: /usr/include/sys/_types/_uid_t.h
obj/PyImports.o: /usr/include/sys/_types/_gid_t.h
obj/PyImports.o: /usr/include/sys/_types/_intptr_t.h
obj/PyImports.o: /usr/include/sys/_types/_off_t.h
obj/PyImports.o: /usr/include/sys/_types/_pid_t.h
obj/PyImports.o: /usr/include/sys/_types/_useconds_t.h
obj/PyImports.o: /usr/include/sys/_types/_null.h /usr/include/sys/select.h
obj/PyImports.o: /usr/include/sys/appleapiopts.h
obj/PyImports.o: /usr/include/sys/_types/_fd_def.h
obj/PyImports.o: /usr/include/sys/_types/_timespec.h
obj/PyImports.o: /usr/include/sys/_types/_timeval.h
obj/PyImports.o: /usr/include/sys/_types/_time_t.h
obj/PyImports.o: /usr/include/sys/_types/_suseconds_t.h
obj/PyImports.o: /usr/include/sys/_types/_sigset_t.h
obj/PyImports.o: /usr/include/sys/_types/_fd_setsize.h
obj/PyImports.o: /usr/include/sys/_types/_fd_set.h
obj/PyImports.o: /usr/include/sys/_types/_fd_clr.h
obj/PyImports.o: /usr/include/sys/_types/_fd_isset.h
obj/PyImports.o: /usr/include/sys/_types/_fd_zero.h
obj/PyImports.o: /usr/include/sys/_types/_fd_copy.h
obj/PyImports.o: /usr/include/sys/_select.h /usr/include/sys/_types/_dev_t.h
obj/PyImports.o: /usr/include/sys/_types/_mode_t.h
obj/PyImports.o: /usr/include/sys/_types/_uuid_t.h /usr/include/gethostuuid.h
obj/PyImports.o: PyImports.h
obj/PyLogging.o: necsim/Logging.h necsim/LogFile.h necsim/CPLCustomHandler.h
obj/PyLogging.o: PyLogging.h necsim/LogFile.h
obj/SpeciationCounter.o: necsim/SpeciationCommands.h necsim/Community.h
obj/SpeciationCounter.o: /usr/include/sqlite3.h necsim/TreeNode.h
obj/SpeciationCounter.o: necsim/Logging.h necsim/LogFile.h
obj/SpeciationCounter.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/SpeciationCounter.o: necsim/DataMask.h necsim/SimParameters.h
obj/SpeciationCounter.o: necsim/ConfigFileParser.h /usr/include/unistd.h
obj/SpeciationCounter.o: /usr/include/_types.h /usr/include/sys/_types.h
obj/SpeciationCounter.o: /usr/include/sys/cdefs.h
obj/SpeciationCounter.o: /usr/include/sys/_symbol_aliasing.h
obj/SpeciationCounter.o: /usr/include/sys/_posix_availability.h
obj/SpeciationCounter.o: /usr/include/machine/_types.h
obj/SpeciationCounter.o: /usr/include/i386/_types.h
obj/SpeciationCounter.o: /usr/include/sys/_pthread/_pthread_types.h
obj/SpeciationCounter.o: /usr/include/sys/unistd.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_posix_vdisable.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_seek_set.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_size_t.h
obj/SpeciationCounter.o: /usr/include/_types/_uint64_t.h
obj/SpeciationCounter.o: /usr/include/Availability.h
obj/SpeciationCounter.o: /usr/include/AvailabilityInternal.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_ssize_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_uid_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_gid_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_intptr_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_off_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_pid_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_useconds_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_null.h
obj/SpeciationCounter.o: /usr/include/sys/select.h
obj/SpeciationCounter.o: /usr/include/sys/appleapiopts.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_fd_def.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_timespec.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_timeval.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_time_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_suseconds_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_sigset_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_fd_setsize.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_fd_set.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_fd_clr.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_fd_isset.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_fd_zero.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_fd_copy.h
obj/SpeciationCounter.o: /usr/include/sys/_select.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_dev_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_mode_t.h
obj/SpeciationCounter.o: /usr/include/sys/_types/_uuid_t.h
obj/SpeciationCounter.o: /usr/include/gethostuuid.h necsim/CustomExceptions.h
obj/SpeciationCounter.o: necsim/Map.h necsim/SpecSimParameters.h
obj/applyspecmodule.o: /usr/include/unistd.h /usr/include/_types.h
obj/applyspecmodule.o: /usr/include/sys/_types.h /usr/include/sys/cdefs.h
obj/applyspecmodule.o: /usr/include/sys/_symbol_aliasing.h
obj/applyspecmodule.o: /usr/include/sys/_posix_availability.h
obj/applyspecmodule.o: /usr/include/machine/_types.h
obj/applyspecmodule.o: /usr/include/i386/_types.h
obj/applyspecmodule.o: /usr/include/sys/_pthread/_pthread_types.h
obj/applyspecmodule.o: /usr/include/sys/unistd.h
obj/applyspecmodule.o: /usr/include/sys/_types/_posix_vdisable.h
obj/applyspecmodule.o: /usr/include/sys/_types/_seek_set.h
obj/applyspecmodule.o: /usr/include/sys/_types/_size_t.h
obj/applyspecmodule.o: /usr/include/_types/_uint64_t.h
obj/applyspecmodule.o: /usr/include/Availability.h
obj/applyspecmodule.o: /usr/include/AvailabilityInternal.h
obj/applyspecmodule.o: /usr/include/sys/_types/_ssize_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_uid_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_gid_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_intptr_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_off_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_pid_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_useconds_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_null.h
obj/applyspecmodule.o: /usr/include/sys/select.h
obj/applyspecmodule.o: /usr/include/sys/appleapiopts.h
obj/applyspecmodule.o: /usr/include/sys/_types/_fd_def.h
obj/applyspecmodule.o: /usr/include/sys/_types/_timespec.h
obj/applyspecmodule.o: /usr/include/sys/_types/_timeval.h
obj/applyspecmodule.o: /usr/include/sys/_types/_time_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_suseconds_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_sigset_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_fd_setsize.h
obj/applyspecmodule.o: /usr/include/sys/_types/_fd_set.h
obj/applyspecmodule.o: /usr/include/sys/_types/_fd_clr.h
obj/applyspecmodule.o: /usr/include/sys/_types/_fd_isset.h
obj/applyspecmodule.o: /usr/include/sys/_types/_fd_zero.h
obj/applyspecmodule.o: /usr/include/sys/_types/_fd_copy.h
obj/applyspecmodule.o: /usr/include/sys/_select.h
obj/applyspecmodule.o: /usr/include/sys/_types/_dev_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_mode_t.h
obj/applyspecmodule.o: /usr/include/sys/_types/_uuid_t.h
obj/applyspecmodule.o: /usr/include/gethostuuid.h applyspecmodule.h
obj/applyspecmodule.o: PyLogging.h necsim/LogFile.h PyImports.h
obj/applyspecmodule.o: necsim/Community.h /usr/include/sqlite3.h
obj/applyspecmodule.o: necsim/TreeNode.h necsim/Logging.h necsim/LogFile.h
obj/applyspecmodule.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/applyspecmodule.o: necsim/DataMask.h necsim/SimParameters.h
obj/applyspecmodule.o: necsim/ConfigFileParser.h necsim/CustomExceptions.h
obj/applyspecmodule.o: necsim/Map.h necsim/SpecSimParameters.h
obj/applyspecmodule.o: necsim/Metacommunity.h necsim/Community.h
obj/applyspecmodule.o: necsim/Tree.h necsim/NRrand.h necsim/DataPoint.h
obj/applyspecmodule.o: necsim/Filesystem.h necsim/Step.h necsim/Cell.h
obj/dispersalmodule.o: dispersalmodule.h PyLogging.h necsim/LogFile.h
obj/dispersalmodule.o: necsim/SimulateDispersal.h /usr/include/sqlite3.h
obj/dispersalmodule.o: necsim/Landscape.h necsim/Map.h necsim/DataMask.h
obj/dispersalmodule.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/dispersalmodule.o: /usr/include/unistd.h /usr/include/_types.h
obj/dispersalmodule.o: /usr/include/sys/_types.h /usr/include/sys/cdefs.h
obj/dispersalmodule.o: /usr/include/sys/_symbol_aliasing.h
obj/dispersalmodule.o: /usr/include/sys/_posix_availability.h
obj/dispersalmodule.o: /usr/include/machine/_types.h
obj/dispersalmodule.o: /usr/include/i386/_types.h
obj/dispersalmodule.o: /usr/include/sys/_pthread/_pthread_types.h
obj/dispersalmodule.o: /usr/include/sys/unistd.h
obj/dispersalmodule.o: /usr/include/sys/_types/_posix_vdisable.h
obj/dispersalmodule.o: /usr/include/sys/_types/_seek_set.h
obj/dispersalmodule.o: /usr/include/sys/_types/_size_t.h
obj/dispersalmodule.o: /usr/include/_types/_uint64_t.h
obj/dispersalmodule.o: /usr/include/Availability.h
obj/dispersalmodule.o: /usr/include/AvailabilityInternal.h
obj/dispersalmodule.o: /usr/include/sys/_types/_ssize_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_uid_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_gid_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_intptr_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_off_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_pid_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_useconds_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_null.h
obj/dispersalmodule.o: /usr/include/sys/select.h
obj/dispersalmodule.o: /usr/include/sys/appleapiopts.h
obj/dispersalmodule.o: /usr/include/sys/_types/_fd_def.h
obj/dispersalmodule.o: /usr/include/sys/_types/_timespec.h
obj/dispersalmodule.o: /usr/include/sys/_types/_timeval.h
obj/dispersalmodule.o: /usr/include/sys/_types/_time_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_suseconds_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_sigset_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_fd_setsize.h
obj/dispersalmodule.o: /usr/include/sys/_types/_fd_set.h
obj/dispersalmodule.o: /usr/include/sys/_types/_fd_clr.h
obj/dispersalmodule.o: /usr/include/sys/_types/_fd_isset.h
obj/dispersalmodule.o: /usr/include/sys/_types/_fd_zero.h
obj/dispersalmodule.o: /usr/include/sys/_types/_fd_copy.h
obj/dispersalmodule.o: /usr/include/sys/_select.h
obj/dispersalmodule.o: /usr/include/sys/_types/_dev_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_mode_t.h
obj/dispersalmodule.o: /usr/include/sys/_types/_uuid_t.h
obj/dispersalmodule.o: /usr/include/gethostuuid.h necsim/Logging.h
obj/dispersalmodule.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/dispersalmodule.o: necsim/CustomExceptions.h
obj/dispersalmodule.o: necsim/DispersalCoordinator.h necsim/NRrand.h
obj/dispersalmodule.o: necsim/Step.h necsim/Cell.h PyImports.h
obj/necsimmodule.o: necsim/Setup.h /usr/include/unistd.h
obj/necsimmodule.o: /usr/include/_types.h /usr/include/sys/_types.h
obj/necsimmodule.o: /usr/include/sys/cdefs.h
obj/necsimmodule.o: /usr/include/sys/_symbol_aliasing.h
obj/necsimmodule.o: /usr/include/sys/_posix_availability.h
obj/necsimmodule.o: /usr/include/machine/_types.h /usr/include/i386/_types.h
obj/necsimmodule.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsimmodule.o: /usr/include/sys/unistd.h
obj/necsimmodule.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsimmodule.o: /usr/include/sys/_types/_seek_set.h
obj/necsimmodule.o: /usr/include/sys/_types/_size_t.h
obj/necsimmodule.o: /usr/include/_types/_uint64_t.h
obj/necsimmodule.o: /usr/include/Availability.h
obj/necsimmodule.o: /usr/include/AvailabilityInternal.h
obj/necsimmodule.o: /usr/include/sys/_types/_ssize_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_uid_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_gid_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_intptr_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_off_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_pid_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_useconds_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_null.h /usr/include/sys/select.h
obj/necsimmodule.o: /usr/include/sys/appleapiopts.h
obj/necsimmodule.o: /usr/include/sys/_types/_fd_def.h
obj/necsimmodule.o: /usr/include/sys/_types/_timespec.h
obj/necsimmodule.o: /usr/include/sys/_types/_timeval.h
obj/necsimmodule.o: /usr/include/sys/_types/_time_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_sigset_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsimmodule.o: /usr/include/sys/_types/_fd_set.h
obj/necsimmodule.o: /usr/include/sys/_types/_fd_clr.h
obj/necsimmodule.o: /usr/include/sys/_types/_fd_isset.h
obj/necsimmodule.o: /usr/include/sys/_types/_fd_zero.h
obj/necsimmodule.o: /usr/include/sys/_types/_fd_copy.h
obj/necsimmodule.o: /usr/include/sys/_select.h
obj/necsimmodule.o: /usr/include/sys/_types/_dev_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_mode_t.h
obj/necsimmodule.o: /usr/include/sys/_types/_uuid_t.h
obj/necsimmodule.o: /usr/include/gethostuuid.h necsimmodule.h PyLogging.h
obj/necsimmodule.o: necsim/LogFile.h necsim/SpatialTree.h
obj/necsimmodule.o: /usr/include/sqlite3.h necsim/Tree.h necsim/TreeNode.h
obj/necsimmodule.o: necsim/Logging.h necsim/LogFile.h
obj/necsimmodule.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/necsimmodule.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsimmodule.o: necsim/CustomExceptions.h necsim/NRrand.h
obj/necsimmodule.o: necsim/DataPoint.h necsim/Community.h necsim/DataMask.h
obj/necsimmodule.o: necsim/Map.h necsim/SpecSimParameters.h
obj/necsimmodule.o: necsim/Filesystem.h necsim/Step.h necsim/Cell.h
obj/necsimmodule.o: necsim/SpeciesList.h necsim/Landscape.h necsim/Setup.h
obj/necsimmodule.o: necsim/DispersalCoordinator.h necsim/ReproductionMap.h
obj/necsimmodule.o: necsim/ProtractedTree.h necsim/SpatialTree.h
obj/necsimmodule.o: necsim/SimulationTemplates.h
obj/necsimmodule.o: necsim/ProtractedSpatialTree.h necsim/ProtractedTree.h
obj/necsim/CPLCustomHandler.o: necsim/CPLCustomHandler.h necsim/Logging.h
obj/necsim/CPLCustomHandler.o: necsim/LogFile.h
obj/necsim/Community.o: necsim/Community.h /usr/include/sqlite3.h
obj/necsim/Community.o: necsim/TreeNode.h necsim/Logging.h necsim/LogFile.h
obj/necsim/Community.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/necsim/Community.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/Community.o: necsim/ConfigFileParser.h /usr/include/unistd.h
obj/necsim/Community.o: /usr/include/_types.h /usr/include/sys/_types.h
obj/necsim/Community.o: /usr/include/sys/cdefs.h
obj/necsim/Community.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/Community.o: /usr/include/sys/_posix_availability.h
obj/necsim/Community.o: /usr/include/machine/_types.h
obj/necsim/Community.o: /usr/include/i386/_types.h
obj/necsim/Community.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/Community.o: /usr/include/sys/unistd.h
obj/necsim/Community.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/Community.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/Community.o: /usr/include/sys/_types/_size_t.h
obj/necsim/Community.o: /usr/include/_types/_uint64_t.h
obj/necsim/Community.o: /usr/include/Availability.h
obj/necsim/Community.o: /usr/include/AvailabilityInternal.h
obj/necsim/Community.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_off_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_null.h
obj/necsim/Community.o: /usr/include/sys/select.h
obj/necsim/Community.o: /usr/include/sys/appleapiopts.h
obj/necsim/Community.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/Community.o: /usr/include/sys/_types/_timespec.h
obj/necsim/Community.o: /usr/include/sys/_types/_timeval.h
obj/necsim/Community.o: /usr/include/sys/_types/_time_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/Community.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/Community.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/Community.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/Community.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/Community.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/Community.o: /usr/include/sys/_select.h
obj/necsim/Community.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/Community.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/Community.o: /usr/include/gethostuuid.h necsim/CustomExceptions.h
obj/necsim/Community.o: necsim/Map.h necsim/SpecSimParameters.h
obj/necsim/Community.o: necsim/Filesystem.h
obj/necsim/ConfigFileParser.o: necsim/ConfigFileParser.h
obj/necsim/ConfigFileParser.o: /usr/include/unistd.h /usr/include/_types.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/cdefs.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_posix_availability.h
obj/necsim/ConfigFileParser.o: /usr/include/machine/_types.h
obj/necsim/ConfigFileParser.o: /usr/include/i386/_types.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/unistd.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_size_t.h
obj/necsim/ConfigFileParser.o: /usr/include/_types/_uint64_t.h
obj/necsim/ConfigFileParser.o: /usr/include/Availability.h
obj/necsim/ConfigFileParser.o: /usr/include/AvailabilityInternal.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_off_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_null.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/select.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/appleapiopts.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_timespec.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_timeval.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_time_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_select.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/ConfigFileParser.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/ConfigFileParser.o: /usr/include/gethostuuid.h
obj/necsim/ConfigFileParser.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/ConfigFileParser.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/DataMask.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/DataMask.o: necsim/ConfigFileParser.h /usr/include/unistd.h
obj/necsim/DataMask.o: /usr/include/_types.h /usr/include/sys/_types.h
obj/necsim/DataMask.o: /usr/include/sys/cdefs.h
obj/necsim/DataMask.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/DataMask.o: /usr/include/sys/_posix_availability.h
obj/necsim/DataMask.o: /usr/include/machine/_types.h
obj/necsim/DataMask.o: /usr/include/i386/_types.h
obj/necsim/DataMask.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/DataMask.o: /usr/include/sys/unistd.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_size_t.h
obj/necsim/DataMask.o: /usr/include/_types/_uint64_t.h
obj/necsim/DataMask.o: /usr/include/Availability.h
obj/necsim/DataMask.o: /usr/include/AvailabilityInternal.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_off_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_null.h
obj/necsim/DataMask.o: /usr/include/sys/select.h
obj/necsim/DataMask.o: /usr/include/sys/appleapiopts.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_timespec.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_timeval.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_time_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/DataMask.o: /usr/include/sys/_select.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/DataMask.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/DataMask.o: /usr/include/gethostuuid.h necsim/Logging.h
obj/necsim/DataMask.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/DataMask.o: necsim/CustomExceptions.h necsim/Map.h
obj/necsim/DataMask.o: necsim/Landscape.h
obj/necsim/DataPoint.o: necsim/DataPoint.h necsim/Logging.h necsim/LogFile.h
obj/necsim/DataPoint.o: necsim/CPLCustomHandler.h
obj/necsim/DispersalCoordinator.o: necsim/DispersalCoordinator.h
obj/necsim/DispersalCoordinator.o: necsim/NRrand.h necsim/Logging.h
obj/necsim/DispersalCoordinator.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/DispersalCoordinator.o: necsim/Map.h necsim/Step.h necsim/Cell.h
obj/necsim/DispersalCoordinator.o: necsim/Landscape.h necsim/DataMask.h
obj/necsim/DispersalCoordinator.o: necsim/SimParameters.h
obj/necsim/DispersalCoordinator.o: necsim/ConfigFileParser.h
obj/necsim/DispersalCoordinator.o: /usr/include/unistd.h
obj/necsim/DispersalCoordinator.o: /usr/include/_types.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/cdefs.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_posix_availability.h
obj/necsim/DispersalCoordinator.o: /usr/include/machine/_types.h
obj/necsim/DispersalCoordinator.o: /usr/include/i386/_types.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/unistd.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_size_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/_types/_uint64_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/Availability.h
obj/necsim/DispersalCoordinator.o: /usr/include/AvailabilityInternal.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_off_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_null.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/select.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/appleapiopts.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_timespec.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_timeval.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_time_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_select.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/DispersalCoordinator.o: /usr/include/gethostuuid.h
obj/necsim/DispersalCoordinator.o: necsim/CustomExceptions.h
obj/necsim/Filesystem.o: /usr/include/zconf.h /usr/include/sys/types.h
obj/necsim/Filesystem.o: /usr/include/sys/appleapiopts.h
obj/necsim/Filesystem.o: /usr/include/sys/cdefs.h
obj/necsim/Filesystem.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/Filesystem.o: /usr/include/sys/_posix_availability.h
obj/necsim/Filesystem.o: /usr/include/machine/types.h
obj/necsim/Filesystem.o: /usr/include/i386/types.h /usr/include/i386/_types.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_int8_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_int16_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_int32_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_int64_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_u_int8_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_u_int16_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_u_int32_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_u_int64_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_uintptr_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types.h
obj/necsim/Filesystem.o: /usr/include/machine/_types.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/Filesystem.o: /usr/include/machine/endian.h
obj/necsim/Filesystem.o: /usr/include/i386/endian.h
obj/necsim/Filesystem.o: /usr/include/sys/_endian.h
obj/necsim/Filesystem.o: /usr/include/libkern/_OSByteOrder.h
obj/necsim/Filesystem.o: /usr/include/libkern/i386/_OSByteOrder.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_blkcnt_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_blksize_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_in_addr_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_in_port_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_ino_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_ino64_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_key_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_nlink_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_id_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_off_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_clock_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_size_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_time_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_rsize_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_errno_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_attr_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_cond_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_condattr_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_mutex_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_mutexattr_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_once_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_rwlock_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_rwlockattr_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_pthread/_pthread_key_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fsblkcnt_t.h
obj/necsim/Filesystem.o: /usr/include/sys/_types/_fsfilcnt_t.h
obj/necsim/Filesystem.o: necsim/Filesystem.h /usr/include/sqlite3.h
obj/necsim/Filesystem.o: necsim/CustomExceptions.h necsim/Logging.h
obj/necsim/Filesystem.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/Landscape.o: necsim/Landscape.h necsim/Map.h necsim/DataMask.h
obj/necsim/Landscape.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Landscape.o: /usr/include/unistd.h /usr/include/_types.h
obj/necsim/Landscape.o: /usr/include/sys/_types.h /usr/include/sys/cdefs.h
obj/necsim/Landscape.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/Landscape.o: /usr/include/sys/_posix_availability.h
obj/necsim/Landscape.o: /usr/include/machine/_types.h
obj/necsim/Landscape.o: /usr/include/i386/_types.h
obj/necsim/Landscape.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/Landscape.o: /usr/include/sys/unistd.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_size_t.h
obj/necsim/Landscape.o: /usr/include/_types/_uint64_t.h
obj/necsim/Landscape.o: /usr/include/Availability.h
obj/necsim/Landscape.o: /usr/include/AvailabilityInternal.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_off_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_null.h
obj/necsim/Landscape.o: /usr/include/sys/select.h
obj/necsim/Landscape.o: /usr/include/sys/appleapiopts.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_timespec.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_timeval.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_time_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/Landscape.o: /usr/include/sys/_select.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/Landscape.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/Landscape.o: /usr/include/gethostuuid.h necsim/Logging.h
obj/necsim/Landscape.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/Landscape.o: necsim/CustomExceptions.h necsim/Filesystem.h
obj/necsim/Landscape.o: /usr/include/sqlite3.h
obj/necsim/LogFile.o: necsim/LogFile.h necsim/Filesystem.h
obj/necsim/LogFile.o: /usr/include/sqlite3.h necsim/CustomExceptions.h
obj/necsim/LogFile.o: necsim/Logging.h necsim/CPLCustomHandler.h
obj/necsim/Logging.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/Logging.o: necsim/CPLCustomHandler.h
obj/necsim/Metacommunity.o: necsim/Metacommunity.h /usr/include/sqlite3.h
obj/necsim/Metacommunity.o: necsim/Community.h necsim/TreeNode.h
obj/necsim/Metacommunity.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/Metacommunity.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/necsim/Metacommunity.o: necsim/DataMask.h necsim/SimParameters.h
obj/necsim/Metacommunity.o: necsim/ConfigFileParser.h /usr/include/unistd.h
obj/necsim/Metacommunity.o: /usr/include/_types.h /usr/include/sys/_types.h
obj/necsim/Metacommunity.o: /usr/include/sys/cdefs.h
obj/necsim/Metacommunity.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/Metacommunity.o: /usr/include/sys/_posix_availability.h
obj/necsim/Metacommunity.o: /usr/include/machine/_types.h
obj/necsim/Metacommunity.o: /usr/include/i386/_types.h
obj/necsim/Metacommunity.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/Metacommunity.o: /usr/include/sys/unistd.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_size_t.h
obj/necsim/Metacommunity.o: /usr/include/_types/_uint64_t.h
obj/necsim/Metacommunity.o: /usr/include/Availability.h
obj/necsim/Metacommunity.o: /usr/include/AvailabilityInternal.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_off_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_null.h
obj/necsim/Metacommunity.o: /usr/include/sys/select.h
obj/necsim/Metacommunity.o: /usr/include/sys/appleapiopts.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_timespec.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_timeval.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_time_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/Metacommunity.o: /usr/include/sys/_select.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/Metacommunity.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/Metacommunity.o: /usr/include/gethostuuid.h
obj/necsim/Metacommunity.o: necsim/CustomExceptions.h necsim/Map.h
obj/necsim/Metacommunity.o: necsim/SpecSimParameters.h necsim/Tree.h
obj/necsim/Metacommunity.o: necsim/NRrand.h necsim/DataPoint.h
obj/necsim/Metacommunity.o: necsim/Filesystem.h necsim/Step.h necsim/Cell.h
obj/necsim/ProtractedTree.o: necsim/ProtractedTree.h necsim/SpatialTree.h
obj/necsim/ReproductionMap.o: necsim/ReproductionMap.h necsim/Map.h
obj/necsim/ReproductionMap.o: necsim/NRrand.h necsim/Logging.h
obj/necsim/ReproductionMap.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/Setup.o: necsim/Setup.h necsim/Logging.h necsim/LogFile.h
obj/necsim/Setup.o: necsim/CPLCustomHandler.h
obj/necsim/SimulateDispersal.o: necsim/SimulateDispersal.h
obj/necsim/SimulateDispersal.o: /usr/include/sqlite3.h necsim/Landscape.h
obj/necsim/SimulateDispersal.o: necsim/Map.h necsim/DataMask.h
obj/necsim/SimulateDispersal.o: necsim/SimParameters.h
obj/necsim/SimulateDispersal.o: necsim/ConfigFileParser.h
obj/necsim/SimulateDispersal.o: /usr/include/unistd.h /usr/include/_types.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/cdefs.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_posix_availability.h
obj/necsim/SimulateDispersal.o: /usr/include/machine/_types.h
obj/necsim/SimulateDispersal.o: /usr/include/i386/_types.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/unistd.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_size_t.h
obj/necsim/SimulateDispersal.o: /usr/include/_types/_uint64_t.h
obj/necsim/SimulateDispersal.o: /usr/include/Availability.h
obj/necsim/SimulateDispersal.o: /usr/include/AvailabilityInternal.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_off_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_null.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/select.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/appleapiopts.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_timespec.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_timeval.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_time_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_select.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/SimulateDispersal.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/SimulateDispersal.o: /usr/include/gethostuuid.h necsim/Logging.h
obj/necsim/SimulateDispersal.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/SimulateDispersal.o: necsim/CustomExceptions.h
obj/necsim/SimulateDispersal.o: necsim/DispersalCoordinator.h necsim/NRrand.h
obj/necsim/SimulateDispersal.o: necsim/Step.h necsim/Cell.h
obj/necsim/SimulateDispersal.o: necsim/Filesystem.h necsim/Community.h
obj/necsim/SimulateDispersal.o: necsim/TreeNode.h necsim/Matrix.h
obj/necsim/SimulateDispersal.o: necsim/SpecSimParameters.h
obj/necsim/SpatialTree.o: necsim/SpatialTree.h
obj/necsim/SpeciationCommands.o: necsim/SpeciationCommands.h
obj/necsim/SpeciationCommands.o: necsim/Community.h /usr/include/sqlite3.h
obj/necsim/SpeciationCommands.o: necsim/TreeNode.h necsim/Logging.h
obj/necsim/SpeciationCommands.o: necsim/LogFile.h necsim/CPLCustomHandler.h
obj/necsim/SpeciationCommands.o: necsim/Matrix.h necsim/DataMask.h
obj/necsim/SpeciationCommands.o: necsim/SimParameters.h
obj/necsim/SpeciationCommands.o: necsim/ConfigFileParser.h
obj/necsim/SpeciationCommands.o: /usr/include/unistd.h /usr/include/_types.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/cdefs.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_posix_availability.h
obj/necsim/SpeciationCommands.o: /usr/include/machine/_types.h
obj/necsim/SpeciationCommands.o: /usr/include/i386/_types.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/unistd.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_size_t.h
obj/necsim/SpeciationCommands.o: /usr/include/_types/_uint64_t.h
obj/necsim/SpeciationCommands.o: /usr/include/Availability.h
obj/necsim/SpeciationCommands.o: /usr/include/AvailabilityInternal.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_off_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_null.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/select.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/appleapiopts.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_timespec.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_timeval.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_time_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_select.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/SpeciationCommands.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/SpeciationCommands.o: /usr/include/gethostuuid.h
obj/necsim/SpeciationCommands.o: necsim/CustomExceptions.h necsim/Map.h
obj/necsim/SpeciationCommands.o: necsim/SpecSimParameters.h
obj/necsim/SpeciesGrid.o: necsim/SpeciesGrid.h necsim/SpeciesList.h
obj/necsim/SpeciesGrid.o: necsim/Matrix.h necsim/Logging.h necsim/LogFile.h
obj/necsim/SpeciesGrid.o: necsim/CPLCustomHandler.h necsim/NRrand.h
obj/necsim/SpeciesList.o: necsim/SpeciesList.h necsim/Matrix.h
obj/necsim/SpeciesList.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/SpeciesList.o: necsim/CPLCustomHandler.h necsim/NRrand.h
obj/necsim/Tree.o: necsim/Tree.h /usr/include/sqlite3.h necsim/TreeNode.h
obj/necsim/Tree.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/Tree.o: necsim/CPLCustomHandler.h necsim/Matrix.h
obj/necsim/Tree.o: necsim/SimParameters.h necsim/ConfigFileParser.h
obj/necsim/Tree.o: /usr/include/unistd.h /usr/include/_types.h
obj/necsim/Tree.o: /usr/include/sys/_types.h /usr/include/sys/cdefs.h
obj/necsim/Tree.o: /usr/include/sys/_symbol_aliasing.h
obj/necsim/Tree.o: /usr/include/sys/_posix_availability.h
obj/necsim/Tree.o: /usr/include/machine/_types.h /usr/include/i386/_types.h
obj/necsim/Tree.o: /usr/include/sys/_pthread/_pthread_types.h
obj/necsim/Tree.o: /usr/include/sys/unistd.h
obj/necsim/Tree.o: /usr/include/sys/_types/_posix_vdisable.h
obj/necsim/Tree.o: /usr/include/sys/_types/_seek_set.h
obj/necsim/Tree.o: /usr/include/sys/_types/_size_t.h
obj/necsim/Tree.o: /usr/include/_types/_uint64_t.h
obj/necsim/Tree.o: /usr/include/Availability.h
obj/necsim/Tree.o: /usr/include/AvailabilityInternal.h
obj/necsim/Tree.o: /usr/include/sys/_types/_ssize_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_uid_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_gid_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_intptr_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_off_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_pid_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_useconds_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_null.h /usr/include/sys/select.h
obj/necsim/Tree.o: /usr/include/sys/appleapiopts.h
obj/necsim/Tree.o: /usr/include/sys/_types/_fd_def.h
obj/necsim/Tree.o: /usr/include/sys/_types/_timespec.h
obj/necsim/Tree.o: /usr/include/sys/_types/_timeval.h
obj/necsim/Tree.o: /usr/include/sys/_types/_time_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_suseconds_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_sigset_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_fd_setsize.h
obj/necsim/Tree.o: /usr/include/sys/_types/_fd_set.h
obj/necsim/Tree.o: /usr/include/sys/_types/_fd_clr.h
obj/necsim/Tree.o: /usr/include/sys/_types/_fd_isset.h
obj/necsim/Tree.o: /usr/include/sys/_types/_fd_zero.h
obj/necsim/Tree.o: /usr/include/sys/_types/_fd_copy.h
obj/necsim/Tree.o: /usr/include/sys/_select.h
obj/necsim/Tree.o: /usr/include/sys/_types/_dev_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_mode_t.h
obj/necsim/Tree.o: /usr/include/sys/_types/_uuid_t.h
obj/necsim/Tree.o: /usr/include/gethostuuid.h necsim/CustomExceptions.h
obj/necsim/Tree.o: necsim/NRrand.h necsim/DataPoint.h necsim/Community.h
obj/necsim/Tree.o: necsim/DataMask.h necsim/Map.h necsim/SpecSimParameters.h
obj/necsim/Tree.o: necsim/Filesystem.h necsim/Step.h necsim/Cell.h
obj/necsim/TreeNode.o: necsim/TreeNode.h necsim/Logging.h necsim/LogFile.h
obj/necsim/TreeNode.o: necsim/CPLCustomHandler.h
obj/necsim/main.o: necsim/SpatialTree.h necsim/SimulationTemplates.h
obj/necsim/main.o: necsim/Logging.h necsim/LogFile.h
obj/necsim/main.o: necsim/CPLCustomHandler.h necsim/CustomExceptions.h
