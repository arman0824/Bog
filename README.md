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