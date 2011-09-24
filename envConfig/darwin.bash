#basic darwin
export MACOSX_DEPLOYMENT_TARGET=10.6
export PYTHONHPC_ARCH=darwin
export PYTHONHPC_PREFIX=${PYTHONHPC}/${PYTHONHPC_ARCH}
export PYTHONHPC_PYTHON=${PYTHONHPC_PREFIX}/Python.framework/Versions/Current/bin/python
export F90=gfortran
export F77=gfortran
export FC= gfortran
export LD_LIBRARY_PATH=${PYTHONHPC_PREFIX}/lib
export DYLD_LIBRARY_PATH=${PYTHONHPC_PREFIX}/lib
export PATH=${PYTHONHPC_PREFIX}/Library/Frameworks/Python.framework/Versions/Current/bin:${PYTHONHPC_PREFIX}/bin:${PATH}
