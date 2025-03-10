#! /usr/bin/env python3
import os
#
# Usage: ./bin/oracle.py <test_smt2_file> <time_file> <solver_file> <bug_folder> <timeout_in_sec> <memlimit_in_bytes>
#
#
import re
import sys
import time
import signal
import shutil
import subprocess

from enum import Enum

invalid_list = [
    "an invalid model was generated",
    "ERRORS SATISFYING ASSERTIONS WITH MODEL"
]
crash_list = [
    "Exception",
    "lang.AssertionError",
    "lang.Error",
    "runtime error",
    "LEAKED",
    "Leaked",
    "Segmentation fault",
    "segmentation fault",
    "segfault",
    "ASSERTION",
    "Assertion",
    "Fatal failure",
    "Internal error detected",
#    "an invalid model was generated",
    "Failed to verify",
    "failed to verify",
    "ERROR: AddressSanitizer:",
    "invalid expression",
    "Aborted"
]

duplicate_list = [
]

ignore_list = [
    "(error ",
    "unsupported",
    "unexpected char",
    "failed to open file",
    "Expected result sat but got unsat",
    "Expected result unsat but got sat",
    "Parse Error",
    "Cannot get model",
    "Symbol 'str.to-re' not declared as a variable",
    "Symbol 'str.to.re' not declared as a variable",
    "Unimplemented code encountered",
    "syntax error when reading token",
    "Sort declaration error",
    "expected command at",
    "Typing error",
    "DAG_symb_hex_str",
    "syntax error on line",
    "undefined symbol",
    "ERROR smtrat.parser:",
    "error : DAG_new",
    "invalid sort",
    "unexpected token"
    "Sort declaration error",
    "Z.of_substring_base:",
    "error : DAG_symb_str",
    "expected 'BitVec' at 'FloatingPoint'",
    "syntax error"
]

logic_map = {
    "opensmt": [
        "QF_UF", "QF_LIA", "QF_LRA", "QF_AX", "QF_IDL", "QF_RDL",
        "QF_ALIA", "QF_UFIDL", "QF_UFLIA", "QF_AUFLIA", "QF_UFLRA",
    ],
    "yices": [
        "QF_UF", "UF",
        "LIA", "LRA", "QF_LIA", "QF_LRA",
        "QF_BV", "BV", "QF_AX", "QF_ABV",
        "QF_NIA", "QF_NRA",
        "QF_IDL", "QF_RDL",
        "QF_ALIA", "QF_ANIA", "QF_LIRA", "QF_NIRA"
        "QF_UFBV", "QF_UFLIA", "QF_UFLRA", "QF_UFNIA", "QF_UFNRA", "QF_UFIDL",
        "QF_AUFBV", "QF_AUFLIA", "QF_AUFNIA",
    ]
}

def plain(cli):
    plain_cli = ""
    for token in cli.split(" "):
        plain_cli += token.split("/")[-1]
    return escape(plain_cli)


def escape(s):
    s = s.replace(".", "")
    s = s.replace("=", "")
    return s

def detect_logics_solver_name(solver_cli):
    if "opensmt" in solver_cli:
        return "opensmt"
    elif "yices" in solver_cli:
        return "yices"
    return None

def report_diff(
    scratchfile,
    bugtype,
    ref_cli,
    ref_stdout,
    ref_stderr,
    sol_cli,
    sol_stdout,
    sol_stderr,
    bugfolder
):
    plain_cli = plain(sol_cli)
    # format: <solver><{crash,wrong,invalid_model}><seed>.<random-str>.smt2
    report = "%s/%s-%s-%s.smt2" % (
        bugfolder,
        bugtype,
        plain_cli,
        scratchfile.split("/")[-1].split(".")[-2]
    )
    try:
        shutil.copy(scratchfile, report)
    except Exception:
        print("error: couldn't copy scratchfile to bugfolder.")
        exit(1)

    logpath = "%s/%s-%s-%s.output" % (
        bugfolder,
        bugtype,
        plain_cli,
        scratchfile.split("/")[-1].split(".")[-2]
    )
    with open(logpath, "w") as log:
        log.write("*** REFERENCE \n")
        log.write("command: " + ref_cli + "\n")
        log.write("stderr:\n")
        log.write(ref_stderr)
        log.write("stdout:\n")
        log.write(ref_stdout)
        log.write("\n\n*** INCORRECT \n")
        log.write("command: " + sol_cli + "\n")
        log.write("stderr:\n")
        log.write(sol_stderr)
        log.write("stdout:\n")
        log.write(sol_stdout)
    return report


