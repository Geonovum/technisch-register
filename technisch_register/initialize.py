from fs.osfs import OSFS
from settings import root_path, build_path, repos_path, sources_path, staging_path, register_path, backups_path
from backend import fetch_repo
from utils import load_repos

root = OSFS(root_path)
build = root.makeopendir(build_path)
build.makedir(sources_path)
build.makedir(staging_path)
build.makedir(register_path)
build.makedir(backups_path)

for repo in load_repos(repos_path).values(): 
    fetch_repo(root, sources_path, repo['id'], repo['url'])