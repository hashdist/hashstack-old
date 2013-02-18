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
    build_spec['build']['script'].insert(0, ['@hdist', 'build-write-files'])

    if not attrs.get('profile_install', True):
        return

    rules = []
    artifact_spec_file['object'] = {
        "install": {
            "import": [{"ref": "LAUNCHER", "id": ctx.launcher_id}],
            "script": [["@hdist", "create-links", "--key=install/link_rules", "artifact.json"]],
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
    script = [
        ['cd', 'src'],
        ["CC=/usr/bin/ccache /usr/bin/gcc"],
        ["CCACHE_NODIRECT=1"],
        ['PYTHONHPC_PREFIX=${ARTIFACT}'],
        ['hdist', 'build-profile', 'push'],
        ]
    if 'configure' in configfiles:
        script += [['sh', '../configure']]
    script += [
        ['make'],
        ['make', 'install'],
        ['hdist', 'build-profile', 'pop'],
        ['hdist', 'build-postprocess', '--shebang=multiline', '--write-protect'],
        ]
    build_spec['build']['script'].append([script]) # make a sub-scope for above comments
    add_profile_install(ctx, attrs, build_spec)

def pure_make_recipe(ctx, attrs, configfiles, build_spec):
    script = [
        ['cd', 'src'],
        ['make', 'install', 'PREFIX=${ARTIFACT}'],
        ['hdist', 'build-postprocess', '--write-protect'],
        ]
    build_spec['build']['script'].append([script]) # make a sub-scope for above comments
    add_profile_install(ctx, attrs, build_spec)

def distutils_recipe(ctx, attrs, configure, build_spec):
    script = [
        ['cd', 'src'],
        ['${PYTHON}/bin/python', 'setup.py', 'install', '--prefix=${ARTIFACT}'],
        ['hdist', 'build-postprocess', '--shebang=multiline', '--write-protect'],
        ]
    build_spec['build']['script'].append([script])
    add_profile_install(ctx, attrs, build_spec)

def profile_recipe(ctx, attrs, configfiles, build_spec):
    # emit 'profile' section in build spec
    profile = []
    for dep in attrs['deps']:
        before = ctx.get_before_list(dep)
        profile.append({"id": ctx.get_artifact_id(dep), "before": before})
    build_spec['profile'] = profile

    # emit command to create profile
    cmd = ["hdist", "create-profile", "--key=profile", "build.json", "$ARTIFACT"]
    build_spec['build']['script'].append(cmd)
