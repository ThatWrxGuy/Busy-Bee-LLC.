# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Executive Brief DTO - Standardized executive output contract."""

from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime
import uuid

from app.product.recommendation_dto import ProductRecommendation


SystemStatus = Literal["operational", "degraded", "offline", "learning"]
StrategicPosture = Literal["offensive", "defensive", "neutral", "opportunistic"]


@dataclass
class DomainScore:
    """Domain scoring for executive view."""
    domain: str
    score: int  # 0-100
    trend: str = "stable"  # improving, declining, stable
    summary: str = ""


@dataclass
class ExecutiveSystemView:
    """System status and posture for executive consumption."""
    system_status: SystemStatus = "operational"
    strategic_posture: StrategicPosture = "neutral"
    top_priorities: list[str] = field(default_factory=list)
    critical_risks: list[str] = field(default_factory=list)
    domain_scores: dict[str, int] = field(default_factory=dict)
    recommendations: list[ProductRecommendation] = field(default_factory=list)
    confidence_score: int = 50  # 0-100
    
    def to_dict(self) -> dict:
        return {
            "system_status": self.system_status,
            "strategic_posture": self.strategic_posture,
            "top_priorities": self.top_priorities,
            "critical_risks": self.critical_risks,
            "domain_scores": self.domain_scores,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "confidence_score": self.confidence_score,
        }


@dataclass
class ExecutiveBrief:
    """Standardized executive brief contract.
    
    This is the primary output format for CEO-level consumption.
    All intelligence MUST be compressed into this format.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_view: ExecutiveSystemView = field(default_factory=ExecutiveSystemView)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    period: str = ""  # e.g., "Q1 2026", "Weekly", "Daily"
    title: str = "Executive Brief"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "period": self.period,
            "generated_at": self.generated_at.isoformat(),
            "system_view": self.system_view.to_dict(),
        }
    
    @property
    def status(self) -> str:
        """Shorthand for system status."""
        return self.system_view.system_status
    
    @property
    def posture(self) -> str:
        """Shorthand for strategic posture."""
        return self.system_view.strategic_posture
    
    @property
    def priorities(self) -> list[str]:
        """Shorthand for top priorities."""
        return self.system_view.top_priorities
    
    @property
    def risks(self) -> list[str]:
        """Shorthand for critical risks."""
        return self.system_view.critical_risks
    
    @property
    def actions(self) -> list[ProductRecommendation]:
        """Shorthand for recommendations."""
        return self.system_view.recommendations
