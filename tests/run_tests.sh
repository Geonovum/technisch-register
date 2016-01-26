#!/bin/bash

if [ ! -f technisch_register/settings.py ]
then
	cp technisch_register/settings-travis.py technisch_register/settings.py
fi

py.test
