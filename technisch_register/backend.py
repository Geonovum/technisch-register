from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from subprocess import call
from webpages import create_standard_webpage
from settings import deploy_path
import codecs
import time
import logging

def build_folders(source, destination_temp, standard, root, repoCluster):
    """Transform the repos' folder structure to that of the register
    and build HTML pages for each standard.
    """

    source_fs = OSFS(source)

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

    html = create_standard_webpage(standard, artifacts)

    # check whether model is part of a cluster
    if repoCluster == "":
        # check whether register/standard exists
        if root.exists('%s/%s' % (destination_temp, standard['id'])) == False:
            root.makedir('%s/%s' % (destination_temp, standard['id']))
        # write standard HTML page to register/standard/index.html
        with codecs.open('%s/%s/index.html' % (destination_temp, standard['id']), 'w', encoding='utf8') as f:
            f.write(html)       
        
    
    else:
        # check whether register/cluster/exists
        if root.exists('%s/%s' % (destination_temp, repoCluster)) == False:
            root.makedir('%s/%s' % (destination_temp, repoCluster))
        # check whether register/cluster/standard exists
        if root.exists('%s/%s/%s' % (destination_temp, repoCluster, standard['id'])) == False:
            root.makedir('%s/%s/%s' % (destination_temp, repoCluster, standard['id']))
    
        # write standard HTML page to register/cluster/standard/index.html
        with codecs.open('%s/%s/%s/index.html' % (destination_temp, repoCluster, standard['id']), 'w', encoding='utf8') as f:
            f.write(html)

    # copy web assets
    root.copydir('web/assets', '%s/r' % destination_temp, overwrite=True)

def fetch_repo(root, source, repo, url):
    """Clone repos from GitHub to source folder."""

    print "Fetching %s from %s" % (repo, url)

    if root.exists('repos/%s' % repo):
        print "Repo %s exists, issuing a git pull..." % repo
        call('cd %s/%s/%s; git pull' % (root.getsysypath('.'), source, repo), shell=True)
    else:
        print "Repo %s does not exist, issuing a git clone..." % repo

        # explicitely create dir as implicit creation fails on server
        # root.makedir('%s/%s' % (destination_temp, repo))
        # call('cd repos; git clone %s %s' % (url, repo), shell=True)
        call('git clone %s %s/%s/%s' % (url, root.getsyspath('.'), source, repo), shell=True)
        # call('git clone %s %s/%s > /dev/null 2>&1' % (repo['url'], source, repo['id']), shell=True)

def create_staging(staging_build):
    """Create a staging version of the register hosted at
    register.geostandaarden.nl/staging
    """

    logging.info("Building staging...")

    # TODO invoke build_folders from here

    # staging moet een dir hoger zitten om op  
    # register.geostandaarden.nl/staging
    # beshickbaar te zijn    

    # TODO: user OSFS like in create_production

    print "Removing current staging..."
    call('rm -rf ../%s' % staging_build, shell=True)

    print 'Moving new register to staging...'
    # TODO rename destination_temp to staging_build
    # call('mv %s staging' % staging_build, shell=True)
    
    # call('mv %s ../' % staging_build, shell=True)
    call('cp -r %s ../' % staging_build, shell=True)
    
    call('chmod -R a+rx ../%s' % staging_build, shell=True)

    logging.info("Staging built successfully!")

def create_production(build_dir, backups, script_dir):
    """Put the staging version to production hosted at 
    register.geostandaarden.nl
    """

    print "Building production..."
    logging.info("Building production...")

    deploy = OSFS(deploy_path)
    # deploy = OSFS('..')
    
    if deploy.exists(backups) == False:
        deploy.makedir(backups)

    deploy.copydir('%s/%s' % (script_dir, build_dir), 'register-new', overwrite=True)

    if deploy.exists('register') == True:
        # server refuses to recursively remove register/staging
        # hence we excplicitly remove symbolic link to staging
        try:
            deploy.remove('register/staging/staging')
        except ResourceNotFoundError:
            print "Warning, register/staging/staging not found..."

        try:
            deploy.removedir('register/staging')
        except ResourceNotFoundError:
            print "Warning, register/staging not found..."
        
        backup_dir = time.strftime('%Y-%m-%d-%H-%M-%S')

        # if deploy.exists('backups/%s' % backup_dir): 
        #     deploy.removedir('backups/%s' % backup_dir, force=True)
        
        deploy.copydir('register', 'backups/%s' % backup_dir, overwrite=True)
        
        try:
            deploy.movedir('register', 'register-old', overwrite=True)
        except ResourceNotFoundError:
            pass

    deploy.movedir('register-new', 'register', overwrite=True)

    # create symbolic link to standalone staging directory
    # fails if production is built first...
    deploy.makedir('register/staging')
    call('cd ../register/staging; ln -s ../../staging', shell=True)
    call('cd ../register; ln -s ../%s/log.txt' % script_dir  , shell=True)
    
    try:
        deploy.removedir('register-old', force=True)
    except ResourceNotFoundError:
        pass

    call('chmod -R a+rx ../register', shell=True)

    print "Done building production..."
    logging.info("Production built successfully!")
