import os
import re

from utils.command import execute_command
from utils.download import download_file, extract_file
from utils.github import get_latest_release


def main():
    owner = 'Z3Prover'
    repo = 'z3'
    pattern = re.compile(r'z3-\d+\.\d+\.\d+-x64-glibc-\d+\.\d+\.zip')
    path_to_solver_binary = "./solver/bin/z3"

    latest_release = get_latest_release(owner, repo)

    matching_asset = None
    for asset in latest_release['assets']:
        if pattern.match(asset['name']):
            matching_asset = asset
            break

    if not matching_asset:
        print("No matching asset found.")
        return

    local_filename = matching_asset['name']
    download_file(matching_asset['browser_download_url'], local_filename)
    extract_file(local_filename, extract_to='./', rename_to="solver")
    os.chmod(path_to_solver_binary, 0o755)

    help_output = execute_command(path_to_solver_binary, ["--help"])
    print(help_output)

if __name__ == '__main__':
    main()
