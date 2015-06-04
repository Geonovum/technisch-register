from fs.osfs import OSFS
from fs.errors import ResourceInvalidError

source = 'repos'
source_fs = OSFS(source)

destination = 'register/'

root = OSFS('./') # 'c:\Users\<login name>' on Windows
root.removedir(destination, force=True)
root.makedir(destination)

# iterate over the contents of root dir
for standard in source_fs.listdir(dirs_only=True):
	
	# skip destination folder
	if standard not in destination:
		print standard
		standard_fs = source_fs.opendir(standard)

		# iterate over dirs in each standard dir
		for sub_standard in standard_fs.listdir(dirs_only=True):
			# skip git dir
			if ".git" not in sub_standard:
				# check whether sub_standard folder exists in root
				if root.exists(destination + sub_standard) == False:
					root.makedir(destination + sub_standard)
					
				root.copydir('%s/%s/%s' % (source, standard, sub_standard),  '%s/%s/%s' % (destination, sub_standard, standard))