# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Product Recommendation DTO - Standardized recommendation contract."""

from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime
import uuid


RecommendationStatus = Literal[
    "generated", "presented", "approved", "rejected", "deferred",
    "converted_to_action", "completed", "outcome_recorded"
]

UrgencyLevel = Literal["critical", "high", "medium", "low"]


@dataclass
class ProductRecommendation:
    """Standard recommendation contract for product output.
    
    This DTO enforces the mandatory format for all recommendations
    surfaced through the ExecutiveOrchestrator.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""
    title: str = ""
    why: str = ""  # Why this recommendation exists
    impact: str = ""  # Expected impact if acted upon
    urgency: UrgencyLevel = "medium"
    action_text: str = ""  # Human-readable action
    requires_approval: bool = True
    confidence: int = 50  # 0-100
    risk_if_ignored: str = ""
    status: RecommendationStatus = "generated"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "why": self.why,
            "impact": self.impact,
            "urgency": self.urgency,
            "action_text": self.action_text,
            "requires_approval": self.requires_approval,
            "confidence": self.confidence,
            "risk_if_ignored": self.risk_if_ignored,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    def present(self) -> "ProductRecommendation":
        """Mark as presented to user."""
        self.status = "presented"
        self.updated_at = datetime.utcnow()
        return self
    
    def approve(self) -> "ProductRecommendation":
        """Mark as approved by user."""
        self.status = "approved"
        self.updated_at = datetime.utcnow()
        return self
    
    def reject(self) -> "ProductRecommendation":
        """Mark as rejected by user."""
        self.status = "rejected"
        self.updated_at = datetime.utcnow()
        return self
    
    def defer(self) -> "ProductRecommendation":
        """Mark as deferred by user."""
        self.status = "deferred"
        self.updated_at = datetime.utcnow()
        return self
    
    def convert_to_action(self) -> "ProductRecommendation":
        """Mark as converted to action."""
        self.status = "converted_to_action"
        self.updated_at = datetime.utcnow()
        return self
    
    def complete(self) -> "ProductRecommendation":
        """Mark as completed."""
        self.status = "completed"
        self.updated_at = datetime.utcnow()
        return self
    
    def record_outcome(self) -> "ProductRecommendation":
        """Mark as outcome recorded."""
        self.status = "outcome_recorded"
        self.updated_at = datetime.utcnow()
        return self
