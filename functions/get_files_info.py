import os

def get_files_info(working_directory, directory=None) -> str:
    # Resolve working_directory if it's not absolute
    if not os.path.isabs(working_directory):
        cwd = os.getcwd()
        potential_path = os.path.join(cwd, working_directory)
        if not os.path.isdir(potential_path):
            return f'Error: "{working_directory}" is not a valid subdirectory of the current directory'
        working_directory = potential_path

    # Use current working_directory if directory is not provided
    if directory is None:
        directory = working_directory
    else:
        if not os.path.isabs(directory):
            directory = os.path.join(working_directory, directory)

    # Validate directory is within working_directory
    try:
        common_path = os.path.commonpath([os.path.abspath(directory), os.path.abspath(working_directory)])
    except ValueError:
        return f'Error: Invalid path comparison between "{directory}" and "{working_directory}"'

    if not os.path.exists(directory):
        return f'Error: "{directory}" does not exist'
    if not os.path.isdir(directory):
        return f'Error: "{directory}" is not a directory'
    if os.path.abspath(common_path) != os.path.abspath(working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    # List contents
    contents = get_directory_contents(directory)
    directory_contents = ""
    for item, size, type in contents:
        is_dir = (type == "directory")
        directory_contents += f"- {item}: file_size={size} bytes, is_dir={str(is_dir)}\n"
    return directory_contents


def get_directory_contents(directory_path):
    """
    Lists files and directories in a directory, along with their sizes.

    Args:
        directory_path: The path to the directory.

    Returns:
        A list of tuples: (name, size in bytes, type = 'file' or 'directory').
    """
    contents = []
    for item in os.listdir(directory_path):
        full_path = os.path.join(directory_path, item)
        try:
            item_size = os.stat(full_path).st_size
            if os.path.isfile(full_path):
                contents.append((item, item_size, "file"))
            elif os.path.isdir(full_path):
                contents.append((item, item_size, "directory"))
        except OSError as e:
            print(f"Error accessing {item}: {e}")
    return contents
