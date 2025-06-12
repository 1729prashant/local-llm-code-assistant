import os
import subprocess

def run_python_file(working_directory, file_path):
    # Resolve working_directory if it's not absolute
    if not os.path.isabs(working_directory):
        cwd = os.getcwd()
        potential_path = os.path.join(cwd, working_directory)
        if not os.path.isdir(potential_path):
            return f'Error: "{working_directory}" is not a valid subdirectory of the current directory'
        working_directory = potential_path

    # Validate that file_path ends with .py
    if not file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    
    # build absolute file path
    relative_file_path = file_path
    if file_path is None:
        file_path = working_directory
    else:
        if not os.path.isabs(file_path):
            file_path = os.path.join(working_directory, file_path)

    # Validate file_path is within working_directory
    try:
        common_path = os.path.commonpath([os.path.abspath(file_path), os.path.abspath(working_directory)])
    except ValueError:
        return f'Error: Invalid path comparison between "{file_path}" and "{working_directory}"'
    
    if os.path.abspath(common_path) != os.path.abspath(working_directory):
        return f'Error: Cannot execute "{relative_file_path}" as it is outside the permitted working directory'

    if not os.path.exists(file_path):
        return f'Error: File "{relative_file_path}" not found.'

    try:
        result = subprocess.run(['python3', file_path], capture_output=True, text=True, timeout=30, cwd=working_directory)
        
        output = []

        if result.stdout:
            output.append("STDOUT:\n" + result.stdout.strip())
        if result.stderr:
            output.append("STDERR:\n" + result.stderr.strip())
        if result.returncode != 0:
            output.append(f'Error: Process exited with code {result.returncode}')

        if not output:
            return "No output produced."
        
        return "\n\n".join(output)
    
    except subprocess.TimeoutExpired:
        return f'Error: Execution timed out after 30 seconds.'
    except Exception as e:
        return f'Error: executing Python file: {e}'