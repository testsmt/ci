import subprocess

def execute_command(binary_path, args=None, shell = False, cwd = None, capture_output = True):
    if args is None:
        args = []
    try:
        command = [binary_path] + args
        result = subprocess.run(command, shell=shell, capture_output=capture_output, text=True, check=True, cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
        print(f"Standard error: {e.stderr}")
        return e.output
