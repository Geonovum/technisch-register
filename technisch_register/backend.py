from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from subprocess import call
# from webpages import create_standard_webpage
from technisch_register import webpages
from settings import build_path, repos_path, sources_path, assets_path, cluster_path, root_path, register_path, backups_path, production_path
from os import path as ospath
from utils import get_artifacts, load_repos, cleanup
import codecs
import time
import logging
from json import load
import shutil


def build_register(initiator):
    """Builds the register in build_dir/sources_path."""

    root = OSFS(root_path)

    logging.info("Sync script started by %s...", initiator)

    # canditate for removal as this is only place it is used
    standards_id, standards = load_repos(repos_path)

    #TODO: move to utils
    clusters_id = {}
    with open(cluster_path) as f:
        clusters = load(f)

        for cluster in clusters:
            clusters_id[cluster['id']] = cluster

    # TODO: move to run.py
    if initiator in standards_id.keys():
        cleanup(initiator)
        
        logging.info("Fetching repo %s..." % initiator)
        fetch_repo(root, initiator, standards_id[initiator]['url'])

        # create_zipfile(initiator, root)
        
        logging.info("Building folders...")
        build_folders( standards_id[initiator], root, standards_id[initiator]['cluster'])
        
        create_infomodel_homepage(root, standards_id[initiator]['cluster'], standards_id[initiator])

        logging.info("Creating homepagepage...")
        webpages.create_register_homepage(clusters)

        if standards_id[initiator]['cluster'] != "":
            webpages.create_cluster_overview(standards, standards_id[initiator]['cluster'], root)
    else:
        print "%s is not listed in repos.json... aborting." % initiator
        logging.error("%s is not listed in repos.json... aborting" % initiator)
        exit()
        #TODO: check if repo needs to be removed from repos/

    print "Done!"


def create_zipfile(initiator, root):
    """Create a zipfile with all artifacts of a repository

    """
    path = ospath.join(build_path, sources_path, initiator)
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
    root.makedir(ospath.join(path, 'zipfile'), recursive=True, allow_recreate=True)
    root.move(path_temp_zip + '.zip', ospath.join(path, 'zipfile', initiator + '.zip'), overwrite=True)


def build_folders(standard, root, repo_cluster):
    """Transforms a repo's folder structure to that of the register

    Copies infomodel/artifact/assets to artifact/infomodel/assets
    """

    artifacts = get_artifacts(root, build_path, sources_path, standard)

    for artifact in artifacts:
        # check whether artifact folder exists in destination_temp 
        if (root.exists(ospath.join(build_path, register_path, artifact))) == False:
            root.makedir(ospath.join(build_path, register_path, artifact), recursive=True)

        # copy standard folders from source to destination_temp in desired structure
        root.copydir(ospath.join(build_path, sources_path, standard['id'], artifact), ospath.join(build_path, register_path, artifact, standard['id']))


def create_infomodel_homepage(root, repo_cluster, standard):
    """Creates the homepage of an information model and copies to correct location

    e.g. https://register.geostandaarden.nl/brt/top10nl/index.html
    """

    artifacts = get_artifacts(root, build_path, sources_path, standard)

    html = webpages.create_standard_webpage(standard, artifacts, assets_path)

    # copy homepage to register/standard exists if part of cluster
    if repo_cluster == "":
        if root.exists(ospath.join(build_path, register_path, standard['id'])) == False:
            root.makedir(ospath.join(build_path, register_path, standard['id']))
        # write standard HTML page to register/standard/index.html
        with codecs.open(ospath.join(root.getsyspath('.'), build_path, register_path, standard['id'], 'index.html'), 'w', encoding='utf8') as f:
            f.write(html)
    else:
        # check whether register/cluster/exists
        if root.exists(ospath.join(build_path, register_path, repo_cluster)) == False:
            root.makedir(ospath.join(build_path, register_path, repo_cluster))

        # check whether register/cluster/standard exists
        if root.exists(ospath.join(build_path, register_path, repo_cluster, standard['id'])) == False:
            root.makedir(ospath.join(build_path, register_path, repo_cluster, standard['id']))
    
        # write standard HTML page to register/cluster/standard/index.html
        with codecs.open(ospath.join(build_path, register_path, repo_cluster, standard['id'], 'index.html'), 'w', encoding='utf8') as f:
            f.write(html)

    # copy web assets
    # root.copydir(ospath.join(assets_path, 'web', 'assets'), ospath.join(build_path, register_path, 'r'), overwrite=True)
    call('cp -r %s %s' % (ospath.join(assets_path, 'web', 'assets'), ospath.join(root.getsyspath('.'), build_path, register_path, 'r')), shell=True)


def fetch_repo(root, repo, url):
    """Clone repos from GitHub to source folder."""

    print "Fetching %s from %s" % (repo, url)

    if root.exists(ospath.join(build_path, sources_path, repo)):
        print "Repo %s exists, issuing a git pull..." % repo
        status = call('cd %s; git reset --hard; git pull' % ospath.join(root.getsyspath('.'), build_path, sources_path, repo), shell=True)
        return 'pull'
    else:
        print "Repo %s does not exist, issuing a git clone..." % repo



        status = call ('git clone %s %s' % (url, ospath.join(root.getsyspath('.'), build_path, sources_path, repo)), shell=True)
        # call('git clone %s %s/%s > /dev/null 2>&1' % (repo['url'], source, repo['id']), shell=True)

        return 'clone'

def deploy_register():
    """Put the staging version to production hosted at 
    register.geostandaarden.nl
    """

    ## TODO: feed this function absolute paths

    print "Deploying production..."
    logging.info("Deploying production...")

    production = OSFS(production_path)

    # NOTE: only build paths within script_dir are currently supported
    call ('cp -r %s %s' % (ospath.join(build_path, register_path), ospath.join(production_path, register_path + '-new')), shell=True)

    if production.exists(register_path):
        backup_dir = time.strftime('%Y-%m-%d-%H-%M-%S')

        production.copydir(register_path, '%s/%s' % (backups_path, backup_dir), overwrite=True)
        
        try:
            production.movedir(register_path, register_path + '-old', overwrite=True)
        except ResourceNotFoundError:
            pass

    production.movedir(register_path + '-new', register_path, overwrite=True)

    try:
        production.removedir(register_path + '-old', force=True)
    except ResourceNotFoundError:
        pass

    call('chmod -R a+rx %s/%s' % (production_path, register_path), shell=True)

    logging.info("Production built successfully!")