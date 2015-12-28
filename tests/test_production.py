import pytest
from fs.osfs import OSFS
from technisch_register.backend import fetch_repo
from technisch_register.settings import sources_path, register_path, build_path
from os import path as ospath

# install technisch-register to be able to test with 
# pip install -e . in root dir (where setup.py) resides 


class TestBackend:

    @pytest.fixture(scope='session')
    def root_directory(self, tmpdir_factory):
        return tmpdir_factory

    @pytest.fixture(scope='session')
    def fetch_repo_parameters(self):
        return 'imkl2015', 'https://www.github.com/Geonovum/imkl2015'

    def test_fetch_repo_clone(self, fetch_repo_parameters, root_directory):
        initiator, url = fetch_repo_parameters
        tmpdir = root_directory

        root = OSFS(str(tmpdir.getbasetemp()))        
        root.makedir(sources_path)

        assert fetch_repo(root, sources_path, initiator, url, build_path) == 'clone'

        assert initiator in root.listdir(ospath.join(build_path, sources_path), dirs_only=True)

    def test_fetch_repo_pull(self, fetch_repo_parameters, root_directory):
        initiator, url = fetch_repo_parameters
        tmpdir = root_directory

        root = OSFS(str(tmpdir.getbasetemp()))

        assert fetch_repo(root, sources_path, initiator, url, build_path) == 'pull'


