from subprocess import Popen
from sys import stdin
import json

payload = json.load(stdin)
prerelease = payload['release']['prerelease']

if prerelease:
    environment = 'staging'
else:
    environment = 'production'

path = '/var/www/geostandaarden/{}/technisch-register/technisch_register/build.py'.format(environment)
Popen(['/usr/bin/python', path], stdin=stdin)
