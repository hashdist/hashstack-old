from __future__ import print_function

import sys
import os
import subprocess
from os.path import join as pjoin
from glob import glob
import traceback
import textwrap
from pprint import pprint

from hashdist.deps import yaml
from hashdist.core import (load_configuration_from_inifile, SourceCache,
        BuildStore, atomic_symlink, make_profile)
from hashdist.core.fileutils import silent_makedirs
from hashdist.hdist_logging import Logger, DEBUG, INFO

from . import recipes as recipes_mod

try:
    import argparse
except ImportError:
    from hashdist.deps import argparse

class Context(object):
    def __init__(self, logger, config, verbose, arch, build_env):
        self.config = config
        self.logger = logger
        self.source_cache = SourceCache.create_from_config(config, logger, create_dirs=True)
        self.build_store = BuildStore.create_from_config(config, logger, create_dirs=True)
        self.arch = arch
        self.build_env = build_env
        self.built = {}
        self.imports_cache = {}

    def get_artifact_id(self, name):
        return self.built[name]['id']

    def build_all(self, packages, root_name):
        built = self.built # { name : dep_spec }
        imports_cache = self.imports_cache
        # depth-first traversal

        def visit(name):
            # returns: dep_spec, that is, dict(ref=..., id=...)
            if name in built:
                return built[name], imports_cache[name]
            pkg = packages[name]
            imports = [] # the imports to build this package

            all_deps = complete_dependencies_stable_order(self, packages, [name])

            for dep in all_deps:
                if dep == name:
                    continue
                spec, _ = visit(dep)
                imports.append(spec)
            artifact_id = build_package(self, pkg, imports)
            dep_spec = {'ref': pkg['provides'].upper(), 'id': artifact_id}
            built[name] = dep_spec
            imports_cache[name] = imports
            return dep_spec, imports

        dep_spec, imports = visit(root_name)
        return dep_spec['id'], imports


def download_sources(ctx, pkg):
    """
    Download source code for a given package
    """
    ctx.logger.info('Downloading sources for %s' % pkg['package'])
    ctx.source_cache.fetch(pkg['url'], pkg['key'], pkg['package'])


def build_package(ctx, pkg, imports):
    # Basic structure.
    # Make sure to deep-copy imports as we may modify it.
    imports = [dict(x) for x in imports]
    commands = []
    buildspec = dict(name=pkg['package'],
                     version='n',
                     build={"import": imports, "commands": commands},
                     on_import=[])
    for key in sorted(ctx.build_env.keys()):
        commands.append({"set": key, "value": ctx.build_env[key]})

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

def complete_dependencies_stable_order(ctx, packages, subset):
    """
    Given a package database `packages` and a list of package names `subset`,
    return `subset` extended so that all ultimate dependencies are included.

    Visits packages ordering first by dependency structure, then
    alphabetically, so that for a given input the output is always the same.
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
            for dep in sorted(pkg.get('deps', [])):
                search(dep)
            visited.add(pkgname)
            result.append(pkgname)
    for root in sorted(subset):
        search(root)
    return result

def create_activate_script(env_path):
    f = open(os.path.join(env_path, "bin", "activate"), "w")
    f.write("""\
ENV_PATH=%s
export PATH=$ENV_PATH/bin:$PATH
echo "Path set. Your \$PATH="
echo $PATH
""" % env_path)

def system_lib(name):
    if name == "":
        return True
    system_libs = [
            "libm",
            "libpthread",
            "libdl",
            "librt",
            "libnsl",

            # linux
            "linux-vdso",

            # gcc
            "libstdc++",
            "libgfortran",
            "libquadmath",
            "libgcc_s",

            # libc
            "libc",
            "libutil",

            # X11
            "libX11",
            "libXau",
            "libXext",
            "libxcb",
            "libXdmcp",
            ]

    for lib in system_libs:
        if name.startswith(lib + ".so"):
            return True
    return False

def check_lib(filename, artifact_path):
    s = subprocess.check_output(["ldd", filename])
    lines = s.split("\n")
    # Fill the libs_dict with library names, paths and addresses
    libs_dict = {}
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if "=>" in line:
            lib, rest = line.split("=>")
        else:
            lib = ""
            rest = line
        rest = rest.strip()
        idx = rest.rfind(" ")
        if idx == -1:
            path = ""
            address = rest
        else:
            path = rest[:idx]
            address = rest[idx:]

        lib = lib.strip()
        path = path.strip()
        address = address.strip()
        libs_dict[lib] = (path, address)

    for lib in libs_dict:
        if system_lib(lib):
            continue
        path, address = libs_dict[lib]
        if path.startswith(artifact_path):
            # Our lib
            continue
        print("Lib:", filename)
        print(lib, path, address)
        print()

def check_libs(artifact_path):
    s = subprocess.check_output(["find", "-L", "local/", "-name", "*.so*"])
    libs = s.split()
    for lib in libs:
        check_lib(lib, artifact_path)

def main(logger, hdist_config_filename):
    # Parse arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    #argparser.add_argument('arch', help='e.g., "linux"')
    #argparser.add_argument('subset', nargs='*', help='only attempt to build packages given '
    #                       '(+ their dependencies)')
    argparser.add_argument('-c', '--copy', help='Create a copy of the profile')
    argparser.add_argument('--check-libs', action="store_true", help='Check .so libraries')
    args = argparser.parse_args()

    with open('config.yml') as f:
        hpcmp_config = yaml.safe_load(f)


    env = {'PATH': ':'.join(hpcmp_config['PATH'])}
    arch = hpcmp_config['arch']
    target_link = 'local'
    
    # Set up Hashdist components, configured by ./hdistconfig
    hdist_config = load_configuration_from_inifile(hdist_config_filename)
    ctx = Context(logger, hdist_config, args.verbose, arch, env)

    if args.check_libs:
        artifact_path = ctx.config["builder/artifacts"]
        check_libs(artifact_path)
        return 0

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

    subset = complete_dependencies_stable_order(ctx, packages, subset)

    # For virtual packages, they must be present among the manually
    # selected set to be selected.
    ctx.launcher_id, imports = ctx.build_all(packages, 'launcher')


    packages['profile'] = {'package': 'profile', 'recipe': 'profile',
                           'deps': subset, 'provides': 'profile'}
    profile_aid, imports = ctx.build_all(packages, 'profile')
    profile_path = ctx.build_store.resolve(profile_aid)
    atomic_symlink(profile_path, target_link)

    if args.copy:
        virtuals = {}
        make_profile(logger, ctx.build_store, imports,
                args.copy, virtuals, hdist_config)
        create_activate_script(args.copy)

    return 0
