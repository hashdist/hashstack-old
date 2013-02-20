# builder.py calls functions in this file names ${recipe}_recipe, where ${recipe}
# is taken from packages.yml
import os
from pprint import pprint

def add_profile_install(ctx, attrs, build_spec):
    artifact_spec_file = {
        "target": "$ARTIFACT/artifact.json",
        "object": {}
        }
    build_spec['files'].append(artifact_spec_file)
    build_spec['build']['script'].insert(0, {'hdist': ['build-write-files']})

    if not attrs.get('profile_install', True):
        return

    rules = []
    artifact_spec_file['object'] = {
        "install": {
            "import": [{"ref": "LAUNCHER", "id": ctx.launcher_id}],
            "script": [{"hdist": ["create-links", "--key=install/link_rules", "artifact.json"]}],
            "link_rules": rules
            }
        }

    if attrs.get('requires_launcher', False):
        rules += [
            {"action": "launcher",
             "select": "$ARTIFACT/bin/*",
             "target": "$PROFILE",
             "prefix": "$ARTIFACT"},
            {"action": "exclude",
             "select": "$ARTIFACT/bin/*"}
            ]

    rules += [
        {"action": "relative_symlink",
         "select": "$ARTIFACT/lib/python*/site-packages/*",
         "prefix": "$ARTIFACT",
         "target": "$PROFILE",
         "dirs": True},
        {"action": "exclude",
         "select": "$ARTIFACT/lib/python*/site-packages/**/*"},
        {"action": "exclude",
         "select": "$ARTIFACT/bin/*.real"},
        {"action": "relative_symlink",
         "select": "$ARTIFACT/*/**/*",
         "prefix": "$ARTIFACT",
         "target": "$PROFILE"}
        ]

def standard_recipe(ctx, attrs, configfiles, build_spec):
    script = []
    script += [{'hdist': ['build-profile', 'push']}]
    if 'configure' in configfiles:
        script += [{'cmd': ['sh', '../configure']}]
    script += [
        {'cmd': ['make']},
        {'cmd': ['make', 'install']},
        {'hdist': ['build-profile', 'pop']},
        {'hdist': ['build-postprocess', '--shebang=multiline', '--write-protect']},
        ]

    scope = {
        'env': {'PYTHONHPC_PREFIX': '$ARTIFACT'},
        'cwd': 'src',
        'scope': script
        }

    build_spec['build']['script'].append(scope)
    add_profile_install(ctx, attrs, build_spec)

def pure_make_recipe(ctx, attrs, configfiles, build_spec):
    script = [
        {'cmd': ['make', 'install', 'PREFIX=${ARTIFACT}']},
        {'hdist': ['build-postprocess', '--write-protect']},
        ]
    scope = {
        'env': {'PYTHONHPC_PREFIX': '$ARTIFACT'},
        'cwd': 'src',
        'scope': script
        }
    build_spec['build']['script'].append(scope) # make a sub-scope for above comments
    add_profile_install(ctx, attrs, build_spec)

def distutils_recipe(ctx, attrs, configure, build_spec):
    script = [
        {'cmd': ['$PYTHON/bin/python', '-c', 'import sys; print sys.version.split()[0][0:3]', ')'],
         'to_var': 'py_version_short'},
        {'env': {'PYTHONPATH': '$ARTIFACT/lib/python${py_version_short}/site-packages'},
         'cwd': 'src',
         'scope': [
             {'cmd': ['mkdir', '-p', '$ARTIFACT/lib/python${py_version_short}/site-packages']},
             {'cmd': ['${PYTHON}/bin/python', 'setup.py', 'install', '--prefix=${ARTIFACT}']},
             {'hdist': ['build-postprocess', '--shebang=multiline', '--write-protect']},
             ]
         }
        ]
    build_spec['build']['script'] += script
    add_profile_install(ctx, attrs, build_spec)

def profile_recipe(ctx, attrs, configfiles, build_spec):
    # emit 'profile' section in build spec
    profile = []
    for dep in attrs['deps']:
        before = ctx.get_before_list(dep)
        profile.append({"id": ctx.get_artifact_id(dep), "before": before})
    build_spec['profile'] = profile

    # emit command to create profile
    cmd = {"hdist": ["create-profile", "--key=profile", "build.json", "$ARTIFACT"]}
    build_spec['build']['script'].append(cmd)
