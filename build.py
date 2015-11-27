from subprocess import Popen
from sys import stdin, exit, argv
from os import devnull

print "Content-Type: text/html"
print 

print "Starting sync script..."

if 'verbose' in argv:
	Popen(['python', 'build.py'], stdin=stdin)	
else:
	with open(devnull, 'w') as fp:
		Popen(['python', 'build.py'], stdin=stdin, stdout=fp)

print "Sync script is running..."
print "Check ... for status"

exit()