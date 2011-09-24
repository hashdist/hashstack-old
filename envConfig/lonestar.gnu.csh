#
#gnu
#
module swap intel gcc
module load atlas
setenv PYTOHNHPC_ARCH lonestar.gnu
setenv PYTOHNHPC_PREFIX ${PYTOHNHPC}/${PYTOHNHPC_ARCH}
setenv PYTOHNHPC_PYTHON ${PYTOHNHPC_PREFIX}/bin/python
setenv PATH .:${PYTOHNHPC_PREFIX}/bin:${HOME}/bin:${PATH}
setenv LD_LIBRARY_PATH ${PYTOHNHPC_PREFIX}/lib:${TACC_ATLAS_LIB}:/opt/apps/limic2/0.5.4/lib:${LD_LIBRARY_PATH}
