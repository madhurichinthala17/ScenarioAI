import os
from pathlib import Path

from src.core.exceptions import FileWriteError
from src.core.logger import get_logger
from src.utils.file_scanner import GENERATED_TESTS_DIR

log = get_logger(__name__)

# Header injected at the top of every file when fail_open=True.
# Immediately visible when a reviewer opens the file in GitHub's diff view.
_WARNING_HEADER = """\
# =============================================================================
# WARNING: ScenarioAI validation failed — this file was written as FAIL-OPEN
# Review the errors listed in the PR description before merging.
# =============================================================================

"""


class FileWriterAgent:

    def run(self, state: dict, fail_open: bool = False) -> dict:
        file_plan = state["file_plan"]
        decision = file_plan["decision"]

        log.info("Node: file_writer [decision=%s, fail_open=%s]", decision.upper(), fail_open)

        if decision == "skip":
            log.info("File writer: skipping — all scenarios already exist")
            return {"files_written": [], "fail_open": fail_open}

        files_written = []

        pairs = [
            (state.get("gherkin"),        file_plan["feature_file"],  False),
            (state.get("pom_content"),     file_plan["pages_file"],    True),
            (state.get("driver_content"),  file_plan["driver_file"],   True),
            (state.get("steps_content"),   file_plan["steps_file"],    True),
        ]

        for content, relative_path, is_python in pairs:
            if not content:
                continue
            try:
                self._write(relative_path, content, decision, fail_open and is_python)
                files_written.append(relative_path)
                log.info("  wrote: generated_tests/%s", relative_path)
            except FileWriteError as e:
                log.error("File write failed: %s", e)
                raise

        log.info("File writer: wrote %d file(s)", len(files_written))
        return {"files_written": files_written, "fail_open": fail_open}

    def _write(self, relative_path: str, content: str, decision: str, add_warning: bool):
        base = Path(GENERATED_TESTS_DIR).resolve()
        target = (base / relative_path).resolve()

        # Path traversal guard: ensure the resolved path is still inside generated_tests/
        # An LLM could theoretically return "../../etc/passwd" as a filename.
        if not str(target).startswith(str(base)):
            raise FileWriteError(f"Path traversal blocked: {relative_path}")

        target.parent.mkdir(parents=True, exist_ok=True)

        final_content = (_WARNING_HEADER + content) if add_warning else content

        if decision == "insert" and target.exists():
            with open(target, "a", encoding="utf-8") as f:
                f.write("\n\n" + final_content)
        else:
            with open(target, "w", encoding="utf-8") as f:
                f.write(final_content)
