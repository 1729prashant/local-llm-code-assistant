import os
from google.genai import types

# Use relative imports for modules within the same package (the 'functions' directory)
from .get_file_content import get_file_content
from .get_files_info import get_files_info
from .run_python import run_python_file
from .write_file import write_file

def call_function(function_call_part, verbose=False):
    """
    Handles the execution of a function based on an LLM's function call suggestion.

    Args:
        function_call_part: A types.FunctionCall object containing the
                            name of the function and its arguments.
        verbose: If True, prints detailed information about the function call and its result.

    Returns:
        A types.Content object with the result of the function call,
        formatted as a function response.
    """
    function_name = function_call_part.name
    function_args = function_call_part.args

    # Print based on verbosity
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    # Define the working directory for security and context
    # This directory is NOT controlled by the LLM
    # Assuming your project's main.py is at the root and 'calculator' is a subdirectory
    # If main.py is run from the root, then use './calculator', test
    working_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "calculator")
    working_directory = os.path.abspath(working_directory) # Resolve to an absolute path


    # Manually add the working_directory to the arguments for the actual function call
    # The LLM doesn't see or provide this argument.
    # Make a mutable copy of the arguments dictionary
    args_for_function_call = dict(function_args)
    args_for_function_call['working_directory'] = working_directory

    function_result = None
    # Based on the function name, call the corresponding Python function
    if function_name == "get_file_content":
        function_result = get_file_content(**args_for_function_call)
    elif function_name == "get_files_info":
        function_result = get_files_info(**args_for_function_call)
    elif function_name == "run_python_file":
        function_result = run_python_file(**args_for_function_call)
    elif function_name == "write_file":
        function_result = write_file(**args_for_function_call)
    else:
        # If the function name is not recognized, return an error
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # Return the result of the function call, formatted for the LLM
    # The result is wrapped in a dictionary with a "result" key as required
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

