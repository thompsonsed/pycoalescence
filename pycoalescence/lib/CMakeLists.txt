cmake_minimum_required(VERSION 3.8)
project(NECSim)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
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
        necsim/Logging.cpp
        necsim/Logging.h
        necsim/main.cpp
        necsim/Map.cpp
        necsim/Map.h
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
        necsim/DataPoint.cpp necsim/SpeciesList.cpp necsim/TreeNode.cpp PyLogging.h necsim/SpatialTree.cpp necsim/SpatialTree.h
        necsim/Tree.cpp necsim/Tree.h
        necsim/SimulationTemplates.h necsim/LogFile.cpp necsim/LogFile.h necsim/ProtractedSpatialTree.h necsim/SpecSimParameters.h)

#set(Boost_INCLUDE_DIR /usr/local/Cellar/boost/1.62.0/include)
#set(Boost_LIBRARY_DIR /usr/local/Cellar/boost/1.62.0/lib)
find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
find_library(gdal 2.1.0 REQUIRED)
find_library(SQL_DIR sqlite3)
#find_library(GDAL_DIR gdal)
include_directories(${Boost_INCLUDE_DIR})
include_directories(/usr/local/include)
include_directories(../)
link_directories(/usr/local/lib)
add_executable(NECSim ${SOURCE_FILES})
add_definitions(-Dwith_gdal -Duse_csv -Dverbose)
if (CMAKE_BUILD_TYPE MATCHES Debug)
    add_definitions(-DDEBUG=1)
endif()
target_link_libraries(NECSim "${SQL_DIR}")
target_link_libraries(NECSim gdal)
#message(${Boost_LIBRARIES})

target_link_libraries(NECSim ${Boost_LIBRARIES})

# DISPERSAL PROGRAM
project(Dispersal)
set(SOURCE_FILES
        necsim/SimulateDispersal.cpp
        necsim/SimulateDispersal.h
        dispersalmodule.cpp
        dispersalmodule.h
        necsim/Filesystem.cpp necsim/Filesystem.h necsim/SpatialTree.cpp necsim/SpatialTree.h necsim/Tree.cpp necsim/Tree.h)
find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
find_package(PythonLibs REQUIRED)
find_library(SQL_DIR sqlite3)
find_library(GDAL_DIR gdal)
include_directories(${Boost_INCLUDE_DIR})
include_directories(/usr/local/include)
link_directories(/usr/local/lib)
add_library(Dispersal SHARED ${SOURCE_FILES})
include_directories(${PYTHON_INCLUDE_DIRS})
add_definitions(-Dwith_gdal)
target_link_libraries(Dispersal ${PYTHON_LIBRARIES})
target_link_libraries(Dispersal "${SQL_DIR}")
target_link_libraries(Dispersal gdal)
target_link_libraries(Dispersal ${Boost_LIBRARIES})
project(applyspecmodule)
set(SOURCE FILES applyspecmodule.cpp applyspecmodule.h necsim/Filesystem.cpp necsim/Filesystem.h PyLogging.cpp necsim/Metacommunity.h
        necsim/Metacommunity.cpp necsim/Community.h necsim/Community.cpp)
project(necsimmodule)
find_package(PythonLibs REQUIRED)
find_library(SQL_DIR sqlite3)
#find_library(GDAL_DIR gdal)
include_directories(${Boost_INCLUDE_DIR})
include_directories(/usr/local/include)
link_directories(/usr/local/lib)
add_library(applyspecmodule SHARED ${SOURCE_FILES})
include_directories(${PYTHON_INCLUDE_DIRS})
add_definitions(-Dwith_gdal)
target_link_libraries(applyspecmodule ${PYTHON_LIBRARIES})
target_link_libraries(applyspecmodule "${SQL_DIR}")
target_link_libraries(applyspecmodule gdal)
target_link_libraries(applyspecmodule ${Boost_LIBRARIES})
set(SOURCE_FILES
        necsimmodule.cpp
        necsimmodule.h
        necsim/Filesystem.cpp necsim/Filesystem.h PyLogging.cpp necsim/SpeciesList.cpp necsim/SpatialTree.cpp necsim/SpatialTree.h
        necsim/Tree.cpp necsim/Tree.h necsim/ProtractedSpatialTree.h)
find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
find_package(PythonLibs REQUIRED)
find_library(SQL_DIR sqlite3)
#find_library(GDAL_DIR gdal)
include_directories(${Boost_INCLUDE_DIR})
include_directories(/usr/local/include)
link_directories(/usr/local/lib)
add_library(necsimmodule SHARED ${SOURCE_FILES})
include_directories(${PYTHON_INCLUDE_DIRS})
add_definitions(-Dwith_gdal)
target_link_libraries(necsimmodule ${PYTHON_LIBRARIES})
target_link_libraries(necsimmodule "${SQL_DIR}")
target_link_libraries(necsimmodule gdal)
target_link_libraries(necsimmodule ${Boost_LIBRARIES})
project(SpeciationCounter)
set(SOURCE_FILES
        SpeciationCounter.cpp
        necsim/Metacommunity.cpp necsim/Metacommunity.h necsim/Filesystem.cpp necsim/Filesystem.h necsim/DataMask.cpp necsim/SpecSimParameters.h)
find_package(Boost 1.5.7 COMPONENTS system filesystem REQUIRED)
find_library(SQL_DIR sqlite3)
#find_library(GDAL_DIR gdal)
include_directories(${Boost_INCLUDE_DIR})
include_directories(/usr/local/include)
link_directories(/usr/local/lib)
add_library(SpeciationCounter SHARED ${SOURCE_FILES} necsim/Metacommunity.cpp necsim/Metacommunity.h)
include_directories(${PYTHON_INCLUDE_DIRS})
add_definitions(-Dwith_gdal)
target_link_libraries(SpeciationCounter ${PYTHON_LIBRARIES})
target_link_libraries(SpeciationCounter "${SQL_DIR}")
target_link_libraries(SpeciationCounter gdal)
target_link_libraries(SpeciationCounter ${Boost_LIBRARIES})



#target_link_libraries(NECSIM ${SQLITE_INCLUDE_DIRS})