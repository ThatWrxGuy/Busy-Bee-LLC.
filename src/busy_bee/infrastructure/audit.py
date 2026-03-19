from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, path: str = "models/artifacts/audit_log.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {"event_type": event_type, "payload": payload}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
