cmake_minimum_required(VERSION 3.8)
# Main necsimmodule python program

project(necsim CXX)
if (CMAKE_BUILD_TYPE STREQUAL Debug)
    message("Detected debug mode")
    add_definitions(-DDEBUG)
endif ()
option(minimal_ram "minimal_ram" OFF)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(SOURCE_DIR_NECSIM "${PROJECT_SOURCE_DIR}/necsim")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
if (NOT ${minimal_ram})
    add_definitions(-Dsql_ram)
endif()
if (${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    set(WINDOWS TRUE)
    add_definitions(-DWIN_INSTALL)

elseif (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(LINUX TRUE)
elseif (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(MACOSX TRUE)
endif()
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
elseif(WINDOWS)
    set(CMAKE_SHARED_LIBRARY_SUFFIX ".pyd")
endif ()
add_library(necsim SHARED ${SOURCE_FILES})
#include_directories(/usr/local/include)
#link_directories(/usr/local/lib)
find_package(GDAL 2.1.0 REQUIRED)
if (DEFINED ENV{CONDA_PREFIX})
    if (APPLE)
        # use, i.e. don't skip the full RPATH for the build tree
        SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
    endif ()
    message("Conda install detected")

    if(NOT WINDOWS)
        target_link_libraries(necsim sqlite3)
        target_link_libraries(necsim boost_filesystem)
        target_link_libraries(necsim boost_system)
    endif()
else ()
    message("Standard python install detected")
    find_package(sqlite3)
    include_directories(${SQLITE3_INCLUDE_DIRS})
    target_link_libraries(necsim ${SQLITE3_LIBRARIES})
    find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
    include_directories(${Boost_INCLUDE_DIR})
    target_link_libraries(necsim ${Boost_LIBRARIES})
endif ()
include_directories(${GDAL_INCLUDE_DIR})

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(necsim ${PYTHON_LIBRARIES})
add_definitions(-Dwith_gdal)



if(WINDOWS)
    SET (CMAKE_LIBRARY_OUTPUT_DIRECTORY  ${OUTPUT_BINDIR} CACHE PATH "build directory")
    message("Detecting libraries for windows")
#    set(Boost_NO_SYSTEM_PATHS true)
#    set (Boost_USE_STATIC_LIBS OFF CACHE BOOL "use static libraries from Boost")
#    set(Boost_USE_MULTITHREADED OFF)
    find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
    include_directories(${Boost_INCLUDE_DIR})
    target_link_libraries(necsim ${Boost_LIBRARIES})
    find_package(sqlite3)
    include_directories(${SQLITE3_INCLUDE_DIRS})
    target_link_libraries(necsim ${SQLITE3_LIBRARIES})
    # disable autolinking in boost
    add_definitions( -DBOOST_ALL_NO_LIB )

    # force all boost libraries to dynamic link (we already disabled
    # autolinking, so I don't know why we need this, but we do!)
    add_definitions( -DBOOST_ALL_DYN_LINK )
    target_link_libraries(necsim ${GDAL_LIBRARY})
#    INSTALL_TARGETS(../necsim/ RUNTIME_DIRECTORY
#            ../necsim/ necsim)
#    INSTALL(TARGETS ExecutableTarget StaticLibraryTarget SharedLibraryTarget
#            RUNTIME DESTINATION bin
#            LIBRARY DESTINATION lib
#            ARCHIVE DESTINATION lib
#            )

else()
    target_link_libraries(necsim ${GDAL_LIBRARY})
#    target_link_libraries(necsim gdal)
endif()
