import sys
import os
from os.path import join as pjoin
import argparse
from glob import glob

from hashdist.deps import yaml
from hashdist.core import load_configuration_from_inifile, SourceCache, BuildStore
from hashdist.hdist_logging import Logger, DEBUG, INFO

# open "recipes.py" directly rather than using the Python package system
from . import recipes as recipes_mod



class Context(object):
    def __init__(self, config, verbose, arch):
        self.config = config
        self.logger = logger = Logger(DEBUG if verbose else INFO)
        self.source_cache = SourceCache.create_from_config(config, logger, create_dirs=True)
        self.build_store = BuildStore.create_from_config(config, logger, create_dirs=True)
        self.arch = arch

def download_sources(ctx, pkg):
    """
    Download source code for a given package
    """
    ctx.logger.info('Downloading sources for %s' % pkg['package'])
    ctx.source_cache.fetch(pkg['url'], pkg['key'])


def build_package(ctx, pkg, imports):
    # Basic structure
    script = []
    buildspec = dict(name=pkg['package'],
                     version='n',
                     build={'script': script, 'import': imports, 'env': {}})

    # Listing the sources to unpack. We want to have:
    #   - $BUILD/src: the tarball/git commit listed in package.json,
    #   - $BUILD: any files named ${package}Config/*.arch

    pattern = '%sConfig/*.%s' % (pkg['package'], ctx.arch)
    files = {}
    for filename in glob(pattern):
        base = os.path.basename(filename)
        assert base.endswith(ctx.arch)
        base = base[:-len(ctx.arch) - 1] # strip .$arch
        with open(filename) as f:
            contents = f.read()
        files[base] = contents
    files_key = ctx.source_cache.put(files)

    buildspec['sources'] = [
        dict(key=files_key, target='.'),
        dict(key=pkg['key'], target='src',
             strip=0 if pkg['key'].startswith('git:') else 1)
        ]
    script.append(["@hdist", "build-unpack-sources"])

    # Environment:

    recipe_func = getattr(recipes_mod, '%s_recipe' % pkg.get('recipe', 'standard'))
    recipe_func(ctx, pkg, buildspec)

    if not ctx.build_store.is_present(buildspec):
        download_sources(ctx, pkg)
    artifact_id, dir = ctx.build_store.ensure_present(buildspec, ctx.config, keep_build='error')
    ctx.logger.info('Building %s' % pkg['package'])
    return artifact_id

def build_all(ctx, packages, subset):
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
        artifact_id = build_package(ctx, pkg, imports)
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
    config = load_configuration_from_inifile('./hdistconfig')
    ctx = Context(config, args.verbose, args.arch)

    with open('packages.yml') as f:
        package_list = yaml.safe_load(f)
    packages = dict((pkg['package'], pkg) for pkg in package_list)

    if not args.subset:
        args.subset = packages.keys()

    build_all(ctx, packages, args.subset)

