import psutil

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