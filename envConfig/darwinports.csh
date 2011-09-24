#mac ports
setenv PYTHONHPC ${HOME}/pythonhpc
setenv PYTHONHPC_ARCH darwinports
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${PYTHONHPC_PREFIX}/Python.framework/Versions/Current/bin/python
setenv DAETK_DIR ${PYTHONHPC}/externalPackages/daetk
setenv DAETK_ARCH darwinports
setenv PETSC_DIR ${PYTHONHPC}/externalPackages/petsc-3.1-p1
setenv PETSC_ARCH darwinports
setenv CC /opt/local/bin/openmpicc
setenv CXX /opt/local/bin/openmpicxx
setenv FC /opt/local/bin/openmpi90
setenv F90 /opt/local/bin/openmpif90
setenv F77 /opt/local/bin/openmpif77
setenv LD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv DYLD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv MACOSX_DEPLOYMENT_TARGET 10.6
setenv PATH ${PYTHONHPC_PREFIX}/Python.framework/Versions/Current/bin:${PYTHONHPC_PREFIX}/bin:/opt/local/bin:${PATH}
