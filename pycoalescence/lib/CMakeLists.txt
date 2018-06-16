cmake_minimum_required(VERSION 3.8)
# Main necsimmodule python program

project(necsim)
set(CMAKE_CXX_STANDARD 14)
set(SOURCE_DIR_NECSIM "necsim")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
#if (DEFINED ENV{CONDA_PREFIX})
#    message(STATUS "Installing inside conda env at $ENV{PREFIX}")
#    set(CMAKE_INSTALL_PREFIX "$ENV{PREFIX}")
#endif()
include_directories(${SOURCE_DIR_NECSIM})
if (${CMAKE_C_COMPILER} MATCHES "icc.*$")
    set(USING_INTEL TRUE)
endif ()
set(SOURCE_FILES
        necsim.cpp
        necsim.h
        ${SOURCE_DIR_NECSIM}/Filesystem.cpp
        ${SOURCE_DIR_NECSIM}/SpatialTree.cpp
        ${SOURCE_DIR_NECSIM}/Tree.cpp
        ${SOURCE_DIR_NECSIM}/SpeciationCommands.cpp
        ${SOURCE_DIR_NECSIM}/ConfigFileParser.cpp
        ${SOURCE_DIR_NECSIM}/DispersalCoordinator.cpp
        ${SOURCE_DIR_NECSIM}/Logger.cpp
        ${SOURCE_DIR_NECSIM}/Landscape.cpp
        ${SOURCE_DIR_NECSIM}/ProtractedTree.cpp
        ${SOURCE_DIR_NECSIM}/Setup.cpp
        ${SOURCE_DIR_NECSIM}/SpeciesList.h
        ${SOURCE_DIR_NECSIM}/Community.cpp
        ${SOURCE_DIR_NECSIM}/ReproductionMap.cpp
        ${SOURCE_DIR_NECSIM}/Metacommunity.cpp
        ${SOURCE_DIR_NECSIM}/DataMask.cpp
        ${SOURCE_DIR_NECSIM}/DataPoint.cpp
        ${SOURCE_DIR_NECSIM}/SpeciesList.cpp
        ${SOURCE_DIR_NECSIM}/TreeNode.cpp
        ${SOURCE_DIR_NECSIM}/LogFile.cpp
        ${SOURCE_DIR_NECSIM}/CPLCustomHandlerNecsim.cpp
        ${SOURCE_DIR_NECSIM}/Cell.cpp
        PyLogger.cpp
        ${SOURCE_DIR_NECSIM}/DoubleComparison.cpp
        PyImports.cpp
        PyLogging.cpp
        LandscapeMetricsCalculator.cpp
        CCommunity.h
        CSimulation.h
        CLandscapeMetricsCalculator.h
        CSimulateDispersal.h
        ${SOURCE_DIR_NECSIM}/SimulateDispersal.cpp)
if (APPLE)
    set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")
endif (APPLE)
#include_directories(/usr/local/include)
#link_directories(/usr/local/lib)
add_library(necsim SHARED ${SOURCE_FILES})
find_package(GDAL 2.1.0 REQUIRED)
if (DEFINED ENV{CONDA_PREFIX})
    if (APPLE)
        # use, i.e. don't skip the full RPATH for the build tree
        SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

    endif ()

    target_link_libraries(necsim sqlite3)
    target_link_libraries(necsim boost_filesystem)
    target_link_libraries(necsim boost_system)
else ()
    find_package(sqlite3)
    include_directories(${SQLITE3_INCLUDE_DIRS})
    target_link_libraries(necsim ${SQLITE3_LIBRARIES})
    find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
    include_directories(${Boost_INCLUDE_DIR})
    target_link_libraries(necsim ${Boost_LIBRARIES})
endif ()
include_directories(${GDAL_INCLUDE_DIR})
#target_link_libraries(${GDAL_LIBRARY})
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(necsim ${PYTHON_LIBRARIES})
add_definitions(-Dwith_gdal)
target_link_libraries(necsim gdal)
if (CMAKE_BUILD_TYPE MATCHES Debug)
    add_definitions(-DDEBUG=1)
endif ()
