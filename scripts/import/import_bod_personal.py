# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Import helper for the public BOD-personal Busy-Bee-V1.3 branch.

This script is intentionally conservative: it does not auto-download code during packaging.
Run it in a network-enabled environment only if you are authorized to import the upstream repo.
"""
from pathlib import Path
import subprocess
import shutil

REPO_URL = "https://github.com/ThatWrxGuy/BOD-personal.git"
BRANCH = "Busy-Bee-V1.3"

def main() -> None:
    target = Path("vendor/source_bod_personal_snapshot")
    if target.exists():
        shutil.rmtree(target)
    subprocess.run([
        "git", "clone", "--depth", "1", "--branch", BRANCH, REPO_URL, str(target)
    ], check=True)
    print(f"Imported {REPO_URL}@{BRANCH} -> {target}")

if __name__ == "__main__":
    main()
