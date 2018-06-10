#!/usr/bin/env bash
export CXXLAGS="${CFLAGS}"

cd $SRC_DIR/lib
./configure --prefix="${PREFIX}" OBJDIR=obj \
BUILDDIR=../necsim \
LIBS="-lpython${PY_VER}m" \
LDFLAGS="-L${SYS_PREFIX}/lib -L${SYS_PREFIX}/lib/python${PY_VER}/config-${PY_VER}m -L${SYS_PREFIX}/bin " \
CPPFLAGS="-I${SYS_PREFIX}/include -I${SYS_PREFIX}/include/python${PY_VER}m" \

make depend
make