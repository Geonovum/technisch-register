from fs.osfs import OSFS
from fs.errors import ResourceInvalidError



source = './'
destination = "../"

root = OSFS('./') # 'c:\Users\<login name>' on Windows
root.removedir(destination, force=True)
root.makedir(destination)

# iterate over the contents of root dir
for standard in root.listdir(dirs_only=True):
	
	# skip destination folder
	if standard not in destination:
		print standard
		standard_fs = root.opendir(standard)

		# iterate over dirs in each standard dir
		for sub_standard in standard_fs.listdir(dirs_only=True):
			# skip git dir
			if ".git" not in sub_standard:
				
				# check whether sub_standard folder exists in root
				if root.exists(destination + sub_standard) == False:
					root.makedir(destination + sub_standard)
					
				root.copydir('%s/%s' % (standard, sub_standard),  '%s/%s/%s' % (destination, sub_standard, standard))