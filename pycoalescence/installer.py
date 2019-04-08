"""
Compile **necsim** with default or provided compilation options. Intended for internal usage during ``pip`` or ``conda``
builds, although manual installation is also possible by running this file from the command line.
``python installer.py`` configures the install by detecting system components and compiles the ``C++`` files, if
possible. Command line flags can be provided to installer.py to modify the install (see
:ref:`Compilation Options <sec Compilation Options>` for more information).
"""

from __future__ import print_function, absolute_import, division  # Only Python 2.x

import itertools
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from distutils import sysconfig

# Import system operations for subprocess executation and log file handling

try:
    from .future_except import FileNotFoundError
    from .system_operations import execute_log_info, set_logging_method, execute_silent, mod_directory
except (ImportError, SystemError, ValueError):  # pragma: no cover
    from future_except import FileNotFoundError
    from system_operations import execute_log_info, set_logging_method, execute_silent, mod_directory
from setuptools.command.build_ext import build_ext


class Installer(build_ext):  # pragma: no cover
    """Wraps configuration and compilation of C++ code."""

    def __init__(self, dist, **kwargs):
        """Generates the link to the mod directory for installation."""
        build_ext.__init__(self, dist)
        self.mod_dir = mod_directory
        self.build_dir = None
        self.obj_dir = None

    def make_depend(self):
        """
        Runs make depend in the lib directory to calculate all dependencies for the header and source files.

        .. note:: Fails silently if makedepend is not installed, printing an error to logging.
        """
        try:
            execute_silent(["make", "depend"], cwd=os.path.join(self.mod_dir, "lib/"))
        except (RuntimeError, subprocess.CalledProcessError) as rte:
            logging.error("Could not execute makedepend: " + str(rte))
            logging.error("Using default dependencies instead.")
            self.use_default_depends()

    def create_default_depend(self):
        """
        Runs the default makedepend command, outputting dependencies to lib/depends_default.

        Used to generate a default dependency file on a system where makedepend exists, for a system where it does not.
        """
        try:
            execute_silent(
                ["makedepend", "*.cpp", "necsim/*.cpp", "-f" "depends_default", "-p", "obj/", "-Y"],
                cwd=os.path.join(self.mod_dir, "lib/"),
            )
        except (RuntimeError, subprocess.CalledProcessError) as rte:
            logging.error("Could not execute makedepend: " + str(rte))

    def use_default_depends(self):
        """
        Uses the default dependencies, copying all contents of depends_default to the end of Makefile.

        .. note:: Zero error-checking is done here as the Makefiles should not change, and the depends_default file should
                  be created using create_default_depend()

        """
        # First read Makefile
        with open(os.path.join(self.mod_dir, "lib", "Makefile"), "r") as f_in:
            lines = f_in.readlines()
        with open(os.path.join(self.mod_dir, "lib", "depends_default"), "r") as f_default:
            lines_default = f_default.readlines()
        # Now write all back out
        with open(os.path.join(self.mod_dir, "lib/Makefile"), "w") as f_out:
            for line in lines:
                if "# DO NOT DELETE" in line:
                    break
                f_out.write(line)
            for line in lines_default:
                f_out.write(line)

    def do_compile(self):
        """
        Compiles the C++ necsim program by running make. This changes the working directory to wherever the module has been
        installed for the subprocess call.
        """
        # Check that the make file exists
        if os.path.exists(os.path.join(self.mod_dir, "lib/")):
            time.sleep(0.5)
            self.make_depend()
            # Sleep to ensure that file timings are updated (support for HPC systems with inaccurate timings).
            time.sleep(1)
            try:
                execute_log_info(["make", "all"], cwd=os.path.join(self.mod_dir, "lib/"))
                logging.info("Compilation exited successfully.")
            except (RuntimeError, subprocess.CalledProcessError) as rte:
                logging.error(str(rte))
                logging.error("Compilation attempted, but error thrown.")
        else:
            raise IOError("C++ library does not exist! Check relative file path")

    def move_shared_object_file(self):
        """
        Moves the shared object (.so) file to the build directory.
        :return:
        """
        directory = os.path.join(self.mod_dir, "necsim")
        dirv = "sharedpy" + sys.version[0]
        for file in ["libnecsim.so"]:
            src = os.path.join(self.mod_dir, "lib", file)
            version_dir = os.path.join(directory, dirv)
            if not os.path.exists(src):
                raise IOError("Shared object file {} does not exists. Check installation was successful.".format(src))
            if not os.path.exists(directory):
                os.mkdir(directory)
            if not os.path.exists(version_dir):
                os.mkdir(version_dir)
            if not os.path.exists(os.path.join(version_dir, "__init__.py")):
                open(os.path.join(version_dir, "__init__.py"), "a").close()
            dst = os.path.join(directory, dirv, file)
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy(src, dst)

    def get_build_dir(self):
        """
        Gets the build directory.

        :return: the build directory path
        """
        if self.build_dir is None:
            directory = os.path.join(self.mod_dir, "necsim")
            return directory
        return os.path.join(self.build_dir)

    def get_obj_dir(self):
        """
        Gets the obj directory for installing obj files to.

        :return: the obj directory path
        """
        if self.obj_dir is None:
            return "obj"
        return self.obj_dir

    def configure(self, opts=None):
        """
        Runs ./configure --opts with the supplied options. This should create the makefile for compilation, otherwise a
        RuntimeError will be thrown.

        :param opts: a list of options to pass to the ./configure call
        """
        if "--with-debug" in opts or self.debug:
            for i, each in enumerate(opts):
                if "-DNDEBUG" in each:
                    opts[i] = opts[i].replace("-DNDEBUG", "")
        if os.path.exists(os.path.join(self.mod_dir, "lib", "configure")):
            try:
                if opts is None:
                    execute_log_info(
                        [
                            "./configure",
                            "--with-verbose",
                            "BUILDDIR={}".format(self.get_build_dir()),
                            "OBJDIR={}".format(self.get_obj_dir()),
                        ],
                        cwd=os.path.join(self.mod_dir, "lib"),
                    )
                else:
                    command = ["./configure"]
                    command.extend(opts)
                    if "BUILDDIR" not in opts:
                        command.append("BUILDDIR={}".format(self.get_build_dir()))
                    if "OBJDIR" not in opts:
                        command.append("OBJDIR={}".format(self.get_obj_dir()))
                    execute_log_info(command, cwd=os.path.join(self.mod_dir, "lib"))
            except subprocess.CalledProcessError as cpe:
                raise subprocess.CalledProcessError("Configuration attempted, but error thrown: ".format(cpe))
        else:
            raise RuntimeError("File src/configure does not exist. Check installation has been successful.")

    def autoconf(self):
        """
        Runs the `autoconf` bash function (assuming that autoconf is available) to create the `configure` executable.
        """
        try:
            execute_log_info(["autoconf"], cwd=os.path.join(self.mod_dir, "lib/"))
        except (RuntimeError, subprocess.CalledProcessError, FileNotFoundError, OSError, IOError) as cpe:
            logging.warning(
                "Could not run autoconf function to generate configure executable. "
                "Please run this functionality manually if installation fails."
            )
            logging.warning(str(cpe))

    def clean(self):
        """
        Runs make clean in the NECSim directory to wipe any previous potential compile attempts.
        """
        try:
            time.sleep(0.5)
            execute_log_info(["make", "obj_dir"], cwd=os.path.join(self.mod_dir, "lib/"))
            execute_log_info(["make", "build_dir"], cwd=os.path.join(self.mod_dir, "lib/"))
            execute_log_info(["make", "clean"], cwd=os.path.join(self.mod_dir, "lib/"))
        except subprocess.CalledProcessError as cpe:
            raise RuntimeError("Make file has not been generated. Cannot clean: ".format(cpe))

    def get_ldflags(self):
        """Get the ldflags that Python was compiled with, removing some problematic options."""
        sysldflags = sysconfig.get_config_var("LDFLAGS")
        if sysldflags is None:
            ldflags = ""
        else:
            ldflags = re.sub(r"-arch \b[^ ]*[\ ]*", "", sysldflags) + " "
        if "--sysroot=" in ldflags:
            logging.warning("--sysroot found in LDFLAGS, removing")
            ldflags = re.sub(r"--sysroot=.*[,\s]", "", ldflags)
        ldflags = ldflags.replace("\n", " ")
        return ldflags

    def get_ldshared(self):
        """Get the ldshared Python variables and replaces -bundle with -shared for proper compilation."""
        ldflags = sysconfig.get_config_var("LDSHARED")
        if ldflags is None:
            return ""
        ldflags = " ".join(ldflags.split()[1:]).replace("-bundle", "-shared")
        return ldflags

    def get_compilation_flags(self, display_warnings=False):
        """
        Generates the compilation flags for passing to ./configure.
        :param display_warnings: If true, runs with the -Wall flag for compilation (displaying all warnings). Default is False.

        :return: list of compilation flags.
        :rtype: list
        """
        # Get the relevant flags that Python was originally compiled with, to be passed to the C++ code.
        include = str("CPPFLAGS=-I" + sysconfig.get_python_inc()).replace("\n", "")
        cflags = " " + sysconfig.get_config_var("CFLAGS")
        cflags = str(re.sub(r"-arch \b[^ ]*", "", cflags)).replace("\n", "")  # remove any architecture flags
        cflags += " "
        py_ldflags = str(
            "-L"
            + sysconfig.get_python_lib(standard_lib=True)
            + " -L"
            + sysconfig.get_config_var("DESTDIRS").replace(" ", " -L")
        ).replace("\n", "")
        py_lib = "PYTHON_LIB=-lpython"
        ldflags = str("LDFLAGS=" + self.get_ldflags())
        # Get the shared object platform-specific compilation flags.
        platform_so = "PLATFORM_SO="
        if platform.system() == "Linux":
            platform_so += "-shared"
        elif platform.system() == "Darwin":
            platform_so += "-dynamiclib"
        elif platform.system() == "Windows":
            raise SystemError(
                "COMPILATION FAILURE: Windows is not yet supported. You must compile the libraries yourself."
            )
        else:
            logging.critical("OS not detected, compilation failures likely. Please report this error.")
        # Make sure that the linker directs to the correct Python library (such as -lpython3.5m)
        # Eventually this will also detect if the install is for an anaconda distribution.
        if "conda" not in sys.version and "Continuum" not in sys.version:
            py_lib += sys.version[0:3]
            if "m" in sysconfig.get_config_var("LIBRARY"):
                py_lib += "m"
        else:
            cflags += "-I{}/include {}".format(os.environ["PREFIX"], "--enable-shared")
            ldflags += "-L{}/lib".format(os.environ["PREFIX"])
            py_lib += sys.version[0:3]
            if "m" in sysconfig.get_config_var("LIBRARY"):
                py_lib += "m"
            cflags += " -DANACONDA"
        ldflags += " " + py_ldflags
        py_ldflags = "PYTHON_LDFLAGS=" + py_ldflags
        call = [include + cflags, py_lib, ldflags, py_ldflags, platform_so]
        # Remove the flags which would potentially cause unnecessary warnings to be thrown.
        # This can be disabled by passing display_warnings=True
        if not display_warnings:
            call = [re.sub("-Wstrict-prototypes|-Wno-unused-result|-Wunused-variable|-Wall", "", x) for x in call]
        return call

    def run_configure(self, argv=None, logging_level=logging.INFO, display_warnings=False):
        """
        Configures the install for compile options provided via the command line, or with default options if no options exist.
        Running with ``-help`` or `-h` will display the compilation configurations called from ``./configure``.

        :param argv: the arguments to pass to configure script
        :param logging_level: the logging level to utilise (defaults to INFO).
        :param display_warnings: If true, runs with the -Wall flag for compilation (displaying all warnings). Default is False.
        """
        if argv is None:
            argv = [None]
        call = self.get_compilation_flags(display_warnings=display_warnings)
        set_logging_method(logging_level=logging_level)
        self.autoconf()
        if len(argv) == 1:
            logging.info("No compile options provided, using defaults.")
            print("Obj: {}".format(self.get_obj_dir()))
            print("Build: {}".format(self.get_build_dir()))
            call.extend(["--with-verbose", "OBJDIR={}", "BUILDDIR={}".format(self.get_obj_dir(), self.get_build_dir())])
        else:
            if argv[1] == "--h" or argv[1] == "-h" or argv[1] == "-help" or argv[1] == "--help":
                execute_log_info(["./configure", "--help"], cwd=os.path.join(self.mod_dir, "lib/"))
            if isinstance(argv, str):
                call.append(argv[2])
            else:
                call.extend(argv[1:])
        logging.info(call)
        self.configure(opts=call)
        self.clean()

    def backup_makefile(self):
        """
        Copies the makefile to a saved folder so that even if the original is overwritten, the last successful
        compilation can be recorded.
        """
        src = os.path.join(self.mod_dir, "lib", "Makefile")
        dst = os.path.join(self.mod_dir, "reference", "Makefile")
        if not os.path.exists(src):
            logging.error("Makefile does not exist at {}. Check successful compilation".format(src))
            return
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)

    def copy_makefile(self):
        """
        Copies the backup makefile to the main directory, if it exists.
        Throws an IOError if no makefile is found.
        """
        src = os.path.join("reference", "Makefile")
        dst = os.path.join("lib", "Makefile")
        if not os.path.exists(src):
            raise IOError("Cannot find backup Makefile, requires running of configuration scripts.")
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)

    def configure_and_compile(self, argv=[None], logging_level=logging.INFO):
        """
        Calls the configure script, then runs the compilation.

        :param argv: the arguments to pass to configure script
        :param logging_level: the logging level to utilise (defaults to INFO).
        :rtype: None
        """
        set_logging_method(logging_level=logging_level)
        display_warnings = "display_warnings=True" in argv
        self.run_configure(argv, logging_level=logging_level, display_warnings=display_warnings)
        self.do_compile()
        self.backup_makefile()

    def setuptools_cmake(self, ext):
        """
        Configures cmake for setuptools usage.

        :param ext: the extension to build cmake on
        """
        if "conda" not in sys.version and "Continuum" not in sys.version:
            extdir = os.path.abspath(
                os.path.join(os.path.dirname(self.get_ext_fullpath(ext.name)), "pycoalescence", "necsim")
            )
        else:
            sp_dir = os.environ.get("SP_DIR")
            if sp_dir is None:
                sp_dir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            extdir = os.path.join(sp_dir, "pycoalescence", "necsim")
        cmake_args, build_args = self.get_default_cmake_args(extdir)
        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get("CXXFLAGS", ""), self.distribution.get_version())
        if "INTEL_LICENSE_FILE" in env.keys():
            env["CXX"] = "icpc"
            env["CC"] = "icc"
            cmake_args.extend(["-DCMAKE_C_COMPILER=icc", "-DCMAKE_CXX_COMPILER=icpc", "-DUSING_INTEL=ON"])
        self.run_cmake(ext.sourcedir, cmake_args, build_args, self.build_temp, env)

    def run_cmake(self, src_dir, cmake_args, build_args, tmp_dir, env):
        """
        Runs cmake to compile necsim.

        :param src_dir: the source directory for necsim .cpp and .h files
        :param cmake_args: arguments to pass to the cmake project
        :param tmp_dir: the build directory to output cmake files to
        :param env: the os.environ (or other environmental variables) to pass on
        """
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        try:
            subprocess.check_call(["cmake", src_dir] + cmake_args, cwd=tmp_dir, env=env)
            subprocess.check_call(["cmake", "--build", ".", "--target", "necsim"] + build_args, cwd=tmp_dir, env=env)
        except subprocess.CalledProcessError as cpe:
            raise SystemError("Fatal error running cmake in directory: {}".format(cpe))
        if platform.system() == "Windows":
            shutil.copy(
                os.path.join(tmp_dir, "Release", "necsim.pyd"), os.path.join(self.get_build_dir(), "libnecsim.pyd")
            )

    def run(self):
        """Runs installation and generates the shared object files - entry point for setuptools"""
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        """Builds the C++ and Python extension."""
        self.build_dir = os.path.abspath(
            os.path.join(os.path.dirname(self.get_ext_fullpath(ext.name)), "pycoalescence", "necsim")
        )
        self.obj_dir = self.build_dir
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        self.setuptools_cmake(ext)

    def clean_cmake(self):
        """Deletes the cmake files and object locations if they exist."""
        for path in [
            os.path.join(self.get_build_dir(), "libnecsim.so"),
            os.path.join(self.get_build_dir(), "libnecsim.so.dSYM"),
            os.path.join(self.get_build_dir(), "libnecsim.pyd"),
            os.path.join(self.get_build_dir(), "libnecsim.dylib"),
            os.path.join(self.mod_dir, "obj"),
        ]:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

    def get_default_cmake_args(self, output_dir):
        """
        Returns the default cmake configure and build arguments.

        :param output_dir: the output directory to use

        :return: tuple of two lists, first containing cmake configure arguments, second containing build arguments
        :rtype: tuple
        """
        cfg = "Debug" if self.debug else "Release"
        cflags = sysconfig.get_config_var("CFLAGS")
        if cflags is not None:
            cflags = str(re.sub(r"-arch \b[^ ]*", "", cflags)).replace("\n", "")  # remove any architecture flags
        else:
            cflags = ""
        gdal_inc_path = None
        gdal_dir = None
        if platform.system() == "Windows":
            libdir = get_python_library("{}.{}".format(sys.version_info.major, sys.version_info.minor))
        else:
            conda_prefix = os.environ.get("PREFIX", None)  # for conda only under unix
            libdir = sysconfig.get_config_var("LIBDIR")
            if conda_prefix is not None:
                gdal_inc_path = os.path.join(conda_prefix, "include")
                gdal_dir = os.path.join(conda_prefix, "lib")
            else:
                try:
                    gdal_inc_path = subprocess.check_output(["gdal-config", "--cflags"], env=os.environ)
                    gdal_dir = subprocess.check_output(["gdal-config", "--prefix"], env=os.environ)
                except subprocess.CalledProcessError:
                    pass
                if gdal_inc_path is not None:
                    gdal_inc_path = gdal_inc_path.decode("utf-8").split(" ")[0][2:].replace("\n", "")
                if gdal_dir is not None:
                    gdal_dir = gdal_dir.decode("utf-8").replace("\n", "")
        if libdir is None:
            libdir = os.path.abspath(os.path.join(sysconfig.get_config_var("LIBDEST"), "..", "libs"))
            if sysconfig.get_config_var("LIBDEST") is None:
                raise SystemError("Cannot detect library directory for Python install.")
        cmake_args = [
            "-DPYTHON_LIBRARY:FILEPATH={}".format(libdir),
            "-DPYTHON_CPPFLAGS:='{}'".format(cflags),
            "-DPYTHON_LDFLAGS:='{}'".format(self.get_ldshared()),
            "-DPYTHON_INCLUDE_DIR:FILEPATH={}".format(sysconfig.get_python_inc()),
            "-DCMAKE_BUILD_TYPE={}".format(cfg),
        ]
        if gdal_inc_path is not None:
            cmake_args.append("-DGDAL_INCLUDE_DIR={}".format(gdal_inc_path))
        if gdal_dir is not None:
            cmake_args.append("-DGDAL_DIR={}".format(gdal_dir))
        build_args = ["--config", cfg]
        if platform.system() == "Windows":
            cmake_args += [
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY:PATH={}".format(
                    # cfg.upper(),
                    output_dir
                )
            ]
            if sys.maxsize > 2 ** 32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
        else:

            cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg, "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY:PATH={}".format(output_dir)]
            build_args += ["--", "-j2"]
        return cmake_args, build_args


