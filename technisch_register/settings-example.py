root_path = '/home/username/technisch-register/technisch_register/'
# location of the assets folder (in this case web/)
assets_path = root_path

repos_path = 'repos.json'
cluster_path = 'cluster.json'

# path to build.py, used to link to log.txt
script_entry_path = '/var/www/technisch-register/cgi-bin/'
# path to build directory in which staging and register are built
build_path = '_build'
# path to cloned/pulled GitHub repositories
sources_path = 'repos'

production_path = '/var/www/technisch-register/'
# path to register within build_path and production_path
register_path = 'register'

deployment_path = production_path + register_path

# path to backups directory relative to production_path 
backups_path = 'backups'

# path to Python executable in e.g. a virtual env
python_path = '/home/<username>/<deployment>/virtualenv/bin/python'