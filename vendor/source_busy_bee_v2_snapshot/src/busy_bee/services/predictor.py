from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from pydantic import BaseModel

from busy_bee.exceptions import ArtifactNotFoundError


class PredictorService:
    def __init__(self, model_path: str) -> None:
        path = Path(model_path)
        if not path.exists():
            raise ArtifactNotFoundError(f"Model artifact not found: {path}")
        self.pipeline = joblib.load(path)

    def predict_one(self, payload: BaseModel) -> Any:
        frame = pd.DataFrame([payload.model_dump()])
        return self.pipeline.predict(frame)[0]

    def predict_many(self, rows: list[dict[str, Any]]) -> list[Any]:
        frame = pd.DataFrame(rows)
        return self.pipeline.predict(frame).tolist()
