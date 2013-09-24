#!/bin/bash

set -e

cmake -DCMAKE_INSTALL_PREFIX:PATH="$ARTIFACT" \
    -DSZIP_USE_EXTERNAL:BOOL=ON \
    -DZLIB_USE_EXTERNAL:BOOL=ON \
    -DCFLAGS:STRING="-I$SZIP/include -I$ZLIB/include" \
    -DLDFLAGS:STRING="-L$SZIP/lib -lsz -L$ZLIB -lz"
make
echo "this doc doesn't exist in the source but install wants it here so I put it here. Your obd't servant, Chris Kees" > release_docs/INSTALL_VMS.txt
make install
