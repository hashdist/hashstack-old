import sys
import os
from os.path import join as pjoin
import argparse
import imp

from hashdist.deps import yaml
from hashdist.core import load_configuration_from_inifile, SourceCache, BuildStore
from hashdist.hdist_logging import Logger, DEBUG, INFO

# open "recipes.py" directly rather than using the Python package system
from . import recipes as recipes_mod

def download_sources(logger, source_cache, pkg):
    """
    Download source code for a given package
    """
    logger.info('Downloading sources for %s' % pkg['package'])
    source_cache.fetch(pkg['url'], pkg['key'])

def build_package(logger, source_cache, build_store, pkg, imports):
    # First, assemble JSON build spec
    build = dict(
        sources=dict(key=pkg['key'], target='.', strip=0 if pkg['key'].startswith('git:') else 0),
        name=pkg['package'],
        version='n', # we don't care
        build={'script': [], 'import': imports},
        )

    recipe = pkg.get('recipe', 'standard')
    recipe_func = getattr(recipes_mod, '%s_recipe' % recipe)
    recipe_func(pkg, build)

    download_sources(logger, source_cache, pkg)
    logger.info('Building %s' % pkg['package'])


def build_all(logger, source_cache, build_store, packages, subset):
    built = {} # { name : (artifact_id, before_list) }
    # depth-first traversal
    def visit(name):
        if name in built:
            return built[name]
        pkg = packages[name]
        imports = [] # the imports to build this package
        before = [] # to be given to dependee, which puts this in before-list for this artifact
        for dep in pkg.get('deps', []):
            dep_artifact_id, dep_before = visit(dep)
            imports.append({'ref': dep.upper(), 'id': dep_artifact_id, 'before': dep_before})
            before.append(dep_artifact_id)
        artifact_id = build_package(logger, source_cache, build_store, pkg, imports)
        result = (artifact_id, before)
        built[name] = result
        return result

    for package in subset:
        visit(package)
    

def main():
    # Parse arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    argparser.add_argument('arch', help='e.g., "linux"')
    argparser.add_argument('subset', nargs='*', help='only attempt to build packages given '
                           '(+ their dependencies)')
    args = argparser.parse_args()

    # Set up Hashdist components, configured by ./hdistconfig
    logger = Logger(DEBUG if args.verbose else INFO)
    config = load_configuration_from_inifile('./hdistconfig')
    source_cache = SourceCache.create_from_config(config, logger, create_dirs=True)
    build_store = BuildStore.create_from_config(config, logger, create_dirs=True)

    with open('packages.yml') as f:
        package_list = yaml.safe_load(f)
    packages = dict((pkg['package'], pkg) for pkg in package_list)

    if not args.subset:
        args.subset = packages.keys()

    build_all(logger, source_cache, build_store, packages, args.subset)

