import pytest
from fs.osfs import OSFS
from technisch_register.backend import fetch_repo
from technisch_register.settings import sources_path, register_path, build_path

# install technisch-register to be able to test with 
# pip install -e . in root dir (where setup.py) resides 


class TestBackend:

    @pytest.fixture
    def parameters(self):
        return 'imkl2015', 'https://www.github.com/Geonovum/imkl2015'

    def test_fetch_repo_clone(self, tmpdir, parameters):
        root = OSFS(str(tmpdir))
        initiator, url = parameters

        root.makedir(sources_path)
        root.makedir(register_path)

        fetch_repo(root, sources_path, initiator, url)

        assert initiator in root.listdir(sources_path, dirs_only=True)

    # def test_fetch_repo_pull(self, tmpdir, parameters):
    #     root = OSFS(str(tmpdir))

    #     source, production_build, initiator, url = parameters

    #     root.makedir('%s/%s' % (source, initiator), recursive=True)
    #     root.makedir(production_build)

    #     assert fetch_repo(source, root, initiator, url, production_build) == 0

