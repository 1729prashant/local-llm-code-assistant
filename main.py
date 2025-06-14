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
            "file_path": types.Schema(type=types.Type.STRING, description="The path to the file to read, relative to the working directory.")
                                    # 'working_directory' is deliberately absent here!
        },
        #required=["file_path"] # Which of these parameters *must* the LLM provide?
    )
)

get_files_info_tool = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files and directories within a specified directory or the current working directory. Paths should be relative to the working directory.",
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
    description="Executes a Python file. The file path should be relative to the working or current directory.",
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
    description="Writes content to a specified file path. Use path relative to the working directory if absolute path not specified. Creates the file if it doesn't exist, overwrites if it does.",
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
    write_file_tool    
    ]
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

All paths you provide should be relative to the working directory. 

When asked to fix a bug, always start by:
1. Exploring the project structure to understand what you're working with
2. Running any executables to reproduce the issue
3. Reading the relevant source code to identify the problem
4. Making the necessary code changes
5. Testing to confirm the fix works

"fix the bug" means "investigate and repair the code," not "create a workaround."
"""


if args.prompt.startswith('--'):
    print("Error: Prompt must be the first argument.")
    sys.exit(1)

client = genai.Client(api_key=api_key)
prompt_content = args.prompt

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt_content)])
]

# --- Multi-Turn Conversation Loop ---
# This loop allows the agent to interact with the LLM in multiple turns,
# executing tool calls and feeding results back, until the LLM provides a final text response
# or a maximum number of iterations is reached.
MAX_ITERATIONS = 20 # Limit to prevent infinite loops

for i in range(MAX_ITERATIONS):
    # Flag to track if a function was called in the current iteration.
    # If no function is called, it means the LLM has provided a final text response.
    function_called_in_this_turn = False

    # Make the API call to generate content.
    # The entire `messages` list is passed to maintain the conversation history.
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages, # Crucially, pass the entire accumulated message history
        config=types.GenerateContentConfig(
            system_instruction=system_prompt, # High-level instructions for the model
            tools=[available_functions]        # Inform the model about available tools
        )
    )

    # Check if the LLM provided any response candidates
    if not response.candidates:
        print("No candidates in response. LLM might be done or encountered an issue.")
        break # Exit the loop if no response is received

    # Get the primary response candidate from the LLM
    candidate = response.candidates[0]

    # Process each part of the LLM's response
    if candidate.content.parts:
        for part in candidate.content.parts:
            # Check if the part is a function call suggested by the LLM
            if part.function_call:
                # If a function call is suggested, execute it using our `call_function` handler.
                function_call_result = call_function(part.function_call, verbose=args.verbose)

                # Validate the structure of the `types.Content` object returned by `call_function`.
                # This ensures we received a valid function response.
                if not (function_call_result and
                        function_call_result.parts and
                        function_call_result.parts[0].function_response and
                        function_call_result.parts[0].function_response.response):
                    raise ValueError("Unexpected structure in function_call_result from call_function.")

                # If verbose mode is enabled, print the result of the function call.
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")

                # Append the LLM's suggested function call to the messages history.
                # This shows the LLM's intent to call a tool.
                messages.append(types.Content(role="model", parts=[part]))
                
                # Append the *result* of the function call (the tool's response) to the messages history.
                # This is crucial for the LLM to understand the outcome of its action and plan the next step.
                messages.append(function_call_result)
                
                # Mark that a function was called in this turn, indicating the loop should continue.
                function_called_in_this_turn = True

            # If the part is a text response from the LLM
            elif part.text:
                # Append the LLM's text response to the messages history.
                messages.append(types.Content(role="model", parts=[part]))
                # Print the LLM's final text response (or intermediate text).
                print('Response (Text): ', part.text)
                
    else:
        # If the LLM's response has no parts (neither text nor function call), it's an unexpected scenario.
        print("Response has no content parts.")
        break # Exit the loop

    # --- Loop Continuation Logic ---
    # If a function was called in this turn, we continue the loop
    # to allow the LLM to process the tool's output and potentially make another call.
    if function_called_in_this_turn:
        # Continue to the next iteration to send the updated message history back to the LLM.
        continue
    else:
        # If no function was called, it means the LLM has provided its final text response
        # or it couldn't make a function call. In either case, we break the loop.
        break

# --- Final Output (for verbose mode) ---
# Print token usage if verbose mode is enabled.
if args.verbose:
    print('User prompt:', prompt_content)
    # Check if usage_metadata exists before accessing
    if response.usage_metadata:
        print('Prompt tokens:', str(response.usage_metadata.prompt_token_count))
        print('Response tokens:', str(response.usage_metadata.candidates_token_count))
else:
    pass