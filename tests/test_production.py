# install technisch-register to be able to test 
# pip install -e . in root dir (where setup.py) resides 

import pytest
from fs.osfs import OSFS
from technisch_register.backend import fetch_repo, build_folders, create_infomodel_homepage, create_zipfile
from technisch_register.settings import assets_path, sources_path, register_path, build_path, staging_path, root_path, repos_path
from os import path as ospath
from subprocess import call
from technisch_register.utils import load_repos

class TestBackend:

    @pytest.fixture(scope='session')
    def root_directory(self, tmpdir_factory):
        return OSFS(str(tmpdir_factory.getbasetemp()))

    @pytest.fixture(scope='session')
    def fetch_repo_parameters(self):
        return 'nen3610', 'https://www.github.com/Geonovum/nen3610'

    def test_fetch_repo_clone(self, fetch_repo_parameters, root_directory):
        """ Test whether a clone request is issue for a non-existing repo """

        initiator, url = fetch_repo_parameters

        root = root_directory
        root.makedir(sources_path)

        assert fetch_repo(root, sources_path, initiator, url, build_path) == 'clone'

        assert initiator in root.listdir(ospath.join(build_path, sources_path), dirs_only=True)

    def test_fetch_repo_pull(self, fetch_repo_parameters, root_directory):
        """ Test whether a pull request is issued for an existing repo """

        initiator, url = fetch_repo_parameters
        root = root_directory

        assert fetch_repo(root, sources_path, initiator, url, build_path) == 'pull'

    def test_create_zipfile(self, root_directory):
        source = sources_path
        initiator = 'nen3610'

        create_zipfile(build_path, source, initiator, root_directory)

        assert root_directory.exists(ospath.join(build_path, source, initiator, 'zipfile', initiator + '.zip'))

    def test_build_folders_staging(self, root_directory):
        """ Checks whether the staging folders have been built successfully"""

        root = root_directory
        standard = load_repos(ospath.join(root_path, repos_path))[0]['nen3610']

        build_folders(sources_path, staging_path, standard, root, '', build_path)

        assert root.exists(ospath.join(build_path, staging_path, 'informatiemodel', 'nen3610'))

    def test_create_infomodel_homepage_staging(self, root_directory):
        root = root_directory

        standard = load_repos(ospath.join(root_path, repos_path))[0]['nen3610']

        create_infomodel_homepage(root, sources_path, assets_path, build_path, staging_path, '', standard)

        assert root.exists(ospath.join(build_path, staging_path, 'nen3610', 'index.html'))