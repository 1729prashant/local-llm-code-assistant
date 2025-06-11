import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
parser = argparse.ArgumentParser(description='Gemini CLI prompt with API')
parser.add_argument("prompt", type=str, help="Prompt to send to Gemini")
parser.add_argument('-v','--verbose', action="store_true")
args = parser.parse_args()

if args.prompt.startswith('--'):
    print("Error: Prompt must be the first argument.")
    sys.exit(1)

client = genai.Client(api_key=api_key)
prompt_content = args.prompt

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt_content)])
]
response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents=messages
)
print('Response: ', response.text)

if args.verbose:
    print('User prompt:',prompt_content)
    print('Prompt tokens:',str(response.usage_metadata.prompt_token_count))
    print('Response tokens:',str(response.usage_metadata.candidates_token_count))
else:
    pass
