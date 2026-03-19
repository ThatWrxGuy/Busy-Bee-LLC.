from __future__ import annotations

from abc import ABC, abstractmethod

from app.ml.common.contracts import PredictionRequest, PredictionResult, ModelHealth


class MLModel(ABC):
    name: str
    version: str
    task_name: str

    @abstractmethod
    def predict(self, request: PredictionRequest) -> PredictionResult:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> ModelHealth:
        raise NotImplementedError
