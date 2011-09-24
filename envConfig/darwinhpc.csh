#basic darwin
setenv MACOSX_DEPLOYMENT_TARGET 10.6
setenv PYTHONHPC_ARCH darwinhpc
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${PYTHONHPC_PREFIX}/Library/Frameworks/Python.framework/Versions/Current/bin/python
setenv LD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv DYLD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv PATH ${PYTHONHPC_PREFIX}/Library/Frameworks/Python.framework/Versions/Current/bin:${PYTHONHPC_PREFIX}/bin:/usr/local/bin:${PATH}
setenv CC  /usr/local/bin/mpicc
setenv CXX /usr/local/bin/mpicxx
setenv FC  /usr/local/bin/mpif90
setenv F77 /usr/local/bin/mpif77
setenv F90 /usr/local/bin/mpif90
