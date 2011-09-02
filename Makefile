#
#to add a new package 'pkg'
#1. Add targets  config_pkg, build_pkg, install_pkg, newConfig_pkg, and editConfig_pkg and add those to the *_core_* or *_extensions_* targets
#2. Add the pristine source for a version to directory or as a submodule
#3. Set up the name of the package in versions.txt
#
include versionsConfig/versions.${PYTHON_HPCMP_ARCH}

all: install

install: install_core install_extensions

install_core: install_core_python install_core_libraries install_core_modules

install_extensions: install_extensions_libraries install_extensions_modules

distclean: 
	rm -f *_progress 
	rm -f install_*
	make -k clean_log distclean_core_python distclean_core_libraries distclean_core_modules distclean_extensions_libraries distclean_extensions_modules

newConfig: newConfig_core_python newConfig_core_libraries newConfig_core_modules newConfig_extensions_libraries newConfig_extensions_modules

versionsConfig/versions.${PYTHON_HPCMP_ARCH}:
	cd versionsConfig && cp versions.${PYTHON_HPCMP_ARCH_OLD} versions.${PYTHON_HPCMP_ARCH}

editConfig: editConfig_core_python editConfig_core_libraries editConfig_core_modules editConfig_extensions_libraries editConfig_extensions_modules

#install
install_core_python: install_zlib install_python

install_core_libraries: install_petsc install_szip install_hdf5

install_core_modules: install_numpy install_nose install_numexpr install_cython install_tables install_mpi4py install_petsc4py

install_extensions_libraries:

install_extensions_modules: install_setuptools install_matplotlib install_sphinx

#distclean
distclean_core_python: distclean_python

distclean_core_libraries: distclean_petsc distclean_zlib distclean_szip distclean_hdf5

distclean_core_modules: distclean_numpy distclean_nose distclean_tables distclean_cython distclean_mpi4py distclean_petsc4py

distclean_extensions_libraries: 

distclean_extensions_modules: distclean_setuptools distclean_readline distclean_matplotlib distclean_sphinx

#newConfig
newConfig_core_python: newConfig_python

newConfig_core_libraries: newConfig_petsc newConfig_zlib newConfig_szip newConfig_hdf5

newConfig_core_modules: newConfig_numpy newConfig_nose newConfig_tables newConfig_cython newConfig_mpi4py newConfig_petsc4py

newConfig_extensions_libraries:

newConfig_extensions_modules: newConfig_setuptools newConfig_readline newConfig_matplotlib newConfig_sphinx

#editConfig
editConfig_core_python: editConfig_python
editConfig_core_libraries: editConfig_petsc editConfig_zlib editConfig_szip editConfig_hdf5

editConfig_core_modules: editConfig_numpy editConfig_nose editConfig_tables editConfig_cython editConfig_mpi4py editConfig_petsc4py

editConfig_extensions_libraries:

editConfig_extensions_modules: newConfig_setuptools newConfig_readline editConfig_matplotlib editConfig_sphinx

#core
#core python
#readline
newConfig_readline:
	echo "no readline customization implemented"

editConfig_readline:
	echo "no readline customization implemented"

config_readline:
	echo "no readline customization implemented" > config_readline_progress 2>&1

