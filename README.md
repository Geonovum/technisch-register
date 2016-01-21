This module links GitHub to http://register.geostandaarden.nl


#### dependencies

This module requires a Unix Shell. Linux and OS X have on by default. If you have installed `git` on Windows you can use `Git Bash`. Can't find it? Try http://babun.github.io/ instead.

#### installing

Clone this repository and install the `technisch_register` module in [editable mode](https://pip.pypa.io/en/latest/reference/pip_install/?highlight=editable#editable-installs) in your favourite Unix shell through `pip` as

    git clone https://www.github.com/geonovum/technisch-register
    cd technisch-register
    pip install ./ -e

The `-e` flag makes sure that "[any changes you make to the code will immediately apply accross the system](http://stackoverflow.com/a/24000174)". This is useful when you plan to work on the code and is mandatory if you want to run the tests (see below).

Rename `settings-example.py` to `settings.py` and provide the needed paths.

#### running

The main script is `build.py`. It reads a GitHub JSON payload from `stdin` and builds the register in `staging` or `production` mode. Run `build.py` as

    cat github-payload.json | python build.py

Line 32 of `github-payload.json` determines whether the script should build `staging` or  `production`. Change `prerelease` to `false` to build `production` and vice versa.

#### testing

Install [pytest](http://pytest.org/latest/) and run the tests as

    pip install pytest
    py.test tests/