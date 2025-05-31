from indexer import collect_files
from prompt_builder import build_prompt
from llm_runner import call_ollama
from utils import pretty_print

if __name__ == '__main__':
    project_path = input("Path to your project: ").strip()
    task = input("What do you want to change or add?: ").strip()

    files = collect_files(project_path)
    prompt = build_prompt(files, task)
    
    # --- ADD THIS LINE ---
    print("\n" + "="*30 + " PROMPT SENT TO LLM " + "="*30 + "\n")
    print(prompt)
    print("\n" + "="*70 + "\n")
    # --- END ADDITION ---

    response = call_ollama(prompt)

    pretty_print(response)