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

    root = OSFS('./') # 'c:\Users\<login name>' on Windows
    # root.makedir(source, allow_recreate=True)
    root.makedir(destination_temp, allow_recreate=True)

    # TODO: use this approach to include standards that are not managed on GitHub
    #standards = OSFS(source).listdir(dirs_only=True)
    with open('repos.json') as f:
        standards = load(f)
    
    backend.fetch_repos(root, destination_temp, standards, source)
    backend.build_folders(source, destination_temp, standards, root)
    webpages.create_overview_page(standards, source, destination_temp)
    backend.create_staging(destination_temp, destination)
    
    print "Done!"

#if __name__ == "__main__":

# TODO: set running to false when script fails
# TODO: remove working dirs
# TODO: create a cleanup function to store above actions

print "Content-Type: text/html"
print 
print "Running sync script..."

# read release type from GitHub hook
# payload = loads(stdin.read())
payload = load(stdin)
try: 
    action = payload['action']
except KeyError:
    print 'This payload does not carry a release... aborting.'
    exit()

prerelease = payload['release']['prerelease']

if action == 'published':
    if prerelease == True:
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