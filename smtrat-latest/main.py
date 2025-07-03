import os
import re

from utils.download import download_file, extract_file
from utils.github import get_latest_release
from utils.os import write_to_file, read_version, write_version
from utils.pipeline import prepare_directories, generate_tests

theories = [
    "Core",
    "Ints",
    "Reals",
    "RealInts",
    "Bitvectors"
]

def main():
    owner = 'ths-rwth'
    repo = 'smtrat'
    pattern = re.compile(r'smtrat\.tgz')
    path_to_solver_binary = "./smtrat-static"
    NUM_TESTS = int(os.getenv("NUM_TESTS", 100))
    latest_release = get_latest_release(owner, repo)

    matching_asset = None
    for asset in latest_release['assets']:
        if pattern.match(asset['name']):
            matching_asset = asset
            break

    if not matching_asset:
        print("No matching asset found.")
        return

    latest_version = latest_release['tag_name']
    current_version = read_version(repo)

    local_filename = matching_asset['name']
    download_file(matching_asset['browser_download_url'], local_filename)
    extract_file(local_filename, extract_to='./')
    os.chmod(path_to_solver_binary, 0o755)

    write_to_file("./solvers.cfg", "./smtrat-static")

    write_version(repo, latest_version)

    with open(os.getenv('GITHUB_OUTPUT'), 'a') as github_output:
        github_output.write('version_changed=true\n')

    for theory in theories:
        prepare_directories(theory)
        generate_tests(theory, NUM_TESTS)

if __name__ == '__main__':
    main()
