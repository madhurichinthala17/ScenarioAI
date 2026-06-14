import ast
import re
import subprocess
import tempfile
import os
from typing import List
from behave.parser import Parser


class ValidatorAgent:

    def run(
        self,
        gherkin: str,
        pom_content: str,
        driver_content: str,
        steps_content: str
    ) -> dict:
        errors = []

        errors.extend(self._check_gherkin_syntax(gherkin))
        errors.extend(self._check_python_syntax(pom_content, "POM"))
        errors.extend(self._check_python_syntax(driver_content, "Driver"))
        errors.extend(self._check_python_syntax(steps_content, "Steps"))
        errors.extend(self._check_pom_purity(pom_content))
        errors.extend(self._check_step_purity(steps_content))
        errors.extend(self._check_step_coverage(gherkin, steps_content))
        errors.extend(self._check_method_existence(pom_content, steps_content))
        errors.extend(self._check_driver_existence(driver_content, steps_content))
        errors.extend(self._lint_python(pom_content, "POM"))
        errors.extend(self._lint_python(steps_content, "Steps"))

        passed = len(errors) == 0

        if passed:
            print("Validator: All checks passed")
        else:
            print(f"Validator: {len(errors)} error(s) found")
            for error in errors:
                print(f"  - {error}")

        return {
            "passed": passed,
            "errors": errors
        }

    # ─── Gherkin checks ───────────────────────────────────────────

    def _check_gherkin_syntax(self, gherkin: str) -> List[str]:
        errors = []
        try:
            parser = Parser()
            parser.parse(gherkin)
        except Exception as e:
            errors.append(f"Gherkin syntax error: {e}")
            return errors

        # Additional structural checks
        scenarios = re.split(r"Scenario:", gherkin)[1:]
        if not scenarios:
            errors.append("Gherkin: No scenarios found")

        for i, scenario in enumerate(scenarios, 1):
            if "Given" not in scenario:
                errors.append(f"Gherkin: Scenario {i} missing Given step")
            if "When" not in scenario:
                errors.append(f"Gherkin: Scenario {i} missing When step")
            if "Then" not in scenario:
                errors.append(f"Gherkin: Scenario {i} missing Then step")

        return errors

    # ─── Python syntax checks ─────────────────────────────────────

    def _check_python_syntax(self, code: str, label: str) -> List[str]:
        errors = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(
                f"{label} syntax error at line {e.lineno}: {e.msg}"
            )
        return errors

    # ─── POM purity ───────────────────────────────────────────────

    def _check_pom_purity(self, pom_content: str) -> List[str]:
        errors = []
        forbidden = ["assert ", "expect(", "should_be", "to_be_visible"]
        for pattern in forbidden:
            if pattern in pom_content:
                errors.append(
                    f"POM purity: Found '{pattern}' — assertions not allowed in page objects"
                )
        return errors

    # ─── Step purity ──────────────────────────────────────────────

    def _check_step_purity(self, steps_content: str) -> List[str]:
        errors = []
        forbidden_playwright = [
            "page.click", "page.fill",
            "page.goto", "page.locator",
            "page.get_by"
        ]
        for pattern in forbidden_playwright:
            if pattern in steps_content:
                errors.append(
                    f"Step purity: Found '{pattern}' — direct Playwright calls not allowed in step definitions"
                )
        return errors

    # ─── Step coverage ────────────────────────────────────────────

    def _check_step_coverage(
        self, gherkin: str, steps_content: str
    ) -> List[str]:
        errors = []

        # Extract all step texts from Gherkin
        step_lines = re.findall(
            r"^\s+(?:Given|When|Then|And|But)\s+(.+)$",
            gherkin,
            re.MULTILINE
        )

        # Extract all decorator texts from step definitions
        decorator_texts = re.findall(
            r'@(?:given|when|then)\(["\'](.+?)["\']\)',
            steps_content,
            re.IGNORECASE
        )

        for step in step_lines:
            step_clean = step.strip()
            matched = any(
                step_clean.lower() == d.lower()
                for d in decorator_texts
            )
            if not matched:
                errors.append(
                    f"Step coverage: No step definition for '{step_clean}'"
                )

        return errors

    # ─── Method existence ─────────────────────────────────────────

    def _check_method_existence(
        self, pom_content: str, steps_content: str
    ) -> List[str]:
        errors = []

        # Extract all method names from POM
        pom_methods = re.findall(
            r"def (\w+)\(", pom_content
        )
        pom_methods = set(pom_methods) - {"__init__"}

        # Find all page object method calls in step definitions
        # Pattern: context.<page_object>.<method>()
        called_methods = re.findall(
            r"context\.\w+\.(\w+)\(",
            steps_content
        )

        for method in called_methods:
            if method not in pom_methods:
                errors.append(
                    f"Method existence: Step calls '{method}' but it does not exist in POM"
                )

        return errors

    # ─── Driver function existence ────────────────────────────────

    def _check_driver_existence(
        self, driver_content: str, steps_content: str
    ) -> List[str]:
        errors = []

        # Extract all function names from driver
        driver_functions = set(re.findall(
            r"^def (\w+)\(", driver_content, re.MULTILINE
        ))

        # Find all driver function calls in step definitions
        # Pattern: perform_<name>() or setup_<name>()
        called_functions = re.findall(
            r"\b(perform_\w+|setup_\w+)\(",
            steps_content
        )

        for func in called_functions:
            if func not in driver_functions:
                errors.append(
                    f"Driver existence: Step calls '{func}' but it does not exist in driver"
                )

        return errors

    # ─── Ruff linting ─────────────────────────────────────────────

    def _lint_python(self, code: str, label: str) -> List[str]:
        errors = []
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8"
            ) as f:
                f.write(code)
                tmp_path = f.name

            if label == "Steps":
                select = ["E"]
                ignore = ["E501", "E302", "E303"]
            else:
                select = ["E", "F"]
                ignore = ["E501"]

            result = subprocess.run(
                ["ruff", "check", tmp_path,
                 "--select", ",".join(select),
                 "--ignore", ",".join(ignore),
                 "--quiet"],
                capture_output=True,
                text=True
            )

            os.unlink(tmp_path)

            if result.returncode != 0:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        clean = re.sub(r".+\.py:", f"{label}:", line)
                        errors.append(f"Lint: {clean}")

        except Exception as e:
            errors.append(f"Lint: Could not run ruff — {e}")

        return errors