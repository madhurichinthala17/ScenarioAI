import os

GENERATED_TESTS_DIR = "generated_tests"
FOLDERS = ["features", "step_definitions", "pages", "driver"]


def ensure_folders_exist():
    for folder in FOLDERS:
        os.makedirs(os.path.join(GENERATED_TESTS_DIR, folder), exist_ok=True)