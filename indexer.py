import os
import re

DEFAULT_EXTENSIONS = {'.go', '.html', '.js', '.ts', '.css', '.json', '.yaml', '.yml', '.md', '.py'}
DEFAULT_EXCLUDES = {'vendor', 'node_modules', 'testdata', '.git', '__pycache__', '.env', 'dist'}

def collect_files(project_path, allowed_exts=DEFAULT_EXTENSIONS, exclude_dirs=DEFAULT_EXCLUDES):
    """
    Collects files from a project path, excluding specified directories and
    filtering by allowed extensions.
    """
    files = []
    for root, dirs, filenames in os.walk(project_path):
        # Modify dirs in-place to prune the walk
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fname in filenames:
            _, ext = os.path.splitext(fname)
            if ext in allowed_exts:
                full_path = os.path.join(root, fname)
                files.append(full_path)
    return files

def get_file_type(file_path):
    """
    Guesses the file type/language based on extension.
    This is a basic heuristic, not a full language detection.
    """
    _, ext = os.path.splitext(file_path)
    if ext in ['.go']: return 'Go'
    if ext in ['.html', '.htm']: return 'HTML'
    if ext in ['.js', '.jsx']: return 'JavaScript'
    if ext in ['.ts', '.tsx']: return 'TypeScript'
    if ext in ['.css', '.scss', '.less']: return 'CSS/Stylesheet'
    if ext in ['.json']: return 'JSON'
    if ext in ['.yaml', '.yml']: return 'YAML'
    if ext in ['.md']: return 'Markdown'
    if ext in ['.py']: return 'Python'
    return 'Text' # Default for unknown extensions

# MODIFIED: Added project_path as a parameter
def filter_files_by_keywords(file_paths, task_description, project_path, top_n=10):
    """
    Filters file paths by relevance to task description keywords.
    This is a very rudimentary form of RAG.
    Prioritizes files containing keywords, then adds general project files.
    """
    keywords = set(re.findall(r'\b\w{3,}\b', task_description.lower()))

    # Files likely to contain UI/frontend code
    ui_keywords = {'html', 'js', 'css', 'template', 'view', 'frontend', 'render', 'script'}

    file_scores = {}
    for path in file_paths:
        score = 0
        file_name_lower = os.path.basename(path).lower()

        # Boost score if filename matches keywords
        for keyword in keywords:
            if keyword in file_name_lower:
                score += 5 # Higher boost for filename matches

        # Read content and score based on keyword presence
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                for keyword in keywords:
                    if keyword in content:
                        score += content.count(keyword) # Score by count of keywords

                # Boost if it's a common UI file and task has UI-related keywords
                if any(uk in file_name_lower or uk in content for uk in ui_keywords) and \
                   any(tk in ui_keywords for tk in keywords):
                    score += 10 # Strong boost for relevant UI files

        except Exception:
            pass # Ignore unreadable files for scoring

        file_scores[path] = score

    # Sort files by score, descending
    sorted_files = sorted(file_scores.items(), key=lambda item: item[1], reverse=True)

    # Separate highly relevant from less relevant
    highly_relevant_files = [path for path, score in sorted_files if score > 0]
    less_relevant_files = [path for path, score in sorted_files if score == 0]

    # Combine: take top N highly relevant, then fill with less relevant if needed
    final_files = highly_relevant_files[:top_n]
    if len(final_files) < top_n:
        final_files.extend(less_relevant_files[:top_n - len(final_files)])

    # Ensure some core files are always included if they exist and aren't already
    core_files = ['main.go', 'app.js', 'index.html', 'server.py', 'main.py']
    for core_file_name in core_files: # Renamed loop variable for clarity
        # MODIFIED: Use the passed project_path to form the full path
        full_core_path_in_project = os.path.join(project_path, core_file_name)
        if os.path.exists(full_core_path_in_project) and full_core_path_in_project not in final_files:
            final_files.insert(0, full_core_path_in_project) # Add to the beginning

    return final_files