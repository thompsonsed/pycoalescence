AC_INIT(all, 1.0)
AC_CONFIG_MACRO_DIR([m4])
CPPFLAGS="$CPPFLAGS -I. -std=c++14"
VPATH="necsim:$VPATH"
OJBDIR="$OBJDIR"
BUILDDIR="$BUILDDIR"
LDFLAGS="$LDFLAGS -L."
platform_so="$PLATFORM_SO"

dnl Check the provided arguments
AC_ARG_WITH(debug, [AS_HELP_STRING([--with-debug],[enable debug mode])],[],[]with_debug=no)
AC_ARG_WITH(verbose, [AS_HELP_STRING([--with-verbose],[enable verbose mode enabled])],[],[with_verbose=no])
AC_ARG_WITH(gdal, [AS_HELP_STRING([--with-gdal[PATH]],[prefix of gdal [guess]])],[],[with_gdal=no])
AC_ARG_WITH(hpc, [AS_HELP_STRING([--with-hpc],[add compile options for icp compilation on IC HPC])],[],[with_hpc=no])
AC_ARG_VAR([PYTHON_INCLUDE], [Include flags for Python, bypassing default paths])
AC_ARG_VAR([PYTHON_LDFLAGS], [Library location for Python header files, bypassing default paths])
AC_ARG_VAR([PYTHON_LIB], [Name of the Python library for linking (e.g. -lpython3.6m)])

dnl Switch to C++ mode
define(m4_pattern_allow)
AC_LANG(C++)
dnl Check if C++ compiler works works.
AC_PROG_CXX([icpc icc g++ gcc])
AX_CXX_COMPILE_STDCXX(14, [], [optional])

if [[ "$HAVE_CXX14" == 1 ]]
then
	fullcpp14="Full"
	echo "Full C++14 support detected..."
else
	fullcpp14="partial/not detected"
	AC_MSG_WARN([Some issues encountered detected C++14, continuing anyway.])
fi
dnl AC_PROG_CXX


dnl test hpc compilation mode
hpc_mode="disabled"
if [[ "$with_hpc" == yes ]]
then
	echo "Attempting icpc usage...."
	hpc_mode="enabled"
	if [[ "$CXX" != icpc ]]
	then
		hpc_mode="disabled"
		AC_MSG_WARN([Could not find icpc compiler. Defaulting to system compiler.])
	else
		verbose_mode="disabled"
		CPPFLAGS="$CPPFLAGS -xSSE4.2 -axAVX,CORE-AVX-I,CORE-AVX2"
	fi
else
	hpc_mode="disabled"
fi


user_options=""
dnl now test the command-line options
dnl test cls-dispersal restriction
debug_mode="disabled"



if [[ "$with_debug" != no ]]
then
	debug_mode="enabled"
	user_options="$user_options -DDEBUG -g"
fi

dnl set verbose mode
verbose_mode="enabled"
if [[ "$with_verbose" == no ]]
then
	verbose_mode="disabled"
else
	user_options="$user_options -Dverbose"
fi

dnl Check sqlite headers exist
AC_CHECK_HEADERS(sqlite3.h, [has_sqlite3=1], [has_sqlite3=0])
with_sqlite3="yes"
if [[ "$has_sqlite3" == 0 ]]
then
	with_sqlite3="no"
	AC_ERROR([A working sqlite3 library is required. Make sure it is correctly installed on your system.])
fi
LIBS="$LIBS -lsqlite3 $PYTHON_LIB"
dnl Check boost headers
AC_LANG(C++)
BOOST_REQUIRE([1.54], AC_ERROR([A working boost library v1.54 or greater is required. Make sure it is correctly installed on your system.]))
ifdef(BOOST_CPPFLAGS,[boost_found="yes"],[boost_found="no"])
substring="-I/"
if [[ "$BOOST_CPPFLAGS" == "${BOOST_CPPFLAGS%$substring*}" ]];
then
	LIBS="$LIBS -lboost_filesystem -lboost_system -lpthread"
	AC_MSG_WARN([Library locations not detecting: using default locations.])
	boost_found="install detected: location unknown"
else
	dnl goofy workaround for boost libraries
	lib_boost="${BOOST_CPPFLAGS}"
	lib_boost="${lib_boost/-I/-L}"
	lib_boost="${lib_boost/include/lib}"
	CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
	LDFLAGS="$LDFLAGS $lib_boost"
	LIBS="$LIBS -lboost_filesystem -lboost_system -lpthread"
	boost_found="yes"
fi

dnl BOOST_FILESYSTEM - disabled as I can't get libtool to work properly
dnl BOOST_SYSTEM
BOOST_FIND_HEADER([boost/filesystem.hpp])
dnl BOOST_FIND_LIBS([filesystem], [filesystem],[], [boost/filesystem.hpp]])
dnl echo "$BOOST_FILESYSTEM_LDFLAGS"

dnl defines contains the list of preprocessors 
defines=""

