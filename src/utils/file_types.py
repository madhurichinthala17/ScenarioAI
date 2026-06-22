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
