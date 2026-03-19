from __future__ import annotations

from typing import Dict

from app.ml.models.base import MLModel


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, MLModel] = {}

    def register(self, model: MLModel) -> None:
        self._models[model.task_name] = model

    def get(self, task_name: str) -> MLModel:
        return self._models[task_name]

    def has(self, task_name: str) -> bool:
        return task_name in self._models
