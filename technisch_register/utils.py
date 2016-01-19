import psutil
from subprocess import call
from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from os import path as ospath
from settings import build_path
from json import load

def run():
    """ Check if the build.py script is already running.
    Return True if it is not i.e. a new instance may be started.
    Return False if it is i.e. a new instance cannot be started.
    """

    print "Checking whether script is running... "

    num_processes = 0

    # pudb.set_trace()

    for proc in psutil.process_iter():
        p_info = proc.as_dict(attrs=['name'])

        p_name = p_info['name']
        if p_name == 'python.exe' or p_name == 'Python' or p_name == 'python':
            builder = proc.as_dict(attrs=['cmdline', 'create_time'])
            if builder['cmdline'][1] == 'run.py':
                print 'found it'
                num_processes += 1

    # if more than one intance of build.py is detected 
    # a new script cannot be launched
    if num_processes > 1:
        return False
    else:
        return True

def cleanup(build_path, source, destination_temp, standard):
    """Remove the source and temporary destination folders."""

    try:
        source_fs = OSFS(ospath.join(build_path, source, standard))
    except ResourceNotFoundError:
        return None

    destination_fs = OSFS(ospath.join(build_path, destination_temp))

    artifacts = source_fs.listdir(dirs_only=True)
    if '.git' in artifacts: artifacts.remove('.git')

    for artifact in artifacts:
        path = ospath.join(artifact, standard)
        if destination_fs.exists(path):
            destination_fs.removedir(path, force=True)

    if destination_fs.exists(standard): destination_fs.removedir(standard, force=True)

# candidate for removal as it is used only once
def load_repos(path):
    standards_id = {}

    with open(path) as f:
        standards = load(f)

        for standard in standards:
            standards_id[standard['id']] = standard

    return standards_id, standards

def get_artifacts(root, build_path, sources_path, standard):
    source_fs = OSFS(ospath.join(root.getsyspath('.'),  build_path, sources_path))

    # print "Processing %s ... " % standard['id']
    standard_fs = source_fs.opendir(standard['id'])
    artifacts = standard_fs.listdir(dirs_only=True)
    if '.git' in artifacts: artifacts.remove(".git")

    return artifacts

if __name__ == "__main__":
    run()
