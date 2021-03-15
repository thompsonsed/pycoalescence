cmake_minimum_required(VERSION 3.6)
# Main necsimmodule Python program

project(necsim CXX)
if (CMAKE_BUILD_TYPE STREQUAL Debug)
    message(STATUS "Detected debug mode")
    add_definitions(-DDEBUG)
    add_compile_options(-Werror=cast-function-type -pedantic -Wc++14-compat -Wcast-function-type)
endif ()
# Change this option to ON if RAM usage is an issue or supply as via CL
option(minimal_ram "minimal_ram" OFF)
option(USING_INTEL "Use intel compilers for compiling necsim." OFF) # Disabled by default

if (${CMAKE_VERSION} VERSION_LESS "3.8.0")
    set(CMAKE_CXX_STANDARD 14)
else ()
    set(CMAKE_CXX_STANDARD 17)
endif ()

#set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(SOURCE_DIR_NECSIM "${PROJECT_SOURCE_DIR}/necsim")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
set(CPP_17_UNSUPPORTED FALSE)
message(STATUS "CXX Standard: ${CMAKE_CXX_STANDARD}")
if (${CMAKE_CXX_STANDARD} LESS 17)
    set(CPP_17_UNSUPPORTED TRUE)
    if (${CMAKE_CXX_STANDARD} LESS 14)
        message(FATAL_ERROR "CMAKE_CXX_STANDARD of {CMAKE_CXX_STANDARD} is not c++14 or higher")
    endif ()
endif ()


message(STATUS "Compiler is ${CMAKE_CXX_COMPILER}")
if (USING_INTEL)
    message(STATUS "Intel compiler option is ${USING_INTEL}")
    if (${USING_INTEL})
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -xSSE4.2 -axAVX,CORE-AVX-I,CORE-AVX2")
    endif ()
endif ()
if (NOT ${minimal_ram})
    add_definitions(-Dsql_ram)
