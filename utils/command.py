import subprocess

def execute_command(binary_path, args=None):
    if args is None:
        args = []
    try:
        command = [binary_path] + args
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
        return e.output
