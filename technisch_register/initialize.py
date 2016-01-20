from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
import settings as s
from backend import fetch_repo, create_production, build
from utils import load_repos

root_fs = OSFS(s.root_path)
build_fs = root_fs.makeopendir(s.build_path)
build_fs.makedir(s.sources_path)
build_fs.makedir(s.staging_path)
build_fs.makedir(s.register_path)
build_fs.makedir(s.backups_path)

# create production directory
try:
    OSFS(s.production_path)
except ResourceNotFoundError:
    path = s.production_path.split('/')[-2]
    OSFS(s.production_path[:len(s.production_path) - (len(path) + 1)]).makedir(path)

# fetch repos from GitHub
for repo in load_repos(s.repos_path)[0].values():
    print 'Fetching %s for the first time' % repo['id']
    fetch_repo(root_fs, s.sources_path, repo['id'], repo['url'], s.build_path)
    build(s.sources_path, s.register_path, root_fs, repo['id'])

create_production(s.register_path, s.backups_path, s.script_entry_path, s.production_path)