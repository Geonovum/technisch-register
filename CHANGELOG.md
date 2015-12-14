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
