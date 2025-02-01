from source.utils import get_latest_release, download_file, extract_file, execute_command
import os
import re

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
