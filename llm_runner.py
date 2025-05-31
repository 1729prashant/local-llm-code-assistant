import subprocess

def call_ollama(prompt, model='qwen2.5-coder:7b'):
    cmd = ['ollama', 'run', model]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=prompt.encode())
    return stdout.decode() if stdout else stderr.decode()