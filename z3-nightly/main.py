import os

from utils.os import write_to_file
from utils.pipeline import prepare_directories, generate_tests
from utils.command import execute_command

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
    repo_url = "https://github.com/Z3Prover/z3.git"
    repo_name = "z3"
    build_dir = "./z3/build"
    solver_binary_path = "./z3/build/z3"
    NUM_TESTS = int(os.getenv("NUM_TESTS", 100))

    if not os.path.exists(repo_name):
        print(f"Cloning repository from {repo_url}...")
        execute_command("git", ["clone", repo_url])
    else:
        print(f"Repository {repo_name} already exists.")

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
        print(f"Created build directory at {build_dir}.")
    else:
        print(f"Build directory already exists at {build_dir}.")

    print(f"Running 'cmake ..' in {build_dir}...")
    execute_command("cmake", [".."], cwd=build_dir, capture_output=False)

    print(f"Building inside {build_dir} with 'make'...")
    execute_command("make", cwd=build_dir, capture_output=False)

    os.chmod(solver_binary_path, 0o755)

    write_to_file("./solvers.cfg", "./z3/build/z3")

    for theory in theories:
        prepare_directories(theory)
        generate_tests(theory, NUM_TESTS)

if __name__ == '__main__':
    main()
