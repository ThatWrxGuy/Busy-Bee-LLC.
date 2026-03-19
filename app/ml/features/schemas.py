from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StrategyScoreFeatures:
    risk_score: float
    readiness_score: float
    stability_score: float


@dataclass(slots=True)
class BehaviorAdherenceFeatures:
    sequence_strength: float
    consistency_score: float
