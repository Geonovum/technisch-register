#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps, loads
from utils import build_script_running, cleanup, load_repos
from sys import stdin, exit
import datetime
import backend
import logging
import settings
from queue import FifoSQLiteQueue

logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

print "\nRunning on %s" % datetime.datetime.now()

# read GitHub's JSON POST payload from stdin
payload = load(stdin)

try:
    # published GitHub releases contain an 'action' key, try to retrieve it
    action = payload['action']
except KeyError:
    logging.error("This payload does not carry a release... aborting.")
    exit()

initiator = payload['repository']['name'].lower()

queue = FifoSQLiteQueue('queue.db')

if action == 'published':
    if not build_script_running():
            backend.build_register(initiator)
            backend.deploy_register()
    else:
        queue.push(initiator)
        exit()

while len(queue) > 0:
    initiator = queue.pop()

    backend.build_register(initiator)
    backend.deploy_register()

queue.close()