build_readline:
	cd ${READLINE_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_readline_progress 2>&1

install_readline: 
	cd ${READLINE_VERSION} &&  ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_readline_progress 2>&1
	cat config_readline_progress build_readline_progress install_readline_progress > install_readline

distclean_readline:
	touch install_readline
	mv -f install_readline install_readline_last
	cd ${READLINE_VERSION} && make distclean

#python
newConfig_python:
	cd pythonConfig && cp configure.${PYTHON_HPCMP_ARCH_OLD} configure.${PYTHON_HPCMP_ARCH}

editConfig_python:
	cd pythonConfig && ${EDITOR} configure.${PYTHON_HPCMP_ARCH}

config_python:
	cd ${PYTHON_VERSION} && ../pythonConfig/configure.${PYTHON_HPCMP_ARCH} > ../config_python_progress 2>&1

build_python:
	cd ${PYTHON_VERSION} && make > ../build_python_progress 2>&1

install_python:
	make config_python build_python
	cd ${PYTHON_VERSION} && PREFIXAPPS=${PYTHON_HPCMP_PREFIX} make install > ../install_python_progress 2>&1
	cat config_python_progress build_python_progress install_python_progress > install_python

distclean_python:
	touch install_python
	mv -f install_python install_python_last
	cd ${PYTHON_VERSION} && make distclean

#core libraries
#zlib
newConfig_zlib:
	cd zlibConfig && cp configure.${PYTHON_HPCMP_ARCH_OLD} configure.${PYTHON_HPCMP_ARCH}

editConfig_zlib:
	cd zlibConfig && ${EDITOR} configure.${PYTHON_HPCMP_ARCH}

config_zlib:
	cd ${ZLIB_VERSION} && ../zlibConfig/configure.${PYTHON_HPCMP_ARCH} > ../config_zlib_progress 2>&1

build_zlib:
	cd ${ZLIB_VERSION} && make > ../build_zlib_progress 2>&1

install_zlib:
	make config_zlib build_zlib
	cd ${ZLIB_VERSION} && make install > ../install_zlib_progress 2>&1
	cat config_zlib_progress build_zlib_progress install_zlib_progress > install_zlib

distclean_zlib:
	touch install_zlib
	mv -f install_zlib install_zlib_last
	cd ${ZLIB_VERSION} && make distclean

#szip
newConfig_szip:
	cd szipConfig && cp configure.${PYTHON_HPCMP_ARCH_OLD} configure.${PYTHON_HPCMP_ARCH}

editConfig_szip:
	cd szipConfig && ${EDITOR} configure.${PYTHON_HPCMP_ARCH}

config_szip:
	cd ${SZIP_VERSION} && ../szipConfig/configure.${PYTHON_HPCMP_ARCH} > ../config_szip_progress 2>&1

build_szip:
	cd ${SZIP_VERSION} && make > ../build_szip_progress 2>&1

install_szip:
	make config_szip build_szip
	cd ${SZIP_VERSION} && make install > ../install_szip_progress 2>&1
	cat config_szip_progress build_szip_progress install_szip_progress > install_szip

distclean_szip:
	touch install_szip
	mv -f install_szip install_szip_last
	cd ${SZIP_VERSION} && make -k distclean

#hdf5
newConfig_hdf5:
	cd hdf5Config && cp configure.${PYTHON_HPCMP_ARCH_OLD} configure.${PYTHON_HPCMP_ARCH}

editConfig_hdf5:
	cd hdf5Config && ${EDITOR} configure.${PYTHON_HPCMP_ARCH}

config_hdf5: install_zlib install_szip
	cd ${HDF5_VERSION} && ../hdf5Config/configure.${PYTHON_HPCMP_ARCH} > ../config_hdf5_progress 2>&1

build_hdf5:
	cd ${HDF5_VERSION} && make > ../build_hdf5_progress 2>&1

install_hdf5:
	make config_hdf5 build_hdf5
	cd ${HDF5_VERSION} && make install > ../install_hdf5_progress 2>&1
	cat config_hdf5_progress build_hdf5_progress install_hdf5_progress > install_hdf5

distclean_hdf5:
	touch install_hdf5
	mv -f install_hdf5 install_hdf5_last
	cd ${HDF5_VERSION} && make -k distclean

#petsc
get_petsc:
	hg clone http://petsc.cs.iit.edu/petsc/petsc-dev
	cd petsc-dev/config && hg clone http://petsc.cs.iit.edu/petsc/BuildSystem BuildSystem

update_petsc:
	cd petsc-dev && hg pull -u
	cd petsc-dev/config/BuildSystem && hg pull -u

newConfig_petsc:
	cd petscConfig && cp configure.${PYTHON_HPCMP_ARCH_OLD} configure.${PYTHON_HPCMP_ARCH}

editConfig_petsc:
	cd petscConfig && ${EDITOR} configure.${PYTHON_HPCMP_ARCH}

config_petsc:
	cd ${PETSC_VERSION} && ../petscConfig/configure.${PYTHON_HPCMP_ARCH} > ../config_petsc_progress 2>&1

build_petsc:
	cd ${PETSC_VERSION} && make > ../build_petsc_progress 2>&1

install_petsc:
	make config_petsc build_petsc
	cd ${PETSC_VERSION} && make install > ../install_petsc_progress 2>&1
	cat config_petsc_progress build_petsc_progress install_petsc_progress > install_petsc

distclean_petsc:
	touch install_petsc
	mv -f install_petsc install_petsc_last
	cd ${PETSC_VERSION} && make -k clean

#numpy
newConfig_numpy:
	cd numpyConfig && cp site.cfg.${PYTHON_HPCMP_ARCH_OLD} site.cfg.${PYTHON_HPCMP_ARCH} 

editConfig_numpy:
	cd numpyConfig && ${EDITOR} site.cfg.${PYTHON_HPCMP_ARCH}

config_numpy:
	echo "numpy has no config step run 'make editConfig_numpy'" > config_numpy_progress 2>&1
	cp -f numpyConfig/site.cfg.${PYTHON_HPCMP_ARCH} ${NUMPY_VERSION}/site.cfg

build_numpy:
	cd ${NUMPY_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_numpy_progress 2>&1

install_numpy:
	make config_numpy build_numpy
	cd ${NUMPY_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_numpy_progress 2>&1
	cat config_numpy_progress build_numpy_progress install_numpy_progress > install_numpy

distclean_numpy:
	touch install_numpy
	mv -f install_numpy install_numpy_last
	cd ${NUMPY_VERSION} && rm -rf build

#numexpr
newConfig_numexpr:
	echo "numexpr has no customization"

editConfig_numexpr:
	echo "numexpr has no customization"

config_numexpr:
	echo "numexpr has no customization" > config_numexpr_progress 2>&1

build_numexpr:
	cd ${NUMEXPR_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_numexpr_progress 2>&1

install_numexpr:
	make config_numexpr build_numexpr
	cd ${NUMEXPR_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_numexpr_progress 2>&1
	cat config_numexpr_progress build_numexpr_progress install_numexpr_progress > install_numexpr

distclean_numexpr:
	touch install_numexpr
	mv -f install_numexpr install_numexpr_last
	cd ${NUMEXPR_VERSION} && rm -rf build

#tables
newConfig_tables:
	cd tablesConfig && cp build.${PYTHON_HPCMP_ARCH_OLD} build.${PYTHON_HPCMP_ARCH} && cp install.${PYTHON_HPCMP_ARCH_OLD} install.${PYTHON_HPCMP_ARCH}

editConfig_tables:
	cd tablesConfig && ${EDITOR} build.${PYTHON_HPCMP_ARCH} install.${PYTHON_HPCMP_ARCH}

config_tables:
	echo "tables has no config step; run make 'make editConfig_tables'" > config_tables_progress 2>&1

build_tables:
	cd ${TABLES_VERSION} && ../tablesConfig/build.${PYTHON_HPCMP_ARCH} > ../build_tables_progress 2>&1

install_tables: install_szip install_zlib install_hdf5
	make config_tables build_tables
	cd ${TABLES_VERSION} && ../tablesConfig/install.${PYTHON_HPCMP_ARCH} > ../install_tables_progress 2>&1
	cat config_tables_progress build_tables_progress install_tables_progress > install_tables

distclean_tables:
	touch install_tables
	mv -f install_tables install_tables_last
	cd ${TABLES_VERSION} && rm -rf build

#nose
newConfig_nose:
	echo "no nose customization implemented"

editConfig_nose:
	echo "no nose customization implemented"

config_nose:
	echo "no nose customization implemented" > config_nose_progress 2>&1

build_nose:
	cd ${NOSE_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_nose_progress 2>&1

install_nose:
	make config_nose build_nose
	cd ${NOSE_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_nose_progress 2>&1
	cat config_nose_progress build_nose_progress install_nose_progress > install_nose

distclean_nose:
	touch install_nose
	mv -f install_nose install_nose_last
	cd ${NOSE_VERSION} && rm -rf build

#setuptools
newConfig_setuptools:
	echo "no setuptools customization implemented"

editConfig_setuptools:
	echo "no setuptools customization implemented"

config_setuptools:
	echo "no setuptools customization implemented" > config_setuptools_progress 2>&1

build_setuptools:
	cd ${SETUPTOOLS_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_setuptools_progress 2>&1

install_setuptools:
	make config_setuptools build_setuptools
	cd ${SETUPTOOLS_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_setuptools_progress 2>&1
	cat config_setuptools_progress build_setuptools_progress install_setuptools_progress > install_setuptools

distclean_setuptools:
	touch install_setuptools
	mv -f install_setuptools install_setuptools_last
	cd ${SETUPTOOLS_VERSION} && rm -rf build

#mpi4py
newConfig_mpi4py:
	cd mpi4pyConfig && cp config.${PYTHON_HPCMP_ARCH_OLD} config.${PYTHON_HPCMP_ARCH}  && cp build.${PYTHON_HPCMP_ARCH_OLD} build.${PYTHON_HPCMP_ARCH} && cp install.${PYTHON_HPCMP_ARCH_OLD} install.${PYTHON_HPCMP_ARCH}

editConfig_mpi4py:
	cd mpi4pyConfig && ${EDITOR} config.${PYTHON_HPCMP_ARCH} build.${PYTHON_HPCMP_ARCH} install.${PYTHON_HPCMP_ARCH}

config_mpi4py:
	cd ${MPI4PY_VERSION} && ../mpi4pyConfig/config.${PYTHON_HPCMP_ARCH} > ../config_mpi4py_progress 2>&1

build_mpi4py:
	cd ${MPI4PY_VERSION} && ../mpi4pyConfig/build.${PYTHON_HPCMP_ARCH} > ../build_mpi4py_progress 2>&1

install_mpi4py:
	make config_mpi4py build_mpi4py
	cd ${MPI4PY_VERSION} && ../mpi4pyConfig/install.${PYTHON_HPCMP_ARCH} > ../install_mpi4py_progress 2>&1
	cat config_mpi4py_progress build_mpi4py_progress install_mpi4py_progress > install_mpi4py

distclean_mpi4py:
	touch install_mpi4py
	mv -f install_mpi4py install_mpi4py_last
	cd ${MPI4PY_VERSION} && make -k clean

get_petsc4py:
	hg clone https://petsc4py.googlecode.com/hg/ petsc4py-dev

update_petsc4py:
	cd petsc4py-dev && hg pull -u

newConfig_petsc4py:
	echo "no petsc4py customization implemented"

editConfig_petsc4py:
	echo "no petsc4py customization implemented"

config_petsc4py:
	cd ${PETSC4PY_VERSION} && PETSC_DIR=${PYTHON_HPCMP_PREFIX} PETSC_ARCH='' ${PYTHON_HPCMP_PYTHON} setup.py config > ../config_petsc4py_progress  2>&1

build_petsc4py:
	cd ${PETSC4PY_VERSION} && PETSC_DIR=${PYTHON_HPCMP_PREFIX} PETSC_ARCH='' ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_petsc4py_progress  2>&1

install_petsc4py: install_petsc
	make config_petsc4py build_petsc4py
	cd ${PETSC4PY_VERSION} && PETSC_DIR=${PYTHON_HPCMP_PREFIX} PETSC_ARCH='' ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_petsc4py_progress 2>&1
	cat config_petsc4py_progress build_petsc4py_progress install_petsc4py_progress > install_petsc4py

distclean_petsc4py:
	touch install_petsc4py
	mv -f install_petsc4py install_petsc4py_last
	cd ${PETSC4PY_VERSION} && make -k clean

#cython
newConfig_cython:
	echo "no cython customization implemented"

editConfig_cython:
	echo "no cython customization implemented"

config_cython:
	cd ${CYTHON_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py config > ../config_cython_progress 2>&1

build_cython:
	cd ${CYTHON_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_cython_progress 2>&1

install_cython:
	make config_cython build_cython
	cd ${CYTHON_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_cython_progress 2>&1
	cat config_cython_progress build_cython_progress install_cython_progress > install_cython

distclean_cython:
	touch install_cython
	mv -f install_cython install_cython_last
	cd ${CYTHON_VERSION} && make -k clean

#extensions
#extensionsModules
#matplotlib
newConfig_matplotlib:
	cd matplotlibConfig && cp setup.cfg.${PYTHON_HPCMP_ARCH_OLD} setup.cfg.${PYTHON_HPCMP_ARCH}

editConfig_matplotlib:
	cd matplotlibConfig && ${EDITOR} setup.cfg.${PYTHON_HPCMP_ARCH}

config_matplotlib:
	cp matplotlibConfig/setup.cfg.${PYTHON_HPCMP_ARCH} ${MATPLOTLIB_VERSION}/setup.cfg
	cd ${MATPLOTLIB_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py config > ../config_matplotlib_progress 2>&1

build_matplotlib:
	cd ${MATPLOTLIB_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_matplotlib_progress 2>&1

install_matplotlib:
	make config_matplotlib build_matplotlib
	cd ${MATPLOTLIB_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_matplotlib_progress 2>&1
	cat config_matplotlib_progress build_matplotlib_progress install_matplotlib_progress > install_matplotlib

distclean_matplotlib:
	touch install_matplotlib
	mv -f install_matplotlib install_matplotlib_last
	cd ${MATPLOTLIB_VERSION} && make -k clean && rm -rf build
#sphinx
newConfig_sphinx:
	echo "no sphinx customization implemented"

editConfig_sphinx:
	echo "no sphinx customization implemented"

config_sphinx:
	cd ${SPHINX_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py config > ../config_sphinx_progress 2>&1

build_sphinx:
	cd ${SPHINX_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py build > ../build_sphinx_progress 2>&1

install_sphinx:
	make config_sphinx build_sphinx
	cd ${SPHINX_VERSION} && ${PYTHON_HPCMP_PYTHON} setup.py install > ../install_sphinx_progress 2>&1
	cat config_sphinx_progress build_sphinx_progress install_sphinx_progress > install_sphinx

distclean_sphinx:
	touch install_sphinx
	mv -f install_sphinx install_sphinx_last
	cd ${SPHINX_VERSION} && make -k clean
