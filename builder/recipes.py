# builder.py calls functions in this file names ${recipe}_recipe, where ${recipe}
# is taken from packages.yml
import os
from pprint import pprint

def add_profile_install(ctx, pkg_attrs, build_spec):
    if not pkg_attrs.get("profile_install", True):
        return

    rules = []
    build_spec["profile_install"] = {
        "import": [{"ref": "LAUNCHER", "id": ctx.launcher_id}],
        "commands": [{"hit": ["create-links", "$in0"],
                      "inputs": [{"json": rules}]}],
        }

    if pkg_attrs.get("requires_launcher", False):
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
        {"action": "relative_symlink",
         "select": "$ARTIFACT/*/**/*",
         "prefix": "$ARTIFACT",
         "target": "$PROFILE"}
        ]

def standard_recipe(ctx, pkg_attrs, configfiles, build_spec):
    commands = []
    commands += [{"hit": ["build-profile", "push"]}]
    if "configure" in configfiles:
        commands += [{"cmd": ["sh", "../configure"]}]
    commands += [
            {"cmd": ["make"]},
            {"cmd": ["make", "install"]},
            {"hit": ["build-profile", "pop"]},
            {"hit": ["build-postprocess", "--shebang=multiline", "--write-protect"]},
        ]

    build_spec["build"]["env"]["PYTHONHPC_PREFIX"] = "$ARTIFACT"
    build_spec["build"].update({
        "cwd": "src",
        "commands": commands})
    add_profile_install(ctx, pkg_attrs, build_spec)

def pure_make_recipe(ctx, pkg_attrs, configfiles, build_spec):
    build_spec["build"].update({
        "cwd": "src",
        "commands": [
            {"cmd": ["make", "install", "PREFIX=${ARTIFACT}"]},
            {"hit": ["build-postprocess", "--write-protect"]}
            ]
        })
    add_profile_install(ctx, pkg_attrs, build_spec)

def configure_make_recipe(ctx, pkg_attrs, configfiles, build_spec):
    build_spec["build"].update({
        "cwd": "src",
        "commands": [
            {"cmd": ["./configure", "--prefix=${ARTIFACT}"]},
            {"cmd": ["make"]},
            {"cmd": ["make", "install"]},
            {"hit": ["build-postprocess", "--write-protect"]}
            ]
        })
    add_profile_install(ctx, pkg_attrs, build_spec)

def json_multiline(s):
    from textwrap import dedent
    return dedent(s).splitlines()

def distutils_recipe(ctx, pkg_attrs, configure, build_spec):
    build_spec["build"].update({
        "cwd": "src",
        "commands": [
            {"cmd": ["${PYTHON}/bin/python", "$in0"],
             "inputs": [
                 {"text": json_multiline("""\
                    import sys
                    import os
                    from os.path import join as pjoin, pathsep
                    import subprocess
                    env = os.environ
                
                    # need to set up a local site-packages and put it in
                    # PYTHONPATH before launching setup.py to make
                    # setuptools/distribute happy. Finding the path emulates
                    # exactly what distutilswhen used with Unix --prefix
                    pyver = sys.version.split()[0][0:3]
                    site_packages = pjoin('lib', 'python' + pyver, 'site-packages')
                
                    # temporarily until an hashdist issue is fixed
                    python_path = [pjoin(x, site_packages) for x in
                                   env['HDIST_IMPORT_PATHS'].split() + [env['ARTIFACT']]]
                    python_path = python_path[::-1]
                    os.makedirs(python_path[0]) # make the local one to keep setuptools happy
                    env['PYTHONPATH'] = pathsep.join(python_path)
                    
                    # TODO: hashdist.build.exportenviron(), then run below in a new command
                    subprocess.check_call([sys.executable, 'setup.py', 'install', '--prefix=' + env['ARTIFACT']])
                    """)
                  }]},
            {"hit": ["build-postprocess", "--shebang=multiline", "--write-protect"]}
            ]
        })
    add_profile_install(ctx, pkg_attrs, build_spec)

def profile_recipe(ctx, attrs, configfiles, build_spec):
    profile_spec = []
    for dep in attrs['deps']:
        before = ctx.get_before_list(dep)
        profile_spec.append({"id": ctx.get_artifact_id(dep), "before": before})

    # emit command to create profile
    build_spec['build'].update({
        "hit": ["create-profile", "$in0", "$ARTIFACT"],
        "inputs": [
            {'json': profile_spec}
            ]})
