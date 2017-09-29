[![Build Status](https://travis-ci.org/Geonovum/technisch-register.svg?branch=master)](https://travis-ci.org/Geonovum/technisch-register)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/Geonovum/technisch-register/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/Geonovum/technisch-register/?branch=master)

A module that automatically syncs geographical information standards managed on GitHub to https://register.geostandaarden.nl

#### documentation

The [Guide for information model owners and maintainers](https://github.com/Geonovum/technisch-register/blob/master/documentatie/Handleiding%20voor%20beheerders%20informatiemodellen.md) [NL] explains how to add information models to GitHub and offer them for tracking to https://register.geostandaarden.nl

The [Guide for registry maintainers](https://github.com/Geonovum/technisch-register/blob/master/documentatie/Handleiding%20voor%20beheerders%20technisch%20register.md) [NL] explains how to setup tracking of new information models by the register.


#### installing

This modules runs on Linux and macOS. You are encouraged to create a `staging` and `production` environment on your server as follows  

1. create your `staging` directory 

        cd /var/www/geostandaarden/
        mkdir staging
    
2. create a virtual environment called e.g. `tr_staging` and activate it

        cd staging
        virtualenv tr_staging
        source tr_staging/bin/activate

3. Clone this repository and install the module in [editable mode](https://pip.pypa.io/en/latest/reference/pip_install/?highlight=editable#editable-installs) with `pip` as

        git clone https://www.github.com/geonovum/technisch-register
        cd technisch-register
        pip install -e ./

    The `-e` flag makes sure that "[any changes you make to the code will immediately apply accross the system](http://stackoverflow.com/a/24000174)". In other words, you don't have to install the module every time you update the code. `pip` will automatically install the project's dependencies (see `setup.py`).
    
4. Switch to the `staging` branch

        git checkout staging

5. Rename `technisch_register/settings-example.py` to `technisch_register/settings.py` and provide the needed paths.   

6. Run `technisch_register/initialize.py` to create the required directories and build the register

        cd technisch_register
        python initialize.py
        
7. Copy `technisch_register/cgi-bin.py` to your server's `cgi-bin` folder, rename it to `build.py` and adapt the paths to `staging` and `production` environments as needed. 

8. Build the `production` environment by following steps 1 - 6 (except 4) while changing all mentions of `staging` to `production`

#### running

The main script is `build.py`. It reads a GitHub JSON payload from `stdin`. Run `build.py` as

    cd technisch_register
    cat github-payload.json | python build.py


#### testing

Install [pytest](http://pytest.org/latest/) and run the tests as

    pip install pytest
    py.test tests/
