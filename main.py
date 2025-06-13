# main.py
import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.call_function import call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
parser = argparse.ArgumentParser(description='Gemini CLI prompt with API')
parser.add_argument("prompt", type=str, help="Prompt to send to Gemini")
parser.add_argument('-v','--verbose', action="store_true")
args = parser.parse_args()


# --- Defining the LLM's Tools (Function Declarations) ---
# This is like writing a "user manual" for each tool your robot body has,
# so the LLM brain knows what it can ask the robot to do.

# Notice 'working_directory' is *NOT* in these declarations.
# This means the LLM brain DOES NOT see, understand, or try to specify
# 'working_directory'. It's completely abstracted away from the LLM.
# Your robot body (your script) handles this context *after* the LLM asks for an action.

get_file_content_tool = types.FunctionDeclaration(
    name="get_file_content", # The name the LLM will use to refer to this tool
    description="Gets the content of a file from the specified file path.", # What the tool does (for the LLM to understand its purpose)
    parameters=types.Schema( # Defines the inputs the tool expects
        type=types.Type.OBJECT, # It expects a set of named parameters
        properties={
            "file_path": types.Schema(type=types.Type.STRING, description="The path to the file to read.")
            # 'working_directory' is deliberately absent here!
        },
        #required=["file_path"] # Which of these parameters *must* the LLM provide?
    )
)

get_files_info_tool = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files and directories within a specified directory or the current working directory. Use path relative to the working directory if aboslute path not specified",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(type=types.Type.STRING, description="The directory to list files from, relative to the working directory. If not provided, lists the current working directory.")
        },
        #required=[] # 'directory' is optional, so nothing is strictly required here.
    )
)

run_python_file_tool = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file, relative to working or current directory ",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(type=types.Type.STRING, description="The filename of the Python script to execute, e.g., 'script.py', 'folder/test.py'. Always ues relative paths")
        },
        required=["file_path"]
    )
)

write_file_tool = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file path. Use path relative to the working directory if aboslute path not specified. Creates the file if it doesn't exist, overwrites if it does.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(type=types.Type.STRING, description="The path to the file to write."),
            "content": types.Schema(type=types.Type.STRING, description="The content to write into the file.")
        },
        #required=["file_path", "content"]
    )
)

# This list is like gathering all the "user manuals" into one binder.

available_functions = types.Tool(
    function_declarations=[
    get_file_content_tool,
    get_files_info_tool,
    run_python_file_tool,
    write_file_tool    ]
)


system_prompt_alternate_not_working = """You are a helpful coding assistant. Your primary goal is to assist the user by using the available tools whenever their request can be fulfilled by a tool.
When calling functions, you only need to provide the parameters explicitly listed in the tool's description.
Do NOT try to specify a 'working_directory'; the user's local script will handle that context.
Always prioritize using a tool if it directly addresses the user's request.
"""
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""


if args.prompt.startswith('--'):
    print("Error: Prompt must be the first argument.")
    sys.exit(1)

client = genai.Client(api_key=api_key)
prompt_content = args.prompt

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt_content)])
]
response = client.models.generate_content(
    model='gemini-2.0-flash-001', 
    contents=messages,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt, # Pass the high-level instructions
        tools=[available_functions]             # You give the LLM the "manuals" for its tools. Now the LLM knows it *can* suggest using these functions.
        )
)
# print('Response: ', response.text)
# --- Interpreting the LLM's Response ---
# This is the robot body receiving a message back from the LLM brain.
# The brain might either:
#   a) Give you pure text (an answer, explanation, etc.)
#   b) Suggest an action (a "tool call") for your robot body to perform.

if response.candidates: # Check if the LLM provided any response (it usually does)
    candidate = response.candidates[0] # Get the primary response
    if candidate.content.parts: # Responses can have multiple "parts" (text, function calls)
        for part in candidate.content.parts:
            if part.text:
                print('Response (Text): ', part.text) # LLM gave a text response
            elif part.function_call:
                # The LLM suggested a function call, so we execute it
                function_call_result = call_function(part.function_call, verbose=args.verbose)

                # Validate the structure of the returned Content object
                if not (function_call_result and
                        function_call_result.parts and
                        function_call_result.parts[0].function_response and
                        function_call_result.parts[0].function_response.response):
                    raise ValueError("Unexpected structure in function_call_result from call_function.")

                # If verbose, print the result of the function call
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")

            else:
                print('Response part is not text or function call:', part)
    else:
        print("Response has no content parts.")
else:
    print("No candidates in response.")


if args.verbose:
    print('User prompt:',prompt_content)
    print('Prompt tokens:',str(response.usage_metadata.prompt_token_count))
    print('Response tokens:',str(response.usage_metadata.candidates_token_count))
else:
    pass