#!/usr/bin/python

from subprocess import Popen, STDOUT
from sys import stdin, exit, argv
from os import devnull, path, chdir
from settings import root_path, python_path

# VERSION = '0.5.0'

print "Content-Type: text/html"
print
print "Starting sync script..."

chdir(root_path)

if 'verbose' in argv:
    Popen([python_path, 'run.py'], stdin=stdin)
else:
    with open('output.txt', 'a') as fp:
        # directing stderr to stdout is essential
        # otherwise script waits for Popen to finish
        # and causes request to timeout
        Popen([python_path, path.join(root_path, 'run.py')], stdin=stdin, stdout=fp, stderr=STDOUT)

print "Check https://register.geostandaarden.nl/log.txt for a status report."

exit()