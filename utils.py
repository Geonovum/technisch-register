import psutil
from subprocess import call

def run():
	num_processes = 0

	for proc in psutil.process_iter():
		pinfo = proc.as_dict(attrs=['name'])

		if pinfo['name'] == 'python.exe':
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
	print "Setting repeat to", action
	with open('repeat.txt', 'w') as f:
		f.write(action)

def get_repeat():
	with open('repeat.txt', 'r') as f:
		return f.read()

def cleanup(source, destination):
	# OSFS' removedir function cannot deal with protected
	# files in each repo's .git folder

	try:
	    print "removing %s" % source    
	    call('rm -rf %s' % (source), shell=True)
	except ResourceNotFoundError: 
	    print "Failed to remove %s... Folder not found." % source

	try:
	    print "removing %s" % destination
	    call('rm -rf %s' % (destination), shell=True)
	except ResourceNotFoundError: 
	    print "Failed to remove %s... Folder not found." % destination