endif ()
if (${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    set(WINDOWS TRUE)
    add_definitions(-DWIN_INSTALL)
elseif (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(MACOSX TRUE)
endif ()
if (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(LINUX TRUE)
endif ()
if (DEFINED ENV{CONDA_PREFIX})
    message(STATUS "Installing inside conda env at $ENV{PREFIX}")
    if (WINDOWS)
        set(CMAKE_INSTALL_PREFIX "$ENV{LIBRARY_PREFIX}")
        set(CMAKE_PREFIX_PATH "$ENV{LIBRARY_PREFIX}")
    elseif (WINDOWS)
        set(CMAKE_INSTALL_PREFIX "$ENV{PREFIX}")
        set(CMAKE_PREFIX_PATH "$ENV{PREFIX}")
    endif ()
endif ()
include_directories(${SOURCE_DIR_NECSIM})

set(SOURCE_FILES
        ${SOURCE_DIR_NECSIM}/RNGController.h
        ${SOURCE_DIR_NECSIM}/Matrix.h
        ${SOURCE_DIR_NECSIM}/Map.h
        ${SOURCE_DIR_NECSIM}/parameters.h
        ${SOURCE_DIR_NECSIM}/parameters.cpp
        ${SOURCE_DIR_NECSIM}/SimParameters.h
        ${SOURCE_DIR_NECSIM}/SpecSimParameters.h
        ${SOURCE_DIR_NECSIM}/file_system.cpp
        ${SOURCE_DIR_NECSIM}/SpatialTree.cpp
        ${SOURCE_DIR_NECSIM}/Tree.cpp
        ${SOURCE_DIR_NECSIM}/SpeciationCommands.cpp
        ${SOURCE_DIR_NECSIM}/ConfigParser.cpp
        ${SOURCE_DIR_NECSIM}/DispersalCoordinator.cpp
        ${SOURCE_DIR_NECSIM}/Logger.cpp
        ${SOURCE_DIR_NECSIM}/Landscape.cpp
        ${SOURCE_DIR_NECSIM}/ProtractedTree.cpp
        ${SOURCE_DIR_NECSIM}/setup.cpp
        ${SOURCE_DIR_NECSIM}/setup.h
        ${SOURCE_DIR_NECSIM}/SimulationTemplates.h
        ${SOURCE_DIR_NECSIM}/SpeciesList.h
        ${SOURCE_DIR_NECSIM}/Community.cpp
        ${SOURCE_DIR_NECSIM}/ActivityMap.cpp
        ${SOURCE_DIR_NECSIM}/Metacommunity.cpp
        ${SOURCE_DIR_NECSIM}/DataMask.cpp
        ${SOURCE_DIR_NECSIM}/DataPoint.cpp
        ${SOURCE_DIR_NECSIM}/SpeciesList.cpp
        ${SOURCE_DIR_NECSIM}/TreeNode.cpp
        ${SOURCE_DIR_NECSIM}/LogFile.cpp
        ${SOURCE_DIR_NECSIM}/cpl_custom_handler.cpp
        ${SOURCE_DIR_NECSIM}/Cell.cpp
        ${SOURCE_DIR_NECSIM}/double_comparison.cpp
        LandscapeMetricsCalculator.cpp
        ${SOURCE_DIR_NECSIM}/SimulateDispersal.cpp
        ${SOURCE_DIR_NECSIM}/custom_exceptions.h
        ${SOURCE_DIR_NECSIM}/SQLiteHandler.cpp
        ${SOURCE_DIR_NECSIM}/SQLiteHandler.h
        ${SOURCE_DIR_NECSIM}/neutral_analytical.cpp
        ${SOURCE_DIR_NECSIM}/neutral_analytical.h
        ${SOURCE_DIR_NECSIM}/parameters.cpp
        ${SOURCE_DIR_NECSIM}/parameters.h
        ${SOURCE_DIR_NECSIM}/SimulatedSpeciesAbundancesHandler.cpp
        ${SOURCE_DIR_NECSIM}/SimulatedSpeciesAbundancesHandler.h
        ${SOURCE_DIR_NECSIM}/AnalyticalSpeciesAbundancesHandler.cpp
        ${SOURCE_DIR_NECSIM}/AnalyticalSpeciesAbundancesHandler.h
        ${SOURCE_DIR_NECSIM}/SpeciesAbundancesHandler.cpp
        ${SOURCE_DIR_NECSIM}/SpeciesAbundancesHandler.h
        ${SOURCE_DIR_NECSIM}/Xoroshiro256plus.h
        ${SOURCE_DIR_NECSIM}/GillespieCalculator.cpp
        ${SOURCE_DIR_NECSIM}/GillespieCalculator.h
        ${SOURCE_DIR_NECSIM}/MapLocation.cpp
        ${SOURCE_DIR_NECSIM}/MapLocation.h
        ${SOURCE_DIR_NECSIM}/eastl/heap.h
        ${SOURCE_DIR_NECSIM}/cpp17_includes.h
        ${SOURCE_DIR_NECSIM}/ghc/filesystem.hpp
        ${SOURCE_DIR_NECSIM}/ghc/fs_fwd.hpp
        ${SOURCE_DIR_NECSIM}/ghc/fs_impl.hpp
        ${SOURCE_DIR_NECSIM}/ghc/fs_std.hpp
        ${SOURCE_DIR_NECSIM}/ghc/fs_std_fwd.hpp
        ${SOURCE_DIR_NECSIM}/ghc/fs_std_impl.hpp
        ${SOURCE_DIR_NECSIM}/eastl/heap.h
        ${SOURCE_DIR_NECSIM}/GenericTree.h necsim/ProtractedSpatialTree.cpp)

if (APPLE)
    set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")
    set(CMAKE_FIND_FRAMEWORK "LAST")
elseif (WINDOWS)
    set(CMAKE_SHARED_LIBRARY_SUFFIX ".pyd")
endif ()
add_library(necsim SHARED ${SOURCE_FILES})
if (GDAL_INCLUDE_DIR AND GDAL_DIR)
    message(STATUS "Provided GDAL_DIR ${GDAL_DIR}")
    message(STATUS "Provided GDAL include location ${GDAL_INCLUDE_DIR}")
    set(ENV{GDAL_DIR} GDAL_DIR)
    set(ENV{GDAL_INCLUDE_DIR} GDAL_INCLUDE_DIR)
endif ()
if (UNIX)
    find_package(GDAL2 2.1.0 REQUIRED)
else ()
    find_package(GDAL 2.1.0 REQUIRED)
endif ()
if (NOT GDAL_FOUND)
    message(FATAL_ERROR "No gdal library found...exiting.")
endif ()
if (DEFINED ENV{CONDA_PREFIX})
    #    if (APPLE)
    # use, i.e. don't skip the full RPATH for the build tree
    #        SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
    #    endif ()
    message(STATUS "Conda install detected")

    if (NOT WINDOWS)
        find_package(sqlite3)
        include_directories(${SQLITE3_INCLUDE_DIRS})
        target_link_libraries(necsim ${SQLITE3_LIBRARIES})
    endif ()
else ()
    message(STATUS "Standard Python install detected")
    find_package(sqlite3)
    include_directories(${SQLITE3_INCLUDE_DIRS})
    target_link_libraries(necsim ${SQLITE3_LIBRARIES})
endif ()
include_directories(${GDAL_INCLUDE_DIR})

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
link_directories(${PYTHON_LIBRARIES})

if (NOT WINDOWS)
    if (PYTHON_CPPFLAGS)

        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${PYTHON_CPPFLAGS}")
    endif ()
    if (PYTHON_LDFLAGS)
        set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${PYTHON_LDFLAGS}")
    endif ()
endif ()

add_definitions(-Dwith_gdal)


if (WINDOWS)
    SET(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_BINDIR} CACHE PATH "build directory")
    target_link_libraries(necsim ${PYTHON_LIBRARIES})
    message(STATUS "Detecting libraries for windows")

    find_package(sqlite3)
    include_directories(${SQLITE3_INCLUDE_DIRS})
    target_link_libraries(necsim ${SQLITE3_LIBRARIES})
    target_link_libraries(necsim ${GDAL_LIBRARY})
else ()
    target_link_libraries(necsim ${GDAL_LIBRARY})
endif ()


# Require C++ 17 support for boost replacement
if (CPP_17_UNSUPPORTED)
    message(STATUS "Using BOOST libraries as C++ 17 not found")
    if (WINDOWS)
        #    set(Boost_NO_SYSTEM_PATHS true)
        #    set (Boost_USE_STATIC_LIBS OFF CACHE BOOL "use static libraries from Boost")
        #    set(Boost_USE_MULTITHREADED ON)
        add_definitions(-DBOOST_ALL_NO_LIB) # <----- This is really important for Windows compatibility
        # force all boost libraries to dynamic link (we already disabled
        # autolinking, so I don't know why we need this, but we do!)
        #    add_definitions( -DBOOST_ALL_DYN_LINK )
        #    set(Boost_USE_MULTITHREAD ON)
        #    set(Boost_USE_STATIC_LIBS ON)
        #    set(Boost_NO_SYSTEM_PATHS ON)
        #    set(Boost_USE_STATIC_LIBS OFF)
        #    set(Boost_USE_MULTITHREADED ON)
        #    set(Boost_USE_STATIC_RUNTIME OFF)
        #    set(Boost_DEBUG ON)  #<---------- Real life saver
        #    add_definitions(-DBOOST_SYSTEM_NO_DEPRECATED)
        find_package(Boost 1.5.7 COMPONENTS system filesystem)
        if (Boost_FOUND)
            add_definitions(-DUSING_BOOST)
            include_directories(${Boost_INCLUDE_DIR})
            target_link_libraries(necsim ${Boost_LIBRARIES})
        endif ()
    else ()
        find_package(Boost 1.5.7 COMPONENTS system filesystem)
        if (Boost_FOUND)
            add_definitions(-DUSING_BOOST)
            include_directories(${Boost_INCLUDE_DIR})
            target_link_libraries(necsim ${Boost_LIBRARIES})
        endif ()
    endif ()
endif ()


message(STATUS "Python include dirs: ${PYTHON_INCLUDE_DIRS}")
message(STATUS "Python libraries: ${PYTHON_LIBRARIES}")
message(STATUS "CXXFLAGS: ${CMAKE_CXX_FLAGS}")
message(STATUS "Shared linker flags: ${CMAKE_SHARED_LINKER_FLAGS}")
if (CPP_17_UNSUPPORTED)
    if (Boost_FOUND)
        message(STATUS "Boost root: ${Boost_ROOT}")
        message(STATUS "Boost include dirs: ${Boost_INCLUDE_DIR}")
    else ()
        message(STATUS "No C++17 or Boost found: using ghc filesystem library")
        include_directories(${SOURCE_DIR_NECSIM}/ghc)
    endif ()

endif ()
message(STATUS "Boost libraries: ${Boost_LIBRARIES}")
message(STATUS "GDAL include location ${GDAL_INCLUDE_DIR}")
message(STATUS "GDAL library location ${GDAL_LIBRARY}")