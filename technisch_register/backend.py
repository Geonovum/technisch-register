from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from subprocess import call
# from webpages import create_standard_webpage
from technisch_register import webpages
from settings import build_path, repos_path, assets_path, cluster_path
from os import path as ospath
from utils import get_artifacts, load_repos, cleanup
import codecs
import time
import logging
from json import load
import shutil

def build(source, build_dir, root, initiator):
    """Builds the register in build_dir/source.

    source is either settings.register_path of setting.staging_path
    """

    logging.info("Sync script started by %s...", initiator)

    # canditate for removal as this is only place it is used
    standards_id, standards = load_repos(repos_path)

    #TODO: move to utils
    clusters_id = {}
    with open(cluster_path) as f:
        clusters = load(f)

        for cluster in clusters:
            clusters_id[cluster['id']] = cluster

    # check if initiator is present in repos.json
    if initiator in standards_id.keys():
        cleanup(build_path, source, build_dir, initiator)
        logging.info("Fetching repo %s..." % initiator)
        fetch_repo(root, source, initiator, standards_id[initiator]['url'], build_path)

        create_zipfile(build_path, source, initiator, root)
        logging.info("Building folders...")
        build_folders(source, build_dir, standards_id[initiator], root, standards_id[initiator]['cluster'], build_path)
        create_infomodel_homepage(root, source, assets_path, build_path, build_dir, standards_id[initiator]['cluster'], standards_id[initiator])

        logging.info("Creating homepagepage...")
        webpages.create_register_homepage(clusters, source, build_dir)

        if standards_id[initiator]['cluster'] != "":
            webpages.create_cluster_overview(standards, source, build_dir, standards_id[initiator]['cluster'], root, assets_path)
    else:
        print "%s is not listed in repos.json... aborting." % initiator
        logging.error("%s is not listed in repos.json... aborting" % initiator)
        exit()
        #TODO: check if repo needs to be removed from repos/

    print "Done!"

def create_zipfile(build_path, source, initiator, root):
    """Create a zipfile with all artifacts of a repository

    """
    path = ospath.join(build_path, source, initiator)
    print path

    # temporary dir for storing ZIPs
    # needed since make_acrhive adds an empty archive 
    # when to-be zipped dir is used as destination dir  
    path_temp = ospath.join(build_path, 'temp')
    root.makedir(ospath.join(path_temp), allow_recreate=True)

    path_temp_zip = ospath.join(path_temp, initiator)
    
    # use explicit absolute paths, needed for tests
    shutil.make_archive(root.getsyspath('.') + path_temp_zip, 'zip', root.getsyspath('.') + path)

    # create the ZIP artefact
    # by moving it from temp dir to zipfile dir
    root.makedir(ospath.join(path, 'zipfile'), recursive=True)
    root.move(path_temp_zip + '.zip', ospath.join(path, 'zipfile', initiator + '.zip'))

def build_folders(sources_path, destination_temp, standard, root, repo_cluster, build_path):
    """Transforms a repo's folder structure to that of the register

    Copies infomodel/artifact/assets to artifact/infomodel/assets
    """

    artifacts = get_artifacts(root, build_path, sources_path, standard)

    for artifact in artifacts:
        # check whether artifact folder exists in destination_temp 
        if (root.exists(ospath.join(build_path, destination_temp, artifact))) == False:
            root.makedir(ospath.join(build_path, destination_temp, artifact), recursive=True)

        # copy standard folders from source to destination_temp in desired structure
        root.copydir(ospath.join(build_path, sources_path, standard['id'], artifact), ospath.join(build_path, destination_temp, artifact, standard['id']))

def create_infomodel_homepage(root, sources_path, assets_path, build_path, destination_temp, repo_cluster, standard):
    """Creates the homepage of an information model and copies to correct location

    e.g. https://register.geostandaarden.nl/brt/top10nl/index.html
    """

    artifacts = get_artifacts(root, build_path, sources_path, standard)

    html = webpages.create_standard_webpage(standard, artifacts, assets_path)

    # copy homepage to register/standard exists if part of cluster
    if repo_cluster == "":
        if root.exists(ospath.join(build_path, destination_temp, standard['id'])) == False:
            root.makedir(ospath.join(build_path, destination_temp, standard['id']))
        # write standard HTML page to register/standard/index.html
        with codecs.open(ospath.join(root.getsyspath('.'), build_path, destination_temp, standard['id'], 'index.html'), 'w', encoding='utf8') as f:
            f.write(html)
    else:
        # check whether register/cluster/exists
        if root.exists(ospath.join(build_path, destination_temp, repo_cluster)) == False:
            root.makedir(ospath.join(build_path, destination_temp, repo_cluster))

        # check whether register/cluster/standard exists
        if root.exists(ospath.join(build_path, destination_temp, repo_cluster, standard['id'])) == False:
            root.makedir(ospath.join(build_path, destination_temp, repo_cluster, standard['id']))
    
        # write standard HTML page to register/cluster/standard/index.html
        with codecs.open(ospath.join(build_path, destination_temp, repo_cluster, standard['id'], 'index.html'), 'w', encoding='utf8') as f:
            f.write(html)

    # copy web assets
    # root.copydir(ospath.join(assets_path, 'web', 'assets'), ospath.join(build_path, destination_temp, 'r'), overwrite=True)
    call('cp -r %s %s' % (ospath.join(assets_path, 'web', 'assets'), ospath.join(root.getsyspath('.'), build_path, destination_temp, 'r')), shell=True)

