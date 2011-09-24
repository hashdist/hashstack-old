#basic darwin64
setenv PYTHONHPC ${HOME}/pythonhpc
setenv PYTHONHPC_ARCH darwin64
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${PYTHONHPC_PREFIX}/Python.framework/Versions/Current/bin/python
setenv DAETK_DIR ${PYTHONHPC}/externalPackages/daetk
setenv DAETK_ARCH darwin64
setenv PETSC_DIR ${PYTHONHPC}/externalPackages/petsc-3.1-p1
setenv PETSC_ARCH darwin64
setenv CC /usr/bin/mpicc
setenv CFLAGS "-arch x86_64"
setenv CPPFLAGS "-arch x86_64"
setenv CXX /usr/bin/mpicxx
setenv CXXFLAGS "-arch x86_64"
setenv FC  /opt/local/bin/openmpif90
setenv FFLAGS "-m64"
setenv F77 /opt/local/bin/openmpif77
setenv F90 /opt/local/bin/openmpif90
setenv LD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv DYLD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib
setenv MACOSX_DEPLOYMENT_TARGET 10.6
setenv PATH ${PYTHONHPC_PREFIX}/Python.framework/Versions/Current/bin:${PYTHONHPC_PREFIX}/bin:${PATH}
