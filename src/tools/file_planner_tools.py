import os
from langchain_core.tools import tool
from src.utils.file_scanner import GENERATED_TESTS_DIR


@tool
def scan_directory() -> str:
    """List all existing test files in generated_tests/ folders."""
    files = []
    for folder in ["features", "step_definitions", "pages", "driver"]:
        path = os.path.join(GENERATED_TESTS_DIR, folder)
        if os.path.exists(path):
            for filename in os.listdir(path):
                files.append(os.path.join(folder, filename))
    if not files:
        return "No existing files found."
    return "\n".join(files)


@tool
def read_file(relative_path: str) -> str:
    """Read the contents of a specific file from generated_tests/.
    
    Args:
        relative_path: path relative to generated_tests/ e.g. features/auth.feature
    """
    full_path = os.path.join(GENERATED_TESTS_DIR, relative_path)
    if not os.path.exists(full_path):
        return f"File not found: {relative_path}"
    with open(full_path, "r") as f:
        return f.read()


FILE_PLANNER_TOOLS = [scan_directory, read_file]