def report(scratchfile, bugtype, cli, stdout, stderr, bugfolder):
    plain_cli = plain(cli)
    # format: <solver><{crash,wrong,invalid_model}><seed>.smt2
    report = "%s/%s-%s-%s.smt2" % (
        bugfolder,
        bugtype,
        plain_cli,
        scratchfile.split("/")[-1].split(".")[-2]
    )
    try:
        shutil.copy(scratchfile, report)
    except Exception as e:
        # print("error: couldn't copy scratchfile to bugfolder.")
        exit(1)
    logpath = "%s/%s-%s-%s.output" % (
        bugfolder,
        bugtype,
        plain_cli,
        scratchfile.split("/")[-1].split(".")[-2]
    )
    with open(logpath, "w") as log:
        log.write("command: " + cli + "\n")
        log.write("stderr:\n")
        log.write(stderr)
        log.write("stdout:\n")
        log.write(stdout)
    return report


def grep_result(stdout):
    """
    Grep the result from the stdout of a solver.
    """
    result = SolverResult()
    for line in stdout.splitlines():
        if re.search("^unsat$", line, flags=re.MULTILINE):
            result.append(SolverQueryResult.UNSAT)
        elif re.search("^sat$", line, flags=re.MULTILINE):
            result.append(SolverQueryResult.SAT)
        elif re.search("^unknown$", line, flags=re.MULTILINE):
            result.append(SolverQueryResult.UNKNOWN)
    return result


def in_list(stdout, stderr, lst):
    stdstream = stdout + " " + stderr
    for err in lst:
        if err in stdstream:
            return True
    return False


def in_crash_list(stdout, stderr):
    return in_list(stdout, stderr, crash_list)


def in_invalid_list(stdout, stderr):
    return in_list(stdout, stderr, invalid_list)


def in_duplicate_list(stdout, stderr):
    return in_list(stdout, stderr, duplicate_list)


def in_ignore_list(stdout, stderr):
    return in_list(stdout, stderr, ignore_list)


