# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Feature transforms for ML pipeline."""

from typing import Any, Dict
import numpy as np


class FeatureTransformer:
    """Transform raw features for ML models."""
    
    @staticmethod
    def normalize_score(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Normalize a score to 0-1 range."""
        return max(min_val, min(max_val, (value - min_val) / (max_val - min_val)))
    
    @staticmethod
    def compute_lag_features(values: list[float], lags: list[int] = [1, 3, 7]) -> Dict[str, float]:
        """Compute lagged features for time-series."""
        result = {}
        for lag in lags:
            if len(values) >= lag:
                result[f"lag_{lag}"] = values[-lag]
                if len(values) >= lag + 1:
                    result[f"diff_{lag}"] = values[-1] - values[-lag]
            else:
                result[f"lag_{lag}"] = 0.0
                result[f"diff_{lag}"] = 0.0
        return result
    
    @staticmethod
    def compute_rolling_stats(values: list[float], window: int = 7) -> Dict[str, float]:
        """Compute rolling statistics."""
        if len(values) < window:
            return {"mean": np.mean(values) if values else 0.0, "std": 0.0}
        recent = values[-window:]
        return {"mean": np.mean(recent), "std": np.std(recent)}
    
    @staticmethod
    def domain_signal_transform(features: Dict[str, Any]) -> Dict[str, float]:
        """Transform domain signals to model features."""
        transformed = {}
        
        # Finance domain transforms
        if "spending_rate" in features:
            transformed["spending_normalized"] = FeatureTransformer.normalize_score(
                features["spending_rate"], 0, 10000
            )
        if "savings_rate" in features:
            transformed["savings_normalized"] = FeatureTransformer.normalize_score(
                features["savings_rate"], 0, 5000
            )
        
        # Health domain transforms
        if "sleep_hours" in features:
            transformed["sleep_score"] = FeatureTransformer.normalize_score(
                features["sleep_hours"], 4, 10
            )
        if "exercise_minutes" in features:
            transformed["exercise_score"] = FeatureTransformer.normalize_score(
                features["exercise_minutes"], 0, 120
            )
        
        # Career domain transforms
        if "focus_hours" in features:
            transformed["focus_score"] = FeatureTransformer.normalize_score(
                features["focus_hours"], 0, 12
            )
        
        # Normalize all domain scores to 0-1
        for key in ["readiness_score", "stability_score", "risk_score", "consistency_score"]:
            if key in features:
                transformed[key] = FeatureTransformer.normalize_score(features[key])
        
        return transformed


class FeatureExtractor:
    """Extract features from domain data."""
    
    @staticmethod
    def extract_finance_features(finance_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from finance domain."""
        return {
            "spending_rate": finance_data.get("monthly_spending", 0),
            "savings_rate": finance_data.get("monthly_savings", 0),
            "debt_ratio": finance_data.get("debt_payment", 0) / max(finance_data.get("income", 1), 1),
            "emergency_fund_months": finance_data.get("emergency_fund", 0) / max(finance_data.get("monthly_expenses", 1), 1),
        }
    
    @staticmethod
    def extract_health_features(health_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from health domain."""
        return {
            "sleep_hours": health_data.get("avg_sleep_hours", 7),
            "exercise_minutes": health_data.get("weekly_exercise_minutes", 0),
            "stress_level": health_data.get("stress_level", 5),
            "recovery_score": health_data.get("recovery_score", 0.5),
        }
    
    @staticmethod
    def extract_career_features(career_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from career domain."""
        return {
            "focus_hours": career_data.get("daily_focus_hours", 0),
            "task_completion_rate": career_data.get("task_completion_rate", 0),
            "skill_development_score": career_data.get("skill_development_score", 0),
        }
    
    @staticmethod
    def extract_combined_features(domains: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Extract and combine features from all domains."""
        features = {}
        
        if "finance" in domains:
            features.update(FeatureExtractor.extract_finance_features(domains["finance"]))
        if "health" in domains:
            features.update(FeatureExtractor.extract_health_features(domains["health"]))
        if "career" in domains:
            features.update(FeatureExtractor.extract_career_features(domains["career"]))
        
        return features
