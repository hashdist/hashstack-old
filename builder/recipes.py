# builder.py calls functions in this file names ${recipe}_recipe, where ${recipe}
# is taken from packages.yml
import os

def add_profile_install(build_spec):
    artifact_spec_file = {
        "target": "$ARTIFACT/artifact.json",
        "object": {
            "install": {
                "script": [["@hdist", "create-links", "--key=install/links", "artifact.json"]],
                "links": [{"action": "symlink",
                           "select": "$ARTIFACT/*/**/*",
                           "prefix": "$ARTIFACT",
                           "target": "$PROFILE"}]
                }
            }
        }
    build_spec['files'].append(artifact_spec_file)
    build_spec['build']['script'].insert(0, ['@hdist', 'build-write-files'])


def standard_recipe(ctx, attrs, configfiles, build_spec):
    script = [
        ['cd', 'src'],
        ["CC=/usr/bin/ccache /usr/bin/gcc"],
        ['PYTHONHPC_PREFIX=${ARTIFACT}']
        ]
    if 'configure' in configfiles:
        script += [['sh', '../configure']]
    script += [
        ['make'],
        ['make', 'install']
        ]
    build_spec['build']['script'].append([script]) # make a sub-scope for above comments
    add_profile_install(build_spec)

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