def fetch_repo(root, source, repo, url, build_path):
    """Clone repos from GitHub to source folder."""

    print "Fetching %s from %s" % (repo, url)

    if root.exists(ospath.join(build_path, source, repo)):
        print "Repo %s exists, issuing a git pull..." % repo
        call('cd %s; git pull' % ospath.join(root.getsyspath('.'), build_path, source, repo), shell=True)
        return 'pull'
    else:
        print "Repo %s does not exist, issuing a git clone..." % repo

        call ('git clone %s %s' % (url, ospath.join(root.getsyspath('.'), build_path, source, repo)), shell=True)
        # call('git clone %s %s/%s > /dev/null 2>&1' % (repo['url'], source, repo['id']), shell=True)

        return 'clone'

def create_staging(staging_path, production_path, build_path):
    """Create a staging version of the register hosted at
    register.geostandaarden.nl/staging
    """

    logging.info("Building staging...")

    production = OSFS(production_path)

    print "Removing current staging..."
    if production.exists(staging_path):
        production.removedir(staging_path, force=True)

    print 'Moving new register to staging...'

    # OSFS cannot copy to arbitrary locations
    call('cp -r %s %s' % (ospath.join(build_path, staging_path), production_path), shell=True)
    
    call('chmod -R a+rx %s' % (ospath.join(production_path, staging_path)), shell=True)

    logging.info("Staging built successfully!")

def create_production(destination, backups, script_entry_path, production_path):
    """Put the staging version to production hosted at 
    register.geostandaarden.nl
    """

    ## TODO: feed this function absolute paths

    print "Building production..."
    logging.info("Building production...")

    production = OSFS(production_path)
    
    # if production.exists(backups) == False:
    #     production.makedir(backups)

    # copy newly baked register/staging to production directory
    # NOTE: only build paths within script_dir are currently supported
    call ('cp -r %s %s' % (ospath.join(build_path, destination), ospath.join(production_path, destination + '-new')), shell=True)
    # production.copydir('%s/%s/%s' % (script_dir, build_path, destination), destination + '-new', overwrite=True)

    if production.exists(destination) == True:
        # server refuses to recursively remove register/staging
        # hence we excplicitly remove symbolic link to staging
        try:
            production.remove('%s/staging/staging' % destination)
        except ResourceNotFoundError:
            print "Warning, %s/staging/staging not found..." % destination

        try:
            production.removedir('%s/staging' % destination)
        except ResourceNotFoundError:
            print "Warning, %s/staging not found..." % destination
        
        backup_dir = time.strftime('%Y-%m-%d-%H-%M-%S')

        # if production.exists('backups/%s' % backup_dir): 
        #     production.removedir('backups/%s' % backup_dir, force=True)
        
        production.copydir(destination, '%s/%s' % (backups, backup_dir), overwrite=True)
        
        try:
            production.movedir(destination, destination + '-old', overwrite=True)
        except ResourceNotFoundError:
            pass

    production.movedir(destination + '-new', destination, overwrite=True)

    # create symbolic link to standalone staging directory
    # fails if production is built first...
    production.makedir('%s/staging' % destination)
    
    call('cd %s; ln -s %s' % (ospath.join(production_path, destination, 'staging'), ospath.join(production_path, 'staging')), shell=True)
    call('cd %s; ln -s %s' % (ospath.join(production_path, destination), ospath.join(script_entry_path, 'log.txt')), shell=True)
    
    try:
        production.removedir(destination + '-old', force=True)
    except ResourceNotFoundError:
        pass

    call('chmod -R a+rx %s/%s' % (production_path, destination), shell=True)

    print "Done building production..."
    logging.info("Production built successfully!")