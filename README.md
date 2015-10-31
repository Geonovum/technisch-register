#### dependencies

* https://pypi.python.org/pypi/fs/0.5.2
* BeautifulSoup 4
* psutil

Install these through e.g. `pip` as

    pip install fs beautifulsoup4 psutil

#### running

The script reads a GitHub JSON payload from `stdin`. To use it locally run

    cat github-payload.json | python build.py