# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Dashboard View DTO - UI-ready dashboard output."""

from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime
import uuid

from app.product.recommendation_dto import ProductRecommendation


@dataclass
class DomainSummary:
    """Summary of a single domain for dashboard."""
    name: str
    score: int  # 0-100
    status: str  # healthy, attention, critical
    pending_actions: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "score": self.score,
            "status": self.status,
            "pending_actions": self.pending_actions,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class SignalSummary:
    """Summary of signals for dashboard."""
    total_signals: int = 0
    critical: int = 0
    warning: int = 0
    info: int = 0
    
    def to_dict(self) -> dict:
        return {
            "total_signals": self.total_signals,
            "critical": self.critical,
            "warning": self.warning,
            "info": self.info,
        }


@dataclass
class DecisionSummary:
    """Summary of decisions for dashboard."""
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    deferred: int = 0
    
    def to_dict(self) -> dict:
        return {
            "pending": self.pending,
            "approved": self.approved,
            "rejected": self.rejected,
            "deferred": self.deferred,
        }


@dataclass
class DashboardView:
    """Dashboard view for frontend consumption.
    
    This DTO provides all data needed for the main dashboard screen.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_status: str = "operational"
    strategic_posture: str = "neutral"
    confidence_score: int = 50
    domains: list[DomainSummary] = field(default_factory=list)
    signals: SignalSummary = field(default_factory=SignalSummary)
    decisions: DecisionSummary = field(default_factory=DecisionSummary)
    top_recommendations: list[ProductRecommendation] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "system_status": self.system_status,
            "strategic_posture": self.strategic_posture,
            "confidence_score": self.confidence_score,
            "domains": [d.to_dict() for d in self.domains],
            "signals": self.signals.to_dict(),
            "decisions": self.decisions.to_dict(),
            "top_recommendations": [r.to_dict() for r in self.top_recommendations],
            "updated_at": self.updated_at.isoformat(),
        }
