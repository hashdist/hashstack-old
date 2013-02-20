import sys
import os
import subprocess
from subprocess import Popen, check_call, CalledProcessError, PIPE

def get_hdist_config_filename():
    return _hdist_config_filename

def fetch_hashdist(hashdist_path, hashdist_commit):
    if os.path.exists(hashdist_path):
        p = Popen(['git', 'rev-parse', 'HEAD'], cwd=hashdist_path, stdout=PIPE)
        out, err = p.communicate()
        if p.wait() != 0:
            raise CalledProcessError("git rev-parse did not work")
        if out.strip() != hashdist_commit:
            sys.stderr.write('Need to update Hashdist...\n')
            # fetch correct version
            subprocess.check_call(['git', 'checkout', 'master'], cwd=hashdist_path)
            subprocess.check_call(['git', 'pull', 'origin', 'master'], cwd=hashdist_path)
            try:
                subprocess.check_call(['git', 'branch', '-D', 'auto'], cwd=hashdist_path,
                                      stderr=PIPE)
            except subprocess.CalledProcessError:
                pass
            subprocess.check_call(['git', 'checkout', '-b', 'auto', hashdist_commit], cwd=hashdist_path)
    else:
        sys.stderr.write("Need to fetch Hashdist...\n")
        subprocess.check_call(['git', 'clone', 'git://github.com/hashdist/hashdist.git', hashdist_path])
        subprocess.check_call(['git', 'checkout', '-b', 'auto', hashdist_commit], cwd=hashdist_path)
    

def setup(root_dir):
    global _hdist_config_filename
    
    # Rest of builder assume the python-hpcmp dir is the cwd
    os.chdir(root_dir)

    _hdist_config_filename = os.path.abspath('hdistconfig')

    # If HASHDIST is set, we are in development mode and we use the Hashdist provided.
    # Otherwise, fetch the correct hashdist into the 'hashdist' subfolder
    hashdist_path = os.environ.get('HASHDIST', None)
    if hashdist_path is None:
        with open('hashdist-version') as f:
            hashdist_commit = f.read().strip()
        hashdist_path = os.path.realpath('_hashdist')
        fetch_hashdist(hashdist_path, hashdist_commit)
    sys.path.insert(0, hashdist_path)

