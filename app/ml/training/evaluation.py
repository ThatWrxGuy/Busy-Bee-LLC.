from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EvaluationSnapshot:
    metric_name: str
    metric_value: float
    split_name: str
    model_name: str
    model_version: str
