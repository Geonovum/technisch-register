#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps, loads
from utils import run, set_repeat, get_repeat, cleanup
from sys import stdin, exit
import codecs
import time
import webpages
import backend
import logging
from settings import repo_path, script_dir

root = OSFS('./')
source = 'repos'
staging_build = 'staging'
production_build = 'register'
backups = 'backups'

logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def build(source, build_dir, root, initiator):
    logging.info("Sync script started by %s...", initiator)

    set_repeat('none')

    cleanup(source, build_dir)
    root.makedir(build_dir, allow_recreate=True)

    # TODO: use this approach to include standards that are not managed on GitHub
    #standards = OSFS(source).listdir(dirs_only=True)
    
    with open(repo_path) as f:
        standards = load(f)
    
    logging.info("Fetching repos...")
    backend.fetch_repos(root, build_dir, standards, source)
    logging.info("Building folders...")
    backend.build_folders(source, build_dir, standards, root)
    # TODO: webpages.create_standard_page()
    logging.info("Creating overview page...")
    webpages.create_overview_page(standards, source, build_dir)

    print "Done!"

#if __name__ == "__main__":

# read GitHub's JSON payload from stdin
# see ./github-payload.json for an example
payload = load(stdin)

try:
    # published GitHub releases contain an 'action' key, try to retrieve it
    action = payload['action']

except KeyError:
    print 'This payload does not carry a release... aborting.'
    exit()

# extract the release type: release or prerelease
prerelease = payload['release']['prerelease']
initiator = payload['repository']['full_name']

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
            set_repeat('staging')
            exit()
    else:
        if run():
            print "Building production..."
            build(source, production_build, root, initiator)
            backend.create_production(production_build, backups, script_dir)
        else:
            print "Script is already running... setting repeat flag to production..."
            set_repeat('production')
            exit()

# check whether we need to run script once more
repeat = get_repeat()

while repeat != 'none':
    if repeat == 'staging':
        print "Repeating staging..."
        build(source, staging_build, root, initiator)
        backend.create_staging(staging_build)
    elif repeat == 'production':
        print "Repeating production..."
        build(source, production_build, root, initiator)
        backend.create_production(production_build, backups, script_dir)

    repeat = get_repeat()
