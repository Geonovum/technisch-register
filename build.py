#!/usr/bin/python

from subprocess import Popen, STDOUT
from sys import stdin, exit, argv
from os import devnull

print "Content-Type: text/html"
print 

print "Starting sync script..."

if 'verbose' in argv:
	Popen(['/usr/bin/python', 'run.py'], stdin=stdin)	
else:
	with open(devnull, 'w') as fp:
		Popen(['/usr/bin/python', 'run.py'], stdin=stdin, stdout=fp, stderror=STDOUT)

print "Sync script is running..."
print "Check ... for status"

exit()