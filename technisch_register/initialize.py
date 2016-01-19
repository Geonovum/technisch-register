from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
import settings as s
from backend import fetch_repo
from utils import load_repos

root = OSFS(s.root_path)
build = root.makeopendir(s.build_path)
build.makedir(s.sources_path)
build.makedir(s.staging_path)
build.makedir(s.register_path)
build.makedir(s.backups_path)

# create production directory
try:
    OSFS(s.production_path)
except ResourceNotFoundError:
    path = s.production_path.split('/')[-2]
    OSFS(s.production_path[:len(s.production_path) - (len(path) + 1)]).makedir(path)

# fetch repos from GitHub
for repo in load_repos(s.repos_path).values():
    fetch_repo(root, sources_path, repo['id'], repo['url'])

# TODO: build the register once