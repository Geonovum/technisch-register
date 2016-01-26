[![Build Status](https://travis-ci.org/Geonovum/technisch-register.svg?branch=master)](https://travis-ci.org/Geonovum/technisch-register)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/Geonovum/technisch-register/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/Geonovum/technisch-register/?branch=master)

A module that automatically syncs geographical information standards managed on GitHub to http://register.geostandaarden.nl

#### dependencies

You need a Unix shell to run this module. Linux and OS X have one by default. If you have installed `git` on Windows you can use `Git Bash`. Can't find it? Try [Babun](http://babun.github.io/) instead.

#### installing

1. Clone this repository and install the module in [editable mode](https://pip.pypa.io/en/latest/reference/pip_install/?highlight=editable#editable-installs) with `pip` as

        git clone https://www.github.com/geonovum/technisch-register
        cd technisch-register
        pip install -e ./

    The `-e` flag makes sure that "[any changes you make to the code will immediately apply accross the system](http://stackoverflow.com/a/24000174)". `pip` will automatically install the project's dependencies (see `setup.py`).

2. Rename `technisch_register/settings-example.py` to `technisch_register/settings.py` and provide the needed paths.

3. Create the required directories and build the register

        cd technisch_register
        python initialize.py

#### running

The main script is `build.py`. It reads a GitHub JSON payload from `stdin` and builds the register in `staging` or `production` mode. Run `build.py` as

    cat github-payload.json | python build.py

Line 32 of `github-payload.json` determines whether the script should build `staging` or  `production`. Change `prerelease` to `false` to build `production` and vice versa.

#### testing

Install [pytest](http://pytest.org/latest/) and run the tests as

    pip install pytest
    py.test tests/

#### notes

The code is written on OS X and deployed on Ubuntu. Windows support is shaky at best. 
