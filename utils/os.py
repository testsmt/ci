import os

def write_to_file(filename, line):
    with open(filename, "a") as file:
        file.write(line + "\n")

def read_version(solver_name):
    try:
        with open('./versions', 'r') as file:
            for line in file:
                name, version = line.strip().split(': ')
                if name == solver_name:
                    return version
    except FileNotFoundError:
        pass
    return None

def write_version(solver_name, version):
    lines = []
    try:
        with open('./versions', 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        pass

    with open('./versions', 'w') as file:
        found = False
        for line in lines:
            name, _ = line.strip().split(': ')
            if name == solver_name:
                file.write(f"{solver_name}: {version}\n")
                found = True
            else:
                file.write(line)
        if not found:
            file.write(f"{solver_name}: {version}\n")