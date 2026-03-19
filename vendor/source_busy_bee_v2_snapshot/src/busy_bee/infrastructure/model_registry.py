from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ModelRegistry:
    def __init__(self, registry_path: str) -> None:
        self.path = Path(registry_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def register(self, record: dict[str, Any]) -> None:
        existing: list[dict[str, Any]] = []
        if self.path.exists():
            existing = json.loads(self.path.read_text(encoding="utf-8"))
        existing.append(record)
        self.path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
