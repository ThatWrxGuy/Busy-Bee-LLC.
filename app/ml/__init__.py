# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""
BB-ARCH-PROD-002 Phase 1: Compatibility Shim

This module re-exports from packages.ml_intelligence.app.ml for backward compatibility.
New code should import directly from packages.ml_intelligence.app.ml.

Migration: Nov 2025 - See BB-ARCH-PROD-002 for details.
"""

# Re-export all from the new package location
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
