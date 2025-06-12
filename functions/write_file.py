import os

def write_file(working_directory, file_path, content) -> str:
    # Resolve working_directory if it's not absolute
    if not os.path.isabs(working_directory):
        cwd = os.getcwd()
        potential_path = os.path.join(cwd, working_directory)
        if not os.path.isdir(potential_path):
            return f'Error: "{working_directory}" is not a valid subdirectory of the current directory'
        working_directory = potential_path

    # build absolute file path
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
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    # write to file
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: Cannot write to "{file_path}", encounterd error"{e}"'