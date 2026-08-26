import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import call_function
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file


MAX_ITERATIONS = 20


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read content to a file
    - Write to a file (Read or Update)
    - Run a python file with optimal Arguments

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    if len(sys.argv) < 2:
        print("I need a prompt")
        sys.exit(1)

    prompt = sys.argv[1]

    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt,
    )

    final_response = None

    for iteration in range(MAX_ITERATIONS):
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=messages,
            config=config,
        )

        if response is None or response.usage_metadata is None:
            print("Response is malformed")
            return

        if verbose_flag:
            print(f"User prompt: {prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        if not response.function_calls:
            final_response = response.text
            break

        assistant_content = response.candidates[0].content
        messages.append(assistant_content)

        for tool_call in response.function_calls:
            try:
                function_response = call_function(tool_call, verbose=verbose_flag)
            except Exception as e:
                raise RuntimeError(
                    f"call_function failed at iteration {iteration} for "
                    f"{getattr(tool_call, 'name', '?')}: {e}"
                )

            if not function_response.parts or not function_response.parts[0].function_response.response.get("result"):
                raise RuntimeError(f"Empty function response from {getattr(tool_call, 'name', '?')}")

            messages.append(function_response)

    if final_response is None:
        print(f"Max iterations ({MAX_ITERATIONS}) reached without a final response. Exiting.")
        sys.exit(1)

    print("Final response:")
    print(final_response)


main()