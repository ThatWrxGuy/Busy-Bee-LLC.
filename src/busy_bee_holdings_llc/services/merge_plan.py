from __future__ import annotations
from pathlib import Path
import shutil

def import_uploaded_v2(v2_root: str | Path, destination: str | Path) -> Path:
    v2_root = Path(v2_root)
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(v2_root, destination)
    return destination
