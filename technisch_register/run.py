#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps, loads
from utils import run, cleanup
from sys import stdin, exit
import codecs
import time
import webpages
import backend
import logging
from settings import repo_path, script_dir, cluster_path
from queue import FifoSQLiteQueue

root = OSFS('./')
source = 'repos'
staging_build = 'staging'
production_build = 'register'
backups = 'backups'

standards_id = {}
with open(repo_path) as f:
    standards = load(f)

    for standard in standards:
        standards_id[standard['id']] = standard

clusters_id = {}
with open(cluster_path) as f:
    clusters = load(f)

    for cluster in clusters:
        clusters_id[cluster['id']] = cluster
        
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def build(source, build_dir, root, initiator):
    logging.info("Sync script started by %s...", initiator)

    # TODO: use this approach to include standards that are not managed on GitHub
    #standards = OSFS(source).listdir(dirs_only=True)
        
    # check if initiator is present in repos.json
    if initiator in standards_id.keys():
        cleanup(source, build_dir, initiator)

        logging.info("Fetching repo %s..." % initiator)
        backend.fetch_repo(root, initiator, standards_id[initiator]['url'], build_dir)
        
        logging.info("Building folders...")
        backend.build_folders(source, build_dir, standards_id[initiator], root, standards_id[initiator]['cluster'])
        
        logging.info("Creating overview page...")
        webpages.create_overview_clusters(clusters, source, build_dir)
        if standards_id[initiator]['cluster'] != "":
            webpages.create_overview_standards(standards, source, build_dir, standards_id[initiator]['cluster'], root)
    else:
        print "%s is not listed in repos.json... aborting." % initiator
        logging.error("%s is not listed in repos.json... aborting" % initiator)
        exit()
        #TODO: check if repo needs to be removed from repos/

    print "Done!"

#if __name__ == "__main__":

# read GitHub's JSON payload from stdin
# see ./github-payload.json for an example
payload = load(stdin)

try:
    # published GitHub releases contain an 'action' key, try to retrieve it
    action = payload['action']
except KeyError:
    print 
    logging.error("This payload does not carry a release... aborting.")
    exit()

# extract the release type: release or prerelease
prerelease = payload['release']['prerelease']
initiator = payload['repository']['name'].lower()

queue = FifoSQLiteQueue('queue.db')

if action == 'published':
    if prerelease == True:
        # check whether we can start the build.py script
        # i.e. whether another instance isn't already running
        if run():
            print "Building staging..."
            build(source, staging_build, root, initiator)
            backend.create_staging(staging_build)
        else:
            print "Script is already running... setting repeat flag to staging..."
            # set_repeat('staging')
            queue.push(initiator, prerelease)
            exit()
    else:
        if run():
            print "Building production..."
            build(source, production_build, root, initiator)
            backend.create_production(production_build, backups, script_dir)
        else:
            print "Script is already running... setting repeat flag to production..."
            # set_repeat('production')
            queue.push(initiator, prerelease)
            exit()

# check whether we need to run script once more
# repeat = get_repeat()

# while repeat != 'none':

while len(queue) > 0:
    initiator, prerelease = queue.pop()

    if prerelease == True:
        print "Repeating staging..."
        build(source, staging_build, root, initiator)
        backend.create_staging(staging_build)
    else:
        print "Repeating production..."
        build(source, production_build, root, initiator)
        backend.create_production(production_build, backups, script_dir)

    # repeat = get_repeat()
queue.close()
