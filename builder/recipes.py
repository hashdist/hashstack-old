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
         "select": "$ARTIFACT/lib/python*/site-packages/mpl_toolkits/**/*",
         "prefix": "$ARTIFACT",
         "target": "$PROFILE"},
        {"action": "exclude",
         "select": "$ARTIFACT/lib/python*/site-packages/mpl_toolkits/**/*"},
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

def disable_imports_env(build_spec):
    # Sets "in_env=False" on all imports; useful when one wants to rely on
    # hit build-profile push instead.
    for import_ in build_spec['build']['import']:
        import_['in_env'] = False

def standard_recipe(ctx, pkg_attrs, configfiles, build_spec, postprocess=True):
    create_temp_profile = pkg_attrs.get('create_temp_profile', False)
    commands = build_spec['build']['commands']
    commands += [
        {"set": "PYTHONHPC_PREFIX", "value": "$ARTIFACT"},
        {"chdir": "src"},
        ]
    if create_temp_profile:
        commands += [
            {"hit": ["build-profile", "push"]},
            {"append_path": "PATH", "value": "$ARTIFACT/bin"},
            ]
    if "configure" in configfiles:
        commands += [{"cmd": ["sh", "../configure"]}]
    commands += [
        {"cmd": ["make"]},
        {"cmd": ["make", "install"]}]
    if create_temp_profile:
        commands += [{"hit": ["build-profile", "pop"]}]
    if postprocess:
        commands += [{"hit": ["build-postprocess", "--shebang=multiline", "--write-protect"]}]

    if create_temp_profile:
        disable_imports_env(build_spec)
    add_profile_install(ctx, pkg_attrs, build_spec)

def pure_make_recipe(ctx, pkg_attrs, configfiles, build_spec):
    build_spec["build"]["commands"] += [
        {"chdir": "src"},
        {"cmd": ["make", "install", "PREFIX=${ARTIFACT}"]},
        {"hit": ["build-postprocess", "--write-protect"]}
        ]
    add_profile_install(ctx, pkg_attrs, build_spec)

def configure_make_recipe(ctx, pkg_attrs, configfiles, build_spec):
    build_spec["build"]["commands"] += [
        {"chdir": "src"},
        {"cmd": ["./configure", "--prefix=${ARTIFACT}"]},
        {"cmd": ["make"]},
        {"cmd": ["make", "install"]},
        {"hit": ["build-postprocess", "--write-protect"]}
        ]
    add_profile_install(ctx, pkg_attrs, build_spec)

def bash_script_recipe(ctx, pkg_attrs, configfiles, build_spec,
        postprocess=True):
    create_temp_profile = pkg_attrs.get('create_temp_profile', False)
    commands = build_spec["build"]["commands"]
    if create_temp_profile:
        commands += [{"hit": ["build-profile", "push"]}]
    commands += [
        {"set": "PYTHONHPC_PREFIX", "value": "$ARTIFACT"},
        {"chdir": "src"},
        {"cmd": ["bash", "../bash_script"]}]
    if create_temp_profile:
        commands += [{"hit": ["build-profile", "pop"]}]
    if postprocess:
        commands += [
            {"hit": ["build-postprocess", "--shebang=multiline", "--write-protect"]},
            ]

    if create_temp_profile:
        disable_imports_env(build_spec)
    add_profile_install(ctx, pkg_attrs, build_spec)

def json_multiline(s):
    from textwrap import dedent
    return dedent(s).splitlines()

def python_recipe(ctx, pkg_attrs, configure, build_spec):
    bash_script_recipe(ctx, pkg_attrs, configure, build_spec, postprocess=False)
    # Use the newly built Python to modify artifact.json so that
    # we make the PYTHON_SITE_PACKAGES_REL variable available, which contains,
    # e.g., "lib/python2.7/site-packages"
    build_spec["build"]["commands"] += [
        {"cmd": ["$ARTIFACT/bin/python", "$in0"], "inputs": [
            {"text": json_multiline("""\
            import os, sys, json
            pjoin = os.path.join

            pyver = sys.version.split()[0][0:3]
            site_packages = pjoin('lib', 'python' + pyver, 'site-packages')
            artifact_json = pjoin(os.environ['ARTIFACT'], 'artifact.json')
            with open(artifact_json) as f:
                doc = json.load(f)
            doc['on_import'] += [{'set': 'PYTHON_SITE_PACKAGES_REL', 'value': site_packages}]
            with open(artifact_json, 'w') as f:
                json.dump(doc, f, indent=2, separators=(', ', ' : '), sort_keys=True)
            """)}
            ]},
        {"hit": ["build-postprocess", "--shebang=multiline", "--write-protect"]}
        ]

