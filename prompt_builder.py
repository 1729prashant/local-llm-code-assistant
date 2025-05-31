def build_prompt(files, task_description):
    prompt = f"You are an expert developer assistant specializing in providing code changes. "
    prompt += f"Your goal is to help the user implement the following feature or make the following change:\n\n"
    prompt += f"**TASK**: {task_description}\n\n"

    prompt += "The user has provided the following relevant project files for context. "
    prompt += "Please analyze them carefully to understand the existing codebase and implement the requested changes. "
    prompt += "Focus on providing only the necessary modifications to achieve the task.\n\n"

    for path in files:
        try:
            with open(path, 'r') as f:
                content = f.read()
            prompt += f"\n===== FILE: {path} =====\n```\n{content}\n```\n" # Use code blocks
        except Exception as e:
            prompt += f"\n[Could not read file: {path} - Error: {e}]\n"

    prompt += "\n**RESPONSE FORMAT**: "
    prompt += "Please provide the updated code by showing either **diffs** (preferred for modifications) or **full file replacements** (for new files or significant rewrites). "
    prompt += "If you provide a full file replacement, clearly indicate the file path. "
    prompt += "If no changes are needed, state that explicitly. "
    prompt += "Ensure your response is clear, concise, and directly addresses the task.\n"
    prompt += "--- START CODING ASSISTANT RESPONSE ---\n" # Clear demarcation for LLM output
    return prompt