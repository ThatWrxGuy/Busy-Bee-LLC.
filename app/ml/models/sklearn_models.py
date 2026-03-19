from __future__ import annotations

from dataclasses import dataclass

from app.ml.common.contracts import ModelHealth, PredictionRequest, PredictionResult
from app.ml.models.base import MLModel


@dataclass
class BaselineStrategyScoreModel(MLModel):
    name: str = "baseline_strategy_score"
    version: str = "0.1.0"
    task_name: str = "strategy_score"

    def predict(self, request: PredictionRequest) -> PredictionResult:
        risk = float(request.features.get("risk_score", 0.5))
        readiness = float(request.features.get("readiness_score", 0.5))
        stability = float(request.features.get("stability_score", 0.5))
        value = max(0.0, min(1.0, (0.45 * readiness) + (0.35 * stability) - (0.20 * risk)))
        return PredictionResult(
            task_name=self.task_name,
            entity_id=request.entity_id,
            model_name=self.name,
            model_version=self.version,
            value=value,
            confidence=0.62,
            source_domains=request.source_domains,
            top_features=["readiness_score", "stability_score", "risk_score"],
            metadata={"framework": "sklearn-compatible-baseline", "kind": "heuristic_stub"},
        )

    def health(self) -> ModelHealth:
        return ModelHealth(model_name=self.name, model_version=self.version, is_available=True)
