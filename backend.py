from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from subprocess import call
from webpages import create_standard_webpage
import codecs
import time

def build_folders(source, destination_temp, standards, root):
    """Transform the repos' folder structure to that of the register
    and build HTML pages for each standard.
    """

    print "Building register..."

    source_fs = OSFS(source)

    # iterate over all standards in source directory
    for standard in standards:
        print "Processing %s ... " % standard['id']
        standard_fs = source_fs.opendir(standard['id'])

        # list all artifacts of a standard
        artifacts = standard_fs.listdir(dirs_only=True)
        if '.git' in artifacts: artifacts.remove(".git")

        for artifact in artifacts:
            # check whether artifact folder exists in destination_temp 
            if root.exists('%s/%s' % (destination_temp, artifact)) == False:
                root.makedir('%s/%s' % (destination_temp, artifact))

            # copy standard folders from source to destination_temp in desired structure
            root.copydir('%s/%s/%s' % (source, standard['id'], artifact),  '%s/%s/%s' % (destination_temp, artifact, standard['id']))

        # TODO: put in own function
        # create standard HTML page
        html = create_standard_webpage(standard, artifacts)

        # check whether standard folder exists in register root
        if root.exists('%s/%s' % (destination_temp, standard['id'])) == False:
            root.makedir('%s/%s' % (destination_temp, standard['id']))
        
        # write standard HTML page to register/standard/index.html
        with codecs.open('%s/%s/index.html' % (destination_temp, standard['id']), 'w', encoding='utf8') as f:
            f.write(html)

def fetch_repos(root, destination_temp, repos, source):
    """Clone repos from GitHub to source folder."""

    print "Fetching repositories..."

    for repo in repos:
        print "Cloning %s in repos/%s" % (repo['url'], repo['id'])
        
        # explicitely create dir as implicit creation fails on server
        # NOTE: possible duplicate with line 34!
        root.makedir('%s/%s' % (destination_temp, repo['id']))
        
        call('git clone %s %s/%s' % (repo['url'], source, repo['id']), shell=True)

    #TODO: use git pull instead of git clone to fetch updates

def create_staging(staging_build):
    """Create a staging version of the register hosted at
    register.geostandaarden.nl/staging
    """

    # TODO invoke build_folders from here

    # staging moet een dir hoger zitten om op  
    # register.geostandaarden.nl/staging
    # beshickbaar te zijn    

    print "Removing current staging..."
    call('rm -rf ../%s' % staging_build, shell=True)

    print 'Moving new register to staging...'
    # TODO rename destination_temp to staging_build
    # call('mv %s staging' % staging_build, shell=True)
    call('mv %s ../' % staging_build, shell=True)
    
    call('chmod -R a+rx ../%s' % staging_build, shell=True)

def create_production(build_dir, backups):
    """Put the staging version to production hosted at 
    register.geostandaarden.nl
    """

    print "Building production..."

    deploy = OSFS('..')
    
    if deploy.exists(backups) == False:
        deploy.makedir(backups)

    deploy.movedir('technisch-register/%s' % build_dir, 'register-new', overwrite=True)

    if deploy.exists('register') == True:
        deploy.copydir('register', 'backups/%s' % time.strftime('%Y-%m-%d'), overwrite=True)
        deploy.movedir('register', 'register-old', overwrite=True)

    deploy.movedir('register-new', 'register', overwrite=True)
    deploy.removedir('register-old', force=True)