class Solver:
    def __init__(self, cil):
        self.cil = cil

    def solve(self, file, tlimit_in_sec, mlimit_in_bytes, debug=False):
        total_time = -1
        try:
            t1 = time.time()
            # cmd = list(filter(None, self.cil.split(" "))) + [file]
            cmd = 'timeout -s 9 {} '.format(tlimit_in_sec) + self.cil + " "+ file
            #print("cmd", cmd)
            if debug:
                print(cmd)
            output = subprocess.run(
                cmd,
                timeout=tlimit_in_sec,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            total_time = time.time() - t1

        except subprocess.TimeoutExpired as te:
            if te.stdout and te.stderr:
                stdout = te.stdout.decode()
                stderr = te.stderr.decode()
            else:
                stdout = ""
                stderr = ""
            return stdout, stderr, 137, -1

        except ValueError:
            stdout = ""
            stderr = ""
            return stdout, stderr, 0, -1

        except FileNotFoundError:
            print('error: solver "' + cmd[0] + '" not found', flush=True)
            exit(ERR_USAGE)

        stdout = output.stdout.decode()
        stderr = output.stderr.decode()
        returncode = output.returncode

        if debug:
            print("output: " + stdout + "\n" + stderr)

        return stdout, stderr, returncode, total_time


class LogicSolver(Solver):
    def __init__(self, cli, logics):
        super().__init__(cli)
        self.logics = logics

    def solve_with_logics(self, file, tlimit_in_sec, mlimit_in_bytes, debug=False):
        for logic in self.logics:
            logic_file = f"{file}.logic.smt2"
            with open(file, "r") as orig, open(logic_file, "w") as temp:
                temp.write(f"(set-logic {logic})\n" + orig.read())

            # Run the solver with the modified file
            stdout, stderr, returncode, total_time = self.solve(logic_file, tlimit_in_sec, mlimit_in_bytes, debug)
            # Check if the output is valid (SAT/UNSAT/UNKNOWN)
            if returncode == 0 and not in_ignore_list(stdout, stderr):
                if re.search(r"^(sat|unsat|unknown)$", stdout, flags=re.MULTILINE):
                    os.remove(logic_file)  # Delete temp file if valid
                    return stdout, stderr, returncode, total_time

            # Clean up temporary logic file on errors
            os.remove(logic_file)

        # Return a "rejected" result if all logics fail
        return None, None, None, None

def sr2str(sol_res):
    if sol_res == SolverQueryResult.SAT: return "sat"
    if sol_res == SolverQueryResult.UNSAT: return "unsat"
    if sol_res == SolverQueryResult.UNKNOWN: return "unknown"

class SolverResult:
    """
    Class to store the result of multiple solver check-sat queries.
    :lst a list of multiple "SolverQueryResult" items
    """

    def __init__(self, result=None):
        self.lst = []
        if result:
            self.lst.append(result)

    def append(self, result):
        self.lst.append(result)

    def equals(self, rhs):
        if type(rhs) == SolverQueryResult:
            return len(self.lst) == 1 and self.lst[0] == rhs
        elif type(rhs) == SolverResult:
            if len(self.lst) != len(rhs.lst):
                return False
            for index in range(0, len(self.lst)):
                if (
                    self.lst[index] != SolverQueryResult.UNKNOWN
                    and rhs.lst[index] != SolverQueryResult.UNKNOWN
                    and self.lst[index] != rhs.lst[index]
                ):
                    return False
            return True
        else:
            return False

    def __str__(self):
        s = sr2str(self.lst[0])
        for res in self.lst[1:]:
            s += "\n" + sr2str(res)
        return s


class SolverQueryResult(Enum):
    """
    Enum storing the result of a single solver check-sat query.
    """
    SAT = 0  # solver query returns "sat"
    UNSAT = 1  # solver query returns "unsat"
    UNKNOWN = 2  # solver query reports "unknown"


def lookup(result_cache, keyword):
    ref_sols = [sol for sol in clis if keyword in sol]
    if result_cache.get(ref_sols[0]):
        return result_cache[ref_sols[0]]
    return None

def get_oracle_result(clis, solver_cli, result_cache, test_input_file):
    """
    Assumption for this function to work
    solver_cfg file of the following format

    z3 reference solver
    cvc5 ref solver
    z3-non-unicode ref solver (needs to contain unicode=false)
    <all other solvers>
    """

    if "cvc" in solver_cli:
        # Result of latest Z3 cfg as specified (lowest line number in solver_cfg)
        return lookup(result_cache, "z3")
    else:
        is_string_logic = "String" in open(test_input_file).read()
        try:
            # z3-v0.v1.v2
            v1 = int(solver_cli.split(" ")[0].split(".")[1])
            v2 = int(solver_cli.split(" ")[0].split(".")[2])
        except:
            return lookup(result_cache, "cvc") #result_cache[[sol for sol in clis if "cvc" in sol][0]]

        if is_string_logic and (v1 <= 8 and v2 <= 10):
            # Special case: on String formulas, use z3-4.8.11 unicode=false as
            # reference for all version of z3-4.8.10 and earlier
            return lookup(result_cache, "unicode=false") #result_cache[[sol for sol in clis if "unicode=false" in sol][0]]
        return lookup(result_cache, "cvc") #result_cache[[sol for sol in clis if "cvc" in sol][0]]


def test(fn, fpath_tmp, clis, tlimit_in_sec, mlimit_in_bytes, result_cache, is_ref_run=False):
    """
    fn: the test input
    fp_tmp
    clis: list of solver clis
    tlimit_in_sec: time limit in seconds for a single solver call
    mlimit_in_bytes: memory limit in bytes for a single solver call
    """
    oracle, reference = SolverResult(SolverQueryResult.UNKNOWN), None
    num_bugs = 0
    if not is_ref_run: fn_tmp = open(fpath_tmp[:-4]+"time", 'w')

    for solver_cli in clis:
        solver_name = detect_logics_solver_name(solver_cli)
        if solver_name:
            # Use LogicSolver for solvers in logic_map
            solver = LogicSolver(solver_cli, logic_map[solver_name])
            stdout, stderr, exitcode, total_time = solver.solve_with_logics(
                fn, tlimit_in_sec, mlimit_in_bytes
            )
        else:
            # Default case for other solvers
            solver = Solver(solver_cli)
            stdout, stderr, exitcode, total_time = solver.solve(
                fn, tlimit_in_sec, mlimit_in_bytes
            )

        if stdout is None and stderr is None and exitcode is None and total_time is None:
            continue

        if not is_ref_run:

            fn_tmp.write(fpath_tmp.split(".")[0].split("/")[-1] + ",")
            fn_tmp.write(solver.cil + ","+ str(total_time)+",")

        if stdout.strip() == "unknown":
            if not is_ref_run:
                fn_tmp.write("unknown\n")
            continue

        if in_invalid_list(stdout, stderr):

            # Match stdout and stderr against the duplicate list
            # (see yinyang/config/Config.py:51) to prevent catching
            # duplicate bug triggers.
            if not in_duplicate_list(stdout, stderr):
                path = report(
                    fn, "invmodel", solver_cli, stdout, stderr, bugfolder
                )
                num_bugs += 1

            if not is_ref_run: fn_tmp.write("invmodel\n")
            continue

        # Match stdout and stderr against the crash list
        # (see yinyang/config/Config.py:27) which contains various
        # crash messages such as assertion errors, check failure,
        # invalid models, etc.
        if in_crash_list(stdout, stderr):

            # Match stdout and stderr against the duplicate list
            # (see yinyang/config/Config.py:51) to prevent catching
            # duplicate bug triggers.
            if not in_duplicate_list(stdout, stderr):
                path = report(
                    fn, "crash", solver_cli, stdout, stderr, bugfolder
                )
                num_bugs += 1

            if not is_ref_run: fn_tmp.write("crash\n")
            continue

        else:
            # Check whether the solver call produced errors, e.g, related
            # to its parser, options, type-checker etc., by matching stdout
            # and stderr against the ignore list
            # (see yinyang/config/Config.py:54).
            if in_ignore_list(stdout, stderr):
                if not is_ref_run:
                    if "memory" in stdout+stderr:
                        fn_tmp.write("memout\n")
                    else:
                        fn_tmp.write("rejected\n")
                continue  # Continue to the next solver.

            if exitcode != 0:
                # Check whether the solver crashed with a segfault.
                if exitcode == -signal.SIGSEGV or exitcode == 245:
                    path = report(
                        fn, "segfault", solver_cli, stdout, stderr, bugfolder
                    )
                    log_segfault_trigger(bugfolder, fn)
                    num_bugs += 1
                    if not is_ref_run: fn_tmp.write(",segfault\n")
                    continue

                # Check whether the solver timed out.
                elif exitcode == 137:
                    if not is_ref_run: fn_tmp.write("timeout\n")
                    continue  # Continue to the next solver.

                # Check whether a "command not found" error occurred.
                elif exitcode == 127:
                    if not is_ref_run: fn_tmp.write("command not found\n")
                    continue  # Continue to the next solver.

            # Check if the stdout contains a valid solver query result,
            # i.e., contains lines with 'sat', 'unsat' or 'unknown'.
            elif (
                not re.search("^unsat$", stdout, flags=re.MULTILINE)
                and not re.search("^sat$", stdout, flags=re.MULTILINE)
                and not re.search("^unknown$", stdout, flags=re.MULTILINE)
            ):
                #print(solver_cli,"rejected",flush=True)
                if not is_ref_run: fn_tmp.write("rejected\n")
                continue  # Continue to the next solver.

            else:
                # Grep for '^sat$', '^unsat$', and '^unknown$' to produce
                # the output (including '^unknown$' to also deal with
                # incremental benchmarks) for comparing with the oracle
                # (yinyang) or with other non-erroneous solver runs
                # (opfuzz) for soundness bugs.
                result = grep_result(stdout)
                result_cache[solver_cli] = (result, solver_cli, fn, stdout, stderr)

                if is_ref_run:
                    reference = (solver_cli, fn, stdout, stderr)
                    oracle = result
                else:
                    ref = get_oracle_result(clis, solver_cli, result_cache, fn)
                    if ref:
                        oracle = ref[0]
                        reference = ref[1:]

                if not oracle.equals(result):
                    # Produce a bug report for soundness bugs
                    # containing a diff with the reference solver
                    ref_cli = reference[0]
                    ref_stdout = reference[1]
                    ref_stderr = reference[2]
                    path = report_diff(
                        fn,
                        "incorrect",
                        ref_cli,
                        ref_stdout,
                        ref_stderr,
                        solver_cli,
                        stdout,
                        stderr,
                        bugfolder
                    )
                    num_bugs += 1
                    if not is_ref_run: fn_tmp.write("unsoundness\n")
                    continue
            if not is_ref_run: fn_tmp.write(stdout+stderr)
    return num_bugs

if len(sys.argv) != 7:
    print("Usage: ./bin/oracle.py <test_smt2_file> <time_file> <solver_file> <bugfolder> <timeout_in_sec> <memlimit_in_bytes>")
    sys.exit(2)

if __name__ == "__main__":
    test_input_file = sys.argv[1]
    time_file = sys.argv[2]
    clis = open(sys.argv[3],"r").read().split("\n")[:-1]
    bugfolder = sys.argv[4]
    tlimit_in_sec, mlimit_in_bytes = float(sys.argv[5]), int(sys.argv[6])

    result_cache = {} # mapping solver_cfg -> result
    test(test_input_file, time_file, clis, tlimit_in_sec, mlimit_in_bytes, result_cache, is_ref_run=False)