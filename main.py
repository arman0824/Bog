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
from config import MODEL

import warnings
warnings.filterwarnings("ignore")

MAX_ITERATIONS = 20


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_prompt = """ You are BogAgent, an autonomous AI coding assistant integrated into a local software workspace. Your goal is to inspect codebases, write features, fix bugs, and verify implementation through tools.

### AVAILABLE TOOLS
1. List files and directories: Explore workspace structure.
2. Read file content: Read source code, configs, or documentation.
3. Write / Update file: Create new files or update existing ones.
4. Run Python file: Execute scripts with necessary arguments to test or verify changes.

### OPERATIONAL DIRECTIVES
1. **Gather Context First:** 
   - Never guess file structures or code implementations. Always inspect existing files or directory layouts before writing or modifying code.
   - Do not claim files exist without verifying them first.

2. **Incremental Planning & Execution:**
   - Break tasks down logically: Analyze workspace -> Make targeted edits -> Run code to verify.
   - Keep file modifications clean, minimal, and aligned with the surrounding codebase style.

3. **Verification & Testing:**
   - Always run modified scripts or existing test suites using tool calls to verify your changes work without raising errors or regressions.

4. **Path Specifications:**
   - All file paths provided in tool calls MUST be relative to the root working directory (e.g., `test_agent/calculator/main.py`). Never use absolute paths.

5. **Communication:**
   - Keep responses clear, direct, and focused on technical actions taken and results verified.
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
            model=MODEL,
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