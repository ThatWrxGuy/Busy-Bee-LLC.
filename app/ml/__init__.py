# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""
BB-ARCH-PROD-002 Phase 1: Compatibility Shim

This module provides backward compatibility for imports from app/ml.
New code should import directly from packages.ml_intelligence.app.ml.

Migration: Nov 2025 - See BB-ARCH-PROD-002 for details.
"""

# Import from the new package location when available
try:
    from packages.ml_intelligence.app.ml.common.contracts import (
        PredictionRequest,
        PredictionResult,
        ModelHealth,
    )
    from packages.ml_intelligence.app.ml.models.base import MLModel
    from packages.ml_intelligence.app.ml.models.sklearn_models import BaselineStrategyScoreModel
    from packages.ml_intelligence.app.ml.models.tensorflow_models import TensorFlowSequenceModel
    from packages.ml_intelligence.app.ml.registry.model_registry import ModelRegistry
    from packages.ml_intelligence.app.ml.governance.policy import MLGovernancePolicy
    from packages.ml_intelligence.app.ml.inference.gateway import InferenceGateway
except ImportError:
    # Fallback for development/testing - define minimal stubs
    from dataclasses import dataclass, field
    from datetime import datetime, timezone
    from typing import Any, Dict, List, Optional
    
    @dataclass(slots=True)
    class PredictionRequest:
        task_name: str
        entity_id: str
        features: Dict[str, Any]
        source_domains: List[str]
        require_explanation: bool = True

    @dataclass(slots=True)
    class PredictionResult:
        task_name: str
        entity_id: str
        model_name: str
        model_version: str
        value: float
        confidence: float
        prediction_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
        source_domains: List[str] = field(default_factory=list)
        top_features: List[str] = field(default_factory=list)
        fallback_used: bool = False
        human_review_required: bool = False
        metadata: Dict[str, Any] = field(default_factory=dict)

    @dataclass(slots=True)
    class ModelHealth:
        model_name: str
        model_version: str
        is_available: bool
        drift_alert: bool = False
        notes: Optional[str] = None

    class MLModel:
        name: str = ""
        version: str = ""
        task_name: str = ""
        
        def predict(self, request: PredictionRequest) -> PredictionResult:
            raise NotImplementedError
        
        def health(self) -> ModelHealth:
            return ModelHealth(self.name, self.version, True)

    class BaselineStrategyScoreModel(MLModel):
        name: str = "baseline_strategy_score"
        version: str = "0.1.0"
        task_name: str = "strategy_score"

    class TensorFlowSequenceModel(MLModel):
        name: str = "tf_sequence_forecaster"
        version: str = "0.1.0"
        task_name: str = "behavior_adherence"

    class ModelRegistry:
        def __init__(self) -> None:
            self._models: Dict[str, MLModel] = {}
        
        def register(self, model: MLModel) -> None:
            self._models[model.task_name] = model
        
        def get(self, task_name: str) -> MLModel:
            return self._models[task_name]
        
        def has(self, task_name: str) -> bool:
            return task_name in self._models

    class PlanUpgradeRequired(Exception):
        """Raised when action requires plan upgrade."""
        pass

    class MLGovernancePolicy:
        def __init__(self, min_confidence: float = 0.60) -> None:
            self.min_confidence = min_confidence
        
        # Capability matrix
        CAPABILITY_MATRIX = {
            "free": {"finance": ["read"], "health": ["read"], "career": ["read"]},
            "pro": {"finance": ["read", "simulate"], "health": ["read", "track"], "career": ["read", "plan"]},
            "enterprise": {"finance": ["read", "simulate", "execute"], "health": ["read", "track", "execute"], "career": ["read", "plan", "execute"]},
        }
        
        def check_capability(self, domain: str, action: str, context) -> bool:
            """Check if context has capability."""
            plan = context.plan_tier if context else "free"
            allowed = self.CAPABILITY_MATRIX.get(plan, {}).get(domain.lower(), [])
            if action not in allowed:
                if plan == "free":
                    raise PlanUpgradeRequired(f"{domain} {action} requires Pro")
                return False
            return True
        
        def check_billing_access(self, tenant_id, feature: str) -> bool:
            """Check billing access."""
            if not tenant_id:
                return False
            try:
                from infrastructure.billing.stripe_service import get_billing_manager
                manager = get_billing_manager()
                return manager.check_feature_access(tenant_id, feature)
            except Exception:
                return False
        
        def apply(self, request: PredictionRequest, result: PredictionResult) -> PredictionResult:
            return result
        
        def requires_human_review(self, domain: str, context=None) -> bool:
            """Check if a domain requires human review."""
            if domain.lower() == "finance":
                return True
            return False

    class InferenceGateway:
        def __init__(self, registry: ModelRegistry, policy: MLGovernancePolicy) -> None:
            self.registry = registry
            self.policy = policy
        
        def predict(self, request: PredictionRequest, context=None) -> PredictionResult:
            # Validate context for SaaS mode
            if context and context.is_saas:
                context.require_scope()
            
            model = self.registry.get(request.task_name)
            result = model.predict(request)
            
            # Apply policy
            result = self.policy.apply(request, result)
            
            # Attach lineage
            if context:
                result.metadata["tenant_id"] = context.tenant_id
                result.metadata["user_id"] = context.user_id
                result.metadata["mode"] = context.mode
            
            return result

__all__ = [
    "PredictionRequest",
    "PredictionResult",
    "ModelHealth",
    "MLModel",
    "BaselineStrategyScoreModel",
    "TensorFlowSequenceModel",
    "ModelRegistry",
    "MLGovernancePolicy",
    "InferenceGateway",
]
