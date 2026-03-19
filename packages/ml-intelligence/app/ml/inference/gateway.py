from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from busybee_contracts.tenant_context import TenantContext

from app.ml.common.contracts import PredictionRequest, PredictionResult
from app.ml.governance.policy import MLGovernancePolicy
from app.ml.registry.model_registry import ModelRegistry


class InferenceGateway:
    """ML Inference Gateway with TenantContext support.
    
    Every inference call requires explicit TenantContext for audit lineage.
    """
    
    def __init__(self, registry: ModelRegistry, policy: MLGovernancePolicy) -> None:
        self.registry = registry
        self.policy = policy

    def predict(
        self,
        request: PredictionRequest,
        context: "TenantContext | None" = None
    ) -> PredictionResult:
        """Execute prediction with tenant context.
        
        Args:
            request: The prediction request
            context: TenantContext for SaaS mode, None for personal
            
        Returns:
            PredictionResult with audit lineage
        """
        # Validate context for SaaS mode
        if context and context.is_saas:
            context.require_scope()
        
        # Get primary model
        model = self.registry.get(request.task_name)
        health = model.health()

        # Handle drift/unavailable - try fallback
        if health.drift_alert or not health.is_available:
            fallback_task = self._get_fallback_task(request.task_name)
            if fallback_task and self.registry.has(fallback_task):
                fallback = self.registry.get(fallback_task)
                result = fallback.predict(request)
                result.fallback_used = True
                result = self.policy.apply(request, result)
                return self._attach_lineage(result, context)
            raise RuntimeError(f"Model unavailable for task={request.task_name}")

        # Execute prediction
        result = model.predict(request)
        
        # Apply governance policy
        result = self.policy.apply(request, result)
        
        # Attach lineage
        return self._attach_lineage(result, context)
    
    def _attach_lineage(
        self,
        result: PredictionResult,
        context: "TenantContext | None"
    ) -> PredictionResult:
        """Attach tenant context lineage to result."""
        if context:
            result.metadata["tenant_id"] = context.tenant_id
            result.metadata["user_id"] = context.user_id
            result.metadata["mode"] = context.mode
            result.metadata["lineage"] = context.to_lineage()
        
        # Always add prediction timestamp
        result.metadata["lineage_timestamp"] = result.prediction_timestamp.isoformat()
        
        return result
    
    def _get_fallback_task(self, task_name: str) -> str | None:
        """Map task to fallback task."""
        fallback_map = {
            "strategy_score": "baseline_strategy_score",
            "behavior_adherence": "tf_sequence_forecaster",
        }
        return fallback_map.get(task_name)
