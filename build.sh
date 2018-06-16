#!/usr/bin/env bash
# TODO remove junk
export CFLAGS="-I$PREFIX/include -I${BUILD_PREFIX}/include"
export CPPFLAGS="-I$PREFIX/include -I${BUILD_PREFIX}/include"
export CXXFLAGS="${CFLAGS}"
#export CPPFLAGS="-I${PREFIX}/include"
export LDFLAGS="-L${PREFIX}/lib -L${BUILD_PREFIX}/lib"
#PYTHON_INCLUDE="${PREFIX}/include/python${PY_VER}m/"
#cd pycoalescence/lib
#./configure --with-verbose OBJDIR=obj "BUILDDIR=@rpath/pycoalescence/necsim" "PYTHON_LIB=-lpython${PY_VER}m "\
# --prefix="${PREFIX}" "PYTHON_INCLUDE=-I/${PYTHON_INCLUDE}"  PLATFORM_SO=-dynamiclib
#make all
#mkdir build
#cd build
#cmake -G $CMAKE_GENERATOR -DCMAKE_INSTALL_PREFIX=$PREFIX
#-DCMAKE_BUILD_TYPE=Release $SRC_DIR
#cmake --build .
#cmake --build . --target install

python setup.py install --single-version-externally-managed --record=record.txt  # Python command to install the script.
