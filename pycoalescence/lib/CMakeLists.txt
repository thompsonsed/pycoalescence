cmake_minimum_required(VERSION 3.8)
project(NECSim)

set(CMAKE_CXX_STANDARD 14)

set(SOURCE_FILES
        necsim/ConfigFileParser.cpp
        necsim/ConfigFileParser.h
        necsim/CustomExceptions.h
        necsim/DataPoint.h
        necsim/DispersalCoordinator.cpp
        necsim/DispersalCoordinator.h
        necsim/NRrand.h
        necsim/LicenseHeader.h
        necsim/Logger.h
        necsim/Logger.cpp
        necsim/Logging.h
        necsim/Logging.cpp
        necsim/LogFile.cpp
        necsim/LogFile.h
        necsim/main.cpp
        necsim/Landscape.cpp
        necsim/Landscape.h
        necsim/Matrix.h
        necsim/ProtractedTree.cpp
        necsim/ProtractedTree.h
        necsim/Setup.cpp
        necsim/Setup.h
        necsim/SpeciesList.h
        necsim/Step.h
        necsim/Community.cpp
        necsim/Community.h
        necsim/TreeNode.h necsim/ReproductionMap.cpp necsim/ReproductionMap.h
        necsim/DataMask.h necsim/SimParameters.h necsim/Metacommunity.cpp necsim/Metacommunity.h necsim/Filesystem.cpp necsim/Filesystem.h
        necsim/DataMask.cpp
        necsim/DataPoint.cpp necsim/SpeciesList.cpp necsim/TreeNode.cpp necsim/SpatialTree.cpp necsim/SpatialTree.h
        necsim/Tree.cpp necsim/Tree.h
        necsim/SimulationTemplates.h necsim/ProtractedSpatialTree.h necsim/SpecSimParameters.h
        necsim/CPLCustomHandlerNecsim.h necsim/cplCustomHandlerNecsim.cpp necsim/Cell.h necsim/DoubleComparison.h necsim/DoubleComparison.cpp)

find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
find_library(gdal 2.1.0 REQUIRED)
find_library(SQL_DIR sqlite3)
include_directories(${Boost_INCLUDE_DIR})
include_directories(/usr/local/include)
include_directories(../)
link_directories(/usr/local/lib)
add_executable(NECSim ${SOURCE_FILES})
add_definitions(-Dwith_gdal -Dverbose)
if (CMAKE_BUILD_TYPE MATCHES Debug)
    add_definitions(-DDEBUG=1)
endif()
target_link_libraries(NECSim "${SQL_DIR}")
target_link_libraries(NECSim gdal)

target_link_libraries(NECSim ${Boost_LIBRARIES})

# Main necsimmodule python program

project(necsimmodule)
set(SOURCE_FILES
        necsimmodule.cpp
        necsimmodule.h
        necsim/Filesystem.cpp necsim/Filesystem.h necsim/SpeciesList.cpp necsim/SpatialTree.cpp necsim/SpatialTree.h
        necsim/Tree.cpp necsim/Tree.h necsim/ProtractedSpatialTree.h
        necsim/SpeciationCommands.cpp
        necsim/SpeciationCommands.h
        necsim/ConfigFileParser.cpp
        necsim/ConfigFileParser.h
        necsim/CustomExceptions.h
        necsim/DataPoint.h
        necsim/DispersalCoordinator.cpp
        necsim/DispersalCoordinator.h
        necsim/NRrand.h
        necsim/LicenseHeader.h
        necsim/Logger.cpp
        necsim/Logger.h
        necsim/Landscape.cpp
        necsim/Landscape.h
        necsim/Matrix.h
        necsim/ProtractedTree.cpp
        necsim/ProtractedTree.h
        necsim/Setup.cpp
        necsim/Setup.h
        necsim/SpeciesList.h
        necsim/Step.h
        necsim/Community.cpp
        necsim/Community.h
        necsim/TreeNode.h necsim/ReproductionMap.cpp necsim/ReproductionMap.h
        necsim/DataMask.h necsim/SimParameters.h necsim/Metacommunity.cpp necsim/Metacommunity.h necsim/Filesystem.cpp necsim/Filesystem.h
        necsim/DataMask.cpp
        necsim/DataPoint.cpp necsim/SpeciesList.cpp necsim/TreeNode.cpp necsim/SpatialTree.cpp necsim/SpatialTree.h
        necsim/Tree.cpp necsim/Tree.h
        necsim/SimulationTemplates.h necsim/LogFile.cpp necsim/LogFile.h necsim/ProtractedSpatialTree.h necsim/SpecSimParameters.h
        necsim/CPLCustomHandlerNecsim.h necsim/cplCustomHandlerNecsim.cpp necsim/Cell.h necsim/Cell.cpp CSimulation.h PyLogger.cpp PyLogger.h
        necsim/DoubleComparison.cpp necsim/DoubleComparison.h PyImports.cpp PyImports.h PyLogging.cpp PyLogging.h
        CSimulateDispersal.h CLandscapeMetricsCalculator.h CCommunity.h LandscapeMetricsCalculator.h LandscapeMetricsCalculator.cpp
        necsim/SimulateDispersal.cpp necsim/SimulateDispersal.h
        PyTemplates.h)
find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
find_package(PythonLibs REQUIRED)
find_library(SQL_DIR sqlite3)
include_directories(${Boost_INCLUDE_DIR})
include_directories(/usr/local/include)
link_directories(/usr/local/lib)
include_directories(${PYTHON_INCLUDE_DIRS})
add_definitions(-Dwith_gdal)
add_library(necsimmodule SHARED ${SOURCE_FILES} PyLogger.cpp PyLogger.h CSimulateDispersal.h)
target_link_libraries(necsimmodule ${PYTHON_LIBRARIES})
target_link_libraries(necsimmodule "${SQL_DIR}")
target_link_libraries(necsimmodule gdal)
target_link_libraries(necsimmodule ${Boost_LIBRARIES})
if (CMAKE_BUILD_TYPE MATCHES Debug)
    add_definitions(-DDEBUG=1)
endif()
