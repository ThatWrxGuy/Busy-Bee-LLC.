from __future__ import annotations

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
