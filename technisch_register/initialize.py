from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
import settings as s
from backend import fetch_repo, deploy_register, build_register
from utils import load_repos

root_fs = OSFS(s.root_path)
root_fs.makedir(s.build_path, recursive=True, allow_recreate=True)
build_fs = OSFS(s.build_path)
build_fs.makedir(s.sources_path, allow_recreate=True)
build_fs.makedir(s.register_path, allow_recreate=True)

# create production directory if needed
try:
    production_fs = OSFS(s.production_path)
except ResourceNotFoundError:
    # grab production dir's parent dir
    path = s.production_path.split('/')[-2]
    print path
    production_fs = OSFS(s.production_path[:len(s.production_path) - (len(path) + 1)]).makeopendir(path)
    print production_fs

if production_fs.exists(s.backups_path):
    production_fs.makedir(s.backups_path)

# fetch repos from GitHub
for repo in load_repos(s.repos_path)[0].values():
    print 'Fetching %s for the first time' % repo['id']
    fetch_repo(root_fs, repo['id'], repo['url'])
    build_register(repo['id'])

deploy_register()