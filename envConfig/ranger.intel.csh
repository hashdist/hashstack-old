#
#ranger.intel
#
module swap pgi intel
#module swap mvapich openmpi
module load mkl
setenv PYTHONHPC_ARCH ranger.intel
setenv CC mpicc
setenv CXX mpicxx
setenv FC mpif90
setenv F77 mpif77
setenv F90 mpif90
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${PYTHONHPC}/${PYTHONHPC_ARCH}/bin/python
setenv PATH ${PYTHONHPC}/${PYTHONHPC_ARCH}/bin:${PATH}
setenv LD_LIBRARY_PATH ${PYTHONHPC}/${PYTHONHPC_ARCH}/lib:${TACC_MKL_LIB}:${LD_LIBRARY_PATH}
