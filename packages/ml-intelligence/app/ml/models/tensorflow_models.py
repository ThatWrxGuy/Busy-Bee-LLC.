from __future__ import annotations

from dataclasses import dataclass

from app.ml.common.contracts import ModelHealth, PredictionRequest, PredictionResult
from app.ml.models.base import MLModel


@dataclass
class TensorFlowSequenceModel(MLModel):
    name: str = "tf_sequence_forecaster"
    version: str = "0.1.0"
    task_name: str = "behavior_adherence"
    endpoint_name: str = "busy-bee-tf-sequence"

    def predict(self, request: PredictionRequest) -> PredictionResult:
        sequence_strength = float(request.features.get("sequence_strength", 0.5))
        consistency = float(request.features.get("consistency_score", 0.5))
        value = max(0.0, min(1.0, 0.55 * sequence_strength + 0.45 * consistency))
        return PredictionResult(
            task_name=self.task_name,
            entity_id=request.entity_id,
            model_name=self.name,
            model_version=self.version,
            value=value,
            confidence=0.71,
            source_domains=request.source_domains,
            top_features=["sequence_strength", "consistency_score"],
            metadata={"framework": "tensorflow", "endpoint": self.endpoint_name, "mode": "stub"},
        )

    def health(self) -> ModelHealth:
        return ModelHealth(model_name=self.name, model_version=self.version, is_available=True)
