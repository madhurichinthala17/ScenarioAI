"""Infer the ScenarioAI file-type label from a path.

Shared by the review entry points (``src.cli.review`` and ``src.cli.apply_review``)
so the ReviewAgent prompt gets a consistent type label regardless of which
CLI invoked it.
"""
from pathlib import Path


def infer_file_type(file_path: str) -> str:
    """Map a generated file path to one of: feature, steps, pom, driver, python."""
    p = Path(file_path)
    if p.suffix == ".feature":
        return "feature"
    if "step" in p.stem or "step" in str(p.parent):
        return "steps"
    if "page" in p.stem or "page" in str(p.parent):
        return "pom"
    if "driver" in p.stem or "helper" in p.stem or "driver" in str(p.parent):
        return "driver"
    return "python"


def page_module_name(pages_file: str) -> str:
    """pages/auth_page.py -> auth_page (the module name steps/driver import)."""
    return pages_file.replace("pages/", "").replace(".py", "")


def page_class_name(pages_file: str) -> str:
    """pages/auth_page.py -> AuthPage.

    Single source of truth for the POM class name. The pom_generator,
    driver_generator and stepdefinition_generator MUST all derive the class
    name the same way, otherwise the driver/steps import a class the POM never
    defined (ImportError at behave --dry-run).
    """
    module = page_module_name(pages_file)
    return "".join(word.capitalize() for word in module.split("_"))
