#
#garnet.gnu
#
module swap PrgEnv-pgi PrgEnv-gnu
module load acml
export PYTHONHPC_ARCH=garnet.gnu
export PYTHONHPC_PREFIX=${PYTHONHPC}/${PYTHONHPC_ARCH}
export PYTHONHPC_PYTHON=${PYTHONHPC_PREFIX}/bin/python
export PATH=.:${PYTHONHPC_PREFIX}/bin:${HOME}/src/pythonhpc/garnet/bin:${PATH}
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PYTHONHPC_PREFIX}/lib:${ACML_DIR}/gnu64/lib
