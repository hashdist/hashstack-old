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
    def __init__(self, config, verbose, arch, build_env):
        self.config = config
        self.logger = logger = Logger(DEBUG if verbose else INFO)
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

            all_deps = complete_dependencies(packages, [name])
            for dep in all_deps:
                if dep == name:
                    continue
                imports.append(visit(dep))

            artifact_id = build_package(self, pkg, imports)
            
            before = [self.get_artifact_id(dep) for dep in pkg['deps']]
            dep_spec = {'ref': name.upper(), 'id': artifact_id, 'before': before}
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
    script = []
    buildspec = dict(name=pkg['package'],
                     version='n',
                     build={'script': script, 'import': imports, 'env': ctx.build_env},
                     files=[])

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
        script.append(["@hdist", "build-unpack-sources"])

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

def complete_dependencies(packages, subset):
    """
    Given a package database `packages` and a list of package names `subset`,
    return `subset` extended so that all ultimate dependencies are included.
    """
    visited = set()
    result = []
    def search(pkgname):
        if pkgname not in visited:
            for dep in packages[pkgname].get('deps', []):
                search(dep)
            visited.add(pkgname)
            result.append(pkgname)
    for root in subset:
        search(root)
    return result

def main():
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
    hdist_config = load_configuration_from_inifile('./hdistconfig')
    ctx = Context(hdist_config, args.verbose, arch, env)
    try:
        with open('packages.yml') as f:
            package_list = yaml.safe_load(f)

        # Add common dependencies to every package
        for pkg in package_list:
            if pkg['package'] in ('launcher,'):
                continue
            pkg['deps'].append('launcher')

        packages = dict((pkg['package'], pkg) for pkg in package_list)


        subset = hpcmp_config.get('packages', packages.keys())
        subset = complete_dependencies(packages, subset)

        ctx.launcher_id = ctx.build_all(packages, 'launcher')


        packages['profile'] = {'package': 'profile', 'recipe': 'profile',
                               'deps': subset}
        profile_aid = ctx.build_all(packages, 'profile')
        profile_path = ctx.build_store.resolve(profile_aid)
        atomic_symlink(profile_path, target_link)
    except:
        if ctx.logger.error_occured:
            sys.exit(127)
        else:
            print
            print "Uncaught exception:"
            traceback.print_exc()
            print
            text = """\
            This exception has not been translated to a human-friendly error
            message, please file an issue at
            https://github.com/hashdist/python-hpcmp2/issues pasting this
            stack trace.
            """
            print textwrap.fill(textwrap.dedent(text), width=78)