def get_python_library(python_version):  # pragma: no cover
    """Get path to the Python library associated with the current Python
    interpreter."""
    # determine direct path to libpython
    python_library = sysconfig.get_config_var("LIBRARY")
    potential_library = None
    # if static (or nonexistent), try to find a suitable dynamic libpython
    if python_library is None or python_library[-2:] == ".a":

        candidate_lib_prefixes = ["", "lib"]

        candidate_extensions = [".lib", ".so"]
        if sysconfig.get_config_var("WITH_DYLD"):
            candidate_extensions.insert(0, ".dylib")

        candidate_versions = [python_version]
        if python_version:
            candidate_versions.append("")
            candidate_versions.insert(0, "".join(python_version.split(".")[:2]))

        abiflags = getattr(sys, "abiflags", "")
        candidate_abiflags = [abiflags]
        if abiflags:
            candidate_abiflags.append("")

        # Ensure the value injected by virtualenv is
        # returned on windows.
        # Because calling `sysconfig.get_config_var('multiarchsubdir')`
        # returns an empty string on Linux, `du_sysconfig` is only used to
        # get the value of `LIBDIR`.
        libdir = sysconfig.get_config_var("LIBDIR")
        if sysconfig.get_config_var("MULTIARCH"):
            masd = sysconfig.get_config_var("multiarchsubdir")
            if masd:
                if masd.startswith(os.sep):
                    masd = masd[len(os.sep) :]
                libdir = os.path.join(libdir, masd)

        if libdir is None:
            libdir = os.path.abspath(os.path.join(sysconfig.get_config_var("LIBDEST"), "..", "libs"))

        candidates = (
            os.path.join(libdir, "".join((pre, "python", ver, abi, ext)))
            for (pre, ext, ver, abi) in itertools.product(
                candidate_lib_prefixes, candidate_extensions, candidate_versions, candidate_abiflags
            )
        )
        for candidate in candidates:
            if os.path.exists(candidate):
                # we found a (likely alternate) libpython
                potential_library = candidate
                if potential_library[-2:] != ".a":
                    break
    # Otherwise still a static library, keep searching
    if potential_library is None:
        raise IOError("No Python libraries found")
    return potential_library


