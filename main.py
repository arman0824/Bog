import os
import sys
import warnings
from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import call_function
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from config import MODEL

warnings.filterwarnings("ignore")

MAX_ITERATIONS = 20


def run_agent_turn(client, messages, config, verbose_flag):
    """Executes a single agent reasoning and tool execution loop."""
    for iteration in range(MAX_ITERATIONS):
        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=config,
        )

        if response is None or response.usage_metadata is None:
            print("[Error] Response is malformed.")
            return None

        if verbose_flag:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        assistant_content = response.candidates[0].content
        
        messages.append(assistant_content)

        if not response.function_calls:
            text_parts = [
                part.text 
                for part in response.candidates[0].content.parts 
                if part.text
            ]
            return "".join(text_parts) if text_parts else None


        for tool_call in response.function_calls:
            try:
                function_response = call_function(tool_call, verbose=verbose_flag)
            except Exception as e:
                print(
                    f"[Error] call_function failed at iteration {iteration} for "
                    f"{getattr(tool_call, 'name', '?')}: {e}"
                )
                return None

            if not function_response.parts or not function_response.parts[0].function_response.response.get("result"):
                print(f"[Error] Empty function response from {getattr(tool_call, 'name', '?')}")
                return None

            messages.append(function_response)

    print(f"[Warning] Max iterations ({MAX_ITERATIONS}) reached for this turn.")
    return None


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_prompt = """ You are Bog, an autonomous AI coding assistant integrated into a local software workspace. Your goal is to inspect codebases, write features, fix bugs, and verify implementation through tools.

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

    verbose_flag = "--verbose" in sys.argv

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

    messages = []

    print("--- Bog, Interactive Workspace Session ---")
    print("Type 'exit' or 'quit' to close the session.\n")

    initial_prompt = None
    args = [arg for arg in sys.argv[1:] if arg != "--verbose"]
    if args:
        initial_prompt = " ".join(args)

    while True:
        try:
            if initial_prompt:
                user_input = initial_prompt
                print(f"User > {user_input}")
                initial_prompt = None
            else:
                user_input = input("User > ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Exiting Bog session.")
                break

            messages.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

            final_response = run_agent_turn(client, messages, config, verbose_flag)

            if final_response:
                print(f"\nBog > {final_response}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Exiting.")
            break


if __name__ == "__main__":
    main()