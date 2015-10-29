#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps, loads
from utils import run, set_repeat, get_repeat, cleanup
from sys import stdin, exit
import codecs
import time
import webpages
import backend

source = 'repos'
destination_temp = 'register2'
destination = 'register'

def build_staging(source, destination_temp, destination):
    set_repeat('none')

    cleanup(source, destination_temp)

    root = OSFS('./')
    root.makedir(destination_temp, allow_recreate=True)

    # TODO: use this approach to include standards that are not managed on GitHub
    #standards = OSFS(source).listdir(dirs_only=True)
    
    with open('repos.json') as f:
        standards = load(f)
    
    backend.fetch_repos(root, destination_temp, standards, source)
    backend.build_folders(source, destination_temp, standards, root)
    # TODO: webpages.create_standard_page()
    webpages.create_overview_page(standards, source, destination_temp)
    backend.create_staging(destination_temp, destination)
    
    print "Done!"

#if __name__ == "__main__":

print "Content-Type: text/html"
print 
print "Running sync script..."

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

if action == 'published':
    if prerelease == True:
        # check whether we can start the build.py script
        # i.e. whether another instance isn't already running
        if run():
            print "Building staging..."
            build_staging(source, destination_temp, destination)
        else:
            print "Script is already running... setting repeat flag to staging..."
            set_repeat('staging')
            exit()
    else:
        if run():
            print "Building production..."
            build_staging(source, destination_temp, destination)
            backend.put_in_production(destination)
        else:
            print "Script is already running... setting repeat flag to production..."
            set_repeat('production')
            exit()

# check whether we need to run script once more
repeat = get_repeat()

while repeat != 'none':
    if repeat == 'staging':
        print "Repeating staging..."
        build_staging(source, destination_temp, destination)
    elif repeat == 'production':
        print "Repeating production..."
        build_staging(source, destination_temp, destination)
        backend.put_in_production(destination)

    repeat = get_repeat()