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
    "Arrays",
    "Bitvectors",
    "FP",
    "Strings"
]

def main():
    owner = 'cvc5'
    repo = 'cvc5'
    pattern = re.compile(r'cvc5-Linux-x86_64-static\.zip')
    path_to_solver_binary = "./solver/bin/cvc5"
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

    if current_version == latest_version:
        print(f"{repo} is up to date with version {current_version}.")
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as github_output:
            github_output.write('version_changed=false\n')
        return

    local_filename = matching_asset['name']
    download_file(matching_asset['browser_download_url'], local_filename)
    extract_file(local_filename, extract_to='./', rename_to="solver")
    os.chmod(path_to_solver_binary, 0o755)

    write_to_file("./solvers.cfg", "./solver/bin/cvc5 -q")

    write_version(repo, latest_version)

    with open(os.getenv('GITHUB_OUTPUT'), 'a') as github_output:
        github_output.write('version_changed=true\n')

    for theory in theories:
        prepare_directories(theory)
        generate_tests(theory, NUM_TESTS)

if __name__ == '__main__':
    main()
