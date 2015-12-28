import pytest
from fs.osfs import OSFS
from technisch_register.backend import fetch_repo
from technisch_register.settings import sources_path, register_path, build_path
from os import path as ospath

# install technisch-register to be able to test with 
# pip install -e . in root dir (where setup.py) resides 


class TestBackend:

    @pytest.fixture(scope='session')
    def parameters(self, tmpdir_factory):
        return 'imkl2015', 'https://www.github.com/Geonovum/imkl2015', tmpdir_factory

    def test_fetch_repo_clone(self, parameters):
        initiator, url, tmpdir = parameters

        root = OSFS(str(tmpdir.getbasetemp()))        
        root.makedir(sources_path)

        assert fetch_repo(root, sources_path, initiator, url, build_path) == 'clone'

        assert initiator in root.listdir(ospath.join(build_path, sources_path), dirs_only=True)

    def test_fetch_repo_pull(self, parameters):
        initiator, url, tmpdir = parameters

        root = OSFS(str(tmpdir.getbasetemp()))

        assert fetch_repo(root, sources_path, initiator, url, build_path) == 'pull'

