#!/usr/bin/env python

# TODO: a proper bootstrap process
import sys
sys.path.insert(0, '/home/dagss/code/hashdist')


import os
from os.path import join as pjoin
import argparse

from hashdist.deps import yaml
from hashdist.core import load_configuration_from_inifile, SourceCache, BuildStore
from hashdist.hdist_logging import Logger, DEBUG, INFO

def load_versions_config(logger, arch):
    """Load list of packages for the given arch from versionsConfig/versions.$ARCH"""
    with open(pjoin('versionsConfig', 'versions.%s' % arch)) as f:
        lines = f.readlines()
    packages = {}
    for line in lines:
        envname, dirname = [x.strip() for x in line.split('=')]
        package_name = envname.split('_VERSION')[0].lower()
        packages[package_name] = dirname
    return packages

def download_sources(logger, source_cache, packages):
    """
    Scan through sources.yml and ensure all source code for the packages are present.
    Since versionsConfig tend to be out of date, we return a new list of packages
    
    """
    with open('sources.yml') as f:
        sources = yaml.safe_load(f)
    possible = {}
    for package, dirname in packages.items():
        try:
            info = sources[package]
        except KeyError:
            logger.warning('Sources not listed for %s' % package)
        else:
            logger.info('Downloading sources for %s' % package)
            source_cache.fetch(info['url'], info['key'])
            possible[package] = dirname
    return possible

def main():
    # Parse arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    argparser.add_argument('arch', help='e.g., "linux"')
    args = argparser.parse_args()

    # Set up Hashdist components, configured by ./hdistconfig
    logger = Logger(DEBUG if args.verbose else INFO)
    config = load_configuration_from_inifile('./hdistconfig')
    source_cache = SourceCache.create_from_config(config, logger, create_dirs=True)
    build_store = BuildStore.create_from_config(config, logger, create_dirs=True)

    # packages: { packagename: dirname }
    packages = load_versions_config(logger, args.arch)
    packages = download_sources(logger, source_cache, packages)
    print packages
    

if __name__ == '__main__':
    main()
