import os
from src.utils.file_scanner import write_file, GENERATED_TESTS_DIR


class FileWriterAgent:

    def run(self, state: dict) -> dict:
        file_plan = state['file_plan']
        decision = file_plan['decision']

        print(f"--- File Writer --- [{decision.upper()}]")

        if decision == "skip":
            print("⏭️  Skipping — all scenarios already exist")
            return {"files_written": []}

        files_written = []

        # Write feature file
        if state.get('gherkin'):
            self._write(
                file_plan['feature_file'],
                state['gherkin'],
                decision
            )
            files_written.append(file_plan['feature_file'])

        # Write POM
        if state.get('pom_content'):
            self._write(
                file_plan['pages_file'],
                state['pom_content'],
                decision
            )
            files_written.append(file_plan['pages_file'])

        # Write driver
        if state.get('driver_content'):
            self._write(
                file_plan['driver_file'],
                state['driver_content'],
                decision
            )
            files_written.append(file_plan['driver_file'])

        # Write step definitions
        if state.get('steps_content'):
            self._write(
                file_plan['steps_file'],
                state['steps_content'],
                decision
            )
            files_written.append(file_plan['steps_file'])

        print(f"Written {len(files_written)} files:")
        for f in files_written:
            print(f"   → generated_tests/{f}")

        return {"files_written": files_written}

    def _write(self, relative_path: str, content: str, decision: str):
        """
        Write content based on decision type.
        CREATE/OVERWRITE → write fresh
        INSERT → append new content to existing file
        """
        full_path = os.path.join(GENERATED_TESTS_DIR, relative_path)

        if decision == "insert" and os.path.exists(full_path):
            with open(full_path, "a", encoding="utf-8") as f:
                f.write("\n\n")
                f.write(content)
        else:
            write_file(relative_path, content)