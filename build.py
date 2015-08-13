#!/usr/bin/python

from fs.osfs import OSFS
from json import load, dumps
from os import chmod, environ
import codecs
import time
import webpages
import backend

def run(status):
    # environ['TR_RUNNING'] = 'true'

    status['running'] = True
    with open('status.json', 'w') as f:
        f.write(dumps(status))

    source = 'repos'
    destination = 'register2'

    root = OSFS('./') # 'c:\Users\<login name>' on Windows

    root.makedir(source)
    root.makedir(destination)

    # TODO: use this approach to include standards that are not managed on GitHub
    #standards = OSFS(source).listdir(dirs_only=True)
    with open('repos.json') as f:
        standards = load(f)
    
    backend.remove_source(source)
    backend.fetch_repos(root, destination, standards)
    backend.build_folders(source, destination, standards, root)
    webpages.create_overview_page(standards, source, destination)
    backend.create_staging(destination)

    with open('status.json') as f:
        status = load(f)

    if status['again'] == True:
        status['again'] = False

        with open('status.json', 'w') as f:
            f.write(dumps(status))

        print "Running once more..."
        run(status)
    else:
        status['running'] = False
        with open('status.json', 'w') as f:
            f.write(dumps(status))

#if __name__ == "__main__":

# TODO: set running to false when script fails
# TODO: remove working dirs
# TODO: create a cleanup function to store above actions
with open('status.json') as f:
    status = load(f)

print "Content-Type: text/html"
print 
print "Running sync script..."

if status['running'] == False:
    status['running'] = True
    try:
        run(status)
    except: 
        print "An error ocurred, please inspect the logs... "

elif status['running'] == True:
    status['again'] = True

    with open('status.json', 'w') as f:
        f.write(dumps(status))

print "Queue: %s" % status['again']

# pseudo code for staging to production

# read release type from GitHub hook
# payload = load(stdin)
# action = payload['action']
# prerelease = payload['release']['prerelease']

# if action == 'released'
#     if prerelaease == True:
#        build staging
#     elif:
#        build staging
#        copy staging to production
#        TODO: create stock production i.e. copy assets to a different dir
