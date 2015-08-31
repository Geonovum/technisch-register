from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from subprocess import call
from webpages import create_standard_webpage
import codecs
import time

def build_folders(source, destination_temp, standards, root):
    print "Building register..."

    source_fs = OSFS(source)

    # iterate over all standards in source directory
    for standard in standards:
        print "Processing %s ... " % standard['id']
        standard_fs = source_fs.opendir(standard['id'])

        # list all sub standards of a standard
        artifacts = standard_fs.listdir(dirs_only=True)
        if '.git' in artifacts: artifacts.remove(".git")

        for artifact in artifacts:
            # check whether artifact folder exists in destination_temp 
            if root.exists('%s/%s' % (destination_temp, artifact)) == False:
                root.makedir('%s/%s' % (destination_temp, artifact))
                
            # copy standard folders from source to destination_temp in desired structure
            root.copydir('%s/%s/%s' % (source, standard['id'], artifact),  '%s/%s/%s' % (destination_temp, artifact, standard['id']))

        # create standard HTML page
        html = create_standard_webpage(standard, artifacts)

        # check whether standard folder exists in register root
        if root.exists('%s/%s' % (destination_temp, standard['id'])) == False:
            root.makedir('%s/%s' % (destination_temp, standard['id']))
        
        # write standard HTML page to register/standard/index.html
        with codecs.open('%s/%s/index.html' % (destination_temp, standard['id']), 'w', encoding='utf8') as f:
            f.write(html)

def fetch_repos(root, destination_temp, repos, source):
    print "Fetching repositories..."

    for repo in repos:
        print "Cloning %s in repos/%s" % (repo['url'], repo['id'])
        # explicitely create dir as implicit cration fails on server
        root.makedir('%s/%s' % (destination_temp, repo['id']))
        call('git clone %s %s/%s' % (repo['url'], source, repo['id']), shell=True)

    #TODO: git pull additions into existing repos, clone new ones

def create_staging(destination_temp, destination):
	print 'Copying register to staging...'
	call('rm -rf ../%s/staging' % destination, shell=True)

	# print 'making new directory'
	# print 'mkdir ../%s' % destination
	# call('mkdir ../%s' % destination, shell=True)

	print 'Moving new register'
	call('mv %s ../%s/staging' % (destination_temp, destination), shell=True)
	# root.copydir(destination_temp, '../register/staging')
	# root.removedir(destination_temp, force=True)
	
	call('chmod -R a+rx ../%s' % destination, shell=True)
	# root.removedir(source, force=True)

def put_in_production(destination):
	print "!! === !!"
	print "Putting staging in production"
	# backup current register

	print "Backing up register..."
	call('cp -r ../%s ../backups/%s' % (destination, time.strftime('%Y-%m-%d')), shell=True)

	#copy staging to parent dir
	print "Preparing staging for launch..."
	call('cp -r ../%s/staging ../register-staging' % destination, shell=True)
	call('cp -r ../%s/staging ../register-staging2' % destination, shell=True)

	#rename old register to temp name
	print "Launching staging into production..."
	call('mv ../%s ../register-old' % destination, shell=True)
	
	#rename staging to new register
	call('mv ../register-staging ../%s' % destination, shell=True)
	# call('mkdir ../register/r')
	call('cp -r web/assets ../%s/r' % destination, shell=True)
	print "Staging launched!"
	
	# delelete old register
	print "Removing old register..."
	call('rm -rf ../register-old', shell=True)

	# move current staging to new register
	print "Moving current staging to new production..."
	call('mv ../register-staging2 ../%s/staging' % destination, shell=True)

	# allow Apache to serve files from this dir
	# call('chmod -R a+rx ../%s' % destination, shell=True)