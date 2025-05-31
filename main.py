from indexer import collect_files
from prompt_builder import build_prompt
from llm_runner import call_ollama
from utils import pretty_print

if __name__ == '__main__':
    project_path = input("Path to your project: ").strip()
    task = input("What do you want to change or add?: ").strip()

    files = collect_files(project_path)
    prompt = build_prompt(files, task)
    response = call_ollama(prompt)

    pretty_print(response)
