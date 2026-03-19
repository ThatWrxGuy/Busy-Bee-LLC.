# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""BB-INT-ML-001: Machine Learning Intelligence Layer - Quick Start

This module demonstrates how to use the ML layer for inference.
"""

from app.ml.common.contracts import PredictionRequest, PredictionResult
from app.ml.models.sklearn_models import BaselineStrategyScoreModel
from app.ml.models.tensorflow_models import TensorFlowSequenceModel
from app.ml.registry.model_registry import ModelRegistry
from app.ml.governance.policy import MLGovernancePolicy
from app.ml.inference.gateway import InferenceGateway
from app.ml.features.transforms import FeatureExtractor, FeatureTransformer


def create_ml_system() -> InferenceGateway:
    """Create and configure the ML inference system.
    
    Returns:
        Configured InferenceGateway ready for predictions
    """
    # Create model registry
    registry = ModelRegistry()
    
    # Register baseline (sklearn-compatible) model
    baseline_model = BaselineStrategyScoreModel()
    registry.register(baseline_model)
    
    # Register TensorFlow model
    tf_model = TensorFlowSequenceModel()
    registry.register(tf_model)
    
    # Create governance policy
    policy = MLGovernancePolicy(min_confidence=0.60)
    
    # Create inference gateway
    gateway = InferenceGateway(registry, policy)
    
    return gateway


def demo_strategy_scoring():
    """Demo: Strategy Score Prediction"""
    print("\n" + "="*60)
    print("DEMO: Strategy Score Prediction")
    print("="*60)
    
    gateway = create_ml_system()
    
    # Create a prediction request
    request = PredictionRequest(
        task_name="strategy_score",
        entity_id="user_001",
        features={
            "risk_score": 0.3,
            "readiness_score": 0.8,
            "stability_score": 0.7,
        },
        source_domains=["finance", "career"],
        require_explanation=True
    )
    
    # Get prediction
    result = gateway.predict(request)
    
    print(f"\nTask: {result.task_name}")
    print(f"Entity: {result.entity_id}")
    print(f"Model: {result.model_name} (v{result.model_version})")
    print(f"Prediction: {result.value:.2%}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Top Features: {result.top_features}")
    print(f"Human Review Required: {result.human_review_required}")
    print(f"Fallback Used: {result.fallback_used}")
    print(f"Metadata: {result.metadata}")
    
    return result


def demo_behavior_forecasting():
    """Demo: Behavior Adherence Forecasting"""
    print("\n" + "="*60)
    print("DEMO: Behavior Adherence Forecasting")
    print("="*60)
    
    gateway = create_ml_system()
    
    request = PredictionRequest(
        task_name="behavior_adherence",
        entity_id="user_001",
        features={
            "sequence_strength": 0.75,
            "consistency_score": 0.65,
        },
        source_domains=["health", "career"],
    )
    
    result = gateway.predict(request)
    
    print(f"\nTask: {result.task_name}")
    print(f"Prediction: {result.value:.2%}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Human Review Required: {result.human_review_required}")
    
    return result


def demo_finance_governance():
    """Demo: Finance domain triggers human review"""
    print("\n" + "="*60)
    print("DEMO: Finance Domain Governance")
    print("="*60)
    
    gateway = create_ml_system()
    
    request = PredictionRequest(
        task_name="strategy_score",
        entity_id="user_001",
        features={
            "risk_score": 0.5,
            "readiness_score": 0.7,
            "stability_score": 0.6,
        },
        source_domains=["finance"],  # Finance domain!
    )
    
    result = gateway.predict(request)
    
    print(f"\nSource Domain: {result.source_domains}")
    print(f"Human Review Required: {result.human_review_required}")
    print("✓ Finance predictions require human approval")
    
    return result


def demo_feature_extraction():
    """Demo: Feature extraction from domain data"""
    print("\n" + "="*60)
    print("DEMO: Feature Extraction")
    print("="*60)
    
    # Sample domain data
    domains = {
        "finance": {
            "monthly_spending": 3000,
            "monthly_savings": 1000,
            "debt_payment": 500,
            "income": 6000,
            "emergency_fund": 15000,
            "monthly_expenses": 4000,
        },
        "health": {
            "avg_sleep_hours": 7.5,
            "weekly_exercise_minutes": 180,
            "stress_level": 4,
            "recovery_score": 0.75,
        },
        "career": {
            "daily_focus_hours": 6,
            "task_completion_rate": 0.85,
            "skill_development_score": 0.7,
        }
    }
    
    # Extract features
    features = FeatureExtractor.extract_combined_features(domains)
    print("\nExtracted Features:")
    for key, value in features.items():
        print(f"  {key}: {value}")
    
    # Transform features
    transformed = FeatureTransformer.domain_signal_transform(features)
    print("\nTransformed Features:")
    for key, value in transformed.items():
        print(f"  {key}: {value:.2f}")
    
    return features


def run_all_demos():
    """Run all demonstration functions."""
    print("\n" + "#"*60)
    print("# BB-INT-ML-001: ML Intelligence Layer Demo")
    print("#"*60)
    
    demo_strategy_scoring()
    demo_behavior_forecasting()
    demo_finance_governance()
    demo_feature_extraction()
    
    print("\n" + "#"*60)
    print("# All demos completed!")
    print("#"*60)


if __name__ == "__main__":
    run_all_demos()
