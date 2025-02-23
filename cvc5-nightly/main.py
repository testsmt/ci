import os
import re

from utils.download import download_file, extract_file
from utils.github import get_latest_pre_release_assets
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
    pattern = re.compile(r'cvc5-Linux-x86_64-static-\d{4}-\d{2}-\d{2}-[a-f0-9]+\.zip')
    path_to_solver_binary = "./solver/bin/cvc5"
    NUM_TESTS = int(os.getenv("NUM_TESTS", 100))

    latest_pre_release = get_latest_pre_release_assets(owner, repo)

    if not latest_pre_release:
        print("No pre-release information found.")
        return

    matching_asset = None
    for asset in latest_pre_release['assets']:
        if pattern.match(asset['name']):
            matching_asset = asset
            break

    if not matching_asset:
        print("No matching asset found.")
        return

    local_filename = matching_asset['name']
    download_file(matching_asset['browser_download_url'], local_filename)
    extract_file(local_filename, extract_to='./', rename_to="solver", folder_prefix="cvc5-Linux-")
    os.chmod(path_to_solver_binary, 0o755)

    write_to_file("./solvers.cfg", "./solver/bin/cvc5 -q")

    for theory in theories:
        prepare_directories(theory)
        generate_tests(theory, NUM_TESTS)

if __name__ == '__main__':
    main()
