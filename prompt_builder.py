from indexer import get_file_type # Import the new function
import os

def build_prompt(files, task_description):
    prompt = f"You are an expert software developer and a helpful AI assistant. "
    prompt += f"Your primary goal is to assist the user by providing code modifications or new code to implement a requested feature or fix.\n\n"
    
    prompt += f"The user has a project and wants to make the following changes:\n\n"
    prompt += f"--- BEGIN TASK DESCRIPTION ---\n"
    prompt += f"{task_description}\n"
    prompt += f"--- END TASK DESCRIPTION ---\n\n"

    prompt += "To help you, here are the contents of relevant files from the project. "
    prompt += "Analyze these files to understand the existing structure, logic, and context necessary to perform the task. "
    prompt += "Focus on the provided context, but infer common project structures if necessary.\n\n"

    # Add file contents with annotations
    for path in files:
        file_type = get_file_type(path)
        relative_path = os.path.relpath(path, os.getcwd()) # Make path relative for cleaner prompt
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            prompt += f"\n===== FILE: {relative_path} (Type: {file_type}) =====\n"
            prompt += f"```\n{content}\n```\n" # Use code blocks
        except Exception as e:
            prompt += f"\n[Could not read file: {relative_path} - Error: {e}]\n"

    prompt += "\n--- IMPORTANT INSTRUCTIONS FOR YOUR RESPONSE ---\n"
    prompt += "1.  **Output Format**: Provide your response as a series of code blocks. For each change, clearly indicate the file path. You can provide:\n"
    prompt += "    * **Diffs**: Recommended for modifications to existing files. Use standard unified diff format (lines starting with `---`, `+++`, `-`, `+`, ` `).\n"
    prompt += "    * **Full File Replacement**: If a file needs extensive changes or is new, provide the entire new content. Clearly state `REPLACE FILE: <path>` or `NEW FILE: <path>`.\n"
    prompt += "    * **Instructions**: Add brief explanations or instructions where necessary, but keep them concise and to the point. Place them *outside* code blocks.\n"
    prompt += "2.  **Focus**: Only provide code relevant to the task. Avoid conversational filler or apologies. If you are unsure, state your assumptions.\n"
    prompt += "3.  **No Changes**: If you believe no changes are needed or the task is impossible with the given context, state that clearly and briefly explain why.\n"
    prompt += "4.  **Assumptions**: If you make any assumptions (e.g., about data models, API endpoints), clearly state them.\n"
    prompt += "\n--- BEGIN PROPOSED CHANGES ---\n"
    return prompt