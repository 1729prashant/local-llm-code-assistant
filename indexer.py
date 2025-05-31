import os

DEFAULT_EXTENSIONS = {'.go', '.html', '.js', '.ts', '.css', '.json', '.yaml', '.yml', '.md'}
DEFAULT_EXCLUDES = {'vendor', 'node_modules', 'testdata', '.git', '__pycache__'}

def collect_files(project_path, allowed_exts=DEFAULT_EXTENSIONS, exclude_dirs=DEFAULT_EXCLUDES):
    files = []
    for root, dirs, filenames in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fname in filenames:
            _, ext = os.path.splitext(fname)
            if ext in allowed_exts:
                full_path = os.path.join(root, fname)
                files.append(full_path)
    return files
