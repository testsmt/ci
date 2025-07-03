import os
import re
import requests
from bs4 import BeautifulSoup

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
    "FP"
]

def fetch_mathsat_binary():
    url = "https://mathsat.fbk.eu/download.html"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    link = soup.find('a', href=re.compile(r'download\.php\?file=mathsat-\d+\.\d+\.\d+-linux-x86_64\.tar\.gz'))

    if not link:
        print("No matching MathSAT binary found.")
        return False, None, None

    href = link['href']
    match = re.search(r'mathsat-(\d+\.\d+\.\d+)-linux-x86_64\.tar\.gz', href)
    if not match:
        print("Could not extract version number from the link.")
        return False, None, None

    version = match.group(1)
    download_url = f"https://mathsat.fbk.eu/{href}"

    return True, version, download_url

def main():
    repo = 'mathsat5'
    path_to_solver_binary = "./solver/bin/mathsat"
    NUM_TESTS = int(os.getenv("NUM_TESTS", 100))

    success, latest_version, download_url = fetch_mathsat_binary()
    if success:
        current_version = read_version(repo)

        local_filename = f"mathsat-{latest_version}-linux-x86_64.tar.gz"
        download_file(download_url, local_filename)
        extract_file(local_filename, extract_to='./', rename_to="solver", folder_prefix="mathsat-")
        os.chmod(path_to_solver_binary, 0o755)

        write_to_file("./solvers.cfg", "./solver/bin/mathsat")

        write_version(repo, latest_version)

        with open(os.getenv('GITHUB_OUTPUT'), 'a') as github_output:
            github_output.write('version_changed=true\n')

        for theory in theories:
            prepare_directories(theory)
            generate_tests(theory, NUM_TESTS)
    else:
        print("Failed to download MathSAT binary.")

if __name__ == '__main__':
    main()
