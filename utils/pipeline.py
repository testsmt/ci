import os
import sqlite3
from pathlib import Path

from utils.command import execute_command

TIMEOUT_IN_SECS = 8.0
MEMOUT_IN_KB = 1048576
SOLVERS_CFG_PATH = "./solvers.cfg"
ORACLE_PATH = "./oracle"
ET_CONFIG_PATH = "./et_config"
RESULTS_DIR = "./results"
NUM_CORES = 4


def prepare_directories(theory):
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR, exist_ok=True)

    theory_dir = os.path.join(RESULTS_DIR, theory)
    temp_dir = os.path.join(theory_dir, "temp")
    bugs_dir = os.path.join(theory_dir, "bugs")
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(bugs_dir, exist_ok=True)

def generate_tests(theory, num_tests):
    theory_g4 = os.path.join(ET_CONFIG_PATH, f"{theory}.g4")
    theory_cfg = os.path.join(ET_CONFIG_PATH, f"{theory}.cfg")
    temp_dir = os.path.join(RESULTS_DIR, theory, "temp")
    execute_command("et", [
        "--output", temp_dir,
        "take", str(num_tests),
        theory_g4,
        theory_cfg
    ])

# def run_solvers(theory):
#     temp_dir = os.path.join(RESULTS_DIR, theory, "temp")
#     bugs_dir = os.path.join(RESULTS_DIR, theory, "bugs")
#
#     find_command = [
#         "find", temp_dir, "-name", "*.smt2", "-print0"
#     ]
#
#     parallel_command = [
#         "parallel", "-0", f"-j{NUM_CORES}", "--eta", "--progress", "--bar", ORACLE_PATH,
#         "{}", "{}.time", SOLVERS_CFG_PATH, bugs_dir, str(TIMEOUT_IN_SECS), str(MEMOUT_IN_KB)
#     ]
#
#     full_command = f"{' '.join(find_command)} | {' '.join(parallel_command)}"
#     execute_command("/bin/bash", ["-c", full_command])

def run_solvers(theory):
    temp_dir = os.path.join(RESULTS_DIR, theory, "temp")
    bugs_dir = os.path.join(RESULTS_DIR, theory, "bugs")

    try:
        # Find all .smt2 files in the temp_dir
        find_result = execute_command("find", [temp_dir, "-type", "f", "-name", "*.smt2"])
        smt2_files = find_result.splitlines()

        print(smt2_files)
        # Debugging output to verify the files found
        print(f"Found {len(smt2_files)} .smt2 files.")

        for smt2_file in smt2_files:
            # Debugging output to verify each file being processed
            print(f"Processing file: {smt2_file}")

            # Execute the command for each .smt2 file
            res = execute_command("python",
       [
                ORACLE_PATH,
                smt2_file,
                f"{smt2_file}.time",
                SOLVERS_CFG_PATH,
                bugs_dir,
                str(TIMEOUT_IN_SECS),
                str(MEMOUT_IN_KB)
            ])
            print(res)

    except Exception as e:
        print(f"An error occurred while processing .smt2 files: {e}")

def create_database(theory):
    db_path = os.path.join(RESULTS_DIR, f"{theory}.sqlite3")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ExpResults (
        formula_idx INTEGER,
        solver_cfg TEXT NOT NULL,
        runtime DOUBLE NOT NULL,
        result TEXT NOT NULL
    )
    """)
    conn.commit()
    return conn, cursor


def import_data_into_db(theory, conn, cursor):
    temp_dir = os.path.join(RESULTS_DIR, theory, "temp")
    time_files = Path(temp_dir).rglob("*.time")

    i = 0
    for time_file in time_files:
        if i % 100 == 0:
            print(f"Processing file {i}: {time_file}")

        with open(time_file, "r") as f:
            lines = f.readlines()[3:]

        for line in lines:
            columns = line.strip().split(",")
            if len(columns) >= 4:
                formula_idx, solver_cfg, runtime, result = columns[0], columns[1], columns[2], columns[3]

                cursor.execute("""
                INSERT INTO ExpResults (formula_idx, solver_cfg, runtime, result)
                VALUES (?, ?, ?, ?)
                """, (formula_idx, solver_cfg, runtime, result))

        conn.commit()
        i += 1


def gather_statistics(theory, cursor, num_tests):
    print(f"\nStatistics for theory: {theory}")

    cursor.execute("SELECT COUNT(DISTINCT solver_cfg) FROM ExpResults;")
    unique_solver_configs = cursor.fetchone()[0]

    cursor.execute("SELECT DISTINCT(result) FROM ExpResults;")
    distinct_results = cursor.fetchall()

    for result in distinct_results:
        result_type = result[0]
        cursor.execute(f"SELECT COUNT(*) FROM ExpResults WHERE result = '{result_type}';")
        count = cursor.fetchone()[0]
        percentage = (count / (unique_solver_configs * num_tests)) * 100
        print(f"Count of '{result_type}': {count} ({percentage:.2f}%)")

    print("---------------------------------------------")