setenv PYTHON_HPCMP_ARCH darwin
setenv PYTHON_HPCMP ${HOME}/src/python-hpcmp
setenv PYTHON_HPCMP_PREFIX ${PYTHON_HPCMP}/${PYTHON_HPCMP_ARCH}
setenv PYTHON_HPCMP_PYTHON ${PYTHON_HPCMP_PREFIX}/bin/python
setenv PETSC_DIR ${PYTHON_HPCMP}/petsc
setenv PETSC_ARCH ${PYTHON_HPCMP_ARCH}
setenv LD_LIBRARY_PATH ${PYTHON_HPCMP_PREFIX}/lib
setenv PATH ${PYTHON_HPCMP_PREFIX}/Library/Frameworks/Python.framework/Versions/Current/bin:${PYTHON_HPCMP_PREFIX}/bin:${PATH}
