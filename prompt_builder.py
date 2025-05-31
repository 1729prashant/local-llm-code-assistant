def build_prompt(files, task_description):
    prompt = f"You are an expert developer. The user wants this change:\n\n{task_description}\n\n"
    prompt += "Here are the relevant project files:\n"

    for path in files:
        try:
            with open(path, 'r') as f:
                content = f.read()
            prompt += f"\n===== FILE: {path} =====\n{content}\n"
        except Exception as e:
            prompt += f"\n[Could not read file: {path}]\n"

    prompt += "\nPlease provide the updated code by showing diffs or full file replacements."
    return prompt
