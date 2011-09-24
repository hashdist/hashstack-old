#
#ranger.gnu
#
module swap pgi gcc
module swap mvapich openmpi
module load atlas
setenv PYTHONHPC_ARCH ranger.gnu
setenv PYTHONHPC_PREFIX ${PYTHONHPC}/${PYTHONHPC_ARCH}
setenv PYTHONHPC_PYTHON ${PYTHONHPC}/${PYTHONHPC_ARCH}/bin/python
setenv PATH ${PYTHONHPC}/${PYTHONHPC_ARCH}/bin:${PATH}
setenv LD_LIBRARY_PATH ${PYTHONHPC}/${PYTHONHPC_ARCH}/lib:${LD_LIBRARY_PATH}
