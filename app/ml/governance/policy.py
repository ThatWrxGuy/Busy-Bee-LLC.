from __future__ import annotations

from app.ml.common.contracts import PredictionRequest, PredictionResult


class MLGovernancePolicy:
    def __init__(self, min_confidence: float = 0.60) -> None:
        self.min_confidence = min_confidence

    def apply(self, request: PredictionRequest, result: PredictionResult) -> PredictionResult:
        if "finance" in [d.lower() for d in request.source_domains]:
            result.human_review_required = True

        if result.confidence < self.min_confidence:
            result.metadata["advisory_only"] = True

        return result
