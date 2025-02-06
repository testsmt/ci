import os
import sqlite3
from pathlib import Path

from utils.command import execute_command

TIMEOUT_IN_SECS = 8.0
MEMOUT_IN_KB = 1048576
SOLVERS_CFG_PATH = "./solvers.cfg"
ORACLE_PATH = "./oracle"
ET_CONFIG_PATH = "./et_config"
RESULTS_DIR = "results"
NUM_CORES = 4


def prepare_directories(theory):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    theory_dir = os.path.join(RESULTS_DIR, theory)
    os.makedirs(os.path.join(theory_dir, "temp"), exist_ok=True)
    os.makedirs(os.path.join(theory_dir, "bugs"), exist_ok=True)

def generate_tests(theory, num_tests):
    theory_g4 = os.path.join(ET_CONFIG_PATH, f"{theory}.g4")
    theory_cfg = os.path.join(ET_CONFIG_PATH, f"{theory}.cfg")
    temp_dir = os.path.join(RESULTS_DIR, theory, "temp")
    command = f"et --output {temp_dir} take {num_tests} {theory_g4} {theory_cfg}"
    execute_command(command)

def run_solvers(theory):
    temp_dir = os.path.join(RESULTS_DIR, theory, "temp")
    bugs_dir = os.path.join(RESULTS_DIR, theory, "bugs")

    # Command to run the solvers in parallel
    command = (
        f"find {temp_dir} -name '*.smt2' -print0 | "
        f"parallel -0 -j{NUM_CORES} --eta --progress --bar {ORACLE_PATH} "
        f"{{}} {{}}.time {SOLVERS_CFG_PATH} {bugs_dir} {TIMEOUT_IN_SECS} {MEMOUT_IN_KB}"
    )
    execute_command(command)


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