dnl Check for fast-csv-parser
AC_CHECK_HEADERS([necsim/fast-cpp-csv-parser/csv.h],[use_csv=1],[use_csv=0])
if [[ "$use_csv" == 1 ]]
then
	fast_cpp_csv_parser="enabled"
	defines="$defines -Duse_csv"
else
	AC_MSG_WARN([src/fast-cpp-csv-parser not found. Download from https://github.com/ben-strasser/fast-cpp-csv-parser to enable])
	fast_cpp_csv_parser="disabled"
fi

dnl Check for gdal library
dnl Check if user-supplied gdal prefix
if [[ "$with_gdal" == no ]]
then
	gdal_libs=$(gdal-config --libs)
	gdal_includes=$(gdal-config --cflags)
else
	gdal_libs="-L$with_gdal -lgdal"
	gdal_includes="-I$with_gdal"
fi
substring="lgdal"
if [[ "$gdal_libs" == "${gdal_config%$substring*}" ]];
then
	AC_ERROR([No gdal-config file found for obtaining library information. Check install is complete.])
else
	BACKUP_CPPFLAGS="$CPPFLAGS"
	CPPFLAGS="$CPPFLAGS $gdal_includes"
	BACKUP_LDFLAGS="$LDFLAGS"
	LDFLAGS="$LDFLAGS $gdal_libs"
	LIBS="$LIBS -lgdal"
fi 
use_gdal=0
dnl echo "$gdal_includes"
AC_CHECK_HEADERS([gdal_priv.h], [use_gdal=1],[use_gdal=0])
AC_CHECK_HEADERS([cpl_conv.h], [use_cpl=1], [use_cpl=0])
if [[ "$use_gdal" == 1 ]]
then
	if [[ "$use_cpl" == 1 ]]
	then
		have_gdal="yes"
		defines="$defines -Dwith_gdal"
	else
		have_gdal="no"
	fi
else
	have_gdal="no"
fi

if [[ "$have_gdal" == no ]]
then
	CPPFLAGS="$BACKUP_CPPFLAGS"
	LDFLAGS="$BACKUP_LDFLAGS"
fi



DEFINES="$defines $user_options"
CPPFLAGS2="$CPPFLAGS $PYTHON_INCLUDE"
CPPFLAGS="$CPPFLAGS $DEFINES -O3 $PYTHON_INCLUDE"
LDFLAGS="$LDFLAGS $PYTHON_LDFLAGS"
AC_SUBST(objs, ["$defines"])

dnl Create the output variables
AC_SUBST(with_gdal, $with_gdal)
AC_SUBST(with_boost, $boost_found)
AC_SUBST(debug_mode, $debug_mode)
AC_SUBST(hpc_mode, $hpc_mode)
AC_SUBST(PLATFORM_SO, $platform_so)
AC_SUBST(VPATH, $VPATH)
AC_SUBST(OBJDIR, $OJBDIR)
AC_SUBST(BUILDDIR, $BUILDDIR)
dnl Process Makefile.in to create Makefile
AC_OUTPUT(Makefile)
dnl ---------------------------------------------------------------------------
dnl Display configuration status
dnl ---------------------------------------------------------------------------

echo "-----------------------------"
echo "  necsim is now configured"
echo "-----------------------------"
echo "  Installation directory:    ${prefix}"
echo "  ----------------"
echo "  Compiler Options"
echo "  ----------------"
echo "    C++ compiler:            ${CXX}"
echo ""
echo "    C++ compile flags:       ${CPPFLAGS2}"
echo ""
echo "    Libraries:               ${LIBS}"
echo ""
echo "    Linker Directories:      ${LDFLAGS}"
echo ""
echo "    Defines:                 ${DEFINES}"
echo ""
echo "    Build Dir:               ${BUILDDIR}"
echo ""
echo "    Object Dir:              ${OBJDIR}"
echo ""
echo "    VPATH:                   ${VPATH}"
echo ""
echo "    HPC Support:             ${hpc_mode}"
echo ""
echo "    Shared object flags:     ${platform_so}"        
echo ""
echo "  ----------------"
echo "  Detected Support"
echo "  ----------------"
echo "    sqlite3 support:         ${with_sqlite3}"
echo ""
echo "    boost support:           ${with_boost}"
echo ""
echo "    gdal support:            ${have_gdal}"
echo "       user-defined prefix:  ${with_gdal}"
echo ""
echo "    fast-cpp-csv-parser      ${fast_cpp_csv_parser}"
echo ""
echo "    C++14 support:           ${fullcpp14}"


echo "  ----------------"
echo "  Detected options"
echo "  ----------------"
echo ""
echo "    Debug mode:              $debug_mode"
echo ""
echo "    Verbose mode:            ${verbose_mode}"
echo ""

dnl LOC_MSG()
dnl LOC_MSG([  LIBZ support:              ${LIBZ_SETTING}])
dnl LOC_MSG([  LIBLZMA support:           ${LIBLZMA_SETTING}])


	
