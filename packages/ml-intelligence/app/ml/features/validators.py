from __future__ import annotations

from typing import Any, Dict, List


def validate_probability_feature(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")


class FeatureValidator:
    """Validate features before ML inference."""
    
    REQUIRED_FEATURES = {
        "strategy_score": ["risk_score", "readiness_score", "stability_score"],
        "behavior_adherence": ["sequence_strength", "consistency_score"],
    }
    
    @staticmethod
    def validate(requested_features: Dict[str, Any], task_name: str) -> bool:
        """Validate features for a given task."""
        required = FeatureValidator.REQUIRED_FEATURES.get(task_name, [])
        for feature in required:
            if feature not in requested_features:
                raise ValueError(f"Missing required feature: {feature}")
        
        # Validate probability features are in range
        for key, value in requested_features.items():
            if "score" in key or "rate" in key:
                validate_probability_feature(value, key)
        
        return True
    
    @staticmethod
    def get_required_features(task_name: str) -> List[str]:
        """Get required features for a task."""
        return FeatureValidator.REQUIRED_FEATURES.get(task_name, [])
