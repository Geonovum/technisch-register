from fs.osfs import OSFS
from settings import deploy_path, source, staging_build, production_build, backups, repo_path
from backend import fetch_repo
from utils import load_repos

root = OSFS('.')
deploy = root.makeopendir(deploy_path)
deploy.makedir(source)
deploy.makedir(staging_build)
deploy.makedir(production_build)
deploy.makedir(backups)

for repo in load_repos(repo_path).values(): 
    fetch_repo(deploy, source, repo['id'], repo['url'])