# 2016-05-03

- add ZIPping functionality. A zip is added to each standard's directory.

# 2016-01-26

- add documentation that details how to connect GitHub to `technisch-register` on register.geostandaarden.nl.
- enable HTTPS.
- enable continous integration with Travis CI.

# 2016-01-19

- add initialization script that builds the register for the first time after the module has been installed.

# 2015-12-28

- setup a `pytest` testing environment and add first tests.

# 2015-12-23

- add `setuptools` setup script 

# 2015-12-16

 - add clusters and clustering. Standards from a single family are now grouped on the homepage. For example, instead of separate entries for TOP50NL and TOP100NL there is now a single entry for BRT.

# 2015-12-14

- use `git pull` to fetch changes instead of `git clone`-ing all the repositories. Previously the whole register was rebuilt whenever a single repository published a new release. This resulted in long build times and allowed users to publish other users' prereleases to production.    

# 2015-12-08

- add SQLite queue
- add simple logging capabilities

# 2015-11-28

- fix a timeout issue that prevented production/staging builds from finishing. The repo list has grown significantly and the script takes longer to execute than GitHub will wait for a response (30 sec). Instead of letting the script finish, Apache terminates it and the register never gets built. Solution is to execute the script in the background through `subprocess.Popen()` and drown all output so that a response can be sent quickly to GitHub.
- fix issue #27 "breadcrumbs always point to IMGeo"
- each build is backed up separately instead the latest of the day as was previously the case

# 2015-11-17 

- separate `staging` build from `production` build. The staging and production build paths are now completely separate. Building one will not interefere with the other. 
