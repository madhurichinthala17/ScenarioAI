import os

GENERATED_TESTS_DIR = "generated_tests"
FOLDERS = ["features", "step_definitions", "pages", "driver"]


def ensure_folders_exist():
    for folder in FOLDERS:
        os.makedirs(os.path.join(GENERATED_TESTS_DIR, folder), exist_ok=True)


def scan_existing_files() -> dict:
    existing = {}
    for folder in FOLDERS:
        path = os.path.join(GENERATED_TESTS_DIR, folder)
        if not os.path.exists(path):
            continue
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    existing[os.path.join(folder, filename)] = f.read()
    return existing


def write_file(relative_path: str, content: str):
    full_path = os.path.join(GENERATED_TESTS_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)


def list_feature_files() -> list:
    path = os.path.join(GENERATED_TESTS_DIR, "features")
    if not os.path.exists(path):
        return []
    return [os.path.join("features", f) for f in os.listdir(path) if f.endswith(".feature")]