def distutils_recipe(ctx, pkg_attrs, configure, build_spec):
    unpack_egg = pkg_attrs.get('unpack_egg', False)
    build_spec["build"]["commands"] += [
        # to make setuptools/distribute happy, one must set up a local site-packages
        # and put it in PYTHONPATH before launching setup.py
        {"prepend_path": "PYTHONPATH", "value": "${ARTIFACT}/${PYTHON_SITE_PACKAGES_REL}"},
        {"cmd": ["mkdir", "-p", "${ARTIFACT}/${PYTHON_SITE_PACKAGES_REL}"]},
        {"chdir": "src"},
        ]
    if unpack_egg:
        build_spec["build"]["commands"] += [
            {"cmd": ["$PYTHON/bin/python", "setup.py", "install", "--prefix=.",
                "--single-version-externally-managed", "--root=$ARTIFACT"]},
        ]
    else:
        build_spec["build"]["commands"] += [
            {"cmd": ["$PYTHON/bin/python", "setup.py", "install",
                "--prefix=$ARTIFACT"]},
        ]
    build_spec["build"]["commands"] += [
        {"hit": ["build-postprocess", "--shebang=multiline", "--write-protect"]}
        ]
    build_spec["on_import"] += [
        {"prepend_path": "PYTHONPATH", "value": "${ARTIFACT}/${PYTHON_SITE_PACKAGES_REL}"}
        ]
    add_profile_install(ctx, pkg_attrs, build_spec)

def profile_recipe(ctx, attrs, configfiles, build_spec):
    profile_spec = []
    for dep in attrs['deps']:
        profile_spec.append({"id": ctx.get_artifact_id(dep)})

    # emit command to create profile
    build_spec['build']['commands'] += [{
        "hit": ["create-profile", "$in0", "$ARTIFACT"],
        "inputs": [
            {'json': profile_spec}
            ]}]

def python_bash_script_recipe(ctx, pkg_attrs, configfiles, build_spec):
    create_temp_profile = pkg_attrs.get('create_temp_profile', False)
    commands = build_spec["build"]["commands"]
    if create_temp_profile:
        commands += [{"hit": ["build-profile", "push"]}]
    commands += [
        # to make setuptools/distribute happy, one must set up a local site-packages
        # and put it in PYTHONPATH before launching setup.py
        {"prepend_path": "PYTHONPATH", "value": "${ARTIFACT}/${PYTHON_SITE_PACKAGES_REL}"},
        {"set": "PYTHONHPC_PREFIX", "value": "$ARTIFACT"},
        {"chdir": "src"},
        {"cmd": ["bash", "../bash_script"]}]
    if create_temp_profile:
        commands += [{"hit": ["build-profile", "pop"]}]
    commands += [
        {"hit": ["build-postprocess", "--shebang=multiline", "--write-protect"]},
        ]

    if create_temp_profile:
        disable_imports_env(build_spec)
    build_spec["on_import"] += [
        {"prepend_path": "PYTHONPATH", "value": "${ARTIFACT}/${PYTHON_SITE_PACKAGES_REL}"}
        ]
    add_profile_install(ctx, pkg_attrs, build_spec)


#
# Host system support
#

def debian_recipe(ctx, pkg_attrs, configfiles, build_spec):
    build_spec["on_import"] += [
        {"set": pkg_attrs['package'].upper(),
         "value": "/usr"}
        ]


def hardcode_recipe(ctx, pkg_attrs, configfiles, build_spec):
    build_spec["on_import"] += [
        {"set": pkg_attrs['package'].upper(),
         "value": pkg_attrs['prefix']},
        ]
    for ld in pkg_attrs.get('ld_library_path', []):
        build_spec["on_import"].append({"append_path": "LD_LIBRARY_PATH", 
                                        "value": ld})
    for p in pkg_attrs.get('path', []):
        build_spec["on_import"].append({"append_path": "PATH", 
                                        "value": p})
    for k, v in pkg_attrs.get('vars', {}).iteritems():
        build_spec["on_import"].append({"set": k, "value": v})
