#!/bin/bash

set -v

# prevent accidental removal of settings.py
if [ ! -f technisch_register/settings.py ]
then
	cp ci/settings.py technisch_register/settings.py
fi

pip install .
