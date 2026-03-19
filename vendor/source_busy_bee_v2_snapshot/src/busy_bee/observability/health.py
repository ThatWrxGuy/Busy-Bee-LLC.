from __future__ import annotations

from pathlib import Path


def readiness(model_path: str) -> dict[str, str]:
    status = "ready" if Path(model_path).exists() else "degraded"
    return {"status": status}
