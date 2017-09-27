#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps, loads
from utils import run, cleanup, load_repos
from sys import stdin, exit
import datetime
import backend
import logging
import settings
from queue import FifoSQLiteQueue

root_path = settings.root_path
root = OSFS(root_path)
repos_path = settings.repos_path
source = settings.sources_path
staging_build = settings.staging_path
backups = settings.backups_path
build_path = settings.build_path
register_path = settings.register_path
script_entry_path = settings.script_entry_path
production_path = settings.production_path
assets_path = settings.assets_path

logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

print "\nRunning on %s" % datetime.datetime.now()

# read GitHub's JSON POST payload from stdin
# see ./github-payload.json for an example
payload = load(stdin)

try:
    # published GitHub releases contain an 'action' key, try to retrieve it
    action = payload['action']
except KeyError:
    logging.error("This payload does not carry a release... aborting.")
    exit()

# extract the release type: release or prerelease
initiator = payload['repository']['name'].lower()

queue = FifoSQLiteQueue('queue.db')

if action == 'published':
    # check whether we can start the build.py script
    # i.e. whether another instance isn't already running
    # TODO: rename run to sync_script_running
    if run():
            #backend.build_register ()
            backend.build_register(source, register_path, root, initiator)

            # backend.deploy_register ()
            backend.deploy_production(register_path, backups, script_entry_path, production_path)
    else:
        print "Script is already running... queueing action." 
        queue.push(initiator)
        exit()

while len(queue) > 0:
    initiator = queue.pop()

    backend.build_register(source, register_path, root, initiator)
    backend.deploy_production(register_path, backups, script_entry_path, production_path)

queue.close()
