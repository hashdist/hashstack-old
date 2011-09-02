python-hpcmp
============

An enhanced Python distribution for HPCMP systems

Installation
------------

1) Initialize and update the submodules:

$cd python-hpcmp
$git submodule init
$git submodule update

2) Setup your environment, for example:

$export PYTHON_HPCMP_ARCH=linux
$export PYTHON_HPCMP=$HOME/src/python-hpcmp
$export PYTHON_HPCMP_PREFIX=$PYTHON_HPCMP/$PYTHON_HPCMP_ARCH
$export PYTHON_HPCMP_PYTHON=$PYTHON_HPCMP_PREFIX/bin/python
$export PETSC_DIR=$PYTHON_HPCMP/petsc
$export PETSC_ARCH=$PYTHON_HPCMP_ARCH

3) Install

$make
