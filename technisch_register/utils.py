import psutil
from subprocess import call
from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError

def run():
	""" Check if the build.py script is already running.
	Return True if it is not i.e. a new instance may be started.
	Return False if it is i.e. a new instance cannot be started.
	"""

	print "Checking whether script is running... "

	num_processes = 0


	# pudb.set_trace()

	for proc in psutil.process_iter():
		p_info = proc.as_dict(attrs=['name'])

		p_name = p_info['name']
		if p_name == 'python.exe' or p_name == 'Python' or p_name == 'python':
			builder = proc.as_dict(attrs=['cmdline', 'create_time'])
			if builder['cmdline'][1] == 'run.py':
				print 'found it'
				num_processes += 1

	# if more than one intance of build.py is detected 
	# a new script cannot be launched
	if num_processes > 1:
		return False
	else:
		return True

def cleanup(source, destination_temp, standard):
	"""Remove the source and temporary destination folders."""

	try:
		source_fs = OSFS('%s/%s' % (source, standard))
	except ResourceNotFoundError:
		return None

	destination_fs = OSFS(destination_temp)

	artifacts = source_fs.listdir(dirs_only=True)
	if '.git' in artifacts: artifacts.remove('.git')

	for artifact in artifacts:
		path = '%s/%s' % (artifact, standard)
		if destination_fs.exists(path):
			destination_fs.removedir(path, force=True)

	if destination_fs.exists(standard): destination_fs.removedir(standard, force=True)

if __name__ == "__main__":
	run()
