#!/usr/bin/python

from subprocess import Popen, PIPE
from sys import stdin
import json

payload = stdin.read()

if json.loads(payload)['release']['prerelease']:
    environment = 'staging'
else:
    environment = 'production'

p = Popen(['/usr/bin/python', '/var/www/geostandaarden/{}/technisch-register/technisch_register/build.py'.format(environment)], stdin=PIPE)
p.communicate(input=payload)
