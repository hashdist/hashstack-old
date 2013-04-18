from __future__ import print_function

import sys
import os
from os.path import join as pjoin
import argparse
from glob import glob
import traceback
import textwrap

from hashdist.deps import yaml
from hashdist.core import load_configuration_from_inifile, SourceCache, BuildStore, atomic_symlink
from hashdist.core.fileutils import silent_makedirs
from hashdist.hdist_logging import Logger, DEBUG, INFO

from . import recipes as recipes_mod

class Context(object):
    def __init__(self, logger, config, verbose, arch, build_env):
        self.config = config
        self.logger = logger
        self.source_cache = SourceCache.create_from_config(config, logger, create_dirs=True)
        self.build_store = BuildStore.create_from_config(config, logger, create_dirs=True)
        self.arch = arch
        self.build_env = build_env
        self.built = {}

    def get_artifact_id(self, name):
        return self.built[name]['id']

    def get_before_list(self, name):
        return self.built[name]['before']

    def build_all(self, packages, root_name):
        built = self.built # { name : dep_spec }
        # depth-first traversal

        def visit(name):
            # returns: dep_spec, that is, dict(ref=..., id=..., before=...)
            if name in built:
                return built[name]
            pkg = packages[name]
            imports = [] # the imports to build this package

            all_deps = complete_dependencies(self, packages, [name])
            for dep in all_deps:
                if dep == name:
                    continue
                imports.append(visit(dep))

            artifact_id = build_package(self, pkg, imports)
            
            before = [self.get_artifact_id(dep) for dep in pkg['deps']]
            dep_spec = {'ref': pkg['provides'].upper(), 'id': artifact_id, 'before': before}
            built[name] = dep_spec
            return dep_spec

        dep_spec = visit(root_name)
        return dep_spec['id']


def download_sources(ctx, pkg):
    """
    Download source code for a given package
    """
    ctx.logger.info('Downloading sources for %s' % pkg['package'])
    ctx.source_cache.fetch(pkg['url'], pkg['key'])


def build_package(ctx, pkg, imports):
    # Basic structure
    buildspec = dict(name=pkg['package'],
                     version='n',
                     build={"import": imports, "env": ctx.build_env})

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

    if 'key' in pkg:
        buildspec['sources'] = [
            dict(key=files_key, target='.'),
            dict(key=pkg['key'], target='src',
                 strip=0 if pkg['key'].startswith('git:') else 1)
            ]

    # Environment:

    recipe_func = getattr(recipes_mod, '%s_recipe' % pkg.get('recipe', 'standard'))
    recipe_func(ctx, pkg, files, buildspec)

    if not ctx.build_store.is_present(buildspec):
        if 'key' in pkg:
            download_sources(ctx, pkg)
        ctx.logger.info('Building %s' % pkg['package'])
    else:
        ctx.logger.info('Up to date: %s' % pkg['package'])
    artifact_id, dir = ctx.build_store.ensure_present(buildspec, ctx.config, keep_build='error')
    return artifact_id

def complete_dependencies(ctx, packages, subset):
    """
    Given a package database `packages` and a list of package names `subset`,
    return `subset` extended so that all ultimate dependencies are included.
    """
    visited = set()
    result = []
    def search(pkgname):
        if pkgname not in visited:
            try:
                pkg = packages[pkgname]
            except KeyError:
                msg = "Package referenced but not found: %s" % pkgname
                ctx.logger.error(msg)
                raise ValueError(msg)
            for dep in pkg.get('deps', []):
                search(dep)
            visited.add(pkgname)
            result.append(pkgname)
    for root in subset:
        search(root)
    return result

def main(logger, hdist_config_filename):
    # Parse arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    #argparser.add_argument('arch', help='e.g., "linux"')
    #argparser.add_argument('subset', nargs='*', help='only attempt to build packages given '
    #                       '(+ their dependencies)')
    args = argparser.parse_args()

    with open('config.yml') as f:
        hpcmp_config = yaml.safe_load(f)


    env = {'PATH': ':'.join(hpcmp_config['PATH'])}
    arch = hpcmp_config['arch']
    target_link = 'local'
    
    # Set up Hashdist components, configured by ./hdistconfig
    hdist_config = load_configuration_from_inifile(hdist_config_filename)
    ctx = Context(logger, hdist_config, args.verbose, arch, env)

    with open('packages.yml') as f:
        package_list = yaml.safe_load(f)

    # Add common dependencies to every package
    packages = {}
    for pkg in package_list:
        if 'deps' not in pkg:
            print("Missing 'deps' in package %s" % pkg['package'], file=sys.stderr)
            return 2

        # Basic default rules for package settings
        if pkg['package'] != 'launcher':
            pkg['deps'].append('launcher')
        if 'provides' not in pkg:
            pkg['provides'] = pkg['package']

    packages = dict((pkg['package'], pkg) for pkg in package_list)

    subset = hpcmp_config.get('packages', packages.keys())
    preferred = dict([(packages[pkgname]['provides'], packages[pkgname])
                      for pkgname in subset])

    # Run over packages and replace deps on virtual packages ("provides")
    # with the ones found in the subset in the config file
    for pkg_name, pkg in packages.items():
        deps = []
        for dep_name in pkg['deps']:
            pref = preferred.get(dep_name, None)
            if pref is not None:
                dep_name = pref['package']
            deps.append(dep_name)
        pkg['deps'] = deps

    subset = complete_dependencies(ctx, packages, subset)

    # For virtual packages, they must be present among the manually
    # selected set to be selected.
    ctx.launcher_id = ctx.build_all(packages, 'launcher')


    packages['profile'] = {'package': 'profile', 'recipe': 'profile',
                           'deps': subset, 'provides': 'profile'}
    profile_aid = ctx.build_all(packages, 'profile')
    profile_path = ctx.build_store.resolve(profile_aid)
    atomic_symlink(profile_path, target_link)
    return 0
