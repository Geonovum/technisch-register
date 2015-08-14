#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps, loads
from utils import run, set_repeat, get_repeat, cleanup
from sys import stdin
import codecs
import time
import webpages
import backend

def build_staging():
    source = 'repos'
    destination = 'register2'

    cleanup(source, destination)

    root = OSFS('./') # 'c:\Users\<login name>' on Windows
    # root.makedir(source, allow_recreate=True)
    root.makedir(destination, allow_recreate=True)

    # TODO: use this approach to include standards that are not managed on GitHub
    #standards = OSFS(source).listdir(dirs_only=True)
    with open('repos.json') as f:
        standards = load(f)
    
    backend.fetch_repos(root, destination, standards, source)
    backend.build_folders(source, destination, standards, root)
    webpages.create_overview_page(standards, source, destination)
    backend.create_staging(destination)
    backend.remove_temp_dirs(source, destination)

    repeat = get_repeat()
    print "Repeat:", repeat
    set_repeat('none')

    if repeat == 'staging':
        print "Repeating to staging..."
        build_staging()

    elif repeat == 'production':
        print "Repeating to production..."
        build_staging()
        # put_in_production()

    print "Done!"

#if __name__ == "__main__":

# TODO: set running to false when script fails
# TODO: remove working dirs
# TODO: create a cleanup function to store above actions

print "Content-Type: text/html"
print 
print "Running sync script..."

# read release type from GitHub hook
payload = loads(stdin.read())
action = payload['action']
prerelease = payload['release']['prerelease']

if action == 'published':
    if prerelease == True:
        if run():
            print "Building staging..."
            build_staging()
        else:
            set_repeat('staging')
    else:
        if run():
            print "Building production..."
            build_staging()
            # put_in_production()
        else:
            set_repeat('production')