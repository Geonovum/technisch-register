#### dependencies

* https://pypi.python.org/pypi/fs/0.5.2
* BeautifulSoup 4
* psutil
* Bash shell

#### installing

A Bash shell is readily available on Linux and OS X. If you have installed `git` on Windows you can use `Git Bash`. Can't find it? Try http://babun.github.io/ instead.

Install the Python modules through e.g. `easy_install`. Open your shell and enter

    easy_install fs beautifulsoup4 psutil

Rename `settings-example.py` to `settings.py`. 

#### running

On the server the script reads GitHub's JSON payload from `stdin`. To use it locally run `build.py` as

    cat github-payload.json | python build.py

Line 32 of `github-payload.json` determines what the script (`staging` or `production`) should build. Change `prerelease` to `false` to build `production` and vice versa.

#### developing and testing

Uncomment `repo_path = 'repos-dev.json'` in `settings.py` to load a shorter list of repositories.