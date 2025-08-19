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

    # Debug: print all links to see what's available
    print("Available links on MathSAT download page:")
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'mathsat' in href.lower() or 'download' in href.lower():
            print(f"  - {href}")

    # Look for the new direct release URL format
    link = soup.find('a', href=re.compile(r'/release/mathsat-\d+\.\d+\.\d+-linux-x86_64\.tar\.gz'))

    if not link:
        print("No matching MathSAT binary found.")
        return False, None, None

    href = link['href']
    match = re.search(r'mathsat-(\d+\.\d+\.\d+)-linux-x86_64\.tar\.gz', href)
    if not match:
        print("Could not extract version number from the link.")
        return False, None, None

    version = match.group(1)
    download_url = f"https://mathsat.fbk.eu{href}"

    return True, version, download_url

def main():
    repo = 'mathsat5'
    path_to_solver_binary = "./solver/bin/mathsat"
    NUM_TESTS = int(os.getenv("NUM_TESTS", 100))

    success, latest_version, download_url = fetch_mathsat_binary()
    if success:
        current_version = read_version(repo)

        # Check if version has actually changed
        version_changed = current_version != latest_version

        local_filename = f"mathsat-{latest_version}-linux-x86_64.tar.gz"
        download_file(download_url, local_filename)
        extract_file(local_filename, extract_to='./', rename_to="solver", folder_prefix="mathsat-")
        os.chmod(path_to_solver_binary, 0o755)

        write_to_file("./solvers-mathsat5.cfg", "./solver/bin/mathsat -theory.bv.div_by_zero_mode=1 -theory.fp.minmax_zero_mode=4 -theory.fp.to_bv_overflow_mode=1 -theory.na.div_by_zero_mode=1")

        write_version(repo, latest_version)

        with open(os.getenv('GITHUB_OUTPUT'), 'a') as github_output:
            github_output.write(f'version_changed={str(version_changed).lower()}\n')

        # Always generate tests (regardless of version change)
        for theory in theories:
            prepare_directories(theory)
            generate_tests(theory, NUM_TESTS)
    else:
        print("Failed to download MathSAT binary.")
        print("This might be due to changes in the download page structure.")
        exit(1)

if __name__ == '__main__':
    main()
