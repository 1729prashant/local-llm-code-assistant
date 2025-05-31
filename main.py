from indexer import collect_files, filter_files_by_keywords
from prompt_builder import build_prompt
from llm_runner import call_ollama
from utils import pretty_print
import os

if __name__ == '__main__':
    project_path = input("Path to your project: ").strip()
    task = input("What do you want to change or add?: ").strip()

    if not os.path.isdir(project_path):
        print(f"Error: Project path '{project_path}' does not exist or is not a directory.")
        exit(1)

    print("\n--- Collecting project files... ---")
    all_files = collect_files(project_path)
    print(f"Found {len(all_files)} total files matching extensions.")

    # Apply keyword filtering for a more focused context
    # Adjust top_n based on your model's context window and project size
    print("\n--- Filtering files based on task relevance (rudimentary RAG)... ---")
    # MODIFIED: Pass project_path to the function
    relevant_files = filter_files_by_keywords(all_files, task, project_path, top_n=15)
    print(f"Selected {len(relevant_files)} potentially relevant files for context.")
    if not relevant_files:
        print("Warning: No relevant files found. The LLM might struggle without context.")
        print("Consider refining your task description or manually specifying files.")

    print("\nSelected files (relative paths):")
    for f in relevant_files:
        print(f"- {os.path.relpath(f, project_path)}")

    print("\n--- Building prompt for LLM... ---")
    prompt = build_prompt(relevant_files, task)

    print("\n" + "="*25 + " PROMPT SENT TO LLM " + "="*25 + "\n")
    print(prompt)
    print("\n" + "="*70 + "\n")

    confirm = input("Press Enter to send to LLM, or 'q' to quit and review prompt: ").strip().lower()
    if confirm == 'q':
        print("Exiting without calling LLM.")
        exit()

    print("\n--- Calling local LLM (ollama)... This may take a moment. ---")
    response = call_ollama(prompt)

    pretty_print(response)