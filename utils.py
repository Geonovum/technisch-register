import psutil
from subprocess import call

def run():
	""" Check if the build.py script is already running.
	Return True if it is not i.e. a new instance may be started.
	Return False if it is i.e. a new instance cannot be started.
	"""

	print "Checking whether somethings is running... "

	num_processes = 0


	# pudb.set_trace()

	for proc in psutil.process_iter():
		pinfo = proc.as_dict(attrs=['name'])

		if pinfo['name'] == 'python.exe' or pinfo['name'] == 'Python':
			builder = proc.as_dict(attrs=['cmdline', 'create_time'])
			if builder['cmdline'][1] == 'build.py':
				num_processes += 1

	# if two intances of build.py are detected 
	# a new script cannot be launched
	if num_processes > 1:
		return False
	else:
		return True

def set_repeat(action):
	# give way to a production call as it will build staging anyway
	if get_repeat() == 'production' and action == 'staging': action = 'production'

	with open('repeat.txt', 'w') as f:
		f.write(action)

def get_repeat():
	with open('repeat.txt', 'r') as f:
		return f.read()

def cleanup(source, destination_temp):
	"""Remove the source and temporary destination folders."""

	# We call the system's rm function because OSFS' removedir function cannot
	# deal with the protected files in each repo's .git folder
	try:
	    print "removing %s" % source    
	    call('rm -rf %s' % (source), shell=True)
	except ResourceNotFoundError: 
	    print "Failed to remove %s... Folder not found." % source

	try:
	    print "removing %s" % destination_temp
	    call('rm -rf %s' % (destination_temp), shell=True)
	except ResourceNotFoundError: 
	    print "Failed to remove %s... Folder not found." % destination_temp


if __name__ == "__main__":
	run()