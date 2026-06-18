import ast
import re
import shutil
import subprocess
import tempfile
import os
from typing import List
from behave.parser import Parser
from src.core.logger import get_logger

log = get_logger(__name__)


class ValidatorAgent:

    def run(
        self,
        gherkin: str,
        pom_content: str,
        driver_content: str,
        steps_content: str
    ) -> dict:
        # ── Phase 1: fast, in-process checks ─────────────────────────
        log.info("Validator phase 1: static checks")
        phase1_errors = []
        phase1_errors.extend(self._check_gherkin_syntax(gherkin))
        phase1_errors.extend(self._check_python_syntax(pom_content, "POM"))
        phase1_errors.extend(self._check_python_syntax(driver_content, "Driver"))
        phase1_errors.extend(self._check_python_syntax(steps_content, "Steps"))
        phase1_errors.extend(self._check_pom_purity(pom_content))
        phase1_errors.extend(self._check_step_purity(steps_content))
        phase1_errors.extend(self._check_step_coverage(gherkin, steps_content))
        phase1_errors.extend(self._check_method_existence(pom_content, steps_content))
        phase1_errors.extend(self._check_driver_existence(driver_content, steps_content))
        phase1_errors.extend(self._lint_python(pom_content, "POM"))
        phase1_errors.extend(self._lint_python(steps_content, "Steps"))

        if phase1_errors:
            log.warning("Phase 1: %d error(s) — skipping phase 2", len(phase1_errors))
            for e in phase1_errors:
                log.warning("  - %s", e)
            return {"passed": False, "errors": phase1_errors, "phase": 1}

        log.info("Phase 1: all checks passed")

        # ── Phase 2: behave --dry-run in isolated temp directory ──────
        # Only runs when phase 1 is clean — no point running behave
        # if the code has syntax errors or purity violations
        log.info("Validator phase 2: behave --dry-run")
        phase2_errors = self._validate_phase2(gherkin, pom_content, driver_content, steps_content)

        if phase2_errors:
            log.warning("Phase 2: %d error(s)", len(phase2_errors))
            for e in phase2_errors:
                log.warning("  - %s", e)
            return {"passed": False, "errors": phase2_errors, "phase": 2}

        log.info("Phase 2: all checks passed")
        return {"passed": True, "errors": [], "phase": 2}

    # ─── Phase 2: behave --dry-run ────────────────────────────────

    def _validate_phase2(
        self,
        gherkin: str,
        pom_content: str,
        driver_content: str,
        steps_content: str,
    ) -> List[str]:
        errors = []
        temp_dir = tempfile.mkdtemp(prefix="scenarioai_")

        try:
            # Build the directory structure behave expects:
            #   features/   → .feature files
            #   steps/      → step definition files
            #   pages/      → page object modules (imported by steps)
            #   driver/     → driver/helper modules (imported by steps)
            features_dir = os.path.join(temp_dir, "features")
            steps_dir    = os.path.join(temp_dir, "steps")
            pages_dir    = os.path.join(temp_dir, "pages")
            driver_dir   = os.path.join(temp_dir, "driver")

            for d in [features_dir, steps_dir, pages_dir, driver_dir]:
                os.makedirs(d)

            # Write the generated gherkin as the feature file
            with open(os.path.join(features_dir, "test.feature"), "w", encoding="utf-8") as f:
                f.write(gherkin)

            # Write step definitions — behave auto-discovers files in steps/
            with open(os.path.join(steps_dir, "steps.py"), "w", encoding="utf-8") as f:
                f.write(steps_content)

            # Resolve imports: parse the step file to find which modules it imports
            # e.g. "from pages.auth_page import LoginPage" → module name = "auth_page"
            # We write the POM/driver content under exactly those names so imports resolve
            page_modules   = re.findall(r"from pages\.(\w+)\s+import", steps_content)
            driver_modules = re.findall(r"from driver\.(\w+)\s+import", steps_content)

            # __init__.py makes pages/ and driver/ proper Python packages
            open(os.path.join(pages_dir,  "__init__.py"), "w").close()
            open(os.path.join(driver_dir, "__init__.py"), "w").close()

            for module_name in page_modules:
                with open(os.path.join(pages_dir, f"{module_name}.py"), "w", encoding="utf-8") as f:
                    f.write(pom_content)

            for module_name in driver_modules:
                with open(os.path.join(driver_dir, f"{module_name}.py"), "w", encoding="utf-8") as f:
                    f.write(driver_content)

            # If no imports were found, write files with generic names as fallback
            if not page_modules:
                with open(os.path.join(pages_dir, "page.py"), "w", encoding="utf-8") as f:
                    f.write(pom_content)
            if not driver_modules:
                with open(os.path.join(driver_dir, "driver.py"), "w", encoding="utf-8") as f:
                    f.write(driver_content)

            # environment.py: behave runs before_scenario before each scenario.
            # We mock context.page so step definitions that touch it don't crash
            # during the dry run (--dry-run skips execution but still imports everything)
            env_content = (
                "from unittest.mock import MagicMock\n\n"
                "def before_scenario(context, scenario):\n"
                "    context.page = MagicMock()\n"
                "    context.browser = MagicMock()\n"
            )
            with open(os.path.join(temp_dir, "environment.py"), "w", encoding="utf-8") as f:
                f.write(env_content)

            # Run behave --dry-run from inside the temp directory.
            # PYTHONPATH=temp_dir ensures "from pages.auth_page import" resolves
            # to the files we just wrote, not the real project
            result = subprocess.run(
                ["behave", "--dry-run", "--no-capture", "--format", "plain", "features/"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": temp_dir},
            )

            if result.returncode != 0:
                output = (result.stdout + result.stderr).strip()
                for line in output.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if "Undefined step" in line:
                        errors.append(f"Phase 2 — Undefined step: {line}")
                    elif "ImportError" in line or "ModuleNotFoundError" in line:
                        errors.append(f"Phase 2 — Import error: {line}")
                    elif line.startswith("Error") or "Exception" in line:
                        errors.append(f"Phase 2 — {line}")

                # If behave gave us output but nothing matched our patterns,
                # surface the raw output so the error is never silently swallowed
                if not errors and output:
                    errors.append(f"Phase 2 — behave --dry-run failed:\n{output[:500]}")

        except Exception as e:
            errors.append(f"Phase 2 — validation could not run: {e}")

        finally:
            # Always clean up the temp dir, even if we crashed above
            shutil.rmtree(temp_dir, ignore_errors=True)

        return errors

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