#!/bin/csh
#
#ranger.pgi
#
module load gotoblas
module load git
setenv PYTHONHPC_ARCH ranger.pgi
setenv CC  pgcc
setenv CXX pgCC
setenv FC  pgf90
setenv F77 pgf77
setenv F90 pgf90
#
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${PYTHONHPC}/${PYTHONHPC_ARCH}/bin/python
setenv PATH ${PYTHONHPC}/${PYTHONHPC_ARCH}/bin:${PATH}
setenv LD_LIBRARY_PATH ${PYTHONHPC}/${PYTHONHPC_ARCH}/lib:${LD_LIBRARY_PATH}
