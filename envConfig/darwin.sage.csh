#basic darwinspkg
setenv SAGE_ROOT ${HOME}/src/femhub
setenv SAGE_LOCAL ${SAGE_ROOT}/local
setenv PYTHONHPC ${HOME}/pythonhpc
setenv PYTHONHPC_ARCH darwinspkg
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${SAGE_LOCAL}/bin/python
setenv DAETK_DIR ${PYTHONHPC}/externalPackages/daetk
setenv DAETK_ARCH darwinspkg
setenv PETSC_DIR ${PYTHONHPC}/externalPackages/petsc-3.1-p1
setenv PETSC_ARCH darwinspkg
unsetenv CC
unsetenv CFLAGS
unsetenv CPPFLAGS
unsetenv CXX
unsetenv CXXFLAGS
setenv FC ${SAGE_LOCAL}/bin/sage_fortran
unsetenv FFLAGS
setenv F77 ${SAGE_LOCAL}/bin/sage_fortran
setenv F90 ${SAGE_LOCAL}/bin/sage_fortran
setenv LD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib:${SAGE_LOCAL}/lib
setenv DYLD_LIBRARY_PATH ${PYTHONHPC_PREFIX}/lib:${SAGE_LOCAL}/lib
setenv MACOSX_DEPLOYMENT_TARGET 10.6
setenv PATH ${SAGE_LOCAL}/bin:${PYTHONHPC_PREFIX}/bin:${PATH}
