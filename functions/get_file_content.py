import os

def get_file_content(working_directory, file_path) -> str:
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

    if not os.path.exists(file_path):
        return f'Error: "{file_path}" does not exist'
    if not os.path.isfile(file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    if os.path.abspath(common_path) != os.path.abspath(working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    read_char_limit = 10000
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if len(content) > read_char_limit:
                return content[:read_char_limit] + f'[...File "{file_path}" truncated at 10000 characters]'
            else:
                return content
    except Exception as e:
        return f'Error: File not found or is not a regular file: "{file_path}"'