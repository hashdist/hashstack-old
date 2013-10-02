#!/usr/bin/env python

import sys
import subprocess

subprocess.check_call(['cygcheck','-c'])

def get_installed_packages():
    packages = subprocess.check_output(['cygcheck','-c', '-d'])
    # split lines on Windows carriage returns
    packages = packages.split('\r\n')
    # header_data
    packages = packages[2:]
    # package name
    packages = [p.split()[0] for p in packages if p]
    return packages
    
if len(sys.argv) > 1:
    cygstack = sys.argv[1]
else:
    cygstack = 'cygstack.txt'

with open(cygstack) as packages:
    # header_data
    packages.readline()
    packages.readline()

    for package_line in packages.readlines():
        installed_packages = get_installed_packages()
        package = package_line.split()[0]
        
        if package in installed_packages:
            print 'already installed', package_line
            continue

        print 'installing', package
        call = ['setup-x86_64.exe', '-q', '-P', package]
        subprocess.check_call(call)
        

