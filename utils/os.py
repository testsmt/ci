import os

def write_to_file(filename, line):
    print(f"DEBUG: write_to_file called with filename='{filename}', line='{line}'")
    with open(filename, "a") as file:
        file.write(line + "\n")
    print(f"DEBUG: Successfully wrote to {filename}")

def read_version(solver_name):
    print(f"DEBUG: read_version called with solver_name='{solver_name}'")
    try:
        with open('./versions', 'r') as file:
            for line in file:
                name, version = line.strip().split(': ')
                if name == solver_name:
                    print(f"DEBUG: Found version '{version}' for solver '{solver_name}'")
                    return version
    except FileNotFoundError:
        print(f"DEBUG: versions file not found for solver '{solver_name}'")
        pass
    print(f"DEBUG: No version found for solver '{solver_name}', returning None")
    return None

def write_version(solver_name, version):
    print(f"DEBUG: write_version called with solver_name='{solver_name}', version='{version}'")
    print(f"DEBUG: Current working directory: {os.getcwd()}")
    print(f"DEBUG: versions file exists: {os.path.exists('./versions')}")
    
    lines = []
    try:
        with open('./versions', 'r') as file:
            lines = file.readlines()
            print(f"DEBUG: Read {len(lines)} lines from versions file")
    except FileNotFoundError:
        print("DEBUG: versions file not found, will create new one")
        pass

    print(f"DEBUG: Writing to versions file...")
    with open('./versions', 'w') as file:
        found = False
        for line in lines:
            name, _ = line.strip().split(': ')
            if name == solver_name:
                file.write(f"{solver_name}: {version}\n")
                found = True
                print(f"DEBUG: Updated existing entry for '{solver_name}'")
            else:
                file.write(line)
        if not found:
            file.write(f"{solver_name}: {version}\n")
            print(f"DEBUG: Added new entry for '{solver_name}'")
    
    print(f"DEBUG: Successfully wrote version '{version}' for solver '{solver_name}'")
    print(f"DEBUG: versions file now exists: {os.path.exists('./versions')}")
    if os.path.exists('./versions'):
        print("DEBUG: Final versions file content:")
        with open('./versions', 'r') as f:
            print(f.read())