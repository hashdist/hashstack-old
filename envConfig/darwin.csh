#basic darwin
setenv MACOSX_DEPLOYMENT_TARGET 10.6
setenv PYTHONHPC_ARCH darwin
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${PYTHONHPC_PREFIX}/Library/Frameworks/Python.framework/Versions/Current/bin/python
setenv F90 gfortran
setenv F77 gfortran
setenv FC  gfortran
setenv LD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv DYLD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv PATH ${PYTHONHPC_PREFIX}/Library/Frameworks/Python.framework/Versions/Current/bin:${PYTHONHPC_PREFIX}/bin:${PATH}
