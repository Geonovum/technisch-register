#!/bin/bash

set -v

if [ ! -f technisch_register/settings.py ]
then
	cp technisch_register/settings-travis.py technisch_register/settings.py
fi

pwd
ls technisch_register

pip install .

py.test
