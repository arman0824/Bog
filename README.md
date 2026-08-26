# Bog AI Agent

A command-line AI coding agent which can we run via Google's API key. Bog can autonomously inspect, read, edit, and execute code in a project through a tool-calling loop.

## Features

- File and directory listing
- File reading and writing
- Python file execution
- Iterative tool-use loop with the model (up to 20 iterations per prompt)
- Verbose mode for token usage and step tracing
- Path sandboxing — all operations are confined to a working directory

## Tech Stack

- Python 3
- Google Gemini API (`google-genai`)
- `uv` for dependency management

## Setup

1. Clone the repository.
2. Create a `.env` file with your Gemini API key:

   ```
   GEMINI_API_KEY=your_key_here
   ```

3. Install dependencies:

   ```
   uv sync
   ```

4. Change Gemini model from config.py

## Usage

```
uv run main.py "your prompt here"
uv run main.py "your prompt here" --verbose
```

### Example Prompts

- `uv run main.py "list files in the calculator directory"`
- `uv run main.py "read main.py in calculator" --verbose`
- `uv run main.py "run tests.py"`
- `uv run main.py "write hello world to notes.txt"`

## Architecture

- `main.py` — entry point, agent loop, and message history management
- `call_function.py` — dispatches model tool calls to the correct function
- `functions/` — tool implementations (`get_files_info`, `get_file_content`, `run_python_file`, `write_file`) and their Gemini function schemas

## Try It: End-to-End Agent Workflow

The `runtime_test/` folder contains a `calculator` subfolder with a small sample program you can use to see the full agent loop in action.

1. Open one of the files in `runtime_test/calculator/` and break the code.
2. Run the agent and let it diagnose and fix the issue:

   ```
   uv run main.py "fix the calculator for me"
   ```

3. Use `--verbose` to watch each tool call and token usage:

   ```
   uv run main.py "fix the calculator for me" --verbose
   ```

The agent will list the directory, read files, run the tests, edit the broken code, and re-run the tests to confirm the fix — all without any further input.