if __name__ == "__main__":  # pragma: no cover
    fail = True
    from distutils.dist import Distribution
    import argparse

    parser = argparse.ArgumentParser(description="Build the C++ library (necsim) required for pycoalescence.")
    parser.add_argument("--cmake", action="store_true", default=True, dest="cmake", help="use the cmake build process")
    parser.add_argument(
        "--autotools",
        action="store_true",
        default=False,
        dest="autotools",
        help="Use the autotools build process (./configure and make)",
    )
    parser.add_argument(
        "--compiler-args",
        metavar="N",
        type=str,
        nargs="+",
        dest="compiler_args",
        default=[],
        help="Additional arguments to pass to the autotools compiler",
    )
    parser.add_argument(
        "--cmake-args",
        metavar="N",
        type=str,
        nargs="+",
        dest="cmake_args",
        default=[],
        help="Additional arguments to pass to the cmake compiler during configuration",
    )
    parser.add_argument(
        "--cmake-build-args",
        metavar="N",
        type=str,
        nargs="+",
        dest="cmake_build_args",
        default=[],
        help="Additional arguments to pass to the cmake compiler at build time",
    )
    parser.add_argument("--debug", action="store_true", default=False, dest="debug", help="Compile using DEBUG defines")
    parser.add_argument(
        "-c",
        "-C",
        "--compile",
        action="store_true",
        default=False,
        dest="compile_only",
        help="Compile only, do not re-configure necsim",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        default=False,
        dest="clean",
        help="Clean previous cmake builds from this directory.",
    )

    args = parser.parse_args()
    if args.cmake and args.autotools:
        raise ValueError("Cannot use both cmake and autotools build process - specify one or the other.")
    if not args.cmake or args.autotools:
        raise ValueError("Must specify compilation either using autotools or cmake.")
    dist = Distribution()
    installer = Installer(dist)
    installer.debug = args.debug
    if args.clean:
        installer.clean_cmake()
    else:
        if args.cmake:
            env = os.environ.copy()
            build_dir = installer.get_build_dir()
            obj_dir = installer.get_obj_dir()
            cmake_args, build_args = installer.get_default_cmake_args(build_dir)
            cmake_args += args.cmake_args
            build_args += args.cmake_build_args
            src_dir = os.path.join(installer.mod_dir, "lib")
            installer.run_cmake(src_dir, cmake_args, build_args, obj_dir, env)
        else:
            if platform.system() != "Windows":
                raise SystemError("Usage of configure and make on a windows system is not supported.")
            if args.compile_only:
                set_logging_method(logging_level=logging.INFO)
                installer.copy_makefile()
                installer.do_compile()
                fail = False
            if fail:
                installer.configure_and_compile(args.compiler_args)
