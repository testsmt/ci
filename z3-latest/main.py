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
    print("=== DEBUG: Starting z3-latest.main ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    owner = 'Z3Prover'
    repo = 'z3'
    pattern = re.compile(r'z3-\d+\.\d+\.\d+-x64-glibc-\d+\.\d+\.zip')
    path_to_solver_binary = "./solver/bin/z3"
    NUM_TESTS = int(os.getenv("NUM_TESTS", 100))
    
    print(f"NUM_TESTS: {NUM_TESTS}")
    print(f"Looking for latest release from {owner}/{repo}")
    
    latest_release = get_latest_release(owner, repo)
    print(f"Latest release: {latest_release['tag_name']}")

    matching_asset = None
    for asset in latest_release['assets']:
        if pattern.match(asset['name']):
            matching_asset = asset
            break

    if not matching_asset:
        print("No matching asset found.")
        return

    print(f"Matching asset: {matching_asset['name']}")

    latest_version = latest_release['tag_name']
    current_version = read_version(repo)
    
    print(f"Latest version: {latest_version}")
    print(f"Current version: {current_version}")

    local_filename = matching_asset['name']
    print(f"Downloading {matching_asset['browser_download_url']} to {local_filename}")
    download_file(matching_asset['browser_download_url'], local_filename)
    
    print(f"Extracting {local_filename}")
    extract_file(local_filename, extract_to='./', rename_to="solver")
    
    print(f"Setting permissions on {path_to_solver_binary}")
    os.chmod(path_to_solver_binary, 0o755)

    print("Writing solver config to ./solvers-z3.cfg")
    write_to_file("./solvers-z3.cfg", "./solver/bin/z3")

    print(f"Writing version {latest_version} for {repo}")
    write_version(repo, latest_version)
    
    print("Checking if versions file was created:")
    if os.path.exists('./versions'):
        print("Versions file exists, content:")
        with open('./versions', 'r') as f:
            print(f.read())
    else:
        print("Versions file does not exist!")

    print("Writing to GITHUB_OUTPUT")
    with open(os.getenv('GITHUB_OUTPUT'), 'a') as github_output:
        github_output.write('version_changed=true\n')
    
    print("GITHUB_OUTPUT content:")
    if os.path.exists(os.getenv('GITHUB_OUTPUT')):
        with open(os.getenv('GITHUB_OUTPUT'), 'r') as f:
            print(f.read())
    else:
        print("GITHUB_OUTPUT file does not exist!")

    print("Preparing directories and generating tests...")
    for theory in theories:
        print(f"Processing theory: {theory}")
        prepare_directories(theory)
        generate_tests(theory, NUM_TESTS)
    
    print("=== DEBUG: Finished z3-latest.main ===")

if __name__ == '__main__':
    main()
