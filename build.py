#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps, loads
from utils import run, set_repeat, get_repeat, cleanup
from sys import stdin, exit
import codecs
import time
import webpages
import backend
from settings import repo_path 

root = OSFS('./')
source = 'repos'
staging_build = 'staging'
production_build = 'register'
backups = 'backups'

def build(source, build_dir, root):
    set_repeat('none')

    cleanup(source, build_dir)
    root.makedir(build_dir, allow_recreate=True)

    # TODO: use this approach to include standards that are not managed on GitHub
    #standards = OSFS(source).listdir(dirs_only=True)
    
    with open(repo_path) as f:
        standards = load(f)
    
    backend.fetch_repos(root, build_dir, standards, source)
    backend.build_folders(source, build_dir, standards, root)
    # TODO: webpages.create_standard_page()
    webpages.create_overview_page(standards, source, build_dir)

    print "Done!"

#if __name__ == "__main__":

print "Content-Type: text/html"
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
            build(source, staging_build, root)
            backend.create_staging(staging_build)
        else:
            print "Script is already running... setting repeat flag to staging..."
            set_repeat('staging')
            exit()
    else:
        if run():
            print "Building production..."
            build(source, production_build, root)
            backend.create_production(production_build, backups)
        else:
            print "Script is already running... setting repeat flag to production..."
            set_repeat('production')
            exit()

# check whether we need to run script once more
repeat = get_repeat()

while repeat != 'none':
    if repeat == 'staging':
        print "Repeating staging..."
        build(source, staging_build, root)
        backend.create_staging(staging_build)
    elif repeat == 'production':
        print "Repeating production..."
        build(source, production_build, root)
        backend.create_production(production_build, backups)

    repeat = get_repeat()
