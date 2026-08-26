import json
from collections.abc import Callable

from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file


WORKING_DIRECTORY = "./calculator"


function_map: dict[str, Callable[..., str]] = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}


def call_function(tool_call, verbose: bool = False) -> types.Content:
    name = _get_name(tool_call)
    raw_args = _get_arguments_raw(tool_call)
    args = json.loads(raw_args) if raw_args else {}

    if verbose:
        print(f" - Calling function: {name}({args})")
    else:
        print(f" - Calling function: {name}")

    function = function_map.get(name)
    if function is None:
        error_message = f"Error: Unknown function: {name}"
        if verbose:
            print(f"-> {error_message}")
        return _build_response(tool_call, name, error_message)

    args["working_directory"] = WORKING_DIRECTORY

    try:
        result = function(**args)
    except Exception as e:
        result = f"Error executing {name}: {e}"

    if verbose:
        print(f"-> {result}")

    if not result:
        raise RuntimeError(f"Function {name} returned empty content")

    return _build_response(tool_call, name, result)


def _get_name(tool_call) -> str:
    if hasattr(tool_call, "name") and tool_call.name:
        return tool_call.name
    if hasattr(tool_call, "function") and hasattr(tool_call.function, "name"):
        return tool_call.function.name
    raise AttributeError("tool_call has no name attribute")


def _get_arguments_raw(tool_call) -> str:
    if hasattr(tool_call, "args"):
        if isinstance(tool_call.args, dict):
            return json.dumps(tool_call.args)
        return tool_call.args or "{}"
    if hasattr(tool_call, "function") and hasattr(tool_call.function, "arguments"):
        return tool_call.function.arguments or "{}"
    return "{}"


def _get_tool_call_id(tool_call) -> str | None:
    return getattr(tool_call, "id", None) or getattr(tool_call, "id", None)


def _build_response(tool_call, name: str, result: str) -> types.Content:
    parts = [
        types.Part.from_function_response(
            name=name,
            response={"result": result},
        )
    ]
    return types.Content(
        role="tool" if _get_tool_call_id(tool_call) else "user",
        parts=parts,
    )