from __future__ import annotations

from app.ml.common.contracts import PredictionRequest, PredictionResult
from app.ml.governance.policy import MLGovernancePolicy
from app.ml.registry.model_registry import ModelRegistry


class InferenceGateway:
    def __init__(self, registry: ModelRegistry, policy: MLGovernancePolicy) -> None:
        self.registry = registry
        self.policy = policy

    def predict(self, request: PredictionRequest, fallback_task_name: str | None = None) -> PredictionResult:
        model = self.registry.get(request.task_name)
        health = model.health()

        if health.drift_alert or not health.is_available:
            if fallback_task_name and self.registry.has(fallback_task_name):
                fallback = self.registry.get(fallback_task_name)
                result = fallback.predict(request)
                result.fallback_used = True
                return self.policy.apply(request, result)
            raise RuntimeError(f"Model unavailable for task={request.task_name}")

        result = model.predict(request)
        return self.policy.apply(